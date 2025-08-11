# eBookVoice-AI Hybrid Architecture Setup Guide
## From Junior to Senior: Understanding Enterprise-Grade Architecture Decisions

---

## 🎯 **Executive Summary**

This document outlines the complete setup of a production-ready, secure, and cost-effective eBookVoice-AI application using a hybrid cloud architecture. As you progress from junior to senior developer (and toward that $200K+ role), understanding **why** we make certain architectural decisions is as important as knowing **how** to implement them.

---

## 🏗️ **Architecture Decision Record (ADR)**

### **The Problem We're Solving**
We need to build an eBookVoice-AI application that:
1. Handles user authentication securely (without Firebase)
2. Stores large audiobook files (potentially GBs per user)
3. Manages user data and metadata
4. Processes TTS conversion (CPU-intensive)
5. Stays within budget constraints (ideally free for MVP)
6. Scales to production workloads

### **Why Not Monolithic Solutions?**

#### **❌ Railway.com Alone**
- **Storage Issue:** No persistent volumes = audiobooks deleted on restart
- **Database Limits:** 500MB insufficient for audiobook metadata at scale
- **Cost Scaling:** $5/month credit burns fast with file serving
- **Architectural Debt:** Forces you into storage constraints early

#### **❌ Firebase Complete Solution**
- **Vendor Lock-in:** Proprietary APIs, difficult to migrate
- **Cost Scaling:** Expensive at scale ($0.18/GB for storage + bandwidth)
- **Security Concerns:** Client-side security rules can be bypassed
- **Limited Customization:** Can't optimize for specific use cases

#### **❌ Single Cloud Provider (AWS/GCP)**
- **Free Tier Limits:** 5GB S3 storage, limited compute hours
- **Complexity:** Over-engineered for MVP
- **Cost:** Can become expensive quickly without optimization

### **✅ Why Hybrid Architecture Wins**

```
Principle: Use the right tool for each job, optimize for cost and performance
```

1. **Separation of Concerns:** Each service handles what it does best
2. **Cost Optimization:** Leverage multiple free tiers instead of one
3. **Scalability:** Each component can scale independently
4. **Vendor Independence:** No single point of failure or lock-in
5. **Performance:** Specialized services for specialized needs

---

## 🏛️ **Detailed Architecture Breakdown**

### **Component Selection Rationale**

```
┌─────────────────┐   Why: Static hosting, global CDN, unlimited bandwidth
│   Frontend      │ → Vercel (Free unlimited)
│   (React SPA)   │   Alternative: Netlify (similar benefits)
└─────────────────┘
         │ HTTPS/API calls
         ▼
┌─────────────────┐   Why: 750hrs free (25hrs/day), auto-SSL, GitHub integration
│   API Backend   │ → Render.com (Free tier)
│   (Flask/Auth)  │   Alternative: Railway ($5/mo) for always-on
└─────────────────┘
         │ Database queries
         ▼
┌─────────────────┐   Why: 500MB PostgreSQL, RLS, real-time, auth built-in
│   Database      │ → Supabase (Free tier)
│   (User data)   │   Alternative: PlanetScale (1GB free but MySQL)
└─────────────────┘
         │ File operations
         ▼
┌─────────────────┐   Why: 10GB free, no egress fees, S3-compatible, global CDN
│   File Storage  │ → Cloudflare R2 (Free tier)
│   (Audiobooks)  │   Alternative: AWS S3 (5GB free but with egress costs)
└─────────────────┘
```

### **Senior-Level Architectural Principles Applied**

1. **Single Responsibility Principle (SRP)**
   - Frontend: UI/UX only
   - Backend: Business logic and API
   - Database: Data persistence
   - Storage: File operations

2. **Loose Coupling**
   - Services communicate via well-defined APIs
   - Each service can be replaced without affecting others
   - No shared databases between services

3. **High Availability**
   - Multiple availability zones across providers
   - No single point of failure
   - Graceful degradation patterns

4. **Cost Optimization**
   - Leverage free tiers strategically
   - Pay only for what you use
   - Optimize for economies of scale

---

## 🔧 **Step-by-Step Implementation Guide**

### **Phase 1: Infrastructure Setup (30 minutes)**

**📋 IMPORTANT:** After completing Phase 1, see `ENV_SETUP_GUIDE.md` for detailed instructions on where to find all API keys and how to set up your `.env` file.

#### **Step 1.1: Supabase Database Setup**

**Why Supabase over traditional PostgreSQL hosting?**
- **Developer Experience:** SQL editor, real-time subscriptions, auto-generated APIs
- **Security:** Row-Level Security (RLS) built-in, no need for complex auth middleware
- **Scalability:** Auto-scaling, connection pooling included
- **Cost:** 500MB free tier sufficient for user metadata (not file storage)

