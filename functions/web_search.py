from ddgs import DDGS
from ddgs.exceptions import RatelimitException

# uses DuckDuckGo (via the ddgs library) to search the live web 
def web_search(query: str, max_results: int = 5) -> str:
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)

        if not results:
            return f'No results found for "{query}"'

        formatted = []
        for r in results:
            formatted.append(
                f"- {r.get('title', 'Untitled')}\n  {r.get('href', '')}\n  {r.get('body', '')}"
            )
        return "\n\n".join(formatted)

    except RatelimitException:
        return "Error: Rate-limited by DuckDuckGo. Wait a bit and try again."
    except Exception as e:
        return f"Error: {e}"


schema_web_search = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Searches the live web for current information and returns a list of relevant results with titles, URLs, and short excerpts",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default 5)",
                },
            },
            "required": ["query"],
        },
    },
}