# Ollama Learning Projects

Small projects built while learning AI app development with [Ollama](https://ollama.com), in order:

| Project | What it is | What it taught |
|---|---|---|
| `intro_mistral.py` | 10-line script calling the Ollama API | The raw generate API |
| `ai_chatbot/` | FastAPI + vanilla JS chat page | Serving a frontend, POST endpoints |
| `ai_text_summarizer/` | FastAPI + vanilla JS summarizer | Form handling, prompt building |
| `ai_workspace/` | Chat + summarize in one structured app | Routers, Pydantic schemas, async httpx, `.env` config, SSE streaming (Milestone 1) |

## Setup

```bash
# 1. Install and start Ollama, then pull a model
ollama pull mistral

# 2. Create a virtualenv and install dependencies
python -m venv ollama_env
ollama_env\Scripts\activate     # Windows
pip install -r requirements.txt
```

Each project folder has its own run instructions; for the newest one see [ai_workspace/README.md](ai_workspace/README.md).
