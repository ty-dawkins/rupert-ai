# api.py - HTTP wrapper around Rupert so it can be called over the network instead of just the CLI

import os
import uuid
import logging
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel

from prompts import system_prompt
from call_function import available_functions, call_function
from main import generate_content  # reusing the same agent logic as the CLI
from database import init_db, save_message, load_conversation, conversation_exists

load_dotenv()
api_key = os.environ.get("OPENROUTER_API_KEY")
rupert_api_key = os.environ.get("RUPERT_API_KEY")  # secret key required to call this API

logging.basicConfig(
    filename="requests.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
)

app = FastAPI()

init_db()  # creates the messages table if it doesn't exist yet, runs once on startup


@app.get("/health")
def health_check():
    return {"status": "ok"}


class PromptRequest(BaseModel):
    prompt: str
    conversation_id: str | None = None  # omit this to start a new conversation


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != rupert_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.post("/agent")
def run_agent(request: PromptRequest, _: None = Depends(verify_api_key)):
    logging.info(f"PROMPT: {request.prompt}")

    # look up existing conversation in the database, or start a new one
    if request.conversation_id and conversation_exists(request.conversation_id):
        conversation_id = request.conversation_id
        messages = load_conversation(conversation_id)
    else:
        conversation_id = str(uuid.uuid4())
        messages = [{"role": "system", "content": system_prompt}]
        save_message(conversation_id, "system", system_prompt)

    save_message(conversation_id, "user", request.prompt)
    messages.append({"role": "user", "content": request.prompt})

    try:
        # agent may need multiple tool calls (reading/writing files, etc.)
        # before it has a final answer, so loop until it does or we hit a cap of 20
        for _ in range(20):
            final_response = generate_content(client, messages, verbose=False)
            if final_response is not None:
                logging.info(f"RESPONSE: {final_response}")
                save_message(conversation_id, "assistant", final_response)
                return {"response": final_response, "conversation_id": conversation_id}

        logging.info("RESPONSE: Max iterations reached, no final response")
        return {"response": "Error: Maximum iterations reached without a final response"}

    except Exception as e:
        # log the real error for debugging, but don't leak internal details to the caller
        logging.error(f"AGENT ERROR: {e}")
        raise HTTPException(
            status_code=502,
            detail="The AI service is currently unavailable. Please try again in a moment.",
        )