# Local Testing Guide

This guide provides step-by-step instructions for testing the encrypted markdown notes application locally before deploying to GCP.

## Prerequisites

- Python 3.13+ installed
- Git (optional, for cloning)
- **Modern web browser with Web Crypto API support** (Chrome 37+, Firefox 34+, Safari 7+, Edge 12+)
- Text editor or IDE
- Developer tools enabled in browser (for encryption testing)

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
PASSWORD_HASH=5f4dcc3b5aa765d61d8327deb882cf99

# Firestore Configuration (for local testing, you can use a test project)
FIRESTORE_PROJECT=your-test-project-id

# Security Configuration
SECRET_KEY=local-development-secret-key-change-in-production

# AES Encryption Key
AES_KEY=your-test-aes-key-here-any-string-will-work

# Environment
ENVIRONMENT=development
```

**Important Notes:**
- `PASSWORD_HASH` above is SHA256 hash of "password"
- For local testing, you can use any test project ID
- `SECRET_KEY` should be changed for production
- `AES_KEY` can be any string - it will be hashed to create the 32-byte AES key
- **CRITICAL**: Users must enter the SAME key you set in `AES_KEY` when prompted

### 2.3 Create Custom Password (Optional)
If you want a different password:

```python
# Run this Python script to generate password hash
import hashlib

password = "your-custom-password"
password_hash = hashlib.sha256(password.encode()).hexdigest()
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

### 5.1 Browser Compatibility Test (IMPORTANT)
**First check:** Verify your browser supports Web Crypto API

Open browser developer console (F12) and run:
```javascript
console.log(!!window.crypto && !!window.crypto.subtle);
// Should return: true
```

✅ **Pass Criteria:** Returns `true` (if `false`, use a modern browser)

### 5.2 Health Check Test
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

### 5.3 Root Redirect Test
**URL:** http://localhost:8080/

**Expected Behavior:** Should redirect to `/login` (since no user is authenticated)

✅ **Pass Criteria:** Redirects to login page

### 5.4 Login Page Test
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

### 5.5 Dynamic AES Encryption Testing (CRITICAL)

#### Test Case 1: AES Key Prompt System
**Steps:**
1. Login successfully 
2. Navigate to `/notes` (or any notes page)
3. If no key is stored, you should see an AES key prompt modal

**Expected:**
- Modal dialog appears asking for AES key
- Input field is of type password (shows dots)
- Modal has OK and Cancel buttons
- Enter the same key you set in `AES_KEY` environment variable

✅ **Pass Criteria:** Key prompt appears and accepts correct key

#### Test Case 2: Key Storage and Persistence
**Steps:**
1. Enter your AES key in the prompt modal
2. Reload the page
3. Navigate to different notes pages

**Expected:**
- Key is remembered (stored in localStorage as SHA-256 hash)
- No additional prompts appear during same session
- Can access all notes functionality normally

✅ **Pass Criteria:** Key persists across page reloads and navigation

#### Test Case 3: Verify Client-Side Encryption
**Steps:**
1. Complete key setup (Test Cases 1-2)
2. Create new note with browser dev tools (F12) → Network tab open
3. Enter title: "Secret Test" and content: "This is **confidential** information"
4. Watch the network request when clicking "Save Note"

**Expected:**
- Form data should show encrypted values (long base64 strings)
- Title and content fields should NOT show plain text
- You should see something like: `title=AbCdEf123...&content=XyZ789...`

✅ **Pass Criteria:** Network traffic shows encrypted data, not plain text

