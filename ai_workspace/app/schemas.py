"""Pydantic models describing every request and response body.

FastAPI uses these to validate incoming JSON (bad input gets a clear 422
automatically) and to document the API at /docs — the contract between
frontend and backend lives here, in one place.
"""

from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    # The full conversation so far. The server stays stateless — the browser
    # keeps the history and sends it each time. Milestone 2 (a database)
    # will move this server-side.
    messages: list[ChatMessage] = Field(min_length=1)
    # Optional override; falls back to the default model from settings.
    model: str | None = None


class SummarizeRequest(BaseModel):
    # max_length keeps the input within the model's context window
    # (~50k characters is roughly 15k tokens; mistral handles 32k tokens).
    text: str = Field(min_length=1, max_length=50_000)
    model: str | None = None


class SummarizeResponse(BaseModel):
    summary: str
    model: str


class ModelInfo(BaseModel):
    name: str
    parameter_size: str | None = None


class ModelsResponse(BaseModel):
    models: list[ModelInfo]
