# 🔐 Complete Google Application Credentials Setup Guide

## Step 1: Create a Google Cloud Project (5 minutes)

### 1.1 Go to Google Cloud Console
- Visit: https://console.cloud.google.com
- Sign in with your Google account

### 1.2 Create New Project
1. Click the **project dropdown** at the top (says "Select a project")
2. Click **"NEW PROJECT"** button (top right)
3. Fill in:
   - **Project name**: `my-docs-agent` (or any name you like)
   - **Location**: Leave as default or select your organization
4. Click **"CREATE"**
5. Wait 10-30 seconds for project creation
6. Select your new project from the dropdown

---

## Step 2: Enable Required APIs (3 minutes)

### 2.1 Navigate to APIs & Services
1. Click the **☰ hamburger menu** (top left)
2. Go to: **APIs & Services** → **Library**

### 2.2 Enable Google Drive API
1. In the search box, type: `Google Drive API`
2. Click on **"Google Drive API"**
3. Click the blue **"ENABLE"** button
4. Wait for confirmation

### 2.3 Enable Google Docs API
1. Click **"← Library"** to go back
2. Search: `Google Docs API`
3. Click on it and click **"ENABLE"**

### 2.4 Enable Google Sheets API
1. Go back to Library
2. Search: `Google Sheets API`
3. Click and **"ENABLE"**

✅ **Checkpoint**: You should see all three APIs listed under "Enabled APIs & services"

---

## Step 3: Create Service Account (5 minutes)

### 3.1 Navigate to Service Accounts
1. Click **☰ hamburger menu**
2. Go to: **IAM & Admin** → **Service Accounts**
3. Click **"+ CREATE SERVICE ACCOUNT"** (top)

### 3.2 Service Account Details
1. **Service account name**: `docs-sheets-agent`
2. **Service account ID**: (auto-filled) `docs-sheets-agent@...`
3. **Description**: `Service account for Google Docs/Sheets MCP Agent`
4. Click **"CREATE AND CONTINUE"**

### 3.3 Grant Access (Optional but Recommended)
1. **Select a role**: Click the dropdown
2. Search for: `Editor` or `Owner`
3. Select: **Basic → Editor**
4. Click **"CONTINUE"**
5. Click **"DONE"**

---

## Step 4: Create and Download JSON Key (2 minutes)

### 4.1 Generate Key
1. You'll see your new service account in the list
2. Click on the **email address** (e.g., `docs-sheets-agent@...`)
3. Go to the **"KEYS"** tab
4. Click **"ADD KEY"** → **"Create new key"**

### 4.2 Download JSON
1. Select key type: **JSON** (default)
2. Click **"CREATE"**
3. A JSON file will automatically download (e.g., `my-docs-agent-abc123.json`)
4. **IMPORTANT**: Save this file securely! You can't download it again

### 4.3 Move the File
Move the downloaded JSON file to your project folder:

```bash
# Create a secure folder for credentials
mkdir -p ~/credentials

# Move the downloaded file (adjust the filename)
mv ~/Downloads/my-docs-agent-*.json ~/credentials/google-credentials.json

# Make it readable only by you
chmod 600 ~/credentials/google-credentials.json
```

---

## Step 5: Share Google Drive Files with Service Account (CRITICAL!)

Your service account needs access to your Google Drive files.

### 5.1 Find Service Account Email
The email looks like: `docs-sheets-agent@my-docs-agent-123456.iam.gserviceaccount.com`

You can find it:
- In the JSON file you downloaded (look for `client_email`)
- Or in Google Cloud Console → Service Accounts list

### 5.2 Share Files/Folders
1. Go to **Google Drive** (drive.google.com)
2. Right-click the **folder** or **file** you want the agent to access
3. Click **"Share"**
4. Paste the **service account email**
5. Set permission: **Editor** (or Viewer if read-only)
6. Click **"Send"**

**💡 Pro Tip**: Share an entire folder instead of individual files!

---

## Step 6: Configure Your Application (2 minutes)

### 6.1 Create .env File
In your project folder, create a file named `.env`:

```bash
# Navigate to your project folder
cd /path/to/your/project

# Create .env file
touch .env
```

### 6.2 Add Credentials Path
Edit `.env` and add:

```bash
# Google Cloud Credentials
GOOGLE_APPLICATION_CREDENTIALS=/home/yourname/credentials/google-credentials.json

# Groq API Key (get from https://console.groq.com)
GROQ_API_KEY=your_groq_api_key_here
```