#### Test Case 4: Wrong Key Handling
**Steps:**
1. Clear localStorage: `localStorage.removeItem('aes_key_hash')`
2. Refresh any notes page
3. When prompted, enter an INCORRECT key (different from server's AES_KEY)
4. Try to view or edit existing notes

**Expected:**
- Decryption fails for existing encrypted notes
- User is automatically re-prompted for correct key
- Modal shows "Decryption failed" message
- After entering correct key, notes display properly

✅ **Pass Criteria:** Automatic re-prompt on decryption failures

#### Test Case 5: Verify Server-Side Decryption
**Steps:**
1. Create a note with content: "# Test Header\nThis is **encrypted** content"
2. Save the note
3. Go back to edit the same note

**Expected:**
- Server correctly decrypts the data
- Note content displays as plain text for editing
- Markdown formatting is preserved

✅ **Pass Criteria:** Notes are correctly decrypted and displayed for editing

#### Test Case 6: Verify Notes List Encryption
**Steps:**
1. Create several notes with different titles
2. Go to notes list (`/notes`)
3. Open browser Network tab and refresh the page
4. Check the API response for the notes list

**Expected:**
- Network response shows encrypted titles and previews
- Page displays decrypted content to user
- All note titles/previews are readable on screen

✅ **Pass Criteria:** List data is transmitted encrypted but displays correctly

#### Test Case 7: Verify Preview Encryption
**Steps:**
1. Create a note with markdown content
2. Click "Preview" button
3. Check Network tab for the preview request

**Expected:**
- Preview HTML is transmitted encrypted
- Page displays properly formatted HTML
- All markdown formatting renders correctly

✅ **Pass Criteria:** Preview content encrypted in transit, properly rendered

#### Test Case 8: Key Derivation Consistency Test
**Steps:**
1. Use browser console to test key derivation
2. Open developer console (F12) and run:
```javascript
// Test that key derivation works
const testKey = "test123";
crypto.subtle.digest('SHA-256', new TextEncoder().encode(testKey))
  .then(hash => {
    const hashArray = Array.from(new Uint8Array(hash));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    console.log('SHA-256 of "test123":', hashHex);
  });
```

**Expected:**
- Should output: `ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae`
- This verifies client-side key derivation is working

✅ **Pass Criteria:** Key derivation produces expected SHA-256 hash

#### Test Case 9: Encryption Error Handling
**Steps:**
1. Open browser console (F12)
2. Temporarily break encryption by typing: `window.NoteCrypto = null`
3. Try to create or edit a note

**Expected:**
- Clear error messages displayed
- User notified of encryption failures
- Application doesn't crash or expose data

✅ **Pass Criteria:** Graceful error handling for encryption issues

### 5.6 Notes Functionality Tests (Requires Firestore)

#### Test Case 1: Empty Notes List
**URL:** http://localhost:8080/notes (after login)

**Expected:**
- "No notes found" message
- "Create your first note" button
- Navigation bar with "List Notes", "Create Note", "Logout"

#### Test Case 2: Create New Note (With Encryption)
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

### 5.7 Logout Test
**Steps:**
1. While logged in, click "Logout" in navigation
2. Try to access `/notes`

**Expected:**
- Session is cleared
- Redirects to login page
- Cannot access protected routes

### 5.8 CSRF Protection Test
**Test:** Manual CSRF token verification

**Steps:**
1. Inspect login form HTML
2. Look for hidden input with name="csrf_token"
3. Try submitting form without token (using browser dev tools)

**Expected:**
- CSRF token present in form
- Form submission fails without valid token

### 5.9 Responsive Design Test
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

### Issue 6: Encryption not working
- Check browser console for JavaScript errors
- Verify Web Crypto API support: `console.log(!!window.crypto.subtle)`
- **Verify AES_KEY matches between server environment and user input**
- Ensure AES_KEY environment variable is set on server
- Check localStorage for stored key hash: `localStorage.getItem('aes_key_hash')`
- Clear localStorage and try again: `localStorage.clear()`
- Check for mixed content issues (HTTP vs HTTPS)

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
- [ ] **Dynamic AES key prompt system works**
- [ ] **Key storage and persistence verified**
- [ ] **Wrong key handling and re-prompt tested**
- [ ] **Encryption tests all pass (CRITICAL)**
- [ ] **Browser compatibility verified (Web Crypto API)**
- [ ] **Network traffic shows encrypted data**
- [ ] **Key derivation consistency verified**
- [ ] Authentication flow works correctly
- [ ] CRUD operations function properly
- [ ] Search functionality works
- [ ] Responsive design tested
- [ ] Error handling tested
- [ ] Performance is acceptable
- [ ] Security measures verified (CSRF, sessions, encryption)

## Success Criteria Summary

Your local testing is successful when:

1. **✅ Application starts** without errors
2. **✅ Health endpoint** returns healthy status
3. **✅ Authentication works** (login/logout)
4. **✅ Dynamic AES key system works** (prompt, storage, re-prompt)
5. **✅ Encryption works end-to-end** (CRITICAL)
6. **✅ CRUD operations** work for notes
7. **✅ Search** finds notes correctly
8. **✅ Responsive design** works on mobile
9. **✅ Security features** are functional (CSRF, sessions, dynamic encryption)

Once all tests pass, you're ready to deploy to GCP App Engine using the instructions in `DEPLOYMENT.md`!

## Next Steps

After successful local testing:
1. Review `DEPLOYMENT.md` for GCP deployment
2. Set up production Firestore database
3. Configure production environment variables
4. Deploy to App Engine
5. Run production smoke tests

Happy testing! 🧪✅