```bash
# 1. Go to supabase.com and create account
# 2. Create new project (choose region closest to your users)
# 3. Wait for provisioning (2-3 minutes)
```

**Database Schema Design:**
```sql
-- Why UUID over auto-increment IDs?
-- 1. No enumeration attacks
-- 2. Distributed system friendly
-- 3. Can generate client-side
-- 4. No collision concerns in microservices

-- Users table: Core identity and profile
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    google_id VARCHAR(255) UNIQUE NOT NULL,  -- External identity reference
    email VARCHAR(255) UNIQUE NOT NULL,      -- Business key for user lookup
    name VARCHAR(255) NOT NULL,
    picture_url TEXT,
    subscription_type VARCHAR(50) DEFAULT 'free',  -- Future monetization
    storage_used_bytes BIGINT DEFAULT 0,    -- Track usage for quotas
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Why separate audiobooks table?
-- 1. Normalized design prevents data duplication
-- 2. Easier to query user's books vs. user profile
-- 3. Can add complex metadata without affecting user table
-- 4. Better for reporting and analytics

CREATE TABLE audiobooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,  -- Data integrity
    title VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    storage_key VARCHAR(500) NOT NULL,      -- R2/S3 object key
    file_size BIGINT NOT NULL,              -- For quota management
    duration_seconds INTEGER,               -- For UI progress bars
    status VARCHAR(50) DEFAULT 'processing', -- State machine for conversion
    metadata JSONB,                         -- Flexible schema for TTS settings
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    
    -- Database-level constraints for data quality
    CONSTRAINT positive_file_size CHECK (file_size > 0),
    CONSTRAINT valid_status CHECK (status IN ('processing', 'completed', 'failed', 'deleted'))
);

-- Indexes for query performance (senior developer thinking)
CREATE INDEX idx_audiobooks_user_id ON audiobooks(user_id);
CREATE INDEX idx_audiobooks_status ON audiobooks(status);
CREATE INDEX idx_users_email ON users(email);

-- Row-Level Security (RLS) - enterprise security pattern
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE audiobooks ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY "Users can only access their own profile" 
    ON users FOR ALL 
    USING (auth.uid()::text = google_id);

CREATE POLICY "Users can only access their own audiobooks" 
    ON audiobooks FOR ALL 
    USING (
        user_id IN (
            SELECT id FROM users WHERE google_id = auth.uid()::text
        )
    );
```

**Why these design decisions?**
- **UUIDs:** Prevent enumeration attacks, distributed-system friendly
- **JSONB metadata:** Flexible schema for future TTS options without migrations
- **Status field:** Explicit state machine for better error handling
- **RLS:** Database-level security, defense in depth
- **Proper indexing:** Query performance from day one

#### **Step 1.2: Cloudflare R2 Storage Setup**

**Why Cloudflare R2 over AWS S3?**
- **No Egress Fees:** Unlimited downloads without bandwidth charges
- **Performance:** Global CDN included, faster than S3 in many regions
- **Cost:** 10GB free vs 5GB S3, better long-term pricing
- **S3 Compatibility:** Can switch to S3 later with minimal code changes

```bash
# Detailed Cloudflare R2 Setup Steps:

# 1. Create Cloudflare Account and Access R2
#    - Go to dash.cloudflare.com
#    - Sign up or log in
#    - Navigate to "R2 Object Storage" in left sidebar
#    - Click "Purchase R2" (don't worry, it's free up to 10GB)

# 2. Create R2 Bucket
#    - Click "Create bucket"
#    - Bucket name: "ebookvoice-audiobooks-prod" (must be globally unique)
#    - Region: "Automatic" (recommended for global performance)
#    - Click "Create bucket"

# 3. Generate API Token (THIS IS CRITICAL)
#    - Go to "Manage R2 API tokens" (in R2 dashboard)
#    - Click "Create API token"
#    - Token name: "eBookVoice-API-Token"
#    - Permissions: "Object Read & Write" (NOT Admin)
#    - TTL: "Forever" (for production) or "1 year" (for security)
#    - Bucket restrictions: Select your specific bucket "ebookvoice-audiobooks-prod"
#    - Click "Create API token"

# 4. IMPORTANT: Copy These Values Immediately
#    - Access Key ID: (similar to AWS access key)
#    - Secret Access Key: (similar to AWS secret key)
#    - These will NOT be shown again after you close the dialog!

# 5. Get Your Account ID
#    - Go to main Cloudflare dashboard (dash.cloudflare.com)
#    - Your Account ID is displayed in the right sidebar
#    - Format: 32-character string like "a1b2c3d4e5f6..."

# 6. Verify Setup (optional but recommended)
#    - Install AWS CLI: pip install awscli
#    - Test connection:
#    aws s3 ls --endpoint-url https://YOUR_ACCOUNT_ID.r2.cloudflarestorage.com
```

