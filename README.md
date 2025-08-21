# eBookVoice AI - MVP

A simple eBook to audiobook converter using AI text-to-speech with production-ready DevOps pipeline.

## 🚀 Features

- Upload PDF, EPUB, or TXT files
- Extract text and convert to audio using AI TTS
- Real-time conversion progress tracking
- Download generated audiobooks
- Cross-platform React Native mobile app
- Production-ready Docker deployment
- CI/CD pipeline with GitHub Actions
- Secure HTTPS hosting on Render

## 📁 Project Structure

```
eBookVoice-AI-Current/
├── backend/              # Flask API server
│   ├── app.py           # Main Flask application
│   ├── config.py        # Production configuration
│   ├── Dockerfile       # Docker container setup
│   ├── requirements.txt # Python dependencies
│   ├── render.yaml      # Render deployment config
│   ├── tests/           # Automated tests
│   ├── uploads/         # Uploaded files
│   └── audiobooks/      # Generated audio files
├── frontend/            # React Native mobile app
│   ├── App.js          # Main app component
│   └── package.json    # Node.js dependencies
├── .github/workflows/   # CI/CD pipelines
│   └── deploy.yml      # GitHub Actions workflow
├── docker-compose.yml  # Local development setup
└── README.md
```

## 🏃‍♂️ Quick Start

### Option 1: Local Development

1. **Clone and setup backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   python app.py
   ```
   Server starts at `http://localhost:5001`

2. **Setup frontend:**
   ```bash
   cd frontend
   npm install
   npm start
   ```
   Use Expo Go app to scan QR code

### Option 2: Docker Development

1. **Run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```
   Backend runs at `http://localhost:5001`

## 🌐 Production Deployment

### Full Stack Deployment (Backend + Frontend)

#### 1. Deploy Backend to Render

1. **Create Render account:** https://render.com

2. **Create new Web Service:**
   - Connect your GitHub repository
   - Choose "Docker" environment
   - Set build context to `./backend`
   - Dockerfile path: `./backend/Dockerfile`

3. **Set Environment Variables in Render:**
   ```
   FLASK_ENV=production
   SECRET_KEY=your-super-secure-secret-key
   CORS_ORIGINS=https://your-frontend.netlify.app,https://localhost:8081
   PORT=8080
   ```

#### 2. Deploy Frontend to Netlify

1. **Create Netlify account:** https://netlify.com

2. **Create new Site:**
   - Connect your GitHub repository
   - Build command: `npm run build`
   - Publish directory: `web-build`
   - Base directory: `frontend`

3. **Set Environment Variables in Netlify:**
   ```
   REACT_APP_API_URL=https://your-backend.onrender.com
   ```

#### 3. Set up GitHub Secrets for Full Stack CI/CD

Go to your repo → Settings → Secrets and variables → Actions:

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

### Alternative: Deploy to Railway

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy:**
   ```bash
   railway login
   railway init
   railway up
   ```

## 🧪 Testing

**Run tests locally:**
```bash
cd backend
python -m pytest tests/ -v
```

**Docker test:**
```bash
docker-compose run backend python -m pytest tests/ -v
```

## 🔧 CI/CD Pipeline

The GitHub Actions workflow automatically:
- ✅ **Tests backend:** Python tests + Docker build
- ✅ **Tests frontend:** React Native web build
- ✅ **Deploys backend:** To Render with health checks
- ✅ **Deploys frontend:** To Netlify with build validation
- ✅ **Full stack verification:** End-to-end connectivity tests
- ✅ **Parallel deployment:** Backend and frontend deploy simultaneously

## 🔒 Security Features

- Production-ready Flask configuration
- Secure secret key management via environment variables
- CORS protection with configurable origins
- Docker security best practices (non-root user)
- HTTPS by default on Render
- Input validation and file type restrictions

## 📡 API Endpoints

- `GET /health` - Health check
- `POST /upload` - Upload and convert eBook
- `GET /conversions` - List all conversions
- `GET /conversions/<job_id>` - Get conversion status
- `GET /download/<job_id>` - Download audio file

## 📱 Usage

### 🌐 **Production (Recommended)**
1. **Access your web app:** `https://your-frontend.netlify.app`
2. **Upload eBook** and monitor conversion in browser
3. **Download audio** directly to your computer
4. **Share with others:** Send them your Netlify URL!

### 📱 **Mobile Development**
1. **Launch Expo:** `npm start` in frontend folder
2. **Scan QR code** with Expo Go app
3. **Upload eBook** from your phone
4. **Download audio** when complete

### 💻 **Local Development**
1. **Start backend:** `python app.py` (or `docker-compose up`)
2. **Start frontend:** `npm run web` for browser or `npm start` for mobile

## 📋 Supported File Types

- PDF (`.pdf`)
- EPUB (`.epub`)
- Plain Text (`.txt`, `.text`)

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Development
FLASK_ENV=development
SECRET_KEY=dev-secret-key
CORS_ORIGINS=http://localhost:8081

# Production (set in hosting provider)
FLASK_ENV=production
SECRET_KEY=super-secure-production-key
CORS_ORIGINS=https://your-domain.com
```

## 📊 Monitoring

- Health check endpoint: `/health`
- Docker health checks configured
- Render provides built-in monitoring
- GitHub Actions deployment notifications

## 🔄 Scaling

**Current MVP limitations:**
- In-memory job storage (lost on restart)
- Single server instance
- File storage on container filesystem

**Future scaling options:**
- Add Redis for job persistence
- Implement queue system (Celery + Redis)
- Use cloud storage (AWS S3, Google Cloud)
- Add database for job history
- Horizontal scaling with load balancer

## 🛠️ Development

**Hot reload with Docker:**
```bash
docker-compose up
# Code changes trigger automatic reload
```

**Local debugging:**
```bash
cd backend
FLASK_ENV=development python app.py
```

**Run specific tests:**
```bash
python -m pytest tests/test_app.py::TestHealthEndpoint -v
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

CI/CD will automatically test your changes!

## 📞 Support

- **Issues:** GitHub Issues
- **Deployment:** Check Render logs
- **CI/CD:** GitHub Actions tab