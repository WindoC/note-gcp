# 📝 Markdown Notes App

A secure, single-user web application for managing personal markdown notes, built with FastAPI and deployed on Google Cloud Platform.

![Python](https://img.shields.io/badge/python-v3.13+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![GCP](https://img.shields.io/badge/GCP-App%20Engine-orange.svg)

## ✨ Features

- 🔐 **Secure Authentication** - Session-based auth with MD5 password hashing
- 📝 **Markdown Editor** - Split-pane editor with real-time preview
- 🔍 **Search Functionality** - Full-text search across note titles and content
- 📱 **Responsive Design** - Works seamlessly on desktop and mobile devices
- ☁️ **Cloud Storage** - Notes persisted in Google Firestore
- 🚀 **Auto-Deploy** - Ready for Google Cloud Platform App Engine
- 🔒 **Security Features** - CSRF protection, secure cookies, HTTPS enforcement

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Browser   │◄──►│   FastAPI App    │◄──►│   Firestore     │
│                 │    │                  │    │   Database      │
│ • Authentication│    │ • Session Mgmt   │    │ • Note Storage  │
│ • Markdown UI   │    │ • CRUD APIs      │    │ • Search Index  │
│ • Real-time     │    │ • Security       │    │ • Backup        │
│   Preview       │    │ • Validation     │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Google Cloud Platform account
- Git (optional)

### 1. Clone or Download

```bash
git clone <repository-url>
cd note-gcp
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
```

Required environment variables:
```env
USERNAME=admin
PASSWORD_HASH=5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8
FIRESTORE_PROJECT=your-gcp-project-id
SECRET_KEY=your-super-secret-key-here
ENVIRONMENT=development
```

### 4. Run Locally

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

Visit: http://localhost:8080

**Default login:** Username: `admin`, Password: `password`

### 5. Deploy to GCP

Follow the detailed guide in [`DEPLOYMENT.md`](DEPLOYMENT.md) for production deployment.

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [`PRD.md`](PRD.md) | Product Requirements Document |
| [`PLAN.md`](PLAN.md) | Implementation Plan & Architecture |
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | GCP App Engine & Firestore Setup Guide |
| [`TEST.md`](TEST.md) | Local Testing Guide |
| [`CLAUDE.md`](CLAUDE.md) | Development Guidelines for AI Assistance |

## 🖥️ Screenshots

### Login Page
Clean, secure authentication with CSRF protection.

### Notes List
Browse all your notes with search functionality and responsive grid layout.

### Markdown Editor
Split-pane editor with real-time preview, syntax highlighting, and keyboard shortcuts.

### Mobile View
Fully responsive design that works perfectly on all devices.

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework for Python
- **Python 3.13** - Latest Python runtime
- **Uvicorn/Gunicorn** - ASGI server for production
- **Pydantic** - Data validation and settings management
- **PyJWT** - JSON Web Token implementation
- **Python-Markdown** - Markdown to HTML conversion

### Database
- **Google Firestore** - NoSQL cloud database
- **Native Mode** - For real-time updates and scaling

### Frontend
- **Jinja2** - Modern templating engine
- **Vanilla JavaScript** - No heavy frameworks, just clean JS
- **CSS Grid/Flexbox** - Modern responsive layouts
- **Progressive Enhancement** - Works without JavaScript

### Deployment
- **Google Cloud App Engine** - Fully managed serverless platform
- **Docker** - Containerized deployment
- **Cloud Build** - Automated CI/CD pipeline

## 🔒 Security Features

- ✅ **Authentication** - Session-based with secure JWT tokens
- ✅ **Password Security** - MD5 hashing (as specified in requirements)
- ✅ **CSRF Protection** - Token-based request validation
- ✅ **Secure Cookies** - HttpOnly, Secure, SameSite flags
- ✅ **HTTPS Enforcement** - Automatic SSL in production
- ✅ **Route Protection** - Authentication required for all operations
- ✅ **Input Validation** - Server-side validation for all user inputs
- ✅ **Session Management** - Automatic expiration and cleanup

## 📱 User Interface Features

### Editor
- **Split-pane layout** - Edit and preview side by side
- **Real-time preview** - See formatted output as you type
- **Syntax highlighting** - Visual feedback for markdown syntax
- **Auto-save** - Never lose your work
- **Keyboard shortcuts** - Ctrl+S to save, Tab support in editor

### Navigation
- **Responsive design** - Adapts to all screen sizes
- **Search functionality** - Find notes quickly
- **Pagination** - Handle large collections efficiently
- **Breadcrumb navigation** - Always know where you are

### Notes Management
- **Create/Edit/Delete** - Full CRUD operations
- **Search** - Full-text search across titles and content
- **Preview mode** - View notes in formatted HTML
- **Timestamps** - Track creation and modification dates

## 🏃‍♂️ Development

### Project Structure

```
note-gcp/
├── app/                    # Main application code
│   ├── main.py            # FastAPI application entry point
│   ├── config.py          # Configuration management
│   ├── auth/              # Authentication logic
│   │   └── auth.py        # Session management & security
│   ├── models/            # Data models
│   │   └── notes.py       # Note data structures
│   ├── repositories/      # Data access layer
│   │   └── firestore.py   # Firestore integration
│   ├── routers/           # API endpoints
│   │   ├── auth.py        # Authentication routes
│   │   └── notes.py       # Notes CRUD routes
│   ├── templates/         # HTML templates
│   │   ├── base.html      # Base template
│   │   ├── login.html     # Login page
│   │   ├── notes_list.html# Notes listing
│   │   ├── note_editor.html# Note editor
│   │   └── note_preview.html# Note preview
│   └── static/            # Static assets
│       ├── css/
│       │   └── style.css  # Main stylesheet
│       └── js/
│           └── editor.js  # Editor functionality
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── app.yaml              # GCP App Engine config
├── .env.example          # Environment variables template
└── docs/                 # Documentation
    ├── PRD.md
    ├── PLAN.md
    ├── DEPLOYMENT.md
    ├── TEST.md
    └── CLAUDE.md
```

### Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8080

# Run tests
python test_basic.py

# Deploy to GCP
gcloud app deploy

# View logs
gcloud app logs tail
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Root redirect to login/notes |
| `GET` | `/health` | Health check endpoint |
| `GET` | `/login` | Login page |
| `POST` | `/login` | Process login |
| `POST` | `/logout` | Logout user |
| `GET` | `/notes` | List all notes |
| `GET` | `/notes/new` | Create note form |
| `POST` | `/notes` | Create new note |
| `GET` | `/notes/{id}` | Edit note form |
| `POST` | `/notes/{id}` | Update note |
| `DELETE` | `/notes/{id}` | Delete note |
| `GET` | `/notes/{id}/preview` | Preview note as HTML |
| `GET` | `/api/notes` | JSON API: Get notes |
| `POST` | `/api/notes/{id}/preview` | JSON API: Preview markdown |

## 🧪 Testing

### Local Testing
Comprehensive testing guide available in [`TEST.md`](TEST.md).

```bash
# Basic health check
curl http://localhost:8080/health

# Run manual tests
python test_basic.py
```

### Test Checklist
- [ ] Authentication flow (login/logout)
- [ ] Note CRUD operations
- [ ] Real-time preview functionality
- [ ] Search capability
- [ ] Responsive design
- [ ] Security features (CSRF, sessions)
- [ ] Error handling
- [ ] Performance

## 🚀 Deployment

### Local Development
1. Follow setup instructions above
2. Use Firestore emulator for testing
3. Run with `--reload` for development

### Production Deployment
1. Set up GCP project and Firestore
2. Configure `app.yaml` with production values
3. Deploy with `gcloud app deploy`
4. Verify deployment and test functionality

Detailed deployment instructions in [`DEPLOYMENT.md`](DEPLOYMENT.md).

## 💰 Cost Considerations

### Free Tier
- **Firestore**: 50K reads, 20K writes per day
- **App Engine Standard**: 28 instance hours per day

### Paid Tier (App Engine Flexible)
- **Estimated cost**: $6-20/month for low-traffic single user
- **Auto-scaling**: Scales to zero when not in use
- **Resource-based pricing**: Pay for CPU, memory, disk usage

## 🔧 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `USERNAME` | Admin username | `admin` |
| `PASSWORD_HASH` | MD5 hash of password | `5e8848...` |
| `FIRESTORE_PROJECT` | GCP project ID | `my-notes-app-123` |
| `SECRET_KEY` | JWT signing key | Random 32+ chars |
| `ENVIRONMENT` | Runtime environment | `development`/`production` |

### Security Configuration
- **Session expiry**: 24 hours
- **CSRF tokens**: Required for state-changing operations
- **Password hashing**: MD5 (as per requirements)
- **Cookie security**: HttpOnly, Secure (in production), SameSite

### Performance Configuration
- **Auto-scaling**: 0-2 instances
- **Memory**: 1GB default
- **CPU**: 1 vCPU default
- **Disk**: 10GB default

## 🤝 Contributing

This is a single-user application designed for personal use. However, if you'd like to extend or improve it:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Development Guidelines
- Follow existing code patterns
- Maintain security standards
- Update documentation
- Test all changes
- Consider mobile responsiveness

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- [`PRD.md`](PRD.md) - Requirements and specifications
- [`PLAN.md`](PLAN.md) - Implementation details
- [`DEPLOYMENT.md`](DEPLOYMENT.md) - Deployment guide
- [`TEST.md`](TEST.md) - Testing procedures

### Troubleshooting
Common issues and solutions:

1. **Login not working**: Check password hash in environment variables
2. **Firestore errors**: Verify project ID and authentication setup
3. **CSS not loading**: Check static file configuration
4. **Deployment fails**: Review GCP project settings and quotas

### Getting Help
- Check application logs: `gcloud app logs tail`
- Review Firestore console for data issues
- Verify environment variables are set correctly
- Test locally before deploying

---

**Built with ❤️ using FastAPI and Google Cloud Platform**

*A secure, efficient, and user-friendly solution for personal markdown note management.*