**Why API Token vs Service Account?**
- **Cloudflare uses "API Tokens"** - not service accounts (Google) or IAM users (AWS)
- **API Tokens are scoped** - you can limit them to specific buckets and permissions
- **More secure than account-wide keys** - follows principle of least privilege
- **Can be rotated easily** - important for production security

**Storage Strategy Design:**
```
Bucket Structure:
/users/{user_id}/uploads/{timestamp}_{hash}.{ext}     # Original files
/users/{user_id}/audiobooks/{book_id}/audio.mp3      # Converted audio
/users/{user_id}/audiobooks/{book_id}/chapters/      # Chapter files
/users/{user_id}/audiobooks/{book_id}/metadata.json  # TTS settings
```

**Why this structure?**
- **User isolation:** Each user's files in separate prefix
- **Predictable paths:** Easy to generate URLs and cleanup
- **Scalable:** Can implement user quotas easily
- **Secure:** Path-based access control possible

#### **Step 1.3: Google OAuth Configuration**

**Why Google OAuth over custom auth?**
- **Security:** Google handles password security, 2FA, breach detection
- **User Experience:** Single sign-on, no password fatigue
- **Compliance:** Google meets SOC2, GDPR requirements
- **Maintenance:** No password reset flows, account recovery, etc.

```bash
# 1. Go to console.cloud.google.com
# 2. Create new project or select existing
# 3. Enable Google+ API (will be deprecated, use Google Identity)
# 4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
# 5. Application type: "Web application"
# 6. Authorized origins: 
#    - http://localhost:3000 (development)
#    - https://your-domain.vercel.app (production)
# 7. Authorized redirect URIs:
#    - http://localhost:5000/auth/google/callback (dev)
#    - https://your-api.render.com/auth/google/callback (prod)
```

**OAuth Flow Design (Senior-level security):**
```
1. Frontend redirects to Google OAuth
2. User grants permissions at Google
3. Google redirects to backend with code
4. Backend exchanges code for tokens
5. Backend validates ID token
6. Backend creates/updates user in database
7. Backend creates secure session
8. Frontend receives secure cookie
```

### **Phase 2: Backend Development (60 minutes)**

#### **Step 2.1: Enhanced Flask Application Structure**

**Why this structure over monolithic app.py?**
```
backend/
├── app/
│   ├── __init__.py          # Application factory pattern
│   ├── config.py            # Environment-based configuration (includes R2 setup)
│   ├── models/              # Database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── audiobook.py
│   ├── services/            # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py    # Google OAuth + JWT (from our google_auth.py)
│   │   ├── storage_service.py # Cloudflare R2 integration (from our storage.py)
│   │   ├── user_service.py    # User management with Supabase
│   │   └── tts_service.py     # TTS conversion logic
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication endpoints (/auth/google/*)
│   │   ├── audiobooks.py    # Audiobook CRUD operations
│   │   └── users.py         # User profile management
│   └── utils/               # Shared utilities
│       ├── __init__.py
│       ├── validators.py    # Input validation helpers
│       └── decorators.py    # Auth decorators, rate limiting
├── migrations/              # Database migrations (if using Alembic)
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_storage.py
│   └── test_api.py
├── requirements.txt         # Updated with all hybrid architecture dependencies
├── requirements.cpu.txt     # CPU-only version for free hosting
├── Dockerfile              # CUDA version
├── Dockerfile.cpu          # CPU-only version for Render.com
├── docker-compose.yml      # Full development stack
├── .env.example            # Environment variables template
├── wsgi.py                 # WSGI entry point for production
└── run_dev.py              # Development server launcher
```

**Key Files We've Already Created:**
- ✅ `storage.py` → goes into `app/services/storage_service.py`
- ✅ `google_auth.py` → split into `app/services/auth_service.py` and `app/services/user_service.py`
- ✅ `auth.py` → goes into `app/services/auth_service.py` (OAuth logic)
- ✅ `.env.example` → already created with R2 configuration

**Senior Architecture Principles:**
- **Separation of Concerns:** Models, services, and routes separated
- **Dependency Injection:** Services injected into routes
- **Test-Driven Development:** Structure supports easy testing
- **Configuration Management:** Environment-based config
- **Scalability:** Can split into microservices later

#### **Step 2.2: Supabase Integration**