**Replace**:
- `/home/yourname/credentials/google-credentials.json` with your actual path
- Use **absolute path**, not relative (starts with `/` or `C:\`)

### 6.3 Verify Path (Linux/Mac)
```bash
# Check if file exists
ls -la ~/credentials/google-credentials.json

# Should show: -rw------- (only you can read)
```

### 6.4 Verify Path (Windows)
```cmd
# Check if file exists
dir C:\credentials\google-credentials.json
```

---

## Step 7: Get Groq API Key (3 minutes)

### 7.1 Sign Up for Groq
1. Visit: https://console.groq.com
2. Click **"Sign Up"** or **"Get Started"**
3. Sign in with Google/GitHub or email
4. Complete registration

### 7.2 Generate API Key
1. Go to **API Keys** section
2. Click **"Create API Key"**
3. Give it a name: `docs-agent`
4. Click **"Create"**
5. **COPY THE KEY** (you can't see it again!)
6. Paste it in your `.env` file:

```bash
GROQ_API_KEY=gsk_abc123xyz789...
```

---

## Step 8: Test Your Setup (2 minutes)

### 8.1 Create Test Script
Create `test_credentials.py`:

```python
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

print("🔍 Testing Google Credentials Setup...\n")

# Check environment variable
creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not creds_path:
    print("❌ GOOGLE_APPLICATION_CREDENTIALS not set in .env")
    exit(1)

print(f"✅ Environment variable set: {creds_path}")

# Check file exists
if not Path(creds_path).exists():
    print(f"❌ File not found: {creds_path}")
    exit(1)

print(f"✅ Credentials file exists")

# Check file is valid JSON
try:
    with open(creds_path, 'r') as f:
        data = json.load(f)
    print(f"✅ Valid JSON file")
    print(f"✅ Service Account Email: {data.get('client_email')}")
    print(f"✅ Project ID: {data.get('project_id')}")
except Exception as e:
    print(f"❌ Invalid JSON: {e}")
    exit(1)

# Check Groq API key
groq_key = os.getenv("GROQ_API_KEY")
if not groq_key:
    print("❌ GROQ_API_KEY not set in .env")
    exit(1)

print(f"✅ Groq API key set (length: {len(groq_key)})")

print("\n🎉 All checks passed! You're ready to run the agent!")
```

### 8.2 Run Test
```bash
python test_credentials.py
```

Expected output:
```
🔍 Testing Google Credentials Setup...

✅ Environment variable set: /home/yourname/credentials/google-credentials.json
✅ Credentials file exists
✅ Valid JSON file
✅ Service Account Email: docs-sheets-agent@my-docs-agent.iam.gserviceaccount.com
✅ Project ID: my-docs-agent
✅ Groq API key set (length: 56)

🎉 All checks passed! You're ready to run the agent!
```

---

## 🎯 Quick Checklist

Before running your agent, verify:

- [ ] Google Cloud Project created
- [ ] Google Drive, Docs, and Sheets APIs enabled
- [ ] Service Account created
- [ ] JSON key downloaded and saved securely
- [ ] Files/folders shared with service account email
- [ ] `.env` file created with correct path
- [ ] Groq API key added to `.env`
- [ ] Test script passes all checks

---

## 🐛 Common Issues & Solutions

### Issue 1: "Access denied" or "Permission denied"
**Solution**: Make sure you shared your Google Drive files with the service account email!

### Issue 2: "File not found"
**Solution**: Use absolute path in `.env`, not relative. Check with `ls` or `dir`.

### Issue 3: "Invalid credentials"
**Solution**: 
- Redownload JSON key from Google Cloud Console
- Check JSON file isn't corrupted (open in text editor)
- Ensure no extra spaces in `.env` file

### Issue 4: "API not enabled"
**Solution**: Go back to APIs & Services → Library and enable missing API

### Issue 5: Can't find service account email
**Solution**: Open the JSON file with text editor, look for `"client_email"` field

---

## 🔒 Security Best Practices

1. **Never commit credentials to Git**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   echo "*.json" >> .gitignore
   echo "credentials/" >> .gitignore
   ```

2. **Set restrictive file permissions**
   ```bash
   chmod 600 ~/credentials/google-credentials.json
   ```

3. **Rotate keys regularly** (every 90 days)

4. **Don't share service account email publicly**

5. **Use separate service accounts** for different projects

---

## 🚀 Next Steps

Once setup is complete:

1. Install Python dependencies:
   ```bash
   pip install agno-sdk python-dotenv mcp groq
   ```

2. Install MCP server:
   ```bash
   npm install -g @modelcontextprotocol/server-gdrive
   ```

3. Run your agent:
   ```bash
   python google_mcp_agent.py
   ```

---

