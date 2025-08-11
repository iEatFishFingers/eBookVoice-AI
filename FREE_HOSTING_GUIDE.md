# Free Hosting Guide for eBookVoice-AI

## 🎯 **Best Free Options (Ranked by Recommendation)**

### 1. **Render.com (Recommended for Production-like)**
- **Free Tier:** 750 hours/month, sleeps after 15min inactivity
- **Pros:** Easy deployment, custom domains, SSL included
- **Cons:** CPU-only, cold starts

**Setup:**
```bash
# 1. Push to GitHub
# 2. Connect Render to your GitHub repo
# 3. Use these settings:
# - Build Command: pip install -r requirements.cpu.txt
# - Start Command: gunicorn --bind 0.0.0.0:$PORT "app:create_app()"
# - Dockerfile: Dockerfile.cpu
```

### 2. **Railway.app**
- **Free Tier:** $5 credit/month (good for ~100 hours)
- **Pros:** Excellent for development, database support
- **Cons:** Limited free hours

**Setup:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

### 3. **Oracle Cloud Always Free**
- **Free Tier:** 2 AMD VMs, 200GB storage, truly always free
- **Pros:** Most generous free tier, no time limits
- **Cons:** No GPU, requires Oracle account

### 4. **Google Cloud Run**
- **Free Tier:** 2 million requests/month, 180,000 GB-seconds
- **Pros:** Serverless, auto-scaling, pay-per-use
- **Cons:** Cold starts, memory limits

## 🚀 **Quick Deploy Solutions**

### **Option A: Render.com (1-Click Deploy)**

Create `render.yaml`:
```yaml
services:
  - type: web
    name: ebookvoice-api
    env: docker
    dockerfilePath: ./backend/Dockerfile.cpu
    envVars:
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: CLOUD_STORAGE_PROVIDER
        value: aws
      - key: AWS_ACCESS_KEY_ID
        sync: false
      - key: AWS_SECRET_ACCESS_KEY
        sync: false
      - key: AWS_S3_BUCKET
        sync: false
```

### **Option B: Railway One-Liner**
```bash
# After connecting to GitHub
railway up --detach
```

### **Option C: Google Cloud Run**
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/ebookvoice
gcloud run deploy --image gcr.io/PROJECT-ID/ebookvoice --platform managed
```

## 🔧 **Optimizations for Free Hosting**

### **CPU-Only TTS Configuration**
```python
# In converter.py, replace GPU TTS with lightweight options
import pyttsx3

def create_lightweight_tts():
    engine = pyttsx3.init()
    engine.setProperty('rate', 180)  # Faster speech
    engine.setProperty('volume', 0.9)
    return engine
```

### **Memory Optimization**
```python
# Add to your app configuration
import gc
import threading

def cleanup_memory():
    """Periodic memory cleanup for free hosting"""
    while True:
        gc.collect()
        threading.Event().wait(300)  # Every 5 minutes

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_memory, daemon=True)
cleanup_thread.start()
```

### **Environment Variables for Free Hosting**
```env
# Optimized for free tiers
FLASK_ENV=production
MAX_CONTENT_LENGTH=10485760  # 10MB instead of 50MB
RATE_LIMIT_PER_MINUTE=30     # Lower rate limit
CLEANUP_TEMP_FILES_HOURS=1   # Aggressive cleanup
MAX_CONCURRENT_CONVERSIONS=1 # Single conversion at a time
```

## 🎮 **GPU Access Workarounds**

### **1. Google Colab for Heavy Processing**
```python
# Use Colab for batch processing, deploy API on free hosting
# colab_processor.py
import requests

def process_via_colab(file_data):
    # Upload to temporary storage
    # Process with GPU in Colab
    # Return download link
    pass
```

### **2. Kaggle Kernels Integration**
```python
# Submit batch jobs to Kaggle
def kaggle_batch_process(files):
    # Use Kaggle API to submit processing job
    # Poll for completion
    # Retrieve results
    pass
```

## 💾 **Free Storage Solutions**

### **1. Firebase Storage (Free Tier)**
```javascript
// 5GB free, good for small files
const storage = firebase.storage();
const storageRef = storage.ref();
```

### **2. Cloudinary (Free Tier)**
```python
# Good for audio files, 25GB free
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name="your-cloud-name",
    api_key="your-api-key",
    api_secret="your-api-secret"
)
```

### **3. AWS S3 Free Tier**
```bash
# 5GB storage, 20K get requests, 2K put requests
# Perfect for starting out
```

## 🔒 **Security on Free Hosting**

### **Environment Variables Security**
```bash
# Never commit .env files
echo ".env" >> .gitignore

# Use platform secret management
# Render: Environment variables in dashboard
# Railway: railway variables set KEY=value
# Google Cloud: Secret Manager
```

### **API Rate Limiting**
```python
# Extra aggressive rate limiting for free tiers
@rate_limit_decorator(limit=10, per=60)  # 10 requests per minute
def upload_endpoint():
    pass
```

### **Request Size Limits**
```python
# Smaller limits for free hosting
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB
```

## 🛠️ **Deployment Scripts**

### **render-deploy.sh**
```bash
#!/bin/bash
echo "Deploying to Render..."
git add .
git commit -m "Deploy to Render"
git push origin main
echo "Deployment triggered!"
```

### **railway-deploy.sh**
```bash
#!/bin/bash
echo "Deploying to Railway..."
railway up --detach
railway logs
```

## 📊 **Monitoring Free Resources**

### **Simple Health Check**
```python
@app.route('/health')
def health_check():
    import psutil
    return {
        'status': 'healthy',
        'memory_usage': f"{psutil.virtual_memory().percent}%",
        'cpu_usage': f"{psutil.cpu_percent()}%",
        'uptime': time.time() - start_time
    }
```

### **Usage Tracking**
```python
# Track API usage to stay within limits
redis_client.incr(f"api_calls:{date.today()}")
```

## ⚠️ **Free Hosting Limitations**

1. **Cold Starts:** Apps sleep after inactivity
2. **Resource Limits:** CPU/memory constraints
3. **No Persistent Storage:** Use cloud storage
4. **Time Limits:** Some platforms have hourly limits
5. **No GPU:** Must use CPU-optimized models

## 🎯 **Recommended Stack for Free Hosting**

```
┌─────────────────┐
│   Frontend      │ → Vercel/Netlify (Free)
│   (React)       │
└─────────────────┘
         │
┌─────────────────┐
│   API Backend   │ → Render.com (Free)
│   (Flask)       │
└─────────────────┘
         │
┌─────────────────┐
│   File Storage  │ → AWS S3 (Free Tier)
│   (S3/Firebase) │
└─────────────────┘
```

This setup gives you a production-ready, secure deployment at zero cost while maintaining all security features!