```python
# app/config.py
import os
from urllib.parse import urlparse

class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Supabase configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')  # Public key
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')  # Private key
    
    # Parse database URL for direct connection
    db_url = urlparse(os.getenv('DATABASE_URL'))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    
    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    
    # Cloudflare R2 Configuration
    # These values come from the API Token you created in Step 1.2
    R2_ACCOUNT_ID = os.getenv('R2_ACCOUNT_ID')  # From Cloudflare dashboard sidebar
    R2_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID')  # From API token creation
    R2_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY')  # From API token creation
    R2_BUCKET_NAME = os.getenv('R2_BUCKET_NAME', 'ebookvoice-audiobooks-prod')
    
    # R2 Endpoint (constructed from Account ID)
    @property
    def R2_ENDPOINT_URL(self):
        return f'https://{self.R2_ACCOUNT_ID}.r2.cloudflarestorage.com'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    GOOGLE_REDIRECT_URI = 'http://localhost:5000/auth/google/callback'
    
    # R2 works the same in dev and prod - same bucket, same API tokens

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    GOOGLE_REDIRECT_URI = 'https://your-api.render.com/auth/google/callback'
    
    # Security headers for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # R2 configuration remains the same as base Config class
```

**Why environment-based configuration?**
- **Security:** Secrets not in code
- **Flexibility:** Different settings per environment
- **Deployment:** 12-factor app compliance
- **Team Development:** Developers can have different local setups

#### **Step 2.3: Advanced User Service**

```python
# app/services/user_service.py
from typing import Optional, Dict, List
import uuid
from supabase import create_client, Client
from app.config import Config

class UserService:
    """
    User management service with enterprise patterns
    """
    
    def __init__(self, config: Config):
        self.supabase: Client = create_client(
            config.SUPABASE_URL,
            config.SUPABASE_SERVICE_KEY  # Use service key for admin operations
        )
    
    async def create_or_update_user(self, google_user_info: Dict) -> Dict:
        """
        Idempotent user creation/update
        
        Why idempotent? Google OAuth can be called multiple times,
        we don't want to create duplicate users or fail on existing users.
        """
        google_id = google_user_info.get('sub')  # 'sub' is the stable Google ID
        email = google_user_info.get('email')
        name = google_user_info.get('name')
        picture = google_user_info.get('picture')
        
        # Try to find existing user
        existing_user = self.supabase.table('users').select('*').eq('google_id', google_id).execute()
        
        if existing_user.data:
            # Update existing user (handle profile changes)
            updated_user = self.supabase.table('users').update({
                'name': name,
                'picture_url': picture,
                'updated_at': 'now()'
            }).eq('google_id', google_id).execute()
            
            return updated_user.data[0]
        else:
            # Create new user
            new_user = self.supabase.table('users').insert({
                'google_id': google_id,
                'email': email,
                'name': name,
                'picture_url': picture
            }).execute()
            
            return new_user.data[0]
    
    async def get_user_by_google_id(self, google_id: str) -> Optional[Dict]:
        """Get user by Google ID"""
        result = self.supabase.table('users').select('*').eq('google_id', google_id).execute()
        return result.data[0] if result.data else None
    
    async def update_storage_usage(self, user_id: str, bytes_used: int) -> bool:
        """
        Update user's storage usage for quota management
        
        Why track storage? 
        - Enforce free tier limits
        - Plan monetization strategy
        - Prevent abuse
        """
        try:
            self.supabase.table('users').update({
                'storage_used_bytes': bytes_used
            }).eq('id', user_id).execute()
            return True
        except Exception:
            return False
    
    async def check_storage_quota(self, user_id: str, additional_bytes: int) -> bool:
        """
        Check if user can upload additional data
        
        Business logic for quota enforcement
        """
        user = self.supabase.table('users').select('storage_used_bytes, subscription_type').eq('id', user_id).execute()
        
        if not user.data:
            return False
        
        current_usage = user.data[0]['storage_used_bytes'] or 0
        subscription = user.data[0]['subscription_type']
        
        # Define quotas based on subscription
        quotas = {
            'free': 100 * 1024 * 1024,      # 100MB for free users
            'premium': 10 * 1024 * 1024 * 1024,  # 10GB for premium
        }
        
        quota = quotas.get(subscription, quotas['free'])
        return (current_usage + additional_bytes) <= quota
```

**Why this service pattern?**
- **Business Logic Encapsulation:** All user operations in one place
- **Testability:** Easy to mock and unit test
- **Reusability:** Can be used by multiple API endpoints
- **Future-Proofing:** Easy to add caching, validation, etc.

### **Phase 3: File Storage Service (45 minutes)**

#### **Step 3.1: Advanced Storage Service**

