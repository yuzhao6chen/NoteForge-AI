# Read2Post

Read2Post is an Agent-powered writing workspace that turns reading notes, excerpts, and rough personal ideas into editable WeChat/blog drafts.

It is designed around a visible Agent workflow: parse the material, clarify the idea, optionally enrich it with web search, generate topics and an outline, write the article, review quality, check factual risk, revise once, optimize titles, and export Markdown.

## Why It Exists

Reading notes often stay as fragments. Read2Post helps transform those fragments into publishable writing while keeping the reasoning process visible enough for the user to inspect, edit, and improve.

## Features

- Turn reading notes or rough ideas into long-form article drafts.
- Generate topic candidates before committing to one direction.
- Produce outline, article draft, and title candidates.
- Review article quality and factual risk.
- Revise the draft automatically when quality or risk checks fail.
- Learn a personal writing style profile from edited final drafts.
- Export the final article as Markdown.
- Use real OpenAI-compatible LLM APIs and Tavily search. No local mock fallback.

## Architecture

Read2Post uses a frontend/backend split with a layered Agent backend.

```text
React / Vite UI
  -> FastAPI REST API
  -> Read2PostAgent orchestrator
  -> Skills: parse, clarify, search digest, topic, outline, write, review, revise, title, style memory
  -> Tools: LLM client, Tavily search, local storage, Markdown export
```

The core orchestration lives in:

- `backend/app/agents/read2post_agent.py`
- `backend/app/agents/skills/`
- `backend/app/agents/tools/`

## Tech Stack

- Frontend: React, TypeScript, Vite, lucide-react
- Backend: FastAPI, Pydantic, SQLAlchemy, SQLite
- Agent runtime: single orchestrator Agent + multiple Skills + Tools
- Storage: local Markdown / JSON files and SQLite
- Deployment: local dev scripts or Docker Compose

## Requirements

- Python 3.9+
- Node.js 18+
- An OpenAI-compatible chat completions API key
- Optional: Tavily API key if web search is enabled

## Quick Start

### 1. Configure backend environment

Create `backend/.env` from the example:

```powershell
copy backend\.env.example backend\.env
```

Edit `backend/.env`:

```env
APP_NAME=Read2Post
DATABASE_URL=sqlite:///./read2post.db
STORAGE_DIR=storage

LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

SEARCH_PROVIDER=tavily
TAVILY_API_KEY=your_tavily_key

MIN_REVIEW_SCORE=88
```

DeepSeek, Qwen, and other OpenAI-compatible providers can be used by changing `OPENAI_BASE_URL` and `OPENAI_MODEL`.

If you do not have a Tavily key, turn off web search in the UI before generating.

### 2. Run the backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Backend docs:

```text
http://127.0.0.1:8000/docs
```

### 3. Run the frontend

```powershell
cd frontend
npm install
npm.cmd run dev
```

Frontend:

```text
http://localhost:5173
```

## Docker

Docker files are included for deployment and architecture documentation.

Before using Docker Compose, create `backend/.env` as described above.

```powershell
docker compose up --build
```

Services:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`

## Project Structure

```text
backend/
  app/
    agents/       Agent orchestration, skills, tools, prompts
    api/          FastAPI routers
    core/         settings and database setup
    models/       SQLAlchemy models
    schemas/      Pydantic request/response models
  requirements.txt

frontend/
  src/
    api/          REST client and TypeScript types
    components/   reusable panels and cards
    pages/        writing workspace

docs/
  figures/        architecture diagrams
  *.pdf / *.docx  course architecture document
```

## Runtime Data

Generated articles, materials, style memory, run logs, local database files, virtual environments, dependency folders, and `.env` files are intentionally ignored by Git.

Do not commit:

- `backend/.env`
- `backend/read2post.db`
- `backend/storage/`
- `backend/.venv/`
- `frontend/node_modules/`
- `frontend/dist/`
- `*.log`

## Roadmap

- Streaming generation progress.
- Article version history and diff view.
- Stronger citation and source validation.
- More platform templates.
- Background task queue for long-running workflows.
- Better onboarding for API provider setup.
- Hosted demo deployment.

## Security

This is a BYOK project: you bring your own LLM/search API keys. Keep keys in `backend/.env`; never commit them to GitHub.

## License

MIT
