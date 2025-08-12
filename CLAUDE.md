# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a single-user markdown note-taking web application with end-to-end encryption designed for deployment on Google Cloud Platform (GCP) App Engine Flexible Environment. The project includes a comprehensive Product Requirements Document (PRD.md), detailed Implementation Plan (PLAN.md), and End-to-End Encryption PRD (e2e_encryption_prd.md).

## Technology Stack

- **Backend Framework**: FastAPI (Python 3.13)
- **Deployment Target**: GCP App Engine Flexible Environment
- **Database**: Google Firestore (Native Mode)
- **Authentication**: Single user with username/MD5 password from environment variables
- **Markdown Rendering**: Python-Markdown library
- **HTTP Server**: Uvicorn with Gunicorn for production
- **Google SDK**: google-cloud-firestore Python client
- **Encryption**: AES-GCM 256-bit encryption using `cryptography` library (server) and Web Crypto API (client)

## Key Architecture Components

Based on the PRD, the application will consist of:

1. **Authentication Layer**: Session-based auth with secure HTTP cookies
2. **API Layer**: RESTful endpoints for notes CRUD operations with encrypted payloads
3. **Data Layer**: Firestore integration for note persistence (notes stored unencrypted)
4. **UI Layer**: Minimal responsive web interface with Jinja2 templates
5. **Encryption Layer**: Client-side AES-GCM encryption/decryption with hard-coded symmetric key
6. **Deployment**: Containerized deployment with Dockerfile and app.yaml

## API Structure

The application implements these core endpoints:
- Authentication: `POST /login`, `POST /logout`
- Notes CRUD: `GET /notes`, `POST /notes`, `GET /notes/{id}`, `POST /notes/{id}`, `DELETE /notes/{id}`
- Preview: `GET /notes/{id}/preview` for HTML rendering
- API Endpoints: `GET /api/notes`, `GET /api/notes/{id}/preview`

**Encryption Implementation**: All note content (titles, content, previews) are encrypted during transmission between client and server using AES-GCM. Data is stored unencrypted in Firestore.

## Data Model

Firestore collection structure:
```
Collection: notes
- title (string, max 255 chars)
- content (string, markdown)
- created_at (timestamp)
- updated_at (timestamp)
```

## Security Requirements

- MD5 password hashing with environment variable storage
- CSRF protection for state-changing requests
- HTTPS enforcement in production
- Secure cookie configuration (HttpOnly, Secure, SameSite)
- Authentication required for all routes except /login

## Project Structure

The application follows a modular FastAPI structure:
```
app/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration and environment variables
├── auth/                # Authentication logic and middleware
├── crypto/              # Encryption utilities (encryption.py)
├── models/              # Data models (notes.py)
├── repositories/        # Firestore repository layer
├── routers/             # API route handlers (auth.py, notes.py)
├── templates/           # Jinja2 HTML templates
└── static/              # CSS and JavaScript assets
    ├── css/             # Stylesheets
    └── js/              # JavaScript modules (crypto.js, editor.js)
```

## Common Development Commands

Based on PLAN.md implementation phases:

**Phase 1 - Setup:**
- `pip install -r requirements.txt` - Install dependencies
- `python -m app.main` - Run FastAPI development server
- `uvicorn app.main:app --reload` - Run with auto-reload

**Development:**
- `gunicorn --bind :8080 --workers 1 --worker-class uvicorn.workers.UvicornWorker app.main:app` - Production server
- `gcloud app deploy` - Deploy to GCP App Engine

**Environment Setup:**
- Copy `.env.example` to `.env` and configure environment variables
- Set USERNAME, PASSWORD_HASH, FIRESTORE_PROJECT, SECRET_KEY

## Implementation Phases

Follow PLAN.md for structured development:
1. **Phase 1**: Project foundation & setup
2. **Phase 2**: Authentication system with MD5 hashing
3. **Phase 3**: Notes CRUD API with Firestore
4. **Phase 4**: Frontend templates and JavaScript
5. **Phase 5**: End-to-end encryption implementation (AES-GCM)
6. **Phase 6**: Deployment configuration
7. **Phase 7**: Testing and validation

## Encryption Implementation

The application uses AES-GCM encryption to protect note content during transmission:

**Server Side** (`app/crypto/encryption.py`):
- Hard-coded 32-byte AES key: `0123456789abcdef0123456789abcdef`
- Uses `cryptography` library AESGCM class
- 12-byte random nonce per encryption
- Base64 encoding for transport

**Client Side** (`app/static/js/crypto.js`):
- Same hard-coded AES key as server
- Uses Web Crypto API for AES-GCM operations
- Automatic encryption of form submissions
- Automatic decryption of received data

**Security Note**: The hard-coded symmetric key is visible in both server and client code. This is insecure by design but acceptable per requirements for simplicity. In production, consider using secure key management.

## Development Environment

- Uses single Firestore instance for both dev and production
- Environment variables configure username, password hash, Firestore project ID
- No Firestore emulator required per PRD specifications
- Same codebase deploys to local and GCP with only environment changes