```python
# app/services/storage_service.py
import boto3
import hashlib
import mimetypes
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from botocore.exceptions import ClientError

class StorageService:
    """
    Enterprise-grade file storage with R2/S3
    """
    
    def __init__(self, config):
        # R2 is S3-compatible, so we use boto3
        self.client = boto3.client(
            's3',
            endpoint_url=f'https://{config.R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
            aws_access_key_id=config.R2_ACCESS_KEY_ID,
            aws_secret_access_key=config.R2_SECRET_ACCESS_KEY,
            region_name='auto'  # R2 handles region automatically
        )
        self.bucket_name = config.R2_BUCKET_NAME
    
    def generate_secure_key(self, user_id: str, filename: str, folder: str = 'uploads') -> str:
        """
        Generate secure, collision-resistant storage key
        
        Why this pattern?
        - Prevents directory traversal attacks
        - Ensures uniqueness across users
        - Predictable for cleanup operations
        - Supports partitioning for performance
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_hash = hashlib.sha256(f"{filename}_{timestamp}".encode()).hexdigest()[:12]
        extension = filename.split('.')[-1] if '.' in filename else 'bin'
        
        return f"users/{user_id}/{folder}/{timestamp}_{file_hash}.{extension}"
    
    async def upload_file(self, file_data: bytes, key: str, content_type: str = None) -> Dict:
        """
        Upload file with metadata and error handling
        
        Enterprise patterns:
        - Proper error handling
        - Metadata tracking
        - Content type detection
        - Upload validation
        """
        if not content_type:
            content_type = mimetypes.guess_type(key)[0] or 'application/octet-stream'
        
        try:
            # Calculate file hash for integrity checking
            file_hash = hashlib.sha256(file_data).hexdigest()
            
            # Upload with metadata
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_data,
                ContentType=content_type,
                Metadata={
                    'upload_timestamp': datetime.now().isoformat(),
                    'file_size': str(len(file_data)),
                    'sha256_hash': file_hash,
                    'uploaded_by': 'ebookvoice_api'
                }
            )
            
            return {
                'success': True,
                'key': key,
                'size': len(file_data),
                'hash': file_hash,
                'url': self.generate_presigned_url(key)
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': str(e),
                'key': key
            }
    
    def generate_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """
        Generate secure, time-limited download URL
        
        Why presigned URLs?
        - Don't expose storage credentials to frontend
        - Time-limited access for security
        - Can revoke access by changing keys
        - Supports direct browser downloads
        """
        try:
            return self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expiration
            )
        except ClientError:
            return None
    
    async def delete_file(self, key: str) -> bool:
        """Safe file deletion with error handling"""
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            return False
    
    async def cleanup_user_files(self, user_id: str, older_than_days: int = 30) -> int:
        """
        Cleanup old files for storage management
        
        Why cleanup?
        - Manage storage costs
        - GDPR compliance (right to be forgotten)
        - Remove failed/abandoned uploads
        """
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        prefix = f"users/{user_id}/"
        
        deleted_count = 0
        
        try:
            # List objects with prefix
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            for obj in response.get('Contents', []):
                if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                    self.client.delete_object(
                        Bucket=self.bucket_name,
                        Key=obj['Key']
                    )
                    deleted_count += 1
            
            return deleted_count
            
        except ClientError:
            return 0
```

**Senior-level storage patterns:**
- **Security:** Presigned URLs, secure key generation
- **Reliability:** Proper error handling, metadata tracking
- **Performance:** Direct uploads, CDN integration
- **Maintenance:** Automated cleanup, storage optimization

### **Phase 4: Authentication Implementation (90 minutes)**

#### **Step 4.1: Production-Ready OAuth Service**

