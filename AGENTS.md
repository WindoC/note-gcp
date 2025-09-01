# Repository Guidelines

This repository contains a FastAPI-based, single-user Markdown notes app with dynamic AES encryption and Google Firestore persistence, deployable to GCP App Engine.

## Project Structure & Module Organization
- `app/`: Application code
  - `main.py`: ASGI entrypoint (FastAPI)
  - `config.py`: Settings and env handling
  - `auth/`, `crypto/`, `models/`, `repositories/`, `routers/`: Core modules
  - `templates/` and `static/`: UI templates and assets
- `.env.example`, `.env.ps1`: Local configuration templates
- `README.md`, `TEST.md`, `DEPLOYMENT.md`, `PLAN.md`, `PRD.md`: Docs

## Build, Test, and Development Commands
```bash
# Setup (recommended)
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt

# Run locally (dev)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# GCP deploy
gcloud app deploy

# Tail logs
gcloud app logs tail
```
PowerShell quick start: run `.\.env.ps1` (sets env vars and starts Uvicorn).

## Coding Style & Naming Conventions
- Python 3.13, PEP 8, 4-space indentation, snake_case modules/functions.
- Prefer type hints for public functions; keep functions small and cohesive.
- Keep FastAPI routers slim; move logic to `repositories/` and `crypto/`.
- Frontend JS/CSS: keep in `static/js` and `static/css`; use descriptive names.

## Testing Guidelines
- No formal test suite; follow `TEST.md` manual checklist (auth, AES key prompt, CRUD, upload, preview, CSRF, responsiveness).
- Add small, self-contained verification scripts under `.temp/` if useful; remove on PR.
- Health check: `curl http://localhost:8080/health`.

## Commit & Pull Request Guidelines
- Use concise, imperative messages. Preferred prefixes: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:` (matches existing history).
- PRs should include: summary, scope, before/after screenshots (UI), related docs updated (`README.md`, `DEPLOYMENT.md`, `TEST.md`), and any config changes.
- Keep PRs focused; avoid unrelated refactors.

## Security & Configuration Tips
- Required env vars: `USERNAME`, `PASSWORD_HASH` (SHA256), `FIRESTORE_PROJECT`, `SECRET_KEY`, `AES_KEY`, `ENVIRONMENT`.
- Never commit secrets; use `.env.ps1` locally and GCP runtime config in production.
- AES: client enters same key as server `AES_KEY`; only hashes stored client-side.

## Agent-Specific Notes
- Follow patterns in `CLAUDE.md` and existing modules.
- Do not introduce new dependencies without necessity; keep App Engine Standard compatible.
