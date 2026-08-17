# AI Workspace (Milestone 1)

Chat + summarize in one app, restructured the way real FastAPI projects are.
This is the "Milestone 1" upgrade of `ai_chatbot` and `ai_text_summarizer`.

## Run it

```bash
# from the ai_workspace folder, with the venv active and Ollama running:
uvicorn app.main:app --reload
# or:  python -m app.main
```

Then open http://127.0.0.1:8000 — interactive API docs are at /docs.

Run from *this* folder (the `.env` file is found relative to where you start).

## What's new here vs the older projects

| Concept | Where | Why it matters |
|---|---|---|
| Routers | `app/routers/` | Endpoints grouped by feature instead of one big file |
| Pydantic schemas | `app/schemas.py` | Bad input gets a clear 422 automatically; the API is self-documenting at /docs |
| Async HTTP | `app/ollama_client.py` | `httpx.AsyncClient` doesn't block the server while Ollama thinks — `requests` did |
| One shared Ollama client | `app/ollama_client.py` | The old apps copy-pasted this code and drifted apart; also the seam for swapping in a cloud API later |
| Real error handling | `OllamaError` + handler in `app/main.py` | Ollama failures become proper HTTP errors with the real message — no more fake 200s |
| Timeouts | `app/config.py` | A stalled Ollama no longer hangs requests forever |
| `.env` config | `app/config.py` + `.env` | Change the model or Ollama URL without touching code |
| Streaming (SSE) | `app/routers/chat.py` + `static/script.js` | Tokens render as they're generated, like every real AI product |
| Safe rendering | `static/script.js` | `textContent` everywhere — the chatbot's `innerHTML` was an XSS bug |

## API

| Endpoint | Body | Returns |
|---|---|---|
| `GET /api/models` | — | Installed Ollama models |
| `POST /api/chat` | `{"messages": [{"role","content"}], "model"?}` | SSE stream of `{"token"}` events |
| `POST /api/summarize` | `{"text", "model"?}` | `{"summary", "model"}` |

The server is stateless: the browser keeps chat history and sends it with each
request. Milestone 2 (database) moves that server-side.