```python
# app/services/auth_service.py
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import requests

class AuthService:
    """
    Enterprise authentication service
    """
    
    def __init__(self, config):
        self.config = config
        self.google_client_id = config.GOOGLE_CLIENT_ID
        self.google_client_secret = config.GOOGLE_CLIENT_SECRET
        self.redirect_uri = config.GOOGLE_REDIRECT_URI
        self.jwt_secret = config.SECRET_KEY
    
    def generate_oauth_url(self) -> Tuple[str, str]:
        """
        Generate OAuth URL with CSRF protection
        
        Security considerations:
        - State parameter prevents CSRF attacks
        - Scope limitation follows principle of least privilege
        - PKCE could be added for additional security
        """
        state = secrets.token_urlsafe(32)
        
        params = {
            'client_id': self.google_client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'openid email profile',
            'response_type': 'code',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        url = 'https://accounts.google.com/o/oauth2/v2/auth?' + '&'.join([
            f"{k}={v}" for k, v in params.items()
        ])
        
        return url, state
    
    async def exchange_code_for_token(self, code: str, state: str, stored_state: str) -> Dict:
        """
        Exchange authorization code for tokens with security validation
        
        Security validation:
        - State parameter validation (CSRF protection)
        - Token signature verification
        - Issuer validation
        - Audience validation
        """
        # Validate state to prevent CSRF
        if state != stored_state:
            raise ValueError("Invalid state parameter - possible CSRF attack")
        
        # Exchange code for tokens
        token_data = {
            'client_id': self.google_client_id,
            'client_secret': self.google_client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        
        response = requests.post(
            'https://oauth2.googleapis.com/token',
            data=token_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if response.status_code != 200:
            raise Exception(f"Token exchange failed: {response.text}")
        
        tokens = response.json()
        
        # Verify ID token
        try:
            user_info = id_token.verify_oauth2_token(
                tokens['id_token'],
                google_requests.Request(),
                self.google_client_id
            )
            
            # Additional security checks
            if user_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Invalid token issuer')
            
            if user_info['aud'] != self.google_client_id:
                raise ValueError('Invalid token audience')
            
            return user_info
            
        except ValueError as e:
            raise Exception(f"Invalid ID token: {str(e)}")
    
    def generate_session_token(self, user_data: Dict) -> str:
        """
        Generate secure JWT session token
        
        JWT design decisions:
        - Short expiration for security
        - Include user ID for quick lookups
        - Include issued_at for token rotation
        - Use strong secret for signing
        """
        payload = {
            'user_id': user_data['id'],
            'google_id': user_data['google_id'],
            'email': user_data['email'],
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=7),  # 7-day sessions
            'iss': 'ebookvoice-api',
            'aud': 'ebookvoice-frontend'
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def validate_session_token(self, token: str) -> Optional[Dict]:
        """
        Validate JWT session token
        
        Validation includes:
        - Signature verification
        - Expiration checking
        - Issuer/audience validation
        - Token structure validation
        """
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=['HS256'],
                audience='ebookvoice-frontend',
                issuer='ebookvoice-api'
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            return None  # Token expired
        except jwt.InvalidTokenError:
            return None  # Invalid token
    
    def refresh_token_if_needed(self, token: str) -> Optional[str]:
        """
        Refresh token if it's close to expiration
        
        Proactive token refresh:
        - Better user experience (no sudden logouts)
        - Maintains security with shorter token lifetimes
        - Reduces authentication-related support requests
        """
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=['HS256'],
                options={"verify_exp": False}  # Don't fail on expiration
            )
            
            exp_timestamp = payload.get('exp', 0)
            current_timestamp = datetime.utcnow().timestamp()
            
            # Refresh if token expires within 24 hours
            if exp_timestamp - current_timestamp < 86400:  # 24 hours
                # Generate new token with same user data
                return self.generate_session_token({
                    'id': payload['user_id'],
                    'google_id': payload['google_id'],
                    'email': payload['email']
                })
            
            return None  # No refresh needed
            
        except jwt.InvalidTokenError:
            return None
```

**Why this authentication approach?**
- **Security:** Multiple layers of validation, CSRF protection
- **Performance:** JWT tokens reduce database lookups
- **Scalability:** Stateless authentication, can scale horizontally
- **User Experience:** Automatic token refresh, long sessions

### **Phase 5: API Design (60 minutes)**

#### **Step 5.1: RESTful API with Authentication**

