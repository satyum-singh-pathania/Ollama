from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .ollama_client import OllamaClient, OllamaError
from .routers import chat, models, summarize


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once at startup / shutdown. One shared Ollama client lives for
    # the whole app; routers reach it through the get_ollama dependency.
    app.state.ollama = OllamaClient(get_settings())
    yield
    await app.state.ollama.aclose()


app = FastAPI(title="AI Workspace", lifespan=lifespan)

app.include_router(chat.router)
app.include_router(summarize.router)
app.include_router(models.router)


@app.exception_handler(OllamaError)
async def ollama_error_handler(request: Request, exc: OllamaError):
    """Turn any Ollama failure into a proper HTTP error instead of a fake 200."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


# Anchor the static dir to this file's location so the app works no matter
# which directory it is launched from (the old projects broke this way).
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def serve_homepage():
    return FileResponse(STATIC_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn

    # The import string ("app.main:app"), NOT the app object — reload only
    # works with the string form; the object form makes uvicorn exit.
    # Run from the ai_workspace folder:  python -m app.main
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
