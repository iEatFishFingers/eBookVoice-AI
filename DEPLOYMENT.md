# 🚀 Deployment Guide

Complete step-by-step guide to deploy eBookVoice AI to production.

## Prerequisites

- GitHub account
- Git installed locally
- Docker (optional, for local testing)

## 🌟 Quick Deploy to Render (Recommended)

### Step 1: Prepare Repository

1. **Fork/clone this repository**
2. **Push to your GitHub repo:**
   ```bash
   git add .
   git commit -m "Initial commit with production setup"
   git push origin main
   ```

### Step 2: Create Render Account

1. Go to https://render.com
2. Sign up with your GitHub account
3. Verify your email

### Step 3: Deploy Backend to Render

1. **Create New Web Service:**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Select your eBookVoice repository

2. **Configure Service:**
   ```
   Name: ebookvoice-backend
   Environment: Docker
   Branch: main
   Build Context: ./backend
   Dockerfile Path: ./backend/Dockerfile
   ```

3. **Set Environment Variables:**
   ```bash
   FLASK_ENV=production
   SECRET_KEY=your-super-secure-random-key-here
   CORS_ORIGINS=https://your-frontend-name.netlify.app,https://localhost:8081
   PORT=8080
   ```

4. **Choose Plan:**
   - Free tier (0 GB RAM, sleeps after 15min inactivity)
   - Or Starter ($7/month, always on)

5. **Deploy:**
   - Click "Create Web Service"
   - Wait 5-10 minutes for first deployment
   - Your API will be available at `https://your-backend-name.onrender.com`
   - **Copy this URL** - you'll need it for the frontend!

### Step 4: Deploy Frontend to Netlify

1. **Create Netlify Account:**
   - Go to https://netlify.com
   - Sign up with your GitHub account

2. **Create New Site:**
   - Click "Add new site" → "Import an existing project"
   - Choose GitHub and select your repository
   - Configure build settings:
   ```
   Base directory: frontend
   Build command: npm run build
   Publish directory: web-build
   ```

3. **Set Environment Variables in Netlify:**
   - Go to Site settings → Environment variables
   - Add:
   ```bash
   REACT_APP_API_URL=https://your-backend-name.onrender.com
   ```

4. **Deploy:**
   - Click "Deploy site"
   - Wait 2-3 minutes for first deployment
   - Your app will be available at `https://your-frontend-name.netlify.app`

### Step 5: Test Full Stack Deployment

1. **Backend Health Check:**
   ```bash
   curl https://your-backend-name.onrender.com/health
   ```
   Expected response:
   ```json
   {
     "status": "healthy",
     "timestamp": "2024-xx-xxT12:xx:xx.xxxxxx",
     "service": "eBookVoice AI Converter"
   }
   ```

2. **Frontend Access:**
   - Visit `https://your-frontend-name.netlify.app`
   - You should see the eBookVoice AI interface
   - Try uploading a text file to test the full workflow

3. **Full Workflow Test:**
   - Upload a small text file
   - Wait for conversion to complete
   - Download the generated audio file
   - Success! 🎉

### Step 6: Setup Full Stack CI/CD (Recommended)

1. **Get Render API Credentials:**
   - Go to Render Dashboard → Account Settings → API Keys
   - Create new API key
   - Copy Service ID from your backend service URL

2. **Get Netlify API Credentials:**
   - Go to Netlify Dashboard → User settings → Personal access tokens
   - Generate new token
   - Copy Site ID from your site settings

3. **Add GitHub Secrets:**
   - Go to your repo → Settings → Secrets and variables → Actions
   - Add all the following secrets:
   
   **Backend (Render):**
   ```
   RENDER_SERVICE_ID=srv-xxxxxxxxxxxxxxxxxx
   RENDER_API_KEY=rnd_xxxxxxxxxxxxxxxxxxxx
   RENDER_SERVICE_URL=https://your-backend.onrender.com
   ```
   
   **Frontend (Netlify):**
   ```
   NETLIFY_SITE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   NETLIFY_AUTH_TOKEN=nfp_xxxxxxxxxxxxxxxxxxxx
   NETLIFY_SITE_URL=https://your-frontend.netlify.app
   ```

4. **Test Full Stack CI/CD:**
   - Make a small change to any code
   - Push to main branch
   - Check GitHub Actions tab
   - Both backend and frontend will deploy automatically! 🚀