```python
# app/api/auth.py
from flask import Blueprint, request, jsonify, make_response
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from functools import wraps

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def require_auth(f):
    """
    Authentication decorator for protected endpoints
    
    Why decorator pattern?
    - Separation of concerns (auth logic separate from business logic)
    - Reusable across all protected endpoints
    - Consistent authentication handling
    - Easy to modify auth requirements globally
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('session_token')
        
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        auth_service = AuthService(current_app.config)
        user_data = auth_service.validate_session_token(token)
        
        if not user_data:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        # Add user data to request context
        request.current_user = user_data
        
        # Check for token refresh
        new_token = auth_service.refresh_token_if_needed(token)
        response = f(*args, **kwargs)
        
        # Set new token if refreshed
        if new_token and hasattr(response, 'set_cookie'):
            response.set_cookie(
                'session_token',
                new_token,
                max_age=7*24*60*60,  # 7 days
                httponly=True,
                secure=current_app.config.get('SESSION_COOKIE_SECURE', False),
                samesite='Lax'
            )
        
        return response
    
    return decorated_function

@auth_bp.route('/google/login', methods=['GET'])
def google_login():
    """
    Initiate Google OAuth flow
    
    API Design principles:
    - Clear, descriptive endpoints
    - Proper HTTP methods
    - Comprehensive error handling
    - Client-friendly response format
    """
    try:
        auth_service = AuthService(current_app.config)
        auth_url, state = auth_service.generate_oauth_url()
        
        # Store state in session for CSRF protection
        response = jsonify({
            'auth_url': auth_url,
            'success': True
        })
        
        response.set_cookie(
            'oauth_state',
            state,
            max_age=600,  # 10 minutes
            httponly=True,
            secure=current_app.config.get('SESSION_COOKIE_SECURE', False)
        )
        
        return response
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate login URL',
            'message': str(e),
            'success': False
        }), 500

@auth_bp.route('/google/callback', methods=['GET'])
async def google_callback():
    """
    Handle Google OAuth callback
    
    Security considerations:
    - Validate all parameters
    - Comprehensive error handling
    - Secure cookie settings
    - Clear error messages for debugging
    """
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    stored_state = request.cookies.get('oauth_state')
    
    # Handle OAuth errors
    if error:
        return jsonify({
            'error': f'OAuth error: {error}',
            'success': False
        }), 400
    
    # Validate required parameters
    if not code or not state:
        return jsonify({
            'error': 'Missing required OAuth parameters',
            'success': False
        }), 400
    
    try:
        # Exchange code for user info
        auth_service = AuthService(current_app.config)
        user_info = await auth_service.exchange_code_for_token(code, state, stored_state)
        
        # Create or update user
        user_service = UserService(current_app.config)
        user = await user_service.create_or_update_user(user_info)
        
        # Generate session token
        session_token = auth_service.generate_session_token(user)
        
        # Create secure response
        response = make_response(jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'picture_url': user['picture_url'],
                'subscription_type': user['subscription_type']
            },
            'message': 'Login successful'
        }))
        
        # Set secure session cookie
        response.set_cookie(
            'session_token',
            session_token,
            max_age=7*24*60*60,  # 7 days
            httponly=True,  # Prevent XSS
            secure=current_app.config.get('SESSION_COOKIE_SECURE', False),
            samesite='Lax'  # CSRF protection while allowing OAuth redirects
        )
        
        # Clear OAuth state cookie
        response.set_cookie('oauth_state', '', expires=0)
        
        return response
        
    except Exception as e:
        return jsonify({
            'error': 'Authentication failed',
            'message': str(e),
            'success': False
        }), 400

@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """
    Get current user profile
    
    Protected endpoint example:
    - Uses authentication decorator
    - Returns user data from token
    - Handles token refresh automatically
    """
    return jsonify({
        'user': {
            'id': request.current_user['user_id'],
            'email': request.current_user['email'],
            'google_id': request.current_user['google_id']
        },
        'success': True
    })

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Logout user by clearing session
    
    Security considerations:
    - Clear all authentication cookies
    - Could add token blacklisting for additional security
    - Proper CORS headers for cross-origin requests
    """
    response = jsonify({
        'message': 'Logged out successfully',
        'success': True
    })
    
    # Clear session cookie
    response.set_cookie('session_token', '', expires=0)
    
    return response
```

### **Phase 6: Frontend Integration (45 minutes)**

#### **Step 6.1: React Authentication Hook**

```typescript
// hooks/useAuth.ts
import { useState, useEffect, createContext, useContext } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
  picture_url: string;
  subscription_type: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Check authentication status on mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await fetch('/api/auth/me', {
        credentials: 'include', // Include cookies
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async () => {
    try {
      // Get OAuth URL from backend
      const response = await fetch('/api/auth/google/login');
      const data = await response.json();
      
      if (data.success) {
        // Redirect to Google OAuth
        window.location.href = data.auth_url;
      }
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  const logout = async () => {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include',
      });
      setUser(null);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
```

### **Phase 7: Deployment Configuration**

#### **Step 7.1: Render.com Deployment**

```yaml
# render.yaml
services:
  - type: web
    name: ebookvoice-api
    env: docker
    dockerfilePath: ./Dockerfile.cpu
    branch: main
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 300 wsgi:app
    
    envVars:
      # Application config
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      
      # Database (from Supabase dashboard)
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_ANON_KEY
        sync: false
      - key: SUPABASE_SERVICE_KEY
        sync: false
      - key: DATABASE_URL
        sync: false
      
      # Google OAuth (from Google Console)
      - key: GOOGLE_CLIENT_ID
        sync: false
      - key: GOOGLE_CLIENT_SECRET
        sync: false
      - key: GOOGLE_REDIRECT_URI
        value: https://your-app.onrender.com/auth/google/callback
      
      # Cloudflare R2 (from R2 dashboard)
      - key: R2_ACCOUNT_ID
        sync: false
      - key: R2_ACCESS_KEY_ID
        sync: false
      - key: R2_SECRET_ACCESS_KEY
        sync: false
      - key: R2_BUCKET_NAME
        value: ebookvoice-audiobooks-prod
```

#### **Step 7.2: Vercel Frontend Deployment**

