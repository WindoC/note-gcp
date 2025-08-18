# Deployment Guide: GCP App Engine & Firestore Setup

This guide will walk you through setting up Google Cloud Platform (GCP) App Engine and Firestore for your encrypted markdown notes application.

## Prerequisites

- Google Cloud Platform account (free tier available)
- `gcloud` CLI installed on your machine
- Basic knowledge of command line operations

## Step 1: Install Google Cloud CLI

### Windows:
1. Download the installer from: https://cloud.google.com/sdk/docs/install
2. Run the installer and follow the prompts
3. Open a new command prompt/terminal

### macOS:
```bash
# Using Homebrew
brew install google-cloud-sdk

# Or using curl
curl https://sdk.cloud.google.com | bash
```

### Linux:
```bash
# Download and install
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### Verify Installation:
```bash
gcloud --version
```

## Step 2: Create and Configure GCP Project

### 2.1 Create a New Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on "Select a project" dropdown at the top
3. Click "New Project"
4. Enter project details:
   - **Project name**: `markdown-notes-app` (or your preferred name)
   - **Project ID**: Will be auto-generated (note this down - you'll need it)
   - **Organization**: Leave default or select your organization
5. Click "Create"

### 2.2 Enable Required APIs
```bash
# Set your project (replace with your actual project ID)
gcloud config set project md-note-469002

# Enable required APIs
gcloud services enable appengine.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 2.3 Initialize gcloud
```bash
# Login to Google Cloud
gcloud auth login

# Set your project as default
gcloud config set project md-note-469002

# Verify configuration
gcloud config list
```

## Step 3: Set Up Firestore Database

