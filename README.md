object oriented project learning the in and outs of making an ai agent.

# Setup

1. Clone the repo
2. Install dependencies: `uv sync`
3. Create a `.env` file with:
   OPENROUTER_API_KEY=your_key_here
   RUPERT_API_KEY=your_chosen_secret_key
4. Run via CLI: `uv run main.py "your prompt here"`
5. Or run as an API: `uv run uvicorn api:app --reload`
   Then visit http://localhost:8000/docs to test interactively

   Uses an agent loop pattern. The model itterates up to 20 times to find a final answer. Conversation history is saved to SQLite so context survives server restarts.