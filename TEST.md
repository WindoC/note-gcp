# Local Testing Guide

This guide provides step-by-step instructions for testing the markdown notes application locally before deploying to GCP.

## Prerequisites

- Python 3.13+ installed
- Git (optional, for cloning)
- Modern web browser
- Text editor or IDE

## Step 1: Environment Setup

### 1.1 Check Python Version
```bash
python --version
# Should show Python 3.13.x or higher

# If using Python 3.13+ but command is python3:
python3 --version
```

### 1.2 Create and Activate Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Verify activation (should show (venv) in prompt)
which python  # macOS/Linux
where python   # Windows
```

### 1.3 Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
```

Expected packages:
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- jinja2==3.1.2
- python-markdown==3.5.1
- google-cloud-firestore==2.13.1
- And others...

## Step 2: Configuration Setup

### 2.1 Create Local Environment File
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your preferred editor
```

### 2.2 Configure .env File
Edit `.env` with the following values:

```env
# Authentication Configuration
USERNAME=admin
PASSWORD_HASH=5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8

# Firestore Configuration (for local testing, you can use a test project)
FIRESTORE_PROJECT=your-test-project-id

# Security Configuration
SECRET_KEY=local-development-secret-key-change-in-production

# Environment
ENVIRONMENT=development
```

**Important Notes:**
- `PASSWORD_HASH` above is MD5 hash of "password"
- For local testing, you can use any test project ID
- `SECRET_KEY` should be changed for production

### 2.3 Create Custom Password (Optional)
If you want a different password:

```python
# Run this Python script to generate password hash
import hashlib

password = "your-custom-password"
password_hash = hashlib.md5(password.encode()).hexdigest()
print(f"Password hash for '{password}': {password_hash}")
```

Update the `PASSWORD_HASH` in your `.env` file with the generated hash.

## Step 3: Firestore Setup for Local Testing

### Option A: Use Firestore Emulator (Recommended for Testing)
```bash
# Install Firebase CLI (if not already installed)
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase in your project directory
firebase init firestore