### 3.1 Create Firestore Database via Console
1. Go to [Firestore Console](https://console.cloud.google.com/firestore)
2. Click "Create database"
3. Choose **"Native mode"** (required for this application)
4. Select database location:
   - **Multi-region**: `nam5 (United States)` for North America
   - **Regional**: Choose closest to your users (e.g., `us-central1`, `europe-west1`)
5. Click "Create database"

### 3.2 Alternative: Create Firestore via CLI
```bash
# Create Firestore database in native mode
gcloud firestore databases create --region=us-west1
```

### 3.3 Set Up Security Rules
1. In Firestore Console, go to "Rules" tab
2. Replace default rules with:
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow authenticated App Engine service to read/write
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```
3. Click "Publish"

## Step 4: Set Up App Engine

### 4.1 Initialize App Engine
```bash
# Initialize App Engine (choose region when prompted)
gcloud app create --region=us-west1

# Common regions:
# us-central (Iowa)
# us-east1 (South Carolina)
# europe-west (Belgium)
# asia-northeast1 (Tokyo)
```

### 4.2 Configure Application

#### Update app.yaml with your project details:
```yaml
runtime: python313
service: default
entrypoint: gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker app.main:app

automatic_scaling:
  min_instances: 0
  max_instances: 10
  target_cpu_utilization: 0.9

env_variables:
  USERNAME: "admin"
  PASSWORD_HASH: "5f4dcc3b5aa765d61d8327deb882cf99"  # MD5 of "password"
  FIRESTORE_PROJECT: "YOUR-PROJECT-ID"  # Replace with your actual project ID
  SECRET_KEY: "your-super-secret-key-change-this-in-production"  # Generate a strong random key
  ENVIRONMENT: "production"
  AES_KEY: "your-aes-key-here-any-string-will-be-hashed-with-sha256"  # User encryption key
```

#### Generate a strong secret key:
```python
# Run this Python script to generate a secure key
import secrets
print(secrets.token_urlsafe(32))
```

#### Update password hash (optional):
```python
# To create a new password hash
import hashlib
password = "your-new-password"
password_hash = hashlib.md5(password.encode()).hexdigest()
print(f"Password hash: {password_hash}")
```

## Step 5: Set Up Local Development Environment

### 5.1 Create .env File
```bash
cp .env.example .env
```

Edit `.env` with your values:
```env
USERNAME=admin
PASSWORD_HASH=5f4dcc3b5aa765d61d8327deb882cf99
FIRESTORE_PROJECT=YOUR-PROJECT-ID
SECRET_KEY=your-super-secret-key-change-this-in-production
AES_KEY=your-aes-key-here-any-string-will-be-hashed-with-sha256
ENVIRONMENT=development
```

### 5.2 Set Up Application Default Credentials
```bash
# Login with application default credentials
gcloud auth application-default login

# This allows your local app to connect to Firestore
```

### 5.3 Install Dependencies and Test Locally
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the application locally
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# Test at http://localhost:8080
```

## Step 6: Deploy to App Engine

### 6.1 Test Locally (Optional)
```bash
# App Engine Standard doesn't use custom Docker containers
# Test directly with your Python environment:
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### 6.2 Deploy to App Engine
```bash
# Deploy the application
gcloud app deploy

# When prompted, type 'y' to continue
# Deployment typically takes 2-5 minutes

# View your deployed application
gcloud app browse
```

### 6.3 Monitor Deployment
```bash
# View deployment logs
gcloud app logs tail -s default

# Check app status
gcloud app describe
```

## Step 7: Configure Domain and HTTPS (Optional)

### 7.1 Custom Domain
```bash
# Add custom domain
gcloud app domain-mappings create www.yourdomain.com

# Verify domain ownership in Google Search Console
```

### 7.2 SSL Certificate
App Engine automatically provides SSL certificates for:
- `https://YOUR-PROJECT-ID.appspot.com`
- Custom domains (after domain verification)

## Step 8: Monitoring and Maintenance

### 8.1 View Application Logs
```bash
# Real-time logs
gcloud app logs tail -s default

# Recent logs
gcloud app logs read -s default --limit 50
```

### 8.2 Monitor Performance
1. Go to [App Engine Console](https://console.cloud.google.com/appengine)
2. View metrics: Requests, Latency, Errors, Memory usage
3. Set up alerts in Monitoring section

### 8.3 Manage Versions
```bash
# List all versions
gcloud app versions list

# Deploy to a specific version
gcloud app deploy --version v2

# Route traffic to different versions
gcloud app services set-traffic default --splits v1=50,v2=50
```

## Step 9: Security Configuration

### 9.1 IAM Permissions
Ensure App Engine service account has Firestore permissions:
```bash
# Get the App Engine service account
gcloud iam service-accounts list

# Grant Firestore access (usually automatic)
gcloud projects add-iam-policy-binding YOUR-PROJECT-ID \
  --member="serviceAccount:YOUR-PROJECT-ID@appspot.gserviceaccount.com" \
  --role="roles/datastore.user"
```

### 9.2 Firestore Security
- Use the security rules provided in Step 3.3
- Monitor access in Firestore console
- Review security regularly

## Step 10: Cost Management

### 10.1 Free Tier Limits
App Engine Standard environment:
- **Included** in free tier up to quotas
- 28 instance hours per day (free tier)
- Can scale to zero for cost savings
- Pay only for actual usage

### 10.2 Cost Optimization
```bash
# App Engine Standard can scale to 0 instances
# Optimized configuration for cost savings:
automatic_scaling:
  min_instances: 0      # Scale to zero when no traffic
  max_instances: 10     # Reasonable limit for most apps
  target_cpu_utilization: 0.9  # Higher threshold reduces instances
```

### 10.3 Monitor Costs
1. Go to [Billing Console](https://console.cloud.google.com/billing)
2. Set up billing alerts
3. Review usage regularly

## Troubleshooting

### Common Issues:

#### 1. **"Project not found" Error**
```bash
# Verify project ID
gcloud config get-value project

# List all projects
gcloud projects list
```

#### 2. **Firestore Permission Denied**
```bash
# Ensure App Engine service account has proper permissions
gcloud projects get-iam-policy YOUR-PROJECT-ID
```

#### 3. **Build Failures**
- Check `requirements.txt` for incompatible versions
- Ensure Python 3.13 runtime is available in your region
- Review build logs: `gcloud app logs tail`

#### 4. **Application Won't Start**
```bash
# Check environment variables in app.yaml
# Verify Firestore connection
# Review application logs
gcloud app logs read --limit 100
```

#### 5. **Local Development Issues**
```bash
# Ensure application default credentials are set
gcloud auth application-default login

# Check environment variables in .env file
# Verify Firestore project ID matches
```

## Quick Reference Commands

```bash
# Deploy application
gcloud app deploy

# View live logs
gcloud app logs tail

# Browse application
gcloud app browse

# Stop all instances (to save costs)
gcloud app versions stop VERSION_ID

# Restart application
gcloud app deploy

# Update configuration only
gcloud app deploy --no-promote

# List all services
gcloud app services list
```

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `USERNAME` | Admin username | `admin` |
| `PASSWORD_HASH` | MD5 hash of password | `5e8848...` (MD5 of "password") |
| `FIRESTORE_PROJECT` | GCP Project ID | `markdown-notes-123456` |
| `SECRET_KEY` | JWT secret key | Random 32+ character string |
| `AES_KEY` | User encryption key | Any string (will be SHA-256 hashed) |
| `ENVIRONMENT` | Environment mode | `production` or `development` |

## AES Encryption Key Management

### 🔐 Dynamic AES Key System

The application uses a **dynamic AES-256 key system** where users provide their own encryption key. The key is automatically hashed using SHA-256 to create a proper 32-byte AES key.

### How It Works:

1. **Server-side**: The `AES_KEY` environment variable contains the raw user key
2. **Client-side**: Users are prompted to enter the same key when accessing notes
3. **Key Derivation**: Both sides use SHA-256 to derive identical 32-byte keys
4. **Storage**: Only the SHA-256 hash is stored in browser localStorage (never the raw key)

### Setting Up Encryption:

1. **Set the server key** in your environment:
   ```bash
   # In .env file or app.yaml
   AES_KEY=your-chosen-encryption-passphrase
   ```

2. **User Experience**:
   - Users visit `/notes` pages and are prompted for the AES key
   - They enter the **same** key you set in the server environment
   - The key is hashed with SHA-256 and stored in localStorage
   - If decryption fails, users are automatically re-prompted

### Key Management Best Practices:

1. **Choose a Strong Key**:
   ```python
   # Generate a secure random key
   import secrets
   import string
   
   alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
   key = ''.join(secrets.choice(alphabet) for i in range(32))
   print(f"Suggested key: {key}")
   ```

2. **Key Distribution**:
   - Share the key securely with users (encrypted email, secure messaging)
   - Consider using a passphrase that's memorable but strong
   - Document the key securely for admin access

3. **Changing Keys**:
   - **Warning**: Changing the `AES_KEY` makes existing notes unreadable
   - Update the environment variable on the server
   - Users will be prompted for the new key automatically
   - Consider data migration if you have important existing notes

### Security Features:

- **No Key Storage**: Raw user input is never stored in localStorage
- **Auto Re-prompt**: Automatic key re-entry if decryption fails
- **SHA-256 Hashing**: Consistent 32-byte key derivation
- **Transport Security**: Keys are only used for encryption, never transmitted
- **Modal Interface**: Clean, secure key entry interface

### Troubleshooting:

- **"Decryption failed"**: User entered wrong key, they'll be re-prompted
- **"AES_KEY not set"**: Server environment variable missing
- **Notes appear corrupted**: Key mismatch between server and client

## Security Checklist

- [ ] Changed default password and generated new hash
- [ ] Generated strong random secret key
- [ ] **Set up secure AES_KEY environment variable**
- [ ] **Tested user key prompt and localStorage functionality**
- [ ] **Verified encryption key derivation works on both client and server**
- [ ] Configured Firestore security rules
- [ ] Enabled HTTPS (automatic with App Engine)
- [ ] Set up proper IAM permissions
- [ ] Configured cost alerts
- [ ] Reviewed application logs
- [ ] Tested authentication flow
- [ ] Verified CSRF protection works
- [ ] **Tested encryption/decryption functionality with dynamic keys**
- [ ] **Verified automatic key re-prompt on decryption failures**

## Next Steps

After deployment:
1. Test all functionality (login, create/edit/delete notes, search)
2. **Test the AES key prompt system** (visit `/notes` pages to verify modal appears)
3. **Verify dynamic encryption is working** (check network traffic shows encrypted content)
4. **Test automatic key re-prompt** (enter wrong key to verify re-prompt functionality)
5. Create your first note to verify Firestore connectivity and encryption
6. Set up monitoring and alerts
7. Plan regular backups if needed
8. Consider setting up a staging environment

Your markdown notes application should now be running securely on GCP App Engine with Firestore as the database backend!

## Support Resources

- [GCP App Engine Documentation](https://cloud.google.com/appengine/docs)
- [Firestore Documentation](https://cloud.google.com/firestore/docs)
- [GCP Free Tier](https://cloud.google.com/free)
- [GCP Support](https://cloud.google.com/support)

For application-specific issues, check the application logs and refer to the PRD.md and PLAN.md files in this repository.