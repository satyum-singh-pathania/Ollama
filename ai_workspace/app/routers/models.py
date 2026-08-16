from fastapi import APIRouter, Depends

from ..ollama_client import OllamaClient, get_ollama
from ..schemas import ModelInfo, ModelsResponse

router = APIRouter(prefix="/api", tags=["models"])


@router.get("/models", response_model=ModelsResponse)
async def list_models(ollama: OllamaClient = Depends(get_ollama)):
    """List locally installed Ollama models, for the frontend's model picker."""
    models = await ollama.list_models()
    return ModelsResponse(
        models=[
            ModelInfo(
                name=m["name"],
                parameter_size=m.get("details", {}).get("parameter_size"),
            )
            for m in models
        ]
    )