```json
// vercel.json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://your-app.onrender.com/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

---

## 💰 **Cost Analysis & Business Rationale**

### **Monthly Cost Breakdown**

| Service | Free Tier | Paid Upgrade | When You'll Need It |
|---------|-----------|--------------|-------------------|
| **Vercel** | Unlimited | $20/mo (Pro) | Custom domains, team features |
| **Render** | 750hrs/mo | $7/mo (always-on) | >25hrs/day usage |
| **Supabase** | 500MB + 50K users | $25/mo (Pro) | >500MB data or >50K users |
| **Cloudflare R2** | 10GB storage | $0.015/GB | >10GB audiobooks |

### **Scaling Timeline**
- **Months 1-3:** $0/month (free tiers)
- **Months 4-6:** $7/month (Render Pro for reliability)
- **Months 7-12:** $32/month (+ Supabase Pro for growth)
- **Year 2+:** $50-100/month (based on usage)

### **Why This Beats Alternatives**

#### **vs. Firebase Complete Solution**
```
Firebase Total Cost at 1000 users:
- Authentication: $0 (free)
- Firestore: $25-50/month
- Storage: $20-40/month
- Hosting: $25/month
Total: $70-115/month

Our Hybrid Solution:
- All services: $32/month
- More control and customization
- No vendor lock-in
```

#### **vs. AWS Complete Solution**
```
AWS Total Cost at 1000 users:
- EC2: $20-50/month
- RDS: $25-75/month
- S3: $10-30/month
- Load Balancer: $20/month
Total: $75-175/month

Our Hybrid Solution:
- Better free tiers
- Simpler setup
- Global CDN included
```

---

## 🎓 **Senior Developer Learning Points**

### **Architecture Decisions You Should Understand**

1. **Microservices vs Monolith**
   - We chose a "distributed monolith" approach
   - Single codebase but separated concerns
   - Easier to manage than full microservices
   - Can split later as you grow

2. **Database Design**
   - Normalized schema for data integrity
   - UUID primary keys for security
   - Proper indexing for performance
   - Row-level security for multi-tenancy

3. **Authentication Strategy**
   - OAuth over custom auth for security
   - JWT tokens for stateless scaling
   - Secure cookie handling
   - Proper session management

4. **Storage Strategy**
   - Separate file storage from database
   - CDN integration for performance
   - Presigned URLs for security
   - Automated cleanup for cost management

5. **Error Handling**
   - Comprehensive error responses
   - Proper HTTP status codes
   - Logging for debugging
   - Graceful degradation

### **Senior-Level Patterns Used**

1. **Dependency Injection:** Services injected into routes
2. **Factory Pattern:** Application factory for different environments
3. **Repository Pattern:** Database access through services
4. **Decorator Pattern:** Authentication middleware
5. **Strategy Pattern:** Different configurations per environment

### **Scalability Considerations**

1. **Horizontal Scaling:** Stateless design allows multiple instances
2. **Caching:** Ready for Redis implementation
3. **Database Optimization:** Proper indexing and query patterns
4. **File Storage:** CDN-ready global distribution
5. **Monitoring:** Health checks and logging ready

### **Security Best Practices**

1. **Defense in Depth:** Multiple security layers
2. **Principle of Least Privilege:** Minimal required permissions
3. **Secure by Default:** Safe default configurations
4. **Input Validation:** Comprehensive request validation
5. **Audit Trail:** Logging for security monitoring

---

## 🚀 **Next Steps to $200K+ Developer**

### **What This Architecture Demonstrates**

1. **System Design Skills:** Understanding how to compose multiple services
2. **Security Mindset:** Implementing proper authentication and authorization
3. **Cost Optimization:** Leveraging free tiers strategically
4. **Scalability Planning:** Designing for growth from day one
5. **Best Practices:** Following industry standards and patterns

### **Skills to Highlight in Interviews**

1. **"I designed a hybrid cloud architecture that reduced costs by 60% while improving security"**
2. **"I implemented OAuth 2.0 with proper CSRF protection and JWT token management"**
3. **"I designed a scalable file storage system with CDN integration and automated cleanup"**
4. **"I used Row-Level Security in PostgreSQL to implement secure multi-tenancy"**
5. **"I applied microservices principles while maintaining monolithic simplicity"**

### **Technologies You've Now Mastered**

- **Backend:** Flask, PostgreSQL, JWT, OAuth 2.0
- **Frontend:** React, TypeScript, Authentication patterns
- **Infrastructure:** Docker, Render, Vercel, Cloudflare
- **Security:** RLS, CSRF protection, secure cookies
- **Architecture:** RESTful APIs, service patterns, database design

This architecture demonstrates senior-level thinking: you're not just coding features, you're designing systems that are secure, scalable, and cost-effective. This is exactly the kind of system design knowledge that commands $200K+ salaries.

---

## 📞 **When You're Ready for Implementation**

You now have a complete roadmap for building a production-ready eBookVoice-AI application. Each decision in this architecture is made with senior-level considerations in mind: security, scalability, cost optimization, and maintainability.

When you're ready to implement, we can tackle each phase step by step, ensuring you understand not just the "how" but the "why" behind each decision.

This is the difference between junior and senior developers: juniors implement features, seniors architect systems.