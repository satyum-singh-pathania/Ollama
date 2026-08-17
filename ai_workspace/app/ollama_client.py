"""A single, shared client for talking to Ollama.

Both older projects in this repo copy-pasted their Ollama code and drifted
apart; this module is the fix — every endpoint goes through here. It is also
the seam for the future: swapping Ollama for a cloud API later means changing
this file, not the routers.
"""

import json
from collections.abc import AsyncIterator

import httpx
from fastapi import Request

from .config import Settings


class OllamaError(Exception):
    """Ollama failed — carries the real status code and error message.

    Routers never see httpx details; they either let this bubble up to the
    app-level exception handler (normal endpoints) or catch it and report it
    inside the stream (streaming endpoints).
    """

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class OllamaClient:
    def __init__(self, settings: Settings):
        self._settings = settings
        # One AsyncClient reused for every request — it keeps connections
        # open, which is much cheaper than reconnecting each time.
        self._http = httpx.AsyncClient(
            base_url=settings.ollama_base_url,
            timeout=httpx.Timeout(settings.read_timeout, connect=settings.connect_timeout),
        )

    async def aclose(self) -> None:
        await self._http.aclose()

    def resolve_model(self, model: str | None) -> str:
        return model or self._settings.default_model

    async def list_models(self) -> list[dict]:
        """Return the raw model list from Ollama's /api/tags."""
        try:
            resp = await self._http.get("/api/tags")
        except httpx.HTTPError as exc:
            raise self._unreachable(exc) from exc
        self._raise_for_error(resp)
        return resp.json()["models"]

    async def chat(self, messages: list[dict], model: str | None = None) -> str:
        """Send a conversation and wait for the complete reply (no streaming)."""
        payload = {"model": self.resolve_model(model), "messages": messages, "stream": False}
        try:
            resp = await self._http.post("/api/chat", json=payload)
        except httpx.HTTPError as exc:
            raise self._unreachable(exc) from exc
        self._raise_for_error(resp)
        return resp.json()["message"]["content"]

    async def chat_stream(self, messages: list[dict], model: str | None = None) -> AsyncIterator[str]:
        """Yield the assistant's reply piece by piece as Ollama generates it.

        With "stream": True, Ollama answers with one JSON object per line
        (NDJSON); each carries the next chunk of text until "done" is true.
        """
        payload = {"model": self.resolve_model(model), "messages": messages, "stream": True}
        try:
            async with self._http.stream("POST", "/api/chat", json=payload) as resp:
                if resp.status_code >= 400:
                    # For streamed responses the body must be read explicitly
                    # before we can look at the error inside it.
                    body = await resp.aread()
                    raise OllamaError(resp.status_code, _error_detail(resp.status_code, body))
                async for line in resp.aiter_lines():
                    if not line.strip():
                        continue
                    chunk = json.loads(line)
                    if chunk.get("error"):
                        raise OllamaError(500, chunk["error"])
                    piece = chunk.get("message", {}).get("content", "")
                    if piece:
                        yield piece
                    if chunk.get("done"):
                        return
        except httpx.HTTPError as exc:
            raise self._unreachable(exc) from exc

    def _unreachable(self, exc: httpx.HTTPError) -> OllamaError:
        return OllamaError(
            503, f"Cannot reach Ollama at {self._settings.ollama_base_url} — is it running? ({exc})"
        )

    def _raise_for_error(self, resp: httpx.Response) -> None:
        # The old projects skipped this check, so Ollama errors came back to
        # the browser disguised as successful (but empty) answers.
        if resp.status_code >= 400:
            raise OllamaError(resp.status_code, _error_detail(resp.status_code, resp.content))


def _error_detail(status_code: int, body: bytes) -> str:
    """Pull the human-readable message out of an Ollama error body."""
    try:
        return json.loads(body)["error"]
    except (json.JSONDecodeError, KeyError, UnicodeDecodeError):
        return f"Ollama returned HTTP {status_code}"


def get_ollama(request: Request) -> OllamaClient:
    """FastAPI dependency returning the shared client created in main.py's lifespan."""
    return request.app.state.ollama
