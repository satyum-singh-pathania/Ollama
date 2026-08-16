from fastapi import APIRouter, Depends

from ..ollama_client import OllamaClient, get_ollama
from ..schemas import SummarizeRequest, SummarizeResponse

router = APIRouter(prefix="/api", tags=["summarize"])

SUMMARY_PROMPT = (
    "Summarize the following text in a few clear sentences. "
    "Reply with only the summary, nothing else.\n\n{text}"
)


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(body: SummarizeRequest, ollama: OllamaClient = Depends(get_ollama)):
    """Return a summary in one response (contrast with /api/chat, which streams).

    If Ollama fails, the OllamaError raised by the client bubbles up to the
    handler in main.py and becomes a real HTTP error — no fake 200s.
    """
    model = ollama.resolve_model(body.model)
    summary = await ollama.chat(
        [{"role": "user", "content": SUMMARY_PROMPT.format(text=body.text)}],
        model,
    )
    return SummarizeResponse(summary=summary.strip(), model=model)
