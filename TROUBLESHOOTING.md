# 🔧 Troubleshooting Guide

## Common Deployment Issues

### ❌ Issue: `ERROR: No matching distribution found for ebooklib==0.18.1`

**Problem:** Docker container fails because ebooklib version doesn't exist.

**Solution 1: Fixed Version (Try First)**
I've updated to use ebooklib==0.19 (latest version):

```bash
git add .
git commit -m "fix: use correct ebooklib version 0.19"
git push origin main
```

**Solution 2: Flexible Requirements (If version conflicts)**
Use flexible version ranges:

```bash
cd backend
cp requirements-flexible.txt requirements.txt
git add requirements.txt
git commit -m "fix: use flexible requirements"
git push origin main
```

**Solution 3: Minimal Dependencies (Guaranteed to work)**
Skip ebooklib completely, support PDF + TXT only:

```bash
cd backend
cp requirements-minimal.txt requirements.txt
git add requirements.txt
git commit -m "fix: use minimal dependencies - PDF and TXT only"
git push origin main
```

**What each solution provides:**
- **Solution 1:** Full support (PDF, EPUB, TXT) 
- **Solution 2:** Full support with flexible versions
- **Solution 3:** PDF and TXT only (guaranteed deployment)

### ❌ Issue: Docker Build Timeout

**Problem:** Build takes too long and times out.

**Solution:**
- Render free tier has build limits
- Try building locally first to verify:
  ```bash
  cd backend
  docker build -t test .
  ```
- Consider upgrading to Render paid plan for faster builds

### ❌ Issue: App Crashes on Startup

**Problem:** Container starts but crashes immediately.

**Solutions:**
1. **Check Render logs** for detailed error messages
2. **Verify environment variables** are set correctly
3. **Test health endpoint** after deployment

### ❌ Issue: Frontend Can't Connect to Backend

**Problem:** CORS errors or connection refused.

**Solutions:**
1. **Update CORS origins** in Render environment variables:
   ```
   CORS_ORIGINS=https://your-frontend.netlify.app,https://localhost:8081
   ```

2. **Update frontend API URL** in Netlify environment variables:
   ```
   REACT_APP_API_URL=https://your-backend.onrender.com
   ```

3. **Check both services are deployed** and healthy

### ❌ Issue: File Upload Fails

**Problem:** Files don't upload or conversion fails.

**Solutions:**
1. **Check file size** (max 50MB)
2. **Check file type** (PDF, TXT supported; EPUB if ebooklib available)  
3. **Check Render logs** for detailed error messages
4. **Verify disk space** on free tier (1GB limit)

### ❌ Issue: TTS (Text-to-Speech) Errors

**Problem:** Audio conversion fails.

**Solutions:**
1. **Check system dependencies** in Dockerfile (espeak, etc.)
2. **Try smaller text files** first
3. **Check available memory** (free tier has limits)

## 🔍 Debugging Steps

### 1. Check Backend Health
```bash
curl https://your-backend.onrender.com/health
```
Should return:
```json
{
  "status": "healthy",
  "timestamp": "2024-xx-xx...",
  "service": "eBookVoice AI Converter"
}
```

### 2. Check Frontend Access
- Visit `https://your-frontend.netlify.app`
- Should load the upload interface
- Open browser console for JavaScript errors

### 3. Check Render Logs
- Go to Render Dashboard → Your Service → Logs
- Look for Python tracebacks or errors
- Check startup messages

### 4. Check Netlify Logs  
- Go to Netlify Dashboard → Your Site → Functions
- Check build logs and deploy logs
- Look for build failures

### 5. Test Local Development
```bash
# Backend
cd backend
python app.py

# Frontend  
cd frontend
npm run web
```

## 🚨 Emergency Fixes

### Quick Fix: Disable EPUB Temporarily
If ebooklib keeps causing issues, you can quickly disable it:

1. **Comment out in requirements.txt:**
   ```
   # ebooklib==0.18.1
   ```

2. **App will still work with PDF and TXT files**

3. **Add EPUB support back later when stable**

### Quick Fix: Use Minimal Backend
If all else fails, use the absolute minimal setup:

```bash
cd backend
echo "Flask==2.3.3
Flask-CORS==4.0.0
PyPDF2==3.0.1
pyttsx3==2.90
beautifulsoup4==4.12.2
requests==2.31.0" > requirements.txt
git add requirements.txt
git commit -m "minimal setup"
git push origin main
```

## 📞 Getting Help

### Check These First:
1. **Render Status:** https://status.render.com
2. **Netlify Status:** https://status.netlify.com  
3. **GitHub Actions:** Check your repo's Actions tab

### Log Locations:
- **Render:** Dashboard → Service → Logs
- **Netlify:** Dashboard → Site → Functions/Deploy logs
- **GitHub Actions:** Repository → Actions tab
- **Local:** Terminal output when running commands

### Common Solutions:
- **Restart services:** Redeploy on Render/Netlify
- **Clear cache:** Force rebuild with "Clear cache" option
- **Check quotas:** Free tiers have limits
- **Verify secrets:** GitHub Actions secrets must be correct