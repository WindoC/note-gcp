import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from jose import jwt, JWTError

from app.config import settings


def hash_sha256(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against SHA256 hash"""
    return hash_sha256(plain_password) == hashed_password


def create_access_token(username: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token for session management"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)  # 24 hour sessions
    
    to_encode = {
        "sub": username,
        "exp": expire,
        "type": "access"
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and return username if valid"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None


def authenticate_user(username: str, password: str) -> bool:
    """Authenticate user against environment variables"""
    if username != settings.username:
        return False
    
    return verify_password(password, settings.password_hash)


def generate_csrf_token() -> str:
    """Generate CSRF token"""
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, session_token: str) -> bool:
    """Verify CSRF token - for simplicity, we'll use a basic implementation"""
    # In a more robust implementation, we'd store CSRF tokens in session
    # For now, we'll validate that the token exists and is properly formatted
    return token and len(token) >= 32


async def get_current_user(request: Request) -> Optional[str]:
    """Get current authenticated user from session cookie"""
    session_token = request.cookies.get("session_token")
    if not session_token:
        return None
    
    username = verify_token(session_token)
    return username


async def require_auth(request: Request) -> str:
    """Dependency to require authentication"""
    username = await get_current_user(request)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username


from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for route protection"""
    
    def __init__(self, app, protected_paths: list = None):
        super().__init__(app)
        self.protected_paths = protected_paths or [
            "/notes", "/upload", "/logout"
        ]
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Check if path needs authentication
        # Handle both exact matches and path patterns
        needs_auth = False
        for protected in self.protected_paths:
            if path == protected or path.startswith(protected + "/"):
                needs_auth = True
                break
        
        if needs_auth:
            username = await get_current_user(request)
            if not username:
                # Redirect to login for HTML requests, return 401 for API requests
                accept_header = request.headers.get("accept", "")
                if "application/json" in accept_header:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Not authenticated"
                    )
                else:
                    from fastapi.responses import RedirectResponse
                    return RedirectResponse(url="/login", status_code=302)
        
        response = await call_next(request)
        return response