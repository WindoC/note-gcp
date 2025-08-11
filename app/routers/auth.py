from datetime import timedelta
from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.auth.auth import authenticate_user, create_access_token, generate_csrf_token
from app.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Display login form"""
    csrf_token = generate_csrf_token()
    
    return templates.TemplateResponse("login.html", {
        "request": request,
        "title": "Login",
        "csrf_token": csrf_token
    })


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...)
):
    """Process login form submission"""
    
    # Basic CSRF validation (in production, this should be more robust)
    if not csrf_token or len(csrf_token) < 32:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid CSRF token"
        )
    
    # Authenticate user
    if not authenticate_user(username, password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "title": "Login",
            "error": "Invalid username or password",
            "csrf_token": generate_csrf_token()
        }, status_code=400)
    
    # Create session token
    access_token_expires = timedelta(hours=24)
    access_token = create_access_token(
        username=username,
        expires_delta=access_token_expires
    )
    
    # Redirect to notes page
    response = RedirectResponse(url="/notes", status_code=302)
    
    # Set secure session cookie
    response.set_cookie(
        key="session_token",
        value=access_token,
        max_age=86400,  # 24 hours
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite
    )
    
    return response


@router.post("/logout")
async def logout():
    """Process logout"""
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(
        key="session_token",
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite
    )
    return response