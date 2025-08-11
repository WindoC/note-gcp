# Implementation Plan

This document outlines the step-by-step implementation plan for the single-user markdown notes application as specified in PRD.md.

## Project Overview

Building a FastAPI-based web application for personal markdown note management, deployable to GCP App Engine Flexible with Firestore as the database.

## Phase 1: Project Foundation & Setup

### 1.1 Project Structure
```
note-gcp/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and environment variables
│   ├── auth/
│   │   ├── __init__.py
│   │   └── auth.py          # Authentication logic
│   ├── models/
│   │   ├── __init__.py
│   │   └── notes.py         # Note data model
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── firestore.py     # Firestore repository
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py          # Auth routes
│   │   └── notes.py         # Notes CRUD routes
│   ├── templates/
│   │   ├── base.html        # Base template
│   │   ├── login.html       # Login page
│   │   ├── notes_list.html  # Notes listing
│   │   ├── note_editor.html # Note create/edit
│   │   └── note_preview.html# Note preview
│   └── static/
│       ├── css/
│       │   └── style.css    # Main stylesheet
│       └── js/
│           └── editor.js    # Editor functionality
├── requirements.txt
├── Dockerfile
├── app.yaml
├── .env.example
├── PRD.md
├── CLAUDE.md
└── PLAN.md
```

### 1.2 Dependencies (requirements.txt)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0
jinja2==3.1.2
python-multipart==0.0.6
python-markdown==3.5.1
google-cloud-firestore==2.13.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
starlette==0.27.0
```

### 1.3 Configuration Setup
- Environment variables for username, password hash, Firestore project ID
- Settings class using Pydantic for configuration management
- Environment-specific configurations (dev/prod)

## Phase 2: Authentication System

### 2.1 Core Authentication Components
- MD5 password hashing utility functions
- Session token generation and validation
- Secure cookie configuration (HttpOnly, Secure, SameSite)
- Authentication middleware for route protection

### 2.2 Auth Routes Implementation
- `POST /login`: Validate credentials, create session
- `POST /logout`: Clear session, invalidate cookie
- Login form with CSRF protection
- Redirect logic for authenticated/unauthenticated users

### 2.3 Security Features
- CSRF token generation and validation
- Session expiry management
- Secure cookie flags based on environment (dev/prod)

## Phase 3: Core Backend (Notes CRUD)

### 3.1 Data Layer
- Firestore client initialization and configuration
- Notes repository with CRUD operations
- Data model validation and serialization
- Error handling for Firestore operations

### 3.2 Notes Data Model
```python
class Note:
    title: str (max 255 chars)
    content: str (markdown)
    created_at: datetime
    updated_at: datetime
    id: Optional[str]
```

### 3.3 API Endpoints Implementation
- `GET /notes`: List all notes with pagination
- `POST /notes`: Create new note
- `GET /notes/{id}`: Get specific note
- `PUT /notes/{id}`: Update existing note
- `DELETE /notes/{id}`: Delete note
- `GET /notes/{id}/preview`: Render markdown as HTML

### 3.4 Search Functionality
- Full-text search in title and content
- Firestore query optimization
- Search results pagination

### 3.5 Markdown Processing
- Python-Markdown integration
- Safe HTML rendering
- Preview generation for editor

## Phase 4: Frontend Implementation

### 4.1 Base Template & Layout
- Responsive design with mobile support
- Navigation bar (List Notes, Create Note, Logout)
- Flash message system for user feedback
- CSRF token inclusion in forms

### 4.2 Authentication UI
- Login form with username/password fields
- Error message display
- Redirect after successful login

### 4.3 Notes Management UI
- **Notes List Page**:
  - Paginated list of notes
  - Search functionality
  - Create new note button
  - Edit/Delete actions for each note

- **Note Editor**:
  - Split-pane layout (editor/preview)
  - Auto-save functionality (optional)
  - Markdown syntax highlighting (optional)
  - Save/Cancel actions

- **Note Preview**:
  - Full-screen markdown rendering
  - Back to editor/list navigation

### 4.4 JavaScript Components
- Real-time preview update in editor
- Form validation and submission
- Search functionality
- AJAX requests for preview updates

## Phase 5: Deployment Configuration

### 5.1 Dockerfile
```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
EXPOSE 8080

CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker app.main:app
```

### 5.2 App Engine Configuration (app.yaml)
```yaml
runtime: python313
service: default
env: flex

automatic_scaling:
  min_num_instances: 0
  max_num_instances: 2

env_variables:
  USERNAME: "admin"
  PASSWORD_HASH: "md5_hash_here"
  FIRESTORE_PROJECT: "your-project-id"
  SECRET_KEY: "your-secret-key"
```

### 5.3 Firestore Setup
- Create Firestore database in Native mode
- Configure IAM permissions for App Engine
- Set up indexes for search queries
- Security rules configuration

## Phase 6: Testing & Validation

### 6.1 Local Development Testing
- Test all CRUD operations
- Verify authentication flow
- Test markdown rendering
- Validate search functionality

### 6.2 Security Testing
- CSRF protection verification
- Session management testing
- Secure cookie configuration
- HTTPS enforcement in production

### 6.3 Deployment Testing
- Local container testing
- GCP App Engine deployment
- Environment variable configuration
- Firestore connectivity verification

### 6.4 Performance Testing
- Pagination functionality
- Search performance
- Note loading times
- Concurrent user simulation (single user, but stress testing)

## Implementation Order

1. **Week 1**: Phase 1 & 2 - Project setup and authentication
2. **Week 2**: Phase 3 - Backend API implementation
3. **Week 3**: Phase 4 - Frontend development
4. **Week 4**: Phase 5 & 6 - Deployment and testing

## Success Criteria Validation

- [ ] User can log in with predefined credentials
- [ ] User can create, edit, delete markdown notes
- [ ] Markdown preview functionality works
- [ ] Search functionality operates correctly
- [ ] Data persists in Firestore across sessions
- [ ] Application runs locally and on GCP
- [ ] Security requirements are met (HTTPS, secure cookies, CSRF)
- [ ] Performance requirements are satisfied

## Risk Mitigation

- **Firestore Quotas**: Monitor usage during development
- **Authentication Security**: Use strong secret keys and proper session management
- **Deployment Issues**: Test deployment early and frequently
- **Performance**: Implement pagination from the start to handle scale

## Future Enhancement Preparation

The architecture supports easy extension for:
- File attachments (Cloud Storage integration)
- Note categorization/tagging
- Export/import functionality
- Enhanced search capabilities