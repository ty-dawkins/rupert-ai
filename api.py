# api.py - wraps Rupert's agent loop in a FastAPI server so it can be called over HTTP instead of only through the CLI (see main.py)

import os
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI
from pydantic import BaseModel

from prompts import system_prompt
from call_function import available_functions, call_function
from main import generate_content  # reusing the same agent logic as the CLI

load_dotenv()
api_key = os.environ.get("OPENROUTER_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
)

app = FastAPI()


# defines what a valid request body looks like: {"prompt": "..."}
# FastAPI validates this automatically and rejects anything problematic
class PromptRequest(BaseModel):
    prompt: str


@app.post("/agent")
def run_agent(request: PromptRequest):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": request.prompt},
    ]

    # agent may need multiple tool calls (reading/writing files, etc.)
    # before it has a final answer, so loop until it does or we hit a cap...
    for _ in range(20):
        final_response = generate_content(client, messages, verbose=False)
        if final_response is not None:
            return {"response": final_response}

    return {"response": "Error: Maximum iterations reached without a final response"}