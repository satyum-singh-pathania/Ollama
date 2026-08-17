import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from ..ollama_client import OllamaClient, OllamaError, get_ollama
from ..schemas import ChatRequest

router = APIRouter(prefix="/api", tags=["chat"])


def sse(data: dict) -> str:
    """Format one Server-Sent Event: a 'data: <json>' line + blank line."""
    return f"data: {json.dumps(data)}\n\n"


@router.post("/chat")
async def chat(body: ChatRequest, ollama: OllamaClient = Depends(get_ollama)):
    """Stream the assistant's reply as Server-Sent Events.

    Events sent to the browser:
      {"token": "..."}  — the next piece of the reply (many of these)
      {"done": true}    — generation finished
      {"error": "..."}  — something went wrong
    """
    messages = [m.model_dump() for m in body.messages]

    async def events():
        # Errors are reported INSIDE the stream: by the time generation
        # fails we have already sent "200 OK" headers, so the app-level
        # OllamaError handler can't help here.
        try:
            async for token in ollama.chat_stream(messages, body.model):
                yield sse({"token": token})
            yield sse({"done": True})
        except OllamaError as exc:
            yield sse({"error": exc.detail})
        except Exception:  # noqa: BLE001 — never let the stream die silently
            yield sse({"error": "Unexpected server error while streaming."})

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )
