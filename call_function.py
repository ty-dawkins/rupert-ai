import json
from collections.abc import Callable

from functions.get_files_info import get_files_info, schema_get_files_info
from functions.get_file_content import get_file_content, schema_get_file_content
from functions.write_file import write_file, schema_write_file
from functions.run_python_file import run_python_file, schema_run_python_file
from functions.web_search import web_search, schema_web_search


available_functions = [
    schema_get_files_info,
    schema_get_file_content,
    schema_write_file,
    schema_run_python_file,
    schema_web_search,
]

function_map: dict[str, Callable[..., str]] = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file,
    "web_search": web_search,
}

# only these touch the local filesystem, so only these get sandboxed to
# ./calculator and web_search reaches out to the live internet instead
FUNCTIONS_NEEDING_WORKING_DIRECTORY = {
    "get_files_info",
    "get_file_content",
    "write_file",
    "run_python_file",
}


def call_function(tool_call, verbose: bool = False) -> dict:
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments or "{}")
    if verbose:
        print(f" - Calling function: {function_name}({function_args})")
    else:
        print(f" - Calling function: {function_name}")

    if function_name not in function_map:
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": f"Error: Unknown function: {function_name}",
        }

    if function_name in FUNCTIONS_NEEDING_WORKING_DIRECTORY:
        function_args["working_directory"] = "./calculator"

    # NEW: the model can hallucinate arguments that don't match a function's
    # real signature. That used to crash the whole agent loop with a raw
    # TypeError and now it turns into a normal error message the model can
    # see and self-correct from on its next turn.
    try:
        function_result = function_map[function_name](**function_args)
    except TypeError as e:
        function_result = f"Error: invalid arguments for {function_name}: {e}"

    return {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": function_result,
    }