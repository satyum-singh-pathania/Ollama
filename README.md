# Ollama Learning Projects

Small projects built while learning to build AI apps on top of a **local** LLM
runtime — [Ollama](https://ollama.com). Every model runs on the machine; there
are no cloud API keys anywhere in this repo.

The repo has two tracks, built roughly in this order:

1. **Web apps** (`ai_*/`) — FastAPI backends serving a plain HTML/JS frontend
2. **Agents** (`AI Agents/`) — LangChain + Streamlit, adding memory, voice, and retrieval

---

## Track 1 — FastAPI web apps

Each folder is a self-contained app: `app.py` (backend) + `static/` (frontend).

| Project | What it is | Model | What it taught |
|---|---|---|---|
| [intro_mistral.py](intro_mistral.py) | 10-line script hitting the Ollama API | `mistral` | The raw `/api/generate` endpoint |
| [ai_chatbot/](ai_chatbot/) | Chat page | `mistral` | Serving a frontend from FastAPI, POST endpoints |
| [ai_text_summarizer/](ai_text_summarizer/) | Paste text → summary | `mistral` | `Form(...)` handling, prompt building |
| [ai_code_assistant/](ai_code_assistant/) | Generate or debug code | `codellama` | Branching prompts off a `mode` field |
| [ai_workspace/](ai_workspace/) | Chat + summarize, properly structured | `mistral` | Routers, Pydantic schemas, async `httpx`, `.env` config, SSE streaming |
| [ai_legal_analyzer/](ai_legal_analyzer/) | Extract clauses, risks, obligations | `phi` | Domain-specific prompting |
| [ai_proofreader/](ai_proofreader/) | Grammar & spelling fixes | `deepseek-r1` | Swapping models per task |
| [ai_content_writer/](ai_content_writer/) | Article from a topic + style | `llama3` | Multi-field prompts |

**`ai_workspace/` is the one to read.** It is the Milestone 1 rewrite of the
earlier apps and fixes what they got wrong — blocking `requests` calls, copy-pasted
Ollama code, hardcoded config, fake `200`s on failure, `innerHTML` XSS. See
[ai_workspace/README.md](ai_workspace/README.md) for the full before/after.

### API surface of the older apps

| Project | Endpoint | Body | Returns |
|---|---|---|---|
| `ai_chatbot` | `POST /chat` | `?prompt=` (query param) | `{"response"}` |
| `ai_text_summarizer` | `POST /summarize` | form: `text` | `{"summary"}` |
| `ai_code_assistant` | `POST /generate_code` | form: `prompt`, `mode` (`generate`\|`debug`) | `{"code"}` |
| `ai_legal_analyzer` | `POST /analyze_legal_text` | form: `text` | `{"insights"}` |
| `ai_proofreader` | `POST /proofread` | form: `text` | `{"corrected_text"}` |
| `ai_content_writer` | `POST /generate` | form: `topic`, `style` | *(see Known gaps)* |

`ai_workspace` has its own — streaming chat, model listing — documented in its README.

---

## Track 2 — LangChain agents (`AI Agents/`)

Streamlit UIs rather than hand-written HTML, and LangChain instead of raw HTTP.

| Day | Script | What it does | Concepts |
|---|---|---|---|
| 1 | [basic_ai_agent.py](AI%20Agents/day1/basic_ai_agent.py) | Chatbot that remembers the conversation | `OllamaLLM`, `PromptTemplate`, `ChatMessageHistory`, `st.session_state` |
| 2 | [ai_voice_assistant.py](AI%20Agents/day2/ai_voice_assistant.py) | Same agent, spoken — CLI loop | `speech_recognition` (mic in), `pyttsx3` (speech out) |
| 2 | [ai_voice_assistant_ui.py](AI%20Agents/day2/ai_voice_assistant_ui.py) | Voice assistant with a Streamlit UI | Push-to-talk button, persisted history |
| 3 | [ai_web_scraper.py](AI%20Agents/day3/ai_web_scraper.py) | URL → scrape `<p>` tags → summary | `requests` + BeautifulSoup, truncating context |
| 3 | [ai_web_scrapper_faiss.py](AI%20Agents/day3/ai_web_scrapper_faiss.py) | Scrape a site, then ask questions about it | Chunking, embeddings, FAISS vector search, RAG |

The day-1 file keeps its earlier CLI-only versions commented out at the bottom,
so the progression (plain LLM → memory → web UI) is visible in one file.

> The voice assistant's *recognition* step calls Google's speech API
> (`recognizer.recognize_google`), so that part needs internet. The LLM itself
> stays local.

---

## Setup

### 1. Ollama and models

Install [Ollama](https://ollama.com), then pull the models the projects use:

```bash
ollama pull mistral      # chatbot, summarizer, workspace, agents
ollama pull llama3       # content writer, day-1 agent
ollama pull codellama    # code assistant
ollama pull phi          # legal analyzer
ollama pull deepseek-r1  # proofreader
```

Only pull what you need — each is a multi-GB download. Ollama serves on
`http://localhost:11434`; check it with `ollama list`.

### 2. Python environment

```bash
python -m venv ollama_env
ollama_env\Scripts\activate      # Windows
source ollama_env/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

`requirements.txt` covers **Track 1 only**. The agents need more:

```bash
pip install streamlit langchain langchain-community langchain-ollama \
            langchain-huggingface sentence-transformers faiss-cpu \
            beautifulsoup4 numpy SpeechRecognition pyttsx3 pyaudio
```

`pyaudio` (microphone access, day 2) needs a system build toolchain and is the
usual install failure — skip it unless you're running the voice assistant.

---

## Running a project

**FastAPI apps** — run from *inside* the project folder; `static/` and `.env`
are resolved relative to the working directory:

```bash
cd ai_code_assistant
uvicorn app:app --reload
```

Then open <http://127.0.0.1:8000> (API docs at `/docs`). `ai_workspace` uses a
package layout, so it's `uvicorn app.main:app --reload` instead.

They all bind port 8000 — run one at a time, or pass `--port 8001`.

**Streamlit agents** — run from the repo root:

```bash
streamlit run "AI Agents/day1/basic_ai_agent.py"
```

Opens on <http://localhost:8501>.

---

## Repo layout

```
intro_mistral.py        first contact with the Ollama API
ai_chatbot/             ┐
ai_text_summarizer/     │
ai_code_assistant/      ├─ Track 1: FastAPI + static frontend
ai_legal_analyzer/      │  (app.py + static/index.html each)
ai_proofreader/         │
ai_content_writer/      ┘
ai_workspace/           the structured rewrite — app/, routers/, config, .env
AI Agents/day1..day3/   Track 2: LangChain + Streamlit
requirements.txt        Track 1 dependencies
ollama_env/             virtualenv (gitignored)
```

---

## Known gaps

Kept honest rather than quietly patched — this is a learning repo, and these are
the next things to fix.

- **`ai_content_writer` is broken.** `generate_content()` builds the prompt and
  calls Ollama but never returns the result, so `/generate` responds `null`
  while the page reads `data.content`. Its `static/script.js` is empty too — the
  real logic is inlined in `index.html`.
- **Empty placeholder `script.js` files** in `ai_chatbot`, `ai_code_assistant`,
  and `ai_content_writer`; those pages use inline `<script>` blocks.
- **`ai_text_summarizer` sends `"Mistral"`** (capitalised) as the model name
  instead of the `MODEL_NAME` constant right above it.
- **Track 1 apps other than `ai_workspace`** share the same weaknesses: blocking
  `requests` calls, no timeouts, hardcoded model and URL, duplicated Ollama
  plumbing. `ai_workspace` exists because of them.
- **Agent dependencies aren't pinned** anywhere — Track 2 has no
  `requirements.txt` of its own.
