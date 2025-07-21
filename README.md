# eBookVoice-AI

## Overview

eBookVoice-AI is a professional AI-powered system that converts ebooks (PDF, EPUB, TXT) into high-quality audiobooks with smart chapter detection and natural neural voice synthesis.

This project consists of:

- **Backend**: Flask API for ebook processing and neural audio generation ([backend/converter.py](backend/converter.py))
- **Frontend**: React landing page and demo interface ([frontend/landing-page/src/App.js](frontend/landing-page/src/App.js))

---

## Prerequisites

- Python 3.8+
- Node.js 16+
- pip (Python package manager)
- npm (Node.js package manager)
- CUDA-enabled GPU (recommended for neural synthesis)
- All required Python libraries (see below)

---

## Backend Setup

1. **Install Python dependencies**  
   Open a terminal in the `backend` folder and run:

   ```sh
   pip install flask flask-cors PyPDF2 ebooklib beautifulsoup4 pyttsx3 TTS
   ```

2. **Start the backend server**  
   In the `backend` folder, run:
   ```sh
   python converter.py
   ```
   - The server will start at `http://localhost:5001`
   - Health check endpoint: `http://localhost:5001/health`

---

## Frontend Setup

1. **Install frontend dependencies**  
   Open a terminal in `frontend/landing-page` and run:

   ```sh
   npm install
   ```

2. **Start the React frontend**  
   In the same folder, run:
   ```sh
   npm start
   ```
   - The app will open at `http://localhost:3000`

---

## Usage

1. **Open the frontend in your browser**  
   Go to `http://localhost:3000`

2. **Upload an ebook**

   - Click "Try Free Demo" or use the upload section.
   - Supported formats: PDF, EPUB, TXT (max 50MB for backend, 5MB for trial).

3. **Start conversion**

   - Click "Convert with AI".
   - The frontend will show progress and detailed statistics.

4. **Listen to your audiobook**
   - Use the built-in audio player to play chapters.
   - View chapter navigation, speaker info, and technical details.

---

## Troubleshooting

- If the backend is not running, check the health status in the frontend.
- For GPU errors, ensure CUDA drivers are installed and compatible.
- For missing dependencies, re-run the pip install command above.

---

## Advanced

- To change conversion settings (word limit, speaker, etc.), modify parameters in [`backend/converter.py`](backend/converter.py).
- For full book conversion, use the `/api/fullconvert` endpoint.
- For chapter-by-chapter testing, use `/api/convert-audio-test`.

---

## File Structure

- `backend/converter.py`: Main backend API and processing logic
- `frontend/landing-page/src/App.js`: Main React app and UI
- `uploads/`, `chapters/`, `audiobooks/`: Backend storage folders (auto-created)

---