# Start Firestore emulator
firebase emulators:start --only firestore
```

Update your `.env` file:
```env
FIRESTORE_PROJECT=demo-test-project
# When using emulator, the project ID can be anything
```

### Option B: Use Real Firestore Project
1. Follow the Firestore setup steps in `DEPLOYMENT.md`
2. Set up Application Default Credentials:
```bash
gcloud auth application-default login
```
3. Use your real project ID in `.env`

### Option C: Mock Firestore (For Basic Testing)
For initial testing without Firestore:
1. Keep `FIRESTORE_PROJECT` empty in `.env`
2. The app will show errors for database operations but auth will work

## Step 4: Run the Application Locally

### 4.1 Start the Development Server
```bash
# Method 1: Using uvicorn directly (recommended)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# Method 2: Using Python module
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# Method 3: Using the main.py directly
python app/main.py
```

### 4.2 Verify Server is Running
You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 4.3 Open in Browser
Navigate to: http://localhost:8080

## Step 5: Manual Testing Checklist

### 5.1 Health Check Test
**URL:** http://localhost:8080/health

**Expected Response:**
```json
{
  "status": "healthy",
  "environment": "development",
  "firestore_project": "your-test-project-id"
}
```

✅ **Pass Criteria:** Status is "healthy" and environment shows "development"

### 5.2 Root Redirect Test
**URL:** http://localhost:8080/

**Expected Behavior:** Should redirect to `/login` (since no user is authenticated)

✅ **Pass Criteria:** Redirects to login page

### 5.3 Login Page Test
**URL:** http://localhost:8080/login

**Test Cases:**

#### Test Case 1: Page Loads Correctly
- ✅ Login form displays
- ✅ Username and password fields present
- ✅ CSRF token hidden field present
- ✅ CSS styles load correctly

#### Test Case 2: Invalid Credentials
**Steps:**
1. Enter username: `wrong`
2. Enter password: `wrong`
3. Click Login

**Expected:** Error message "Invalid username or password"

#### Test Case 3: Valid Credentials
**Steps:**
1. Enter username: `admin`
2. Enter password: `password` (or your custom password)
3. Click Login

**Expected:** Redirect to `/notes` with session cookie set

✅ **Pass Criteria:** Successfully logs in and redirects

### 5.4 Authentication Protection Test
**Test:** Try to access `/notes` without logging in

**Steps:**
1. Clear browser cookies or use incognito mode
2. Navigate to: http://localhost:8080/notes

**Expected:** Redirects to `/login`

✅ **Pass Criteria:** Protected routes require authentication

### 5.5 Notes Functionality Tests (Requires Firestore)

#### Test Case 1: Empty Notes List
**URL:** http://localhost:8080/notes (after login)

**Expected:**
- "No notes found" message
- "Create your first note" button
- Navigation bar with "List Notes", "Create Note", "Logout"

#### Test Case 2: Create New Note
**Steps:**
1. Click "Create Note" or go to `/notes/new`
2. Enter title: "Test Note"
3. Enter content: "This is a **test** note with *markdown*"
4. Click "Create Note"

**Expected:**
- Note is created successfully
- Redirects to edit view
- Success message displayed
- Preview shows formatted markdown

#### Test Case 3: Edit Existing Note
**Steps:**
1. Go to notes list
2. Click "Edit" on a note
3. Modify title and content
4. Click "Update Note"

**Expected:**
- Note is updated
- Changes are saved
- Success message displayed

#### Test Case 4: Real-time Preview
**Steps:**
1. In note editor, type markdown in left pane
2. Observe right pane (preview)

**Expected:**
- Preview updates automatically as you type
- Markdown is rendered as HTML
- Code blocks, headers, bold/italic work

#### Test Case 5: Note Preview
**Steps:**
1. Click "Preview" button on a note
2. View the full preview page

**Expected:**
- Full-screen markdown rendering
- Proper HTML formatting
- Navigation buttons work

#### Test Case 6: Delete Note
**Steps:**
1. In notes list, click "Delete" on a note
2. Confirm deletion

**Expected:**
- Confirmation dialog appears
- Note is deleted after confirmation
- Returns to notes list

#### Test Case 7: Search Functionality
**Steps:**
1. Create multiple notes with different titles/content
2. Use search box on notes list
3. Search for specific terms

**Expected:**
- Search results filter notes
- Clear search button works
- Empty search shows all notes

### 5.6 Logout Test
**Steps:**
1. While logged in, click "Logout" in navigation
2. Try to access `/notes`

**Expected:**
- Session is cleared
- Redirects to login page
- Cannot access protected routes

### 5.7 CSRF Protection Test
**Test:** Manual CSRF token verification

**Steps:**
1. Inspect login form HTML
2. Look for hidden input with name="csrf_token"
3. Try submitting form without token (using browser dev tools)

**Expected:**
- CSRF token present in form
- Form submission fails without valid token

### 5.8 Responsive Design Test
**Steps:**
1. Test on different screen sizes
2. Use browser dev tools to simulate mobile devices
3. Check navigation, forms, and editor layout

**Expected:**
- Layout adapts to screen size
- Navigation collapses on mobile
- Editor switches to single column on mobile
- All functionality remains accessible

## Step 6: API Endpoint Testing

### 6.1 Using curl Commands

#### Health Check
```bash
curl http://localhost:8080/health
```

#### Login (get session cookie)
```bash
# First get CSRF token from login page
curl -c cookies.txt http://localhost:8080/login

# Extract CSRF token from HTML (or use browser dev tools)
# Then login:
curl -b cookies.txt -c cookies.txt -X POST \
  -d "username=admin&password=password&csrf_token=YOUR_CSRF_TOKEN" \
  http://localhost:8080/login
