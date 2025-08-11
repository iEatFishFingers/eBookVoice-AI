# Environment Variables Setup Guide
## Complete Guide to Finding and Setting Up All API Keys

---

## 🔑 **Complete Environment Variables Checklist**

### **1. Supabase Configuration**

#### **Where to Find These Values (Updated 2025):**

**Go to:** [supabase.com](https://supabase.com) → Your Project Dashboard

1. **SUPABASE_URL**
   - **NEW Location:** Project Dashboard → Settings → API
   - **Format:** `https://your-project-id.supabase.co`
   - **Example:** `https://abcdefghijklmnop.supabase.co`

2. **SUPABASE_ANON_KEY**
   - **NEW Location:** Project Dashboard → Settings → API
   - **Look for:** "anon" key (not "anon public" anymore)
   - **Format:** Long JWT token starting with `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9`
   - **Note:** This is safe to use in frontend code

3. **SUPABASE_SERVICE_KEY** ⚠️ **UPDATED PROCESS**
   - **Option A - Legacy Projects:** Project Dashboard → Settings → API → "service_role" key
   - **Option B - New Projects (Recommended):** Create a Secret Key instead
     - Go to: Project Dashboard → Settings → API → "Create Secret Key"
     - Name: "Backend API Key"
     - Permissions: Full access
     - **Format:** `sb_secret_xxxxx...` (new format) OR JWT token (legacy)
   - **⚠️ IMPORTANT:** Keep this secret! Never expose in frontend code

4. **DATABASE_URL** ⚠️ **UPDATED LOCATION**
   - **NEW Method:** Project Dashboard → **"Connect" button** (top of dashboard)
   - **Alternative:** Settings → Database → Connection Parameters
   - **Steps:**
     1. Click **"Connect"** button at top of your project dashboard
     2. Select **"Connection string"** tab
     3. Choose **"URI"** format
     4. Copy the connection string
   - **Format:** `postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres`
   - **Note:** Replace `[password]` with your actual database password

#### **Updated Screenshot Locations (2025):**
```
Supabase Dashboard (NEW LAYOUT):
├── Project Dashboard (main page)
│   └── "Connect" Button (top) ← DATABASE_URL
├── Settings (left sidebar)
└── API (submenu)
    ├── Project URL ← SUPABASE_URL
    ├── anon ← SUPABASE_ANON_KEY  
    ├── service_role ← SUPABASE_SERVICE_KEY (legacy)
    └── "Create Secret Key" ← SUPABASE_SERVICE_KEY (new method)

Connection Information:
├── "Connect" Button → Connection string → URI ← DATABASE_URL
└── Settings → Database → Connection Parameters (alternative)
```

#### **🆕 Important 2025 Changes:**
- **Service Role Key:** Supabase is migrating to new "Secret Keys" (`sb_secret_...`)
- **Connection String:** Now found via "Connect" button, not buried in settings
- **API Keys:** Layout updated, "anon public" is now just "anon"
- **Security:** New secret keys have better security than legacy JWT tokens

---

### **2. Cloudflare R2 Configuration (Updated 2025)**

#### **Complete Step-by-Step Process:**

**Go to:** [dash.cloudflare.com](https://dash.cloudflare.com)

### **STEP 1: Get Your Account ID**
1. **Login to Cloudflare Dashboard**
2. **Look at the RIGHT SIDEBAR** - you'll see "Account ID"
3. **Copy this value** - this is your `R2_ACCOUNT_ID`
4. **Format:** 32-character string like `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

### **STEP 2: Access R2 Object Storage**
1. **Left sidebar:** Click **"R2 Object Storage"** OR just **"R2"**
2. **First time?** You'll see **"Purchase R2"** - click it (free up to 10GB)
3. **Add payment method** if required (for verification, won't be charged)

### **STEP 3: Create Your Bucket**
1. Click **"Create bucket"**
2. **Bucket name:** `ebookvoice-audiobooks-prod` (must be unique globally)
   - **Rules:** Only lowercase letters, numbers, and hyphens
   - **Length:** 3-63 characters
   - **Cannot:** Start or end with hyphens
3. **Region:** Leave as "Automatic" (recommended)
4. Click **"Create bucket"**
5. **Save the bucket name** - this is your `R2_BUCKET_NAME`

### **STEP 4: Create API Token (CRITICAL STEP)**
1. **From R2 main page:** Click **"Manage R2 API tokens"**
   - **Alternative:** Under "API" dropdown → "Manage API tokens"
2. Click **"Create API token"**
3. **Choose token type:**
   - **Recommended:** "User API Token" (tied to your user)
   - **Alternative:** "Account API Token" (requires Super Admin)

### **STEP 5: Configure Token Settings**
1. **Token name:** `eBookVoice-API-Token`
2. **Permissions:** Select **"Object Read and Write"**
   - **NOT "Admin Read & Write"** (too powerful)
   - **NOT "Object Read only"** (can't upload)
3. **Token scope:** Select **"Apply to specific buckets only"**
4. **Select buckets:** Choose your bucket `ebookvoice-audiobooks-prod`
5. **TTL:** Choose "Custom" → "1 year" or "Forever"

### **STEP 6: Get Your Credentials (ONLY SHOWN ONCE)**
After clicking "Create API token":
1. **Access Key ID:** Copy this immediately - this is your `R2_ACCESS_KEY_ID`
2. **Secret Access Key:** Copy this immediately - this is your `R2_SECRET_ACCESS_KEY`
3. **⚠️ CRITICAL:** These are shown ONLY ONCE - copy them now!

#### **Updated Navigation (2025):**
```
Cloudflare Dashboard (2025 Layout):
├── dash.cloudflare.com
├── Right Sidebar → "Account ID" ← R2_ACCOUNT_ID (copy first!)
├── Left Sidebar → "R2 Object Storage" or "R2"
│   ├── "Purchase R2" (if first time - click it)
│   ├── "Create bucket" 
│   │   ├── Name: lowercase-letters-only ← R2_BUCKET_NAME
│   │   ├── Region: "Automatic"
│   │   └── Create
│   └── "Manage R2 API tokens" OR API dropdown → "Manage API tokens"
│       └── "Create API token"
│           ├── Type: "User API Token" (recommended)
│           ├── Name: "eBookVoice-API-Token"
│           ├── Permissions: "Object Read and Write"
│           ├── Scope: "Apply to specific buckets only"
│           ├── Select: Your bucket name
│           └── Create → COPY KEYS IMMEDIATELY!
│               ├── Access Key ID ← R2_ACCESS_KEY_ID
│               └── Secret Access Key ← R2_SECRET_ACCESS_KEY
```

#### **🆕 2025 Updates:**
- **Token Types:** Now choose between "User" and "Account" API tokens
- **Bucket Rules:** Stricter naming requirements (lowercase only)
- **Permissions:** More granular permission options
- **Scope:** Must explicitly select which buckets the token can access

---

### **3. Google OAuth Configuration**

#### **Where to Find These Values:**

**Go to:** [console.cloud.google.com](https://console.cloud.google.com)

1. **GOOGLE_CLIENT_ID**
   - **Location:** Google Cloud Console → APIs & Services → Credentials
   - **Find:** Your OAuth 2.0 Client ID (Web application)
   - **Format:** `123456789012-abcdefghijklmnopqrstuvwxyz123456.apps.googleusercontent.com`

2. **GOOGLE_CLIENT_SECRET**
   - **Location:** Same as Client ID → Click on your OAuth client
   - **Format:** `GOCSPX-abcdefghijklmnopqrstuvwxyz`
   - **Note:** Shown in the client details page

3. **GOOGLE_REDIRECT_URI**
   - **For Development:** `http://localhost:5000/auth/google/callback`
   - **For Production:** `https://your-domain.com/auth/google/callback`
   - **Note:** Must match what you configured in Google Console

#### **Screenshot Locations:**
```
Google Cloud Console:
├── Select Your Project
├── APIs & Services (left menu)
├── Credentials (submenu)
└── OAuth 2.0 Client IDs section
    └── Your Web Application Client
        ├── Client ID ← GOOGLE_CLIENT_ID
        └── Client Secret ← GOOGLE_CLIENT_SECRET
```

#### **⚠️ If You Need to Create OAuth Credentials:**
1. Go to Google Cloud Console → APIs & Services → Credentials
2. Click "Create Credentials" → "OAuth 2.0 Client ID"
3. Application type: "Web application"
4. Name: "eBookVoice-AI"
5. Authorized redirect URIs: `http://localhost:5000/auth/google/callback`
6. Click "Create" → Copy Client ID and Client Secret

---

### **4. Application Security Keys**

#### **Generate These Random Values:**

1. **SECRET_KEY**
   - **Purpose:** Flask session encryption
   - **Generate:** Use a random string generator or command below
   - **Format:** At least 32 characters, random
   - **Example:** `k8Bg3vN2mQ9rF5wX7zE1aS4dH6jL0pY3`

2. **JWT_SECRET_KEY**
   - **Purpose:** JWT token signing
   - **Generate:** Different from SECRET_KEY, also random
   - **Format:** At least 32 characters, random  
   - **Example:** `pL2nR8vB5xH9mK4qW7fG1aD6sJ3yE0zC`

#### **How to Generate Secure Random Keys:**

**Method 1: Python (Recommended)**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Method 2: Online Generator**
- Go to: [randomkeygen.com](https://randomkeygen.com)
- Use "CodeIgniter Encryption Keys" (256-bit)

**Method 3: Manual**
- Type random letters, numbers, symbols
- At least 32 characters long
- Mix uppercase, lowercase, numbers

---

## 📝 **Complete .env File Template**

```env
# Environment Configuration for eBookVoice-AI
# KEEP THIS FILE SECURE - NEVER COMMIT TO GIT

# Application Settings
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=your-32-character-random-string-here
JWT_SECRET_KEY=your-different-32-character-random-string

# Supabase Configuration (from Supabase Dashboard → Settings → API)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DATABASE_URL=postgresql://postgres:your-password@db.your-project-id.supabase.co:5432/postgres

# Google OAuth (from console.cloud.google.com → APIs & Services → Credentials)
GOOGLE_CLIENT_ID=123456789012-abc...xyz.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/google/callback

# Cloudflare R2 (from dash.cloudflare.com → R2)
R2_ACCOUNT_ID=your-32-character-account-id
R2_ACCESS_KEY_ID=your-20-character-access-key
R2_SECRET_ACCESS_KEY=your-40-character-secret-key
R2_BUCKET_NAME=ebookvoice-audiobooks-prod

# Security Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:5000
MAX_CONTENT_LENGTH=52428800
RATE_LIMIT_PER_MINUTE=60

# TTS Configuration
TTS_MODEL=tts_models/en/ljspeech/tacotron2-DDC
TTS_VOCODER=vocoder_models/en/ljspeech/hifigan_v2
CUDA_VISIBLE_DEVICES=0

# Development Settings
LOG_LEVEL=DEBUG
ENABLE_METRICS=false
```

---

## ✅ **Verification Checklist**

After filling in your `.env` file, verify each section:

### **Supabase ✓**
- [ ] SUPABASE_URL starts with `https://` and ends with `.supabase.co`
- [ ] SUPABASE_ANON_KEY is a long JWT token (starts with `eyJ`)
- [ ] SUPABASE_SERVICE_KEY is a different JWT token (starts with `eyJ`)
- [ ] DATABASE_URL contains your actual database password

### **Cloudflare R2 ✓**
- [ ] R2_ACCOUNT_ID is exactly 32 characters
- [ ] R2_ACCESS_KEY_ID is about 20 characters
- [ ] R2_SECRET_ACCESS_KEY is about 40 characters
- [ ] R2_BUCKET_NAME matches your bucket name exactly

### **Google OAuth ✓**
- [ ] GOOGLE_CLIENT_ID ends with `.apps.googleusercontent.com`
- [ ] GOOGLE_CLIENT_SECRET starts with `GOCSPX-`
- [ ] GOOGLE_REDIRECT_URI matches your OAuth configuration

### **Security Keys ✓**
- [ ] SECRET_KEY is at least 32 random characters
- [ ] JWT_SECRET_KEY is different from SECRET_KEY
- [ ] Both keys contain mix of letters, numbers, symbols

---

## 🚨 **Security Warnings**

1. **Never commit `.env` to git**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   ```

2. **Never share these keys publicly**
   - Don't paste in forums, chat, or screenshots
   - Each key gives access to your services

3. **Use different keys for production**
   - Generate new keys for production deployment
   - Never use development keys in production

4. **Rotate keys regularly**
   - Change keys every 6-12 months
   - Immediately change if compromised

---

## 🔧 **Testing Your Configuration**

Once you've filled in all values, test your setup:

```bash
cd "C:\Users\yoann\Documents\1. Programming Projects\eBookVoice-AI-Current\backend"
python run_dev.py
```

**Expected output:**
```
* Running on http://0.0.0.0:5000
* Debug mode: on
```

**Test endpoints:**
- `http://localhost:5000/health` - Should return `{"status": "healthy"}`
- `http://localhost:5000/auth/google/login` - Should return Google OAuth URL

---

## 🆘 **Troubleshooting**

### **Common Issues:**

1. **"Supabase credentials not configured"**
   - Check SUPABASE_URL and SUPABASE_SERVICE_KEY are correct
   - Ensure no extra spaces or quotes

2. **"Google OAuth credentials not configured"**
   - Verify GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
   - Check redirect URI matches Google Console settings

3. **"R2 connection failed"**
   - Confirm R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY
   - Verify bucket name exists and is accessible

4. **"Flask secret key not set"**
   - Generate proper SECRET_KEY and JWT_SECRET_KEY
   - Ensure they're different from each other

### **Supabase 2025 Specific Issues:**

1. **"Can't find service_role key"**
   - **Solution:** Create a new Secret Key instead
   - Go to Settings → API → "Create Secret Key"
   - Use the new `sb_secret_...` format key

2. **"Connect button not showing connection string"**
   - **Solution:** Try the alternative method
   - Go to Settings → Database → Connection Parameters
   - Build the URL manually using the provided parameters

3. **"Connection string format different"**
   - **New format:** `postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres`
   - **Old format:** `postgresql://postgres:[password]@db.your-project-id.supabase.co:5432/postgres`
   - Both work, use whichever you see in your dashboard

4. **"API keys section looks different"**
   - Supabase updated their dashboard in 2025
   - Look for "anon" instead of "anon public"
   - "service_role" may not be available on new projects

### **Getting Help:**
If you're still stuck:
1. Double-check each value against the 2025 updated locations above
2. Try creating new Secret Keys instead of using legacy service_role
3. Use the "Connect" button for connection strings
4. Check service dashboards for any configuration issues

---

This guide ensures you have all the credentials needed for your eBookVoice-AI hybrid architecture with the latest 2025 Supabase dashboard changes!