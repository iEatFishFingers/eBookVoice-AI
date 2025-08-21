import os
import uuid
import threading
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import PyPDF2
import ebooklib
from ebooklib import epub
import pyttsx3
from bs4 import BeautifulSoup
from config import config

def create_app(config_name=None):
    """Application factory pattern."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Configure CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Configure logging for production
    if config_name == 'production':
        logging.basicConfig(level=logging.INFO)
        app.logger.setLevel(logging.INFO)
    
    # Create directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['AUDIOBOOKS_FOLDER'], exist_ok=True)
    
    return app

app = create_app()

# In-memory storage for conversion jobs
conversion_jobs = {}

class SimpleEBookConverter:
    def __init__(self):
        self.tts_engine = pyttsx3.init()
        
    def extract_text_from_pdf(self, file_path):
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def extract_text_from_epub(self, file_path):
        book = epub.read_epub(file_path)
        text = ""
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text += soup.get_text() + "\n"
        return text
    
    def extract_text_from_txt(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def text_to_speech(self, text, output_path):
        self.tts_engine.save_to_file(text, output_path)
        self.tts_engine.runAndWait()

def background_conversion(job_id, file_path):
    try:
        converter = SimpleEBookConverter()
        job = conversion_jobs[job_id]
        
        # Update status
        job['status'] = 'processing'
        job['progress'] = 10
        job['current_phase'] = 'Extracting text from file'
        job['updatedAt'] = datetime.now().isoformat()
        
        # Extract text based on file type
        file_extension = Path(file_path).suffix.lower()
        if file_extension == '.pdf':
            text = converter.extract_text_from_pdf(file_path)
        elif file_extension == '.epub':
            text = converter.extract_text_from_epub(file_path)
        elif file_extension in ['.txt', '.text']:
            text = converter.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        job['progress'] = 50
        job['current_phase'] = 'Converting text to speech'
        job['updatedAt'] = datetime.now().isoformat()
        
        # Generate audio
        output_filename = f"{job_id}_audiobook.wav"
        output_path = os.path.join(app.config['AUDIOBOOKS_FOLDER'], output_filename)
        converter.text_to_speech(text, output_path)
        
        # Complete conversion
        job['status'] = 'completed'
        job['progress'] = 100
        job['current_phase'] = 'Conversion completed'
        job['audioFile'] = output_filename
        job['updatedAt'] = datetime.now().isoformat()
        
    except Exception as e:
        job['status'] = 'failed'
        job['error'] = str(e)
        job['updatedAt'] = datetime.now().isoformat()
        app.logger.error(f"Conversion failed for job {job_id}: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'eBookVoice AI Converter'
    })

@app.route('/upload', methods=['POST'])
def upload_and_convert():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Validate file type
        original_filename = uploaded_file.filename
        file_extension = Path(original_filename).suffix.lower()
        supported_extensions = {'.pdf', '.epub', '.txt', '.text'}
        
        if file_extension not in supported_extensions:
            return jsonify({
                'success': False,
                'error': f'Unsupported file type: {file_extension}',
                'supported_types': list(supported_extensions)
            }), 400
        
        # Save uploaded file
        filename = f"{job_id}_{original_filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(file_path)
        
        # Create conversion job
        conversion_jobs[job_id] = {
            'id': job_id,
            'title': Path(original_filename).stem,
            'fileName': original_filename,
            'status': 'pending',
            'progress': 0,
            'current_phase': 'File uploaded, queued for processing',
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
        
        # Start background conversion
        thread = threading.Thread(target=background_conversion, args=(job_id, file_path))
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'data': conversion_jobs[job_id]})
        
    except Exception as e:
        app.logger.error(f"Upload failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/conversions/<job_id>', methods=['GET'])
def get_conversion_status(job_id):
    if job_id not in conversion_jobs:
        return jsonify({'success': False, 'error': 'Conversion job not found'}), 404
    
    return jsonify({'success': True, 'data': conversion_jobs[job_id]})

@app.route('/conversions', methods=['GET'])
def get_all_conversions():
    sorted_jobs = sorted(
        conversion_jobs.values(),
        key=lambda x: x['createdAt'],
        reverse=True
    )
    return jsonify({'success': True, 'data': sorted_jobs})

@app.route('/download/<job_id>', methods=['GET'])
def download_audiobook(job_id):
    if job_id not in conversion_jobs:
        return jsonify({'success': False, 'error': 'Conversion job not found'}), 404
    
    job = conversion_jobs[job_id]
    if job['status'] != 'completed':
        return jsonify({'success': False, 'error': 'Conversion not completed'}), 400
    
    audio_file_path = os.path.join(app.config['AUDIOBOOKS_FOLDER'], job['audioFile'])
    if not os.path.exists(audio_file_path):
        return jsonify({'success': False, 'error': 'Audio file not found'}), 404
    
    return send_file(audio_file_path, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("Starting eBookVoice AI MVP")
    print("Upload eBooks and convert to audio")
    print(f"Server running on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)