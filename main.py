
import sys
import os
import json
import argparse
from dotenv import load_dotenv
from openai import OpenAI

from prompts import system_prompt     

from call_function import available_functions, call_function


def generate_content(client, messages, verbose):
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        tools=available_functions,
        temperature=0,
    )

    if response.usage is None:
        raise RuntimeError(
            "No usage data found in response. The API call may have failed."
        )

    if verbose:
       
        print(f"Prompt tokens: {response.usage.prompt_tokens}")
        print(f"Response tokens: {response.usage.completion_tokens}")

    message = response.choices[0].message
    messages.append(message)

    if message.tool_calls:
        for tool_call in message.tool_calls:
            result_message = call_function(tool_call, verbose)

            if not result_message["content"]:
                raise Exception(f"Fatal error calling function {tool_call.function.name}")

            if verbose:
                print(f"-> {result_message['content']}")
            messages.append(result_message)
        return None

    else:
        return message.content


def main():
    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY not found. Make sure you have a .env file "
            "with OPENROUTER_API_KEY set."
        )

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")

    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt},
    ]

    for _ in range(20):
        final_response = generate_content(client, messages, args.verbose)
        if final_response is not None:
            print("Final response:")
            print(final_response)
            return
    
    print("Error: Maximum iterations reached without a final response")
    sys.exit(1)

if __name__ == "__main__":
    main()