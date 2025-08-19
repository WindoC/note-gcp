
# Product Requirements Document (PRD)

## 1. Overview
A single-user web application for managing personal markdown notes.
The app will be deployed to Google Cloud Platform (GCP) App Engine Flexible Environment with Python 3.13 runtime, using FastAPI as the backend framework.
Authentication will be performed using a pre-defined username and SHA256-hashed password stored in environment variables.
Only one user (the owner) will be able to log in and use the system.

The app will use a single Google Firestore (Native Mode) instance for both development and production, ensuring data persistence and consistency across environments.

---

## 2. Goals
- Provide a secure, simple interface to create, read, update, and delete markdown notes.
- Store all notes in Firestore (Native Mode) for persistence and scalability.
- Render markdown into HTML for preview.
- Ensure app is deployable and maintainable within GCP App Engine Flexible Environment.

---

## 3. Non-Goals
- Multi-user support.
- Public sharing of notes.
- Offline-first sync between multiple devices (future enhancement).

---

## 4. System Requirements

### 4.1 Technology Stack
- **Backend Framework:** FastAPI (Python 3.13 runtime)
- **Deployment Target:** Google Cloud Platform App Engine Flexible Environment
- **Database:** Google Firestore (Native Mode)
  - A single Firestore instance used for both development and production.
- **Authentication:** Single user login with username and SHA256-hashed password stored in environment variables.
- **Markdown Rendering:** Python-Markdown library or equivalent.
- **HTTP Server:** Uvicorn (with Gunicorn for production).
- **Google SDK:** `google-cloud-firestore` Python client.

### 4.2 Functional Requirements

#### 4.2.1 Authentication
- Authenticate using username and SHA256-hashed password from environment variables.
- Login session managed with secure HTTP cookies (with expiry).
- No password reset (single-user system).

#### 4.2.2 Notes Management
- Create new markdown note.
- Edit existing markdown note.
- Delete note.
- View note in raw markdown.
- View note in rendered HTML preview.
- Search notes by title or content.

#### 4.2.3 Data Model
**In Firestore:**
```

Collection: notes
Document fields:
title        (string, max 255 chars)
content      (string, markdown)
created\_at   (timestamp)
updated\_at   (timestamp)

```

#### 4.2.4 API Endpoints
- `POST /login` — Authenticate.
- `POST /logout` — End session.
- `GET /notes` — List all notes.
- `POST /notes` — Create new note.
- `GET /notes/{id}` — Get note details.
- `PUT /notes/{id}` — Update note.
- `DELETE /notes/{id}` — Delete note.
- `GET /notes/{id}/preview` — Render note as HTML.

#### 4.2.5 UI Requirements
- Minimal responsive web interface (FastAPI + Jinja2 templates or lightweight frontend JS).
- Markdown editor with:
  - Text area for markdown input.
  - Side-by-side preview.
- Navigation bar with:
  - List Notes
  - Create Note
  - Logout

### 4.3 Security Requirements
- SHA256 password stored in env variable, compared against SHA256 hash of user input.
- All routes except `/login` require authentication.
- CSRF protection for POST/PUT/DELETE requests.
- HTTPS enforced in production.
- Secure cookie flags: `HttpOnly`, `Secure`, `SameSite`.

### 4.4 Performance & Scalability
- Single-user, low-traffic; Firestore free tier is sufficient.
- Pagination for large note lists.
- Indexed queries in Firestore for search.

### 4.5 Deployment
- **Dockerfile** for GCP App Engine Flexible (Python 3.13 + FastAPI + Uvicorn + Gunicorn).
- **app.yaml** for environment settings (env vars for username, password hash, Firestore project ID).
- Use the same Firestore credentials and project ID in all environments.
- Protect Firestore with appropriate IAM permissions.
- No Firestore emulator required.

---

## 5. Success Criteria
- User can log in with predefined credentials.
- User can create, edit, delete, and preview markdown notes.
- Data persists in Firestore, consistent across development and production.
- App runs locally and in GCP without code changes (only environment/config changes).