## 🚄 Alternative: Deploy to Railway

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

### Step 2: Deploy

```bash
# Login
railway login

# Initialize in backend directory
cd backend
railway init

# Deploy
railway up
```

### Step 3: Configure Environment

```bash
# Set environment variables
railway variables set FLASK_ENV=production
railway variables set SECRET_KEY=your-secure-key
railway variables set CORS_ORIGINS=https://localhost:8081
```

## 🐳 Local Production Testing

Test production build locally before deployment:

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build and run manually
cd backend
docker build -t ebookvoice-backend .
docker run -p 8080:8080 -e FLASK_ENV=production ebookvoice-backend
```

## 📱 Update Frontend for Production

1. **Update API URL in `frontend/App.js`:**
   ```javascript
   const API_BASE_URL = 'https://your-service-name.onrender.com';
   ```

2. **Test with Expo:**
   ```bash
   cd frontend
   npm start
   ```

## 🔧 Environment Variables Reference

### Required Production Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `production` |
| `SECRET_KEY` | Flask secret key | `super-secure-random-key` |
| `PORT` | Server port | `8080` |
| `CORS_ORIGINS` | Allowed origins | `https://expo.dev,https://localhost:8081` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `UPLOAD_FOLDER` | Upload directory | `uploads` |
| `AUDIOBOOKS_FOLDER` | Audio output directory | `audiobooks` |

## 🔍 Monitoring & Troubleshooting

### Check Deployment Status

1. **Render Dashboard:**
   - View logs in real-time
   - Monitor resource usage
   - Check deployment history

2. **Health Check:**
   ```bash
   curl https://your-service.onrender.com/health
   ```

### Common Issues

**Issue: Service won't start**
- Check environment variables are set
- Verify Dockerfile builds locally
- Check Render logs for Python errors

**Issue: CORS errors in frontend**
- Add your Expo development URL to `CORS_ORIGINS`
- Format: `exp://192.168.x.x:19006`

**Issue: File uploads fail**
- Check file size limits (50MB max)
- Verify upload directory permissions
- Monitor disk space (1GB max on free tier)

### Log Access

**Render Logs:**
```bash
# Install Render CLI (optional)
npm install -g @render/cli
render login
render logs
```

**Application Logs:**
- Available in Render dashboard
- Real-time streaming
- Downloadable for analysis

## 🔄 Updates & Rollbacks

### Automated Updates (CI/CD)

Once CI/CD is setup, every push to main branch automatically:
1. Runs tests
2. Builds Docker image  
3. Deploys to Render
4. Performs health check

### Manual Updates

1. **Push code changes:**
   ```bash
   git push origin main
   ```

2. **Trigger deployment in Render Dashboard:**
   - Go to your service
   - Click "Manual Deploy" → "Deploy latest commit"

### Rollback

1. **In Render Dashboard:**
   - Go to Deployments tab
   - Click "Rollback" on previous successful deployment

2. **Or redeploy specific commit:**
   - Select commit from dropdown
   - Click "Deploy"

## 🛡️ Security Checklist

- ✅ Use strong `SECRET_KEY` (32+ random characters)
- ✅ Set `FLASK_ENV=production`
- ✅ Configure CORS origins properly
- ✅ Never commit secrets to Git
- ✅ Use HTTPS only (automatic on Render)
- ✅ Regular dependency updates
- ✅ Monitor logs for suspicious activity

## 💰 Cost Estimates

### Render Free Tier
- **Cost:** $0/month
- **Limitations:** 
  - 750 hours/month
  - Sleeps after 15min inactivity
  - 1GB storage
  - Shared CPU/RAM

### Render Starter
- **Cost:** $7/month
- **Features:**
  - Always on
  - Dedicated resources
  - Custom domains
  - Priority support

### Railway
- **Cost:** Usage-based
- **Free tier:** $5 credit monthly
- **Typical cost:** $5-15/month for MVP

## 📞 Support

**Render Support:**
- Documentation: https://render.com/docs
- Community: https://community.render.com
- Status: https://status.render.com

**Railway Support:**
- Documentation: https://docs.railway.app
- Discord: https://discord.gg/railway
- Status: https://status.railway.app

**Project Issues:**
- GitHub Issues: Create issue in your repository
- Include deployment logs and error messages