```

#### API Endpoints (after authentication)
```bash
# Get notes list
curl -b cookies.txt http://localhost:8080/api/notes

# Create note (requires proper session)
curl -b cookies.txt -X POST \
  -H "Content-Type: application/json" \
  -d '{"title":"API Test","content":"Created via API"}' \
  http://localhost:8080/notes
```

### 6.2 Using Browser Developer Tools

1. **Open DevTools** (F12)
2. **Network Tab**: Monitor API requests
3. **Console Tab**: Check for JavaScript errors
4. **Application Tab**: Inspect cookies and local storage

## Step 7: Performance Testing

### 7.1 Load Time Test
- Measure page load times
- Check for slow database queries
- Monitor memory usage

### 7.2 Concurrent Users Simulation (Advanced)
```bash
# Install Apache Bench (optional)
# Test login endpoint
ab -n 10 -c 2 http://localhost:8080/login
```

## Step 8: Error Handling Tests

### 8.1 Database Connection Issues
**Test:** Stop Firestore emulator while app is running

**Expected:** Graceful error handling, meaningful error messages

### 8.2 Invalid Data Tests
- Submit empty forms
- Submit overly long titles (>255 characters)
- Submit malformed markdown

### 8.3 Session Expiry Tests
- Wait for session to expire (24 hours)
- Try to access protected routes
- Verify automatic redirect to login

## Troubleshooting Common Issues

### Issue 1: "Module not found" errors
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 2: Port already in use
```bash
# Kill process using port 8080
# Windows:
netstat -ano | findstr :8080
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8080 | xargs kill
```

### Issue 3: Firestore connection errors
```bash
# Check authentication
gcloud auth application-default login

# Verify project ID in .env
# Check Firestore emulator is running
```

### Issue 4: CSS/JS not loading
- Check static files path in main.py
- Verify files exist in app/static/
- Clear browser cache

### Issue 5: Login not working
- Verify password hash in .env
- Check secret key configuration
- Look for CSRF token issues

## Testing Automation (Optional)

### Create a simple test script:
```python
# test_basic.py
import requests
import time

BASE_URL = "http://localhost:8080"

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✅ Health check passed")

def test_login_page():
    response = requests.get(f"{BASE_URL}/login")
    assert response.status_code == 200
    assert "login" in response.text.lower()
    print("✅ Login page loads")

def test_auth_protection():
    response = requests.get(f"{BASE_URL}/notes", allow_redirects=False)
    assert response.status_code == 302  # Redirect to login
    print("✅ Authentication protection works")

if __name__ == "__main__":
    print("Running basic tests...")
    test_health()
    test_login_page()
    test_auth_protection()
    print("✅ All basic tests passed!")
```

Run with: `python test_basic.py`

## Pre-Deployment Checklist

Before deploying to production:

- [ ] All manual tests pass
- [ ] No console errors in browser
- [ ] Authentication flow works correctly
- [ ] CRUD operations function properly
- [ ] Real-time preview works
- [ ] Search functionality works
- [ ] Responsive design tested
- [ ] Error handling tested
- [ ] Performance is acceptable
- [ ] Security measures verified (CSRF, sessions)

## Success Criteria Summary

Your local testing is successful when:

1. **✅ Application starts** without errors
2. **✅ Health endpoint** returns healthy status
3. **✅ Authentication works** (login/logout)
4. **✅ CRUD operations** work for notes
5. **✅ Real-time preview** functions in editor
6. **✅ Search** finds notes correctly
7. **✅ Responsive design** works on mobile
8. **✅ Security features** are functional (CSRF, sessions)

Once all tests pass, you're ready to deploy to GCP App Engine using the instructions in `DEPLOYMENT.md`!

## Next Steps

After successful local testing:
1. Review `DEPLOYMENT.md` for GCP deployment
2. Set up production Firestore database
3. Configure production environment variables
4. Deploy to App Engine
5. Run production smoke tests

Happy testing! 🧪✅