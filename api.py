# api.py - HTTP wrapper around Rupert so it can be called over the network instead of just the CLI

import os
import logging
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel

from prompts import system_prompt
from call_function import available_functions, call_function
from main import generate_content  # reusing the same agent logic as the CLI

load_dotenv()
api_key = os.environ.get("OPENROUTER_API_KEY")
rupert_api_key = os.environ.get("RUPERT_API_KEY")  # secret key required to call this API

# logs every request to a file, so past prompts/responses are recoverable for debugging
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


# simple endpoint to confirm the server is running - no auth needed,
# since monitoring tools typically check this before anything else
@app.get("/health")
def health_check():
    return {"status": "ok"}


# defines what a valid request body looks like: {"prompt": "..."}
# FastAPI validates this automatically and rejects anything malformed
class PromptRequest(BaseModel):
    prompt: str


# checks the incoming request for a valid API key before letting it through
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != rupert_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.post("/agent")
def run_agent(request: PromptRequest, _: None = Depends(verify_api_key)):
    logging.info(f"PROMPT: {request.prompt}")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": request.prompt},
    ]

    # agent may need multiple tool calls (reading/writing files, etc.)
    # before it has a final answer, so loop until it does or we hit a cap
    for _ in range(20):
        final_response = generate_content(client, messages, verbose=False)
        if final_response is not None:
            logging.info(f"RESPONSE: {final_response}")
            return {"response": final_response}

    logging.info("RESPONSE: Max iterations reached, no final response")
    return {"response": "Error: Maximum iterations reached without a final response"}