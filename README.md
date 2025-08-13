# 📝 Markdown Notes App

A secure, single-user web application for managing personal markdown notes, built with FastAPI and deployed on Google Cloud Platform.

![Python](https://img.shields.io/badge/python-v3.13+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![GCP](https://img.shields.io/badge/GCP-App%20Engine-orange.svg)

## ✨ Features

- 🔐 **Secure Authentication** - Session-based auth with MD5 password hashing
- 🔒 **End-to-End Encryption** - AES-GCM encryption protects note content during transmission
- 📝 **Markdown Editor** - Rich editor with syntax highlighting and auto-save
- 📁 **File Upload** - Secure drag-and-drop upload for .txt and .md files
- 🔍 **Search Functionality** - Full-text search across note titles and content
- 📱 **Responsive Design** - Works seamlessly on desktop and mobile devices
- ☁️ **Cloud Storage** - Notes persisted in Google Firestore
- 🚀 **Auto-Deploy** - Ready for Google Cloud Platform App Engine
- 🛡️ **Security Features** - CSRF protection, secure cookies, HTTPS enforcement

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Browser   │◄──►│   FastAPI App    │◄──►│   Firestore     │
│                 │    │                  │    │   Database      │
│ • Authentication│    │ • Session Mgmt   │    │ • Note Storage  │
│ • Markdown UI   │    │ • CRUD APIs      │    │ • Search Index  │
│ • AES-GCM       │    │ • AES-GCM        │    │ • Backup        │
│   Encryption    │    │   Decryption     │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                       ▲
         │    🔒 Encrypted       │
         │     Transmission      │
         └───────────────────────┘
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
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

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
PASSWORD_HASH=5f4dcc3b5aa765d61d8327deb882cf99
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
| [`e2e_encryption_prd.md`](e2e_encryption_prd.md) | End-to-End Encryption Requirements |
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
- **Cryptography** - AES-GCM encryption library

### Database
- **Google Firestore** - NoSQL cloud database
- **Native Mode** - For real-time updates and scaling

### Frontend
- **Jinja2** - Modern templating engine
- **Vanilla JavaScript** - No heavy frameworks, just clean JS
- **Web Crypto API** - Browser-native AES-GCM encryption
- **CSS Grid/Flexbox** - Modern responsive layouts
- **Progressive Enhancement** - Core features work without JavaScript

### Deployment
- **Google Cloud App Engine** - Fully managed serverless platform
- **Docker** - Containerized deployment
- **Cloud Build** - Automated CI/CD pipeline

## 🔒 Security Features

- ✅ **Authentication** - Session-based with secure JWT tokens
- ✅ **End-to-End Encryption** - AES-GCM 256-bit encryption for all note data
- ✅ **Password Security** - MD5 hashing (as specified in requirements)
- ✅ **CSRF Protection** - Token-based request validation
- ✅ **Secure Cookies** - HttpOnly, Secure, SameSite flags
- ✅ **HTTPS Enforcement** - Automatic SSL in production
- ✅ **Route Protection** - Authentication required for all operations
- ✅ **Input Validation** - Server-side validation for all user inputs
- ✅ **Session Management** - Automatic expiration and cleanup
- ⚠️ **Encryption Key** - Hard-coded in source (see Security Notes below)

## 📱 User Interface Features

### Editor
- **Automatic encryption** - All content encrypted before transmission
- **Real-time editing** - Smooth editing experience with encryption
- **Syntax highlighting** - Visual feedback for markdown syntax
- **Auto-save** - Never lose your work (with encryption)
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

### File Upload
- **Drag-and-drop interface** - Intuitive file upload experience
- **Secure encryption** - Files encrypted client-side before upload
- **File validation** - Support for .txt and .md files up to 1MB
- **Automatic processing** - Uploaded files become editable notes
- **Error handling** - Clear feedback for invalid files or errors

## 🏃‍♂️ Development

### Project Structure

```
note-gcp/
├── app/                    # Main application code
│   ├── main.py            # FastAPI application entry point
│   ├── config.py          # Configuration management
│   ├── auth/              # Authentication logic
│   │   └── auth.py        # Session management & security
│   ├── crypto/            # Encryption utilities
│   │   └── encryption.py  # AES-GCM encryption functions
│   ├── models/            # Data models
│   │   └── notes.py       # Note data structures
│   ├── repositories/      # Data access layer
│   │   └── firestore.py   # Firestore integration
│   ├── routers/           # API endpoints
│   │   ├── auth.py        # Authentication routes
│   │   └── notes.py       # Notes CRUD routes (with encryption)
│   ├── templates/         # HTML templates
│   │   ├── base.html      # Base template
│   │   ├── login.html     # Login page
│   │   ├── notes_list.html# Notes listing (with decryption)
│   │   ├── note_editor.html# Note editor (with encryption)
│   │   ├── note_preview.html# Note preview (with decryption)
│   │   └── upload.html    # File upload page
│   └── static/            # Static assets
│       ├── css/
│       │   └── style.css  # Main stylesheet (includes upload styles)
│       └── js/
│           ├── crypto.js  # Client-side encryption utilities
│           ├── editor.js  # Editor functionality
│           └── upload.js  # File upload handling
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── app.yaml              # GCP App Engine config
├── .env.example          # Environment variables template
├── e2e_encryption_prd.md  # End-to-end encryption requirements
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
| `GET` | `/upload` | File upload page |
| `POST` | `/upload` | Process file upload (encrypted) |
| `GET` | `/notes/{id}/preview` | Preview note as HTML (encrypted) |
| `GET` | `/api/notes` | JSON API: Get notes (encrypted) |
| `GET` | `/api/notes/{id}/preview` | JSON API: Preview markdown (encrypted) |

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
- [ ] Note CRUD operations with encryption
- [ ] File upload functionality (.txt and .md files)
- [ ] Client-side encryption/decryption
- [ ] Preview functionality with encrypted content
- [ ] Search capability (server-side on unencrypted data)
- [ ] Responsive design
- [ ] Security features (CSRF, sessions, encryption)
- [ ] Browser compatibility (Web Crypto API)
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

### Encryption Configuration

**⚠️ Security Note**: The application uses a hard-coded AES key for encryption. This is insecure by design but accepted per requirements for simplicity.

**Current Key**: `0123456789abcdef0123456789abcdef` (32 bytes)

**To change the encryption key**:
1. Update `AES_KEY_BYTES` in `app/crypto/encryption.py`
2. Update the corresponding key in `app/static/js/crypto.js`
3. Ensure both keys are identical (32 bytes each)
4. **Warning**: Changing the key will make existing encrypted data unreadable

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for detailed key change instructions.

### Security Configuration
- **Session expiry**: 24 hours
- **CSRF tokens**: Required for state-changing operations
- **Password hashing**: MD5 (as per requirements)
- **Cookie security**: HttpOnly, Secure (in production), SameSite
- **Encryption**: AES-GCM 256-bit, 12-byte nonce, Base64 encoding
- **Browser requirements**: Modern browser with Web Crypto API support

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
5. **Encryption errors**: Ensure browser supports Web Crypto API
6. **Key mismatch**: Verify server and client encryption keys are identical
7. **Old data unreadable**: Encryption key may have changed

### Getting Help
- Check application logs: `gcloud app logs tail`
- Review Firestore console for data issues
- Verify environment variables are set correctly
- Test locally before deploying

---

**Built with ❤️ using FastAPI and Google Cloud Platform**

*A secure, efficient, and user-friendly solution for personal markdown note management.*
