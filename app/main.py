from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import os

from app.config import settings
from app.routers import auth, notes
from app.auth.auth import get_current_user

app = FastAPI(
    title="Markdown Notes",
    description="Single-user markdown note-taking application",
    version="1.0.0"
)

# Security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(auth.router, tags=["authentication"])
app.include_router(notes.router, tags=["notes"])

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # Check if user is authenticated, redirect accordingly
    current_user = await get_current_user(request)
    if current_user:
        return RedirectResponse(url="/notes", status_code=302)
    else:
        return RedirectResponse(url="/login", status_code=302)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "firestore_project": settings.firestore_project or "Not configured"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)