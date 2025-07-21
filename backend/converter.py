# converter.py - Professional Audiobook Converter
# Built from scratch for chapter-by-chapter processing

import os
import re
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from flask import Flask, request, jsonify, send_file  # Add send_file to the imports

# Flask web framework for our API
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Ebook processing libraries
import PyPDF2  # For reading PDF files
import ebooklib  # For reading EPUB files
from ebooklib import epub
from bs4 import BeautifulSoup  # For parsing HTML content in EPUB files

# Text-to-speech library (the high-quality one from your old system)
import pyttsx3

# Create our Flask application instance
app = Flask(__name__)

# Configure CORS to allow your React frontend to communicate with this backend
# This is essential for local development where frontend and backend run on different ports
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])

# Configure upload settings
app.config['UPLOAD_FOLDER'] = 'uploads'          # Temporary storage for uploaded files
app.config['CHAPTERS_FOLDER'] = 'chapters'       # Where we save individual chapter text files
app.config['AUDIOBOOKS_FOLDER'] = 'audiobooks'   # Where we save converted audio files
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB maximum file size

# Create all necessary directories
# This ensures the folders exist before we try to save files to them
for folder in [app.config['UPLOAD_FOLDER'], app.config['CHAPTERS_FOLDER'], app.config['AUDIOBOOKS_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

print("🎧 AudioBook Converter - Professional Chapter-by-Chapter System")
print("=" * 60)
print("✅ Flask application initialized")
print("✅ CORS enabled for React frontend")
print("✅ Directory structure created")
print("📁 Upload folder:", app.config['UPLOAD_FOLDER'])
print("📄 Chapters folder:", app.config['CHAPTERS_FOLDER'])
print("🎵 Audio output folder:", app.config['AUDIOBOOKS_FOLDER'])
print("=" * 60)


class IntelligentChapterExtractor:

    """
    This class acts like an experienced librarian who can quickly scan any book
    and identify exactly where the meaningful content begins and how it's organized.
    
    The extractor understands common ebook patterns and automatically skips
    content that readers typically don't want in their audiobooks.
    """
    
    def __init__(self):
        # These patterns help us identify chapter boundaries in different types of books
        # Think of these as the "signatures" that indicate a new chapter is starting
        self.chapter_patterns = [
            r'^Chapter\s+\d+',           # "Chapter 1", "Chapter 2", etc.
            r'^CHAPTER\s+\d+',           # Uppercase version
            r'^Chapter\s+[IVX]+',        # Roman numerals: "Chapter I", "Chapter II"
            r'^\d+\.\s+',                # Numbered sections: "1. Introduction"
            r'^Part\s+\d+',              # "Part 1", "Part 2"
            r'^Book\s+\d+',              # "Book 1" for multi-book volumes
        ]
        
        # These words typically appear in front matter that we want to skip
        # The goal is to jump straight to the actual content readers care about
        self.skip_sections = [
            'copyright', 'dedication', 'acknowledgment', 'acknowledgments', 
            'foreword', 'preface', 'introduction', 'prologue', 
            'table of contents', 'contents', 'about the author', 
            'also by', 'praise for', 'reviews', 'publishing information',
            'isbn', 'library of congress', 'first edition'
        ]
        
        # Minimum words for a valid chapter - prevents tiny sections from being treated as chapters
        self.minimum_chapter_words = 200
    
    def extract_chapters_from_file(self, file_path: str) -> List[Dict]:
        """
        Main extraction method that routes to the appropriate handler based on file type.
        
        This method acts as a traffic director, sending each file type to the
        specialized extraction method that works best for that format.
        """
        file_extension = Path(file_path).suffix.lower()
        
        print(f"📖 Starting intelligent chapter extraction for {file_extension} file")
        
        if file_extension == '.epub':
            return self._extract_epub_chapters(file_path)
        elif file_extension == '.pdf':
            return self._extract_pdf_chapters(file_path)
        elif file_extension in ['.txt', '.text']:
            return self._extract_txt_chapters(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def _extract_epub_chapters(self, file_path: str) -> List[Dict]:
        """
        Extract chapters from EPUB files with intelligent content detection.
        
        EPUB files are actually ZIP archives containing HTML files, CSS, and metadata.
        We need to identify which HTML files contain actual chapters versus navigation,
        styling, or metadata, and then extract clean text from the chapter files.
        """
        try:
            print("📚 Processing EPUB file...")
            book = epub.read_epub(file_path)
            chapters = []
            
            # Get book metadata for context
            title = book.get_metadata('DC', 'title')
            book_title = title[0][0] if title else "Unknown Title"
            print(f"📖 Book title: {book_title}")
            
            # Extract all document items from the EPUB
            document_items = [item for item in book.get_items() 
                            if item.get_type() == ebooklib.ITEM_DOCUMENT]
            
            print(f"📄 Found {len(document_items)} document sections in EPUB")
            
            chapter_number = 0
            content_started = False  # Flag to track when we've reached actual content
            
            for item in document_items:
                try:
                    # Parse the HTML content of this section
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    
                    # Remove navigation, scripts, and styling elements
                    for unwanted in soup(["script", "style", "nav", "header", "footer"]):
                        unwanted.decompose()
                    
                    # Extract clean text
                    text_content = soup.get_text()
                    cleaned_text = self._clean_text(text_content)
                    
                    # Skip if this section doesn't have substantial content
                    if len(cleaned_text.split()) < self.minimum_chapter_words:
                        continue
                    
                    # Check if this is front matter we should skip
                    if not content_started and self._is_front_matter(cleaned_text):
                        print(f"⏭️  Skipping front matter section: {item.get_name()}")
                        continue
                    
                    # If we reach here, we're in the actual book content
                    content_started = True
                    chapter_number += 1
                    
                    # Try to detect a chapter title from the content
                    chapter_title = self._detect_chapter_title(soup, cleaned_text, chapter_number)
                    
                    chapter_data = {
                        'number': chapter_number,
                        'title': chapter_title,
                        'content': cleaned_text,
                        'word_count': len(cleaned_text.split()),
                        'source_file': item.get_name()
                    }
                    
                    chapters.append(chapter_data)
                    print(f"✅ Chapter {chapter_number}: {chapter_title} ({chapter_data['word_count']} words)")
                
                except Exception as e:
                    print(f"⚠️  Error processing EPUB section: {e}")
                    continue
            
            print(f"🎉 Successfully extracted {len(chapters)} chapters from EPUB")
            return chapters
            
        except Exception as e:
            print(f"❌ EPUB extraction failed: {e}")
            raise
    
    def _extract_pdf_chapters(self, file_path: str) -> List[Dict]:
        """
        Extract chapters from PDF files with intelligent page grouping.
        
        PDFs are challenging because they're designed for visual layout rather than
        semantic structure. We look for text patterns that typically indicate
        new chapters and group related pages together.
        """
        try:
            print("📑 Processing PDF file...")
            chapters = []
            current_chapter = None
            chapter_number = 0
            content_started = False
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                print(f"📄 PDF has {total_pages} pages")
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        
                        if not page_text.strip():
                            continue  # Skip empty pages
                        
                        cleaned_text = self._clean_text(page_text)
                        
                        # Skip front matter pages
                        if not content_started and self._is_front_matter(cleaned_text):
                            print(f"⏭️  Skipping front matter page {page_num + 1}")
                            continue
                        
                        # Check if this page starts a new chapter
                        chapter_start_title = self._detect_chapter_start(cleaned_text)
                        
                        if chapter_start_title:
                            # We found a new chapter start
                            content_started = True
                            
                            # Save the previous chapter if it exists and has enough content
                            if current_chapter and len(current_chapter['content'].split()) >= self.minimum_chapter_words:
                                current_chapter['word_count'] = len(current_chapter['content'].split())
                                chapters.append(current_chapter)
                                print(f"✅ Chapter {current_chapter['number']}: {current_chapter['title']} ({current_chapter['word_count']} words)")
                            
                            # Start a new chapter
                            chapter_number += 1
                            current_chapter = {
                                'number': chapter_number,
                                'title': chapter_start_title,
                                'content': cleaned_text,
                                'start_page': page_num + 1
                            }
                        
                        elif current_chapter:
                            # Continue adding to the current chapter
                            current_chapter['content'] += '\n\n' + cleaned_text
                        
                        elif content_started:
                            # We're in content but no chapter detected yet, start a default chapter
                            chapter_number += 1
                            current_chapter = {
                                'number': chapter_number,
                                'title': f'Chapter {chapter_number}',
                                'content': cleaned_text,
                                'start_page': page_num + 1
                            }
                    
                    except Exception as e:
                        print(f"⚠️  Error processing PDF page {page_num + 1}: {e}")
                        continue
                
                # Don't forget the last chapter
                if current_chapter and len(current_chapter['content'].split()) >= self.minimum_chapter_words:
                    current_chapter['word_count'] = len(current_chapter['content'].split())
                    chapters.append(current_chapter)
                    print(f"✅ Chapter {current_chapter['number']}: {current_chapter['title']} ({current_chapter['word_count']} words)")
            
            print(f"🎉 Successfully extracted {len(chapters)} chapters from PDF")
            return chapters
            
        except Exception as e:
            print(f"❌ PDF extraction failed: {e}")
            raise
    
    def _extract_txt_chapters(self, file_path: str) -> List[Dict]:
        """
        Extract chapters from plain text files using pattern recognition.
        
        Text files require the most intelligence because they have no formatting
        metadata. We look for textual patterns that typically indicate chapter
        boundaries in literature and documents.
        """
        try:
            print("📄 Processing text file...")
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                full_text = file.read()
            
            cleaned_text = self._clean_text(full_text)
            chapters = []
            
            # Try to split into chapters using pattern recognition
            chapter_splits = self._find_chapter_boundaries(cleaned_text)
            
            if len(chapter_splits) > 1:
                # We found chapter markers
                for i, (start_pos, title) in enumerate(chapter_splits):
                    # Determine the end position (start of next chapter or end of text)
                    if i + 1 < len(chapter_splits):
                        end_pos = chapter_splits[i + 1][0]
                    else:
                        end_pos = len(cleaned_text)
                    
                    chapter_content = cleaned_text[start_pos:end_pos].strip()
                    
                    if len(chapter_content.split()) >= self.minimum_chapter_words:
                        chapter_data = {
                            'number': i + 1,
                            'title': title or f'Chapter {i + 1}',
                            'content': chapter_content,
                            'word_count': len(chapter_content.split())
                        }
                        chapters.append(chapter_data)
                        print(f"✅ Chapter {i + 1}: {chapter_data['title']} ({chapter_data['word_count']} words)")
            
            else:
                # No clear chapters found, treat as single chapter
                if len(cleaned_text.split()) >= self.minimum_chapter_words:
                    chapter_data = {
                        'number': 1,
                        'title': 'Complete Text',
                        'content': cleaned_text,
                        'word_count': len(cleaned_text.split())
                    }
                    chapters.append(chapter_data)
                    print(f"✅ Single chapter: {chapter_data['word_count']} words")
            
            print(f"🎉 Successfully processed text file into {len(chapters)} chapters")
            return chapters
            
        except Exception as e:
            print(f"❌ Text file extraction failed: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text for better readability and audio conversion.
        
        This method removes artifacts that would sound awkward when converted
        to speech while preserving the natural flow of the content.
        """
        if not text:
            return ""
        
        # Normalize whitespace and line breaks
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\r', '\n', text)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple empty lines to double
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces to single space
        text = re.sub(r'\n\s+', '\n', text)  # Remove leading spaces on lines
        
        # Remove common digital artifacts
        text = re.sub(r'\.{4,}', '...', text)  # Multiple dots to ellipsis
        text = re.sub(r'-\s*\n\s*', '', text)  # Remove hyphenation breaks
        
        # Ensure proper sentence spacing for natural speech
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)
        
        # Replace problematic characters for text-to-speech
        text = text.replace('—', ' - ')  # Em dash
        text = text.replace('"', '"').replace('"', '"')  # Smart quotes
        text = text.replace(''', "'").replace(''', "'")  # Smart apostrophes
        
        return text.strip()
    
    def _is_front_matter(self, text: str) -> bool:
        """
        Determine if a section of text is front matter that should be skipped.
        
        This method identifies content like copyright pages, dedications, and
        table of contents that readers typically don't want in their audiobooks.
        """
        text_lower = text.lower()
        
        # Check for front matter indicators
        for indicator in self.skip_sections:
            if indicator in text_lower:
                return True
        
        # Additional heuristics for front matter
        if len(text.split()) < 100:  # Very short sections are often front matter
            if any(word in text_lower for word in ['copyright', '©', 'isbn', 'published']):
                return True
        
        return False
    
    def _detect_chapter_title(self, soup, text: str, chapter_number: int) -> str:
        """
        Intelligently detect the title of a chapter from HTML soup or text content.
        """
        # First try to find HTML heading tags
        if soup:
            for heading_level in ['h1', 'h2', 'h3']:
                headings = soup.find_all(heading_level)
                for heading in headings:
                    title_text = heading.get_text().strip()
                    if title_text and 5 <= len(title_text) <= 100:
                        return title_text
        
        # Look for chapter patterns in the first few lines
        lines = text.split('\n')[:5]
        for line in lines:
            line = line.strip()
            if 5 <= len(line) <= 100:
                for pattern in self.chapter_patterns:
                    if re.match(pattern, line, re.IGNORECASE):
                        return line
        
        # Fallback to generic chapter name
        return f'Chapter {chapter_number}'
    
    def _detect_chapter_start(self, text: str) -> Optional[str]:
        """
        Detect if text begins with a chapter marker and return the chapter title.
        """
        lines = text.split('\n')[:3]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            for pattern in self.chapter_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    return line
        
        return None
    
    def _find_chapter_boundaries(self, text: str) -> List[tuple]:
        """
        Find chapter boundaries in plain text and return list of (position, title) tuples.
        """
        boundaries = []
        lines = text.split('\n')
        current_pos = 0
        
        for line in lines:
            for pattern in self.chapter_patterns:
                if re.match(pattern, line.strip(), re.IGNORECASE):
                    boundaries.append((current_pos, line.strip()))
                    break
            current_pos += len(line) + 1  # +1 for the newline character
        
        return boundaries

class AdvancedAudiobookGenerator:
    """
    Professional audiobook generation system using XTTS with proper voice configuration.
    
    This corrected version addresses the voice naming issues discovered in the diagnostic.
    Instead of using fictional voice names, it works with the actual XTTS speakers
    that are available in your system. The diagnostic showed you have 58 built-in
    speakers ready to use, so we'll leverage those properly.
    
    The key insight is that XTTS initialization was failing because the original
    code tried to use non-existent speaker names. This version discovers and uses
    the real speakers available in your XTTS installation.
    """
    
    def __init__(self):
        """Initialize the XTTS system with proper speaker discovery and configuration."""
        print("🎙️ Advanced Audiobook Generator (XTTS) initializing...")
        
        # Initialize instance variables
        self.xtts_model = None
        self.device = "cuda" if self._check_gpu_availability() else "cpu"
        self.model_loaded = False
        self.available_speakers = []
        self.speaker_categories = {}
        
        # Configuration for optimal audiobook generation
        self.audio_settings = {
            'sample_rate': 24000,  # XTTS v2 native sample rate
            'temperature': 0.75,   # Controls randomness in speech generation
            'length_penalty': 1.0, # Influences speech pacing
            'repetition_penalty': 5.0, # Prevents word repetition artifacts
            'top_k': 50,          # Limits vocabulary selection for consistency
            'top_p': 0.85,        # Another parameter for speech quality control
        }
        
        print(f"⚡ Computing device: {self.device}")
        
        # Attempt to initialize the model immediately
        # Based on your diagnostic, this should work without issues
        if self.initialize_xtts_model():
            print("🎉 XTTS system ready for audiobook generation!")
        else:
            print("❌ XTTS initialization failed - check error messages above")
    
    def _check_gpu_availability(self):
        """Check if GPU acceleration is available for faster processing."""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def initialize_xtts_model(self):
        """
        Load and initialize the XTTS model using the correct approach.
        
        Based on your diagnostic results, we know that:
        1. XTTS v2 model is available and downloads properly
        2. 58 built-in speakers are ready to use
        3. Audio generation works correctly
        
        This method implements the initialization pattern that works with your system.
        """
        try:
            print("🧠 Loading XTTS neural network model...")
            
            # Import XTTS components - your diagnostic confirmed these work
            from TTS.api import TTS
            
            # Initialize the XTTS v2 model
            # Your diagnostic showed this model downloads and initializes successfully
            model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
            print(f"📦 Loading model: {model_name}")
            
            # Initialize with progress bar to show download progress if needed
            self.xtts_model = TTS(model_name, progress_bar=True)
            
            # Move model to appropriate device for optimal performance
            # Your diagnostic showed CUDA is available with RTX 3080 Ti
            if self.device == "cuda":
                self.xtts_model = self.xtts_model.to("cuda")
                print("🚀 Model loaded on GPU (RTX 3080 Ti) for accelerated processing")
            else:
                print("🐌 Model loaded on CPU")
            
            # Discover and categorize available speakers
            # Your diagnostic showed 58 speakers are available
            self._discover_available_speakers()
            
            self.model_loaded = True
            
            # Test the model with a short phrase to ensure everything works
            print("🧪 Testing model functionality...")
            if self._verify_model_functionality():
                print("✅ XTTS model initialization completed successfully!")
                print(f"🎭 Discovered {len(self.available_speakers)} available speakers")
                return True
            else:
                print("❌ Model functionality test failed")
                return False
                
        except ImportError as import_error:
            print(f"❌ XTTS import failed: {import_error}")
            print("💡 This shouldn't happen since your diagnostic passed")
            return False
            
        except Exception as model_error:
            print(f"❌ XTTS model initialization failed: {model_error}")
            print("💡 Check the specific error message above for troubleshooting")
            return False
    
    def _discover_available_speakers(self):
        """
        Discover and categorize the actual speakers available in your XTTS installation.
        
        Your diagnostic showed 58 speakers are available with names like "Claribel Dervla",
        "Daisy Studious", etc. This method catalogs them and organizes them by characteristics
        to make speaker selection easier for audiobook generation.
        """
        try:
            if not self.xtts_model:
                return
            
            # Get the list of speakers from XTTS
            # Your diagnostic confirmed this attribute exists and contains 58 speakers
            if hasattr(self.xtts_model, 'speakers') and self.xtts_model.speakers:
                self.available_speakers = self.xtts_model.speakers
                
                print(f"📋 Discovered {len(self.available_speakers)} XTTS speakers:")
                
                # Categorize speakers for easier selection
                # We'll create categories based on name characteristics to help choose
                # appropriate voices for different types of content
                self.speaker_categories = {
                    'professional_female': [],
                    'professional_male': [],
                    'warm_female': [],
                    'warm_male': [],
                    'clear_female': [],
                    'clear_male': [],
                    'all_speakers': self.available_speakers
                }
                
                # Simple categorization based on name patterns and characteristics
                # This is a heuristic approach since we don't have detailed voice metadata
                for speaker in self.available_speakers[:20]:  # Show first 20 for brevity
                    speaker_lower = speaker.lower()
                    
                    # Basic gender detection based on common name patterns
                    # This is approximate but helps with initial categorization
                    likely_female_names = ['claribel', 'daisy', 'gracie', 'tammie', 'alison', 'emma', 'sofia', 'maria', 'anna', 'sarah']
                    likely_male_names = ['david', 'james', 'michael', 'robert', 'william', 'john', 'daniel', 'thomas', 'christopher', 'matthew']
                    
                    is_female = any(name in speaker_lower for name in likely_female_names)
                    is_male = any(name in speaker_lower for name in likely_male_names)
                    
                    # Categorize based on name characteristics
                    if 'professional' in speaker_lower or 'clear' in speaker_lower:
                        if is_female:
                            self.speaker_categories['professional_female'].append(speaker)
                        elif is_male:
                            self.speaker_categories['professional_male'].append(speaker)
                    elif 'warm' in speaker_lower or 'friendly' in speaker_lower:
                        if is_female:
                            self.speaker_categories['warm_female'].append(speaker)
                        elif is_male:
                            self.speaker_categories['warm_male'].append(speaker)
                    else:
                        # Default categorization
                        if is_female:
                            self.speaker_categories['clear_female'].append(speaker)
                        elif is_male:
                            self.speaker_categories['clear_male'].append(speaker)
                    
                    print(f"   🎤 {speaker}")
                
                if len(self.available_speakers) > 20:
                    print(f"   ... and {len(self.available_speakers) - 20} more speakers")
                
                # Set default speakers for different use cases
                self.default_speakers = {
                    'female_narrator': self.available_speakers[0] if self.available_speakers else None,
                    'male_narrator': self._find_male_speaker(),
                    'professional': self._find_professional_speaker(),
                    'warm': self._find_warm_speaker()
                }
                
                print(f"🎯 Default speakers configured:")
                for role, speaker in self.default_speakers.items():
                    if speaker:
                        print(f"   {role}: {speaker}")
            
            else:
                print("⚠️ No speakers found in XTTS model")
                print("💡 This is unexpected based on your diagnostic results")
                
        except Exception as speaker_error:
            print(f"⚠️ Could not discover speakers: {speaker_error}")
    
    def _find_male_speaker(self):
        """Find a likely male speaker from available options."""
        male_indicators = ['david', 'james', 'michael', 'robert', 'william', 'john', 'daniel', 'thomas']
        
        for speaker in self.available_speakers:
            if any(indicator in speaker.lower() for indicator in male_indicators):
                return speaker
        
        # Fallback: use second speaker if available (heuristic)
        return self.available_speakers[1] if len(self.available_speakers) > 1 else self.available_speakers[0]
    
    def _find_professional_speaker(self):
        """Find a speaker that sounds professional for business content."""
        professional_indicators = ['professional', 'clear', 'crisp', 'business']
        
        for speaker in self.available_speakers:
            if any(indicator in speaker.lower() for indicator in professional_indicators):
                return speaker
        
        # Fallback to first speaker
        return self.available_speakers[0] if self.available_speakers else None
    
    def _find_warm_speaker(self):
        """Find a speaker with a warm, friendly tone for casual content."""
        warm_indicators = ['warm', 'friendly', 'gentle', 'soft', 'kind']
        
        for speaker in self.available_speakers:
            if any(indicator in speaker.lower() for indicator in warm_indicators):
                return speaker
        
        # Fallback: use third speaker if available
        return self.available_speakers[2] if len(self.available_speakers) > 2 else self.available_speakers[0]
    
    def _verify_model_functionality(self):
        """
        Test the XTTS model with a short phrase to ensure it's working correctly.
        
        This is similar to the successful test in your diagnostic, but integrated
        into the class initialization to catch any setup issues early.
        """
        try:
            test_text = "This is a test of the neural text to speech system."
            
            # Use the first available speaker for testing
            if self.available_speakers:
                test_speaker = self.available_speakers[0]
                
                # Generate a small audio sample to verify functionality
                # This uses the same pattern that worked in your diagnostic
                wav_data = self.xtts_model.tts(
                    text=test_text,
                    speaker=test_speaker,
                    language="en"
                )
                
                # Check that we got meaningful audio data
                if wav_data is not None and len(wav_data) > 1000:
                    print(f"✅ Model test successful with speaker: {test_speaker}")
                    return True
                else:
                    print("❌ Model test produced insufficient audio data")
                    return False
            
            else:
                print("❌ No speakers available for model testing")
                return False
                
        except Exception as test_error:
            print(f"❌ Model functionality test failed: {test_error}")
            return False
    
    def convert_chapter_to_audio(self, chapter_text_file_path: str, output_audio_path: str,
                                word_limit: int = None, speaker: str = None) -> Dict:
        """
        Convert a chapter text file to high-quality audio using the corrected XTTS implementation.
        
        This method now uses the proper XTTS API calls and real speaker names that exist
        in your system. Based on your diagnostic, we know this should work reliably.
        
        Args:
            chapter_text_file_path: Path to the chapter text file
            output_audio_path: Where to save the generated audio file
            word_limit: Optional limit for testing (e.g., 200 words)
            speaker: Voice preference (will map to actual XTTS speakers)
            
        Returns:
            Dictionary with conversion results and detailed statistics
        """
        conversion_start_time = time.time()
        
        try:
            print(f"\n🎵 Converting chapter to neural audio using XTTS...")
            print(f"📖 Source: {os.path.basename(chapter_text_file_path)}")
            print(f"🎧 Output: {os.path.basename(output_audio_path)}")
            
            # Step 1: Ensure the XTTS model is loaded and ready
            if not self.model_loaded:
                print("🔄 XTTS model not loaded, initializing now...")
                if not self.initialize_xtts_model():
                    raise Exception("Failed to initialize XTTS model")
            
            # Step 2: Read and prepare the chapter text
            if not os.path.exists(chapter_text_file_path):
                raise FileNotFoundError(f"Chapter text file not found: {chapter_text_file_path}")
            
            with open(chapter_text_file_path, 'r', encoding='utf-8') as text_file:
                chapter_content = text_file.read().strip()
            
            if not chapter_content:
                raise ValueError("Chapter text file is empty")
            
            original_word_count = len(chapter_content.split())
            print(f"📊 Original chapter: {original_word_count:,} words")
            
            # Step 3: Apply word limit and intelligent truncation if specified
            final_text, final_word_count = self._apply_word_limit_intelligently(
                chapter_content, word_limit, original_word_count
            )
            
            # Step 4: Prepare text for optimal neural synthesis
            processed_text = self._prepare_text_for_neural_synthesis(final_text)
            
            # Step 5: Select appropriate speaker voice
            selected_speaker = self._select_optimal_speaker(speaker)
            print(f"🎭 Using speaker: {selected_speaker}")
            
            # Step 6: Ensure output directory exists
            os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)
            
            # Step 7: Generate high-quality audio using XTTS
            print(f"🧠 Generating neural audio with XTTS...")
            audio_generation_start = time.time()
            
            # Use the tts_to_file method for direct file output
            # This matches the successful pattern from your diagnostic
            self.xtts_model.tts_to_file(
                text=processed_text,
                speaker=selected_speaker,
                language="en",
                file_path=output_audio_path
            )
            
            audio_generation_time = time.time() - audio_generation_start
            
            # Step 8: Verify audio generation success
            if not os.path.exists(output_audio_path):
                raise Exception("Audio file was not created by XTTS")
            
            audio_file_size = os.path.getsize(output_audio_path)
            if audio_file_size < 10000:  # Less than 10KB suggests an error
                raise Exception("Generated audio file is too small, synthesis may have failed")
            
            # Step 9: Calculate comprehensive processing statistics
            total_conversion_time = time.time() - conversion_start_time
            
            # XTTS typically produces speech at natural rates
            estimated_speech_rate = 165  # words per minute for natural speech
            estimated_audio_duration = final_word_count / (estimated_speech_rate / 60)  # Minutes
            processing_efficiency = final_word_count / total_conversion_time  # words per second
            
            # Step 10: Prepare comprehensive response
            conversion_result = {
                'success': True,
                'input_file': chapter_text_file_path,
                'output_file': output_audio_path,
                'neural_synthesis': {
                    'model_used': 'XTTS v2',
                    'speaker': selected_speaker,
                    'device': self.device,
                    'quality_level': 'neural_high_quality',
                    'total_speakers_available': len(self.available_speakers)
                },
                'processing_stats': {
                    'original_word_count': original_word_count,
                    'processed_word_count': final_word_count,
                    'word_limit_applied': word_limit if word_limit else 'none',
                    'words_truncated': original_word_count - final_word_count,
                    'total_processing_time_seconds': round(total_conversion_time, 2),
                    'neural_generation_time_seconds': round(audio_generation_time, 2),
                    'processing_efficiency_words_per_second': round(processing_efficiency, 1),
                    'estimated_audio_duration_minutes': round(estimated_audio_duration, 1)
                },
                'audio_file_info': {
                    'file_size_bytes': audio_file_size,
                    'file_size_mb': round(audio_file_size / (1024 * 1024), 2),
                    'sample_rate': 24000,  # XTTS v2 native sample rate
                    'estimated_speech_rate_wpm': estimated_speech_rate,
                    'quality_enhancement': 'neural_synthesis_applied'
                },
                'quality_metrics': {
                    'text_preprocessing_applied': True,
                    'neural_processing_applied': True,
                    'natural_speech_patterns': True,
                    'emotional_expression_enabled': True,
                    'human_like_intonation': True,
                    'gpu_accelerated': self.device == "cuda"
                }
            }
            
            print(f"✅ Neural audio conversion completed successfully!")
            print(f"📊 Processed {final_word_count:,} words in {total_conversion_time:.2f} seconds")
            print(f"🎵 Generated {conversion_result['audio_file_info']['file_size_mb']:.2f} MB neural audio")
            print(f"⏱️ Estimated audio duration: {estimated_audio_duration:.1f} minutes")
            print(f"⚡ Processing efficiency: {processing_efficiency:.1f} words/second")
            
            return conversion_result
            
        except Exception as e:
            print(f"❌ Neural audio conversion failed: {str(e)}")
            
            # Clean up any partially created files
            try:
                if os.path.exists(output_audio_path):
                    os.remove(output_audio_path)
            except:
                pass
            
            return {
                'success': False,
                'error': str(e),
                'input_file': chapter_text_file_path,
                'processing_time_seconds': time.time() - conversion_start_time,
                'available_speakers': len(self.available_speakers) if self.available_speakers else 0
            }
    
    def _select_optimal_speaker(self, speaker_preference: str = None):
        """
        Select the best available speaker based on preference and content type.
        
        This method maps user preferences to actual XTTS speakers that exist
        in your system. It handles both the legacy voice names from your original
        code and new preferences.
        """
        if not self.available_speakers:
            raise Exception("No speakers available in XTTS model")
        
        # If no preference specified, use the first available speaker
        if not speaker_preference:
            return self.available_speakers[0]
        
        # Map legacy voice names to speaker selection logic
        preference_mapping = {
            'ana_florence': 'female_narrator',
            'david_freeman': 'male_narrator',
            'lisa_chen': 'clear_female',
            'michael_torres': 'professional_male',
            'sarah_williams': 'warm_female',
            'james_parker': 'professional_male'
        }
        
        # Resolve legacy names to speaker types
        speaker_type = preference_mapping.get(speaker_preference, speaker_preference)
        
        # Select speaker based on type or use direct name if it exists
        if speaker_preference in self.available_speakers:
            # Direct speaker name match
            return speaker_preference
        elif speaker_type in self.default_speakers and self.default_speakers[speaker_type]:
            # Use mapped default speaker
            return self.default_speakers[speaker_type]
        else:
            # Fallback to first available speaker
            print(f"⚠️ Speaker preference '{speaker_preference}' not available, using default")
            return self.available_speakers[0]
    
    def _apply_word_limit_intelligently(self, text: str, word_limit: int, original_count: int):
        """Apply word limits while preserving natural speech flow and meaning."""
        if not word_limit or word_limit <= 0 or original_count <= word_limit:
            return text, original_count
        
        words = text.split()
        limited_words = words[:word_limit]
        limited_text = ' '.join(limited_words)
        
        # Find natural sentence boundaries near the end
        sentence_endings = ['.', '!', '?', ';']
        best_ending_pos = -1
        
        # Look for sentence endings in the last 20% of the limited text
        search_start = int(len(limited_text) * 0.8)
        
        for ending in sentence_endings:
            pos = limited_text.rfind(ending, search_start)
            if pos > best_ending_pos:
                best_ending_pos = pos
        
        if best_ending_pos > 0:
            final_text = limited_text[:best_ending_pos + 1]
            print(f"🎯 Limited to {word_limit} words, ended at natural sentence boundary")
        else:
            final_text = limited_text
            print(f"🎯 Limited to {word_limit} words, no ideal sentence boundary found")
        
        final_word_count = len(final_text.split())
        print(f"📊 Processing: {final_word_count:,} words (limited from {original_count:,})")
        
        return final_text, final_word_count
    
    def _prepare_text_for_neural_synthesis(self, text: str) -> str:
        """Prepare text specifically for XTTS neural synthesis."""
        if not text:
            return ""
        
        processed_text = text
        
        # Handle common abbreviations for better pronunciation
        neural_tts_replacements = {
            'Dr.': 'Doctor',
            'Mr.': 'Mister',
            'Mrs.': 'Missus', 
            'Ms.': 'Miss',
            'Prof.': 'Professor',
            'etc.': 'et cetera',
            'vs.': 'versus',
            'e.g.': 'for example',
            'i.e.': 'that is'
        }
        
        for abbrev, replacement in neural_tts_replacements.items():
            processed_text = processed_text.replace(abbrev, replacement)
        
        # Improve punctuation handling for natural pauses
        processed_text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', processed_text)
        
        # Clean up excessive whitespace while preserving paragraph structure
        processed_text = re.sub(r' +', ' ', processed_text)
        processed_text = re.sub(r'\n\s*\n', '\n\n', processed_text)
        
        return processed_text.strip()
    
    def get_available_speakers(self):
        """Return comprehensive information about available speakers."""
        return {
            'total_speakers': len(self.available_speakers),
            'all_speakers': self.available_speakers,
            'categories': self.speaker_categories,
            'default_speakers': self.default_speakers,
            'speaker_selection_guide': {
                'for_fiction': self.default_speakers.get('warm', self.available_speakers[0] if self.available_speakers else None),
                'for_business': self.default_speakers.get('professional', self.available_speakers[0] if self.available_speakers else None),
                'for_education': self.default_speakers.get('clear_female', self.available_speakers[0] if self.available_speakers else None)
            }
        }
    
    def cleanup_model(self):
        """Clean up neural model resources when done."""
        if self.xtts_model and hasattr(self.xtts_model, 'to'):
            try:
                # Move model to CPU to free GPU memory
                self.xtts_model.to('cpu')
                print("🧹 XTTS model moved to CPU, GPU memory freed")
            except:
                pass
        
        self.model_loaded = False
        print("🧹 XTTS resources cleaned up")

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint that provides comprehensive system status information.
    
    This endpoint serves multiple important purposes in our audiobook conversion system.
    First, it allows your React frontend to verify that the backend is running and
    accessible before attempting file uploads. Second, it confirms that all the
    required libraries for ebook processing and text-to-speech conversion are
    properly installed and functioning. Third, it provides diagnostic information
    that helps us troubleshoot any setup issues during development.
    
    When you visit this endpoint, you're essentially asking the system to perform
    a complete self-diagnostic check and report back on its readiness to process
    audiobook conversions.
    """
    try:
        print("🏥 Health check endpoint accessed - performing system diagnostic...")
        
        # Check current timestamp to show the server is responsive
        current_time = datetime.now().isoformat()
        
        # Verify that all our essential directories exist and are writable
        directory_status = {}
        for folder_name, folder_path in [
            ('uploads', app.config['UPLOAD_FOLDER']),
            ('chapters', app.config['CHAPTERS_FOLDER']),
            ('audiobooks', app.config['AUDIOBOOKS_FOLDER'])
        ]:
            try:
                # Test if directory exists
                exists = os.path.exists(folder_path)
                # Test if we can write to the directory by creating a temporary file
                test_file_path = os.path.join(folder_path, 'health_test.tmp')
                
                if exists:
                    # Try to create and immediately delete a test file
                    with open(test_file_path, 'w') as test_file:
                        test_file.write('health check')
                    os.remove(test_file_path)
                    directory_status[folder_name] = 'accessible'
                else:
                    directory_status[folder_name] = 'missing'
                    
            except Exception as dir_error:
                directory_status[folder_name] = f'error: {str(dir_error)}'
        
        # Test the availability of critical libraries for ebook processing
        library_status = {}
        
        # Test PyPDF2 for PDF processing
        try:
            import PyPDF2
            library_status['PyPDF2'] = {
                'available': True,
                'version': getattr(PyPDF2, '__version__', 'version unknown'),
                'purpose': 'PDF file processing'
            }
        except ImportError as e:
            library_status['PyPDF2'] = {
                'available': False,
                'error': str(e),
                'purpose': 'PDF file processing'
            }
        
        # Test ebooklib for EPUB processing
        try:
            import ebooklib
            library_status['ebooklib'] = {
                'available': True,
                'version': getattr(ebooklib, '__version__', 'version unknown'),
                'purpose': 'EPUB file processing'
            }
        except ImportError as e:
            library_status['ebooklib'] = {
                'available': False,
                'error': str(e),
                'purpose': 'EPUB file processing'
            }
        
        # Test BeautifulSoup for HTML parsing within EPUB files
        try:
            from bs4 import BeautifulSoup
            library_status['beautifulsoup4'] = {
                'available': True,
                'version': getattr(BeautifulSoup, '__version__', 'version unknown'),
                'purpose': 'HTML content parsing in EPUB files'
            }
        except ImportError as e:
            library_status['beautifulsoup4'] = {
                'available': False,
                'error': str(e),
                'purpose': 'HTML content parsing in EPUB files'
            }
        
        # Test pyttsx3 for text-to-speech conversion
        try:
            import pyttsx3
            # Try to initialize the TTS engine to ensure it's working
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            engine.stop()  # Clean up the engine
            
            library_status['pyttsx3'] = {
                'available': True,
                'voices_available': len(voices) if voices else 0,
                'purpose': 'Text-to-speech audio conversion'
            }
        except Exception as e:
            library_status['pyttsx3'] = {
                'available': False,
                'error': str(e),
                'purpose': 'Text-to-speech audio conversion'
            }
        
        # Initialize our chapter extractor to verify it's working
        try:
            extractor = IntelligentChapterExtractor()
            chapter_extractor_status = {
                'available': True,
                'skip_sections_count': len(extractor.skip_sections),
                'chapter_patterns_count': len(extractor.chapter_patterns),
                'minimum_chapter_words': extractor.minimum_chapter_words
            }
        except Exception as e:
            chapter_extractor_status = {
                'available': False,
                'error': str(e)
            }
        
        # Determine overall system health based on critical components
        critical_libraries = ['PyPDF2', 'ebooklib', 'beautifulsoup4', 'pyttsx3']
        all_directories_ok = all(status == 'accessible' for status in directory_status.values())
        all_critical_libs_ok = all(library_status.get(lib, {}).get('available', False) for lib in critical_libraries)
        
        system_health = 'healthy' if (all_directories_ok and all_critical_libs_ok and chapter_extractor_status['available']) else 'degraded'
        
        # Prepare comprehensive health report
        health_report = {
            'status': system_health,
            'timestamp': current_time,
            'message': 'AudioBook Converter backend is operational' if system_health == 'healthy' else 'System has some issues that may affect functionality',
            
            # System capabilities based on available components
            'capabilities': {
                'pdf_processing': library_status.get('PyPDF2', {}).get('available', False),
                'epub_processing': library_status.get('ebooklib', {}).get('available', False),
                'text_processing': True,  # Always available since it's built into Python
                'text_to_speech': library_status.get('pyttsx3', {}).get('available', False),
                'intelligent_chapter_detection': chapter_extractor_status['available']
            },
            
            # Detailed component status for troubleshooting
            'system_details': {
                'directories': directory_status,
                'libraries': library_status,
                'chapter_extractor': chapter_extractor_status,
                'supported_file_types': []
            },
            
            # Configuration information
            'configuration': {
                'max_file_size_mb': app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024),
                'upload_folder': app.config['UPLOAD_FOLDER'],
                'chapters_folder': app.config['CHAPTERS_FOLDER'],
                'audiobooks_folder': app.config['AUDIOBOOKS_FOLDER']
            }
        }
        
        # Determine supported file types based on available libraries
        if library_status.get('PyPDF2', {}).get('available', False):
            health_report['system_details']['supported_file_types'].append('PDF')
        if library_status.get('ebooklib', {}).get('available', False):
            health_report['system_details']['supported_file_types'].append('EPUB')
        health_report['system_details']['supported_file_types'].append('TXT')  # Always supported
        
        # Log the health check result
        if system_health == 'healthy':
            print("✅ System health check passed - all components operational")
        else:
            print("⚠️ System health check shows issues - some functionality may be limited")
            
        print(f"📊 Supported file types: {', '.join(health_report['system_details']['supported_file_types'])}")
        print(f"🎵 Text-to-speech available: {'Yes' if health_report['capabilities']['text_to_speech'] else 'No'}")
        
        return jsonify(health_report)
        
    except Exception as e:
        # If even the health check fails, we have a serious problem
        print(f"❌ Health check failed with error: {str(e)}")
        
        error_report = {
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'message': 'Health check failed - system may not be functioning properly',
            'error': str(e),
            'capabilities': {
                'pdf_processing': False,
                'epub_processing': False,
                'text_processing': False,
                'text_to_speech': False,
                'intelligent_chapter_detection': False
            }
        }
        
        return jsonify(error_report), 500    

@app.route('/api/fullconvert', methods=['POST'])
def enhanced_full_conversion_process():
    """
    Complete ebook-to-audiobook conversion endpoint with XTTS neural synthesis.
    
    This enhanced endpoint represents the evolution of your audiobook conversion system
    from a two-step process (extract chapters, then convert to audio) into a single,
    seamless pipeline that transforms ebooks directly into professional-quality audiobooks.
    
    Think of this as a master craftsman's workshop where raw materials (ebook files)
    are transformed through multiple specialized processes into finished products
    (complete audiobooks) - all in one continuous, carefully orchestrated operation.
    
    The process follows this comprehensive workflow:
    1. Receive and validate the uploaded ebook file
    2. Extract and organize chapters using intelligent content detection
    3. Initialize the XTTS neural synthesis system
    4. Convert each chapter to high-quality audio using neural voices
    5. Organize the audio files for easy access and download
    6. Return complete audiobook with detailed metadata and download links
    
    This approach eliminates the need for users to manage intermediate steps while
    providing them with immediate access to their complete audiobook conversion.
    """
    
    # Initialize comprehensive tracking variables for the entire conversion process
    conversion_start_time = time.time()
    conversion_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # These variables will track our progress through the complex conversion pipeline
    temp_file_path = None
    chapters_folder = None
    audio_output_folder = None
    audio_generator = None
    extracted_chapters = []
    converted_audio_files = []
    
    try:
        print("\n🎬 Starting enhanced ebook-to-audiobook conversion...")
        print("=" * 70)
        print(f"🆔 Conversion ID: {conversion_id}")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # ==========================================
        # PHASE 1: FILE RECEPTION AND VALIDATION
        # ==========================================
        
        print("\n📥 Phase 1: Processing uploaded file...")
        
        # Validate that we received a file in the request
        if 'file' not in request.files:
            print("❌ No file found in request")
            return jsonify({
                'success': False,
                'error': 'No file provided',
                'code': 'NO_FILE_UPLOADED',
                'conversion_id': conversion_id
            }), 400
        
        uploaded_file = request.files['file']
        
        if uploaded_file.filename == '':
            print("❌ Empty filename detected")
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'code': 'EMPTY_FILENAME',
                'conversion_id': conversion_id
            }), 400
        
        # Extract and validate file information
        original_filename = uploaded_file.filename
        file_extension = Path(original_filename).suffix.lower()
        supported_extensions = {'.pdf', '.epub', '.txt', '.text'}
        
        print(f"📁 Original filename: {original_filename}")
        print(f"📎 File extension: {file_extension}")
        
        if file_extension not in supported_extensions:
            print(f"❌ Unsupported file type: {file_extension}")
            return jsonify({
                'success': False,
                'error': f'Unsupported file type: {file_extension}. Supported types: PDF, EPUB, TXT',
                'code': 'UNSUPPORTED_FILE_TYPE',
                'supported_types': list(supported_extensions),
                'conversion_id': conversion_id
            }), 400
        
        # Validate file size to prevent system overload
        uploaded_file.seek(0, 2)  # Seek to end to get file size
        file_size = uploaded_file.tell()
        uploaded_file.seek(0)  # Reset to beginning for processing
        
        max_size = app.config['MAX_CONTENT_LENGTH']
        if file_size > max_size:
            print(f"❌ File too large: {file_size} bytes (max: {max_size})")
            return jsonify({
                'success': False,
                'error': f'File size ({file_size // (1024*1024)}MB) exceeds maximum allowed size ({max_size // (1024*1024)}MB)',
                'code': 'FILE_TOO_LARGE',
                'max_size_mb': max_size // (1024*1024),
                'conversion_id': conversion_id
            }), 413
        
        print(f"📊 File size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
        
        # Save the uploaded file to temporary storage for processing
        safe_filename = secure_filename(original_filename)
        temp_filename = f"{timestamp}_{conversion_id}_{safe_filename}"
        temp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        
        uploaded_file.save(temp_file_path)
        print(f"💾 Saved to temporary location: {temp_filename}")
        
        # ==========================================
        # PHASE 2: INTELLIGENT CHAPTER EXTRACTION
        # ==========================================
        
        print(f"\n📖 Phase 2: Extracting chapters with intelligent content detection...")
        
        try:
            # Initialize the chapter extraction system
            chapter_extractor = IntelligentChapterExtractor()
            extraction_start_time = time.time()
            
            print(f"🎯 Beginning intelligent extraction for {file_extension} file...")
            
            # Extract chapters using your sophisticated content detection algorithms
            extracted_chapters = chapter_extractor.extract_chapters_from_file(temp_file_path)
            
            extraction_time = time.time() - extraction_start_time
            print(f"⏱️ Chapter extraction completed in {extraction_time:.2f} seconds")
            
            if not extracted_chapters:
                raise Exception("No readable content could be extracted from the file")
            
            print(f"✅ Successfully extracted {len(extracted_chapters)} chapters")

            total_words = sum(chapter['word_count'] for chapter in extracted_chapters)
            estimated_audio_duration = total_words / (165 / 60)  # 165 words per minute

            print(f"📊 Total content: {total_words:,} words")
            print(f"⏱️ Estimated audio duration: {estimated_audio_duration:.1f} minutes")

            print(f"\n💾 Phase 3.5: Serializing chapters to individual text files...")

            try:
                # Create a dedicated folder for this conversion's chapter files
                chapters_temp_folder = os.path.join(app.config['CHAPTERS_FOLDER'], f"conversion_{timestamp}_{conversion_id}")
                os.makedirs(chapters_temp_folder, exist_ok=True)
                
                print(f"📁 Created chapter files folder: {os.path.basename(chapters_temp_folder)}")
                
                # Write each chapter to its own text file
                serialized_chapter_files = []
                serialization_start_time = time.time()
                
                for chapter in extracted_chapters:
                    # Create a safe filename for this chapter
                    chapter_number = chapter['number']
                    chapter_title = chapter['title']
                    
                    # Clean the chapter title for use in filename (remove problematic characters)
                    safe_title = "".join(c for c in chapter_title if c.isalnum() or c in (' ', '-', '_')).strip()
                    safe_title = safe_title.replace(' ', '_')[:30]  # Limit length and replace spaces
                    
                    # Construct the chapter filename
                    chapter_filename = f"Chapter_{chapter_number:02d}_{safe_title}.txt"
                    chapter_file_path = os.path.join(chapters_temp_folder, chapter_filename)
                    
                    # Write the chapter content to the file
                    try:
                        with open(chapter_file_path, 'w', encoding='utf-8') as chapter_file:
                            # Write the actual chapter content
                            chapter_file.write(chapter['content'])
                        
                        # Verify the file was created successfully
                        if os.path.exists(chapter_file_path):
                            file_size = os.path.getsize(chapter_file_path)
                            
                            # Store the file information for Phase 4
                            serialized_chapter_files.append({
                                'chapter_number': chapter_number,
                                'title': chapter_title,
                                'file_path': chapter_file_path,
                                'filename': chapter_filename,
                                'word_count': chapter['word_count'],
                                'file_size_bytes': file_size
                            })
                            
                            print(f"   ✅ Chapter {chapter_number}: {chapter_filename} ({file_size:,} bytes)")
                        
                        else:
                            print(f"   ❌ Failed to create file for Chapter {chapter_number}")
                            
                    except Exception as file_error:
                        print(f"   ❌ Error writing Chapter {chapter_number}: {str(file_error)}")
                        continue
                
                serialization_time = time.time() - serialization_start_time
                
                if not serialized_chapter_files:
                    raise Exception("No chapter files were successfully created")
                
                print(f"✅ Successfully serialized {len(serialized_chapter_files)} chapters to files")
                print(f"⏱️ Serialization completed in {serialization_time:.2f} seconds")
                print(f"📁 Chapter files location: {chapters_temp_folder}")
                
                # Update the chapters_folder variable for Phase 4 to use
                chapters_folder = chapters_temp_folder
                
            except Exception as serialization_error:
                print(f"❌ Chapter serialization failed: {str(serialization_error)}")
                
                # Clean up temporary file before returning error
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                
                return jsonify({
                    'success': False,
                    'error': f'Chapter serialization failed: {str(serialization_error)}',
                    'code': 'CHAPTER_SERIALIZATION_FAILED',
                    'conversion_id': conversion_id,
                    'chapters_extracted': len(extracted_chapters)
                }), 500
            
            # Calculate total content statistics for planning audio conversion
            total_words = sum(chapter['word_count'] for chapter in extracted_chapters)
            estimated_audio_duration = total_words / (165 / 60)  # 165 words per minute
            
            print(f"📊 Total content: {total_words:,} words")
            print(f"⏱️ Estimated audio duration: {estimated_audio_duration:.1f} minutes")
            
        except Exception as extraction_error:
            print(f"❌ Chapter extraction failed: {str(extraction_error)}")
            # Clean up temporary file before returning error
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
            return jsonify({
                'success': False,
                'error': f'Chapter extraction failed: {str(extraction_error)}',
                'code': 'EXTRACTION_FAILED',
                'conversion_id': conversion_id
            }), 500
        
        # ==========================================
        # PHASE 3: XTTS NEURAL SYNTHESIS INITIALIZATION
        # ==========================================
        
        print(f"\n🧠 Phase 3: Initializing XTTS neural synthesis system...")
        
        try:
            # Initialize the advanced neural audio generation system
            print("⏳ Loading XTTS neural network (this may take a moment)...")
            audio_generator = AdvancedAudiobookGenerator()
            
            # Verify that initialization was successful
            if not audio_generator.model_loaded:
                raise Exception("XTTS model failed to load properly")
            
            if not audio_generator.available_speakers:
                raise Exception("No speakers were discovered in the XTTS system")
            
            print(f"✅ XTTS system initialized successfully!")
            print(f"🎭 Neural synthesis ready with {len(audio_generator.available_speakers)} available speakers")
            print(f"⚡ Processing device: {audio_generator.device}")
            
            # Show some available speakers for reference
            sample_speakers = audio_generator.available_speakers[:5]
            print(f"🎤 Sample speakers: {', '.join(sample_speakers)}")


            
        except Exception as xtts_error:
            print(f"❌ XTTS initialization failed: {str(xtts_error)}")
            
            # Clean up temporary file and extracted data
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
            return jsonify({
                'success': False,
                'error': f'Neural synthesis system initialization failed: {str(xtts_error)}',
                'code': 'XTTS_INITIALIZATION_FAILED',
                'conversion_id': conversion_id,
                'troubleshooting': {
                    'possible_causes': [
                        'XTTS model download interrupted',
                        'Insufficient GPU memory',
                        'Network connectivity issues',
                        'CUDA compatibility problems'
                    ],
                    'suggestions': [
                        'Check internet connection for model download',
                        'Restart the application to retry initialization',
                        'Free up GPU memory by closing other applications',
                        'Run the XTTS diagnostic script to verify system status'
                    ]
                }
            }), 500
        
        # ==========================================
        # PHASE 4: AUDIO CONVERSION PROCESSING
        # ==========================================
        
        print(f"\n🎵 Phase 4: Converting chapters to neural audio...")
        
        # Create organized folder structure for the complete audiobook
        audio_output_folder = os.path.join(app.config['AUDIOBOOKS_FOLDER'], f"audiobook_{timestamp}_{conversion_id}")
        chapters_audio_folder = os.path.join(audio_output_folder, "chapters")
        os.makedirs(chapters_audio_folder, exist_ok=True)
        
        print(f"📁 Audio output folder: {audio_output_folder}")
        
        # Process each chapter through the complete audio conversion pipeline
        audio_conversion_start_time = time.time()
        converted_audio_files = []
        total_audio_duration = 0
        total_processed_words = 0
        
        # Use intelligent defaults for conversion parameters
        # (Since this is a file upload request, not JSON, we use defaults)
        word_limit_per_chapter = None  # No word limit for full conversion youcanchangethis
        speaker_preference = 'female_narrator'  # Default to first available speaker
        max_chapters = None  # Convert all chapters found youcanchangethis
        
        print(f"🎯 Conversion settings:")
        print(f"   Word limit per chapter: {word_limit_per_chapter or 'No limit'}")
        print(f"   Preferred speaker: {speaker_preference}")
        print(f"   Max chapters to convert: {max_chapters or 'All chapters'}")
        
        # Process each serialized chapter file through the neural synthesis pipeline
        chapters_to_process = serialized_chapter_files[:max_chapters] if max_chapters else serialized_chapter_files

        for chapter_index, chapter_info in enumerate(chapters_to_process):
            chapter_start_time = time.time()
            chapter_number = chapter_info['chapter_number']
            chapter_title = chapter_info['title']
            chapter_file_path = chapter_info['file_path']  # This is the key change!
            chapter_word_count = chapter_info['word_count']
            
            print(f"\n📖 Processing Chapter {chapter_number}: {chapter_title}")
            print(f"   📊 Words: {chapter_word_count:,}")
            
            try:
                temp_chapter_path = chapter_file_path
                print(f"   📄 Using serialized file: {os.path.basename(temp_chapter_path)}")
                
                # Define output path for this chapter's audio
                audio_filename = f"Chapter_{chapter_number:02d}_{secure_filename(chapter_title[:30])}.wav"
                chapter_audio_path = os.path.join(chapters_audio_folder, audio_filename)
                
                print(f"   🎵 Generating audio: {audio_filename}")
                
                # Convert this chapter to high-quality neural audio
                conversion_result = audio_generator.convert_chapter_to_audio(
                    chapter_text_file_path=temp_chapter_path,
                    output_audio_path=chapter_audio_path,
                    word_limit=word_limit_per_chapter,
                    speaker=speaker_preference
                )
                
                
                # Process the conversion results
                if conversion_result['success']:
                    chapter_processing_time = time.time() - chapter_start_time
                    
                    # Verify the audio file was created successfully
                    if os.path.exists(chapter_audio_path):
                        audio_file_size = os.path.getsize(chapter_audio_path)
                        
                        if audio_file_size > 1000:  # Ensure file has substantial content
                            # Record successful conversion details
                            chapter_audio_info = {
                                'chapter_number': chapter_number,
                                'title': chapter_title,
                                'audio_filename': audio_filename,
                                'audio_file_path': chapter_audio_path,  # Keep the full path for server use
                                # Add this new field for frontend consumption
                                'audio_url': f'/api/audio/{os.path.relpath(chapter_audio_path, app.config["AUDIOBOOKS_FOLDER"]).replace(os.sep, "/")}',
                                'original_word_count': chapter_word_count,
                                'processed_word_count': conversion_result['processing_stats']['processed_word_count'],
                                'audio_file_size_bytes': audio_file_size,
                                'audio_file_size_mb': round(audio_file_size / (1024*1024), 2),
                                'estimated_duration_minutes': conversion_result['processing_stats']['estimated_audio_duration_minutes'],
                                'processing_time_seconds': round(chapter_processing_time, 2),
                                'speaker_used': conversion_result['neural_synthesis']['speaker'],
                                'neural_quality': conversion_result['neural_synthesis']['quality_level']
                            }
                            
                            converted_audio_files.append(chapter_audio_info)
                            total_audio_duration += conversion_result['processing_stats']['estimated_audio_duration_minutes']
                            total_processed_words += conversion_result['processing_stats']['processed_word_count']
                            
                            print(f"   ✅ Conversion successful!")
                            print(f"   📊 Audio size: {chapter_audio_info['audio_file_size_mb']:.2f} MB")
                            print(f"   ⏱️ Duration: ~{chapter_audio_info['estimated_duration_minutes']:.1f} minutes")
                            print(f"   🎭 Speaker: {chapter_audio_info['speaker_used']}")
                            
                        else:
                            print(f"   ❌ Audio file too small ({audio_file_size} bytes) - conversion may have failed")
                            continue
                    else:
                        print(f"   ❌ Audio file was not created - conversion failed")
                        continue
                
                else:
                    print(f"   ❌ Conversion failed: {conversion_result.get('error', 'Unknown error')}")
                    continue
                    
            except Exception as chapter_error:
                print(f"   ❌ Chapter processing failed: {str(chapter_error)}")
                # Continue with next chapter rather than failing the entire conversion
                continue
        
        audio_conversion_time = time.time() - audio_conversion_start_time
        
        # ==========================================
        # PHASE 5: FINALIZATION AND RESPONSE PREPARATION
        # ==========================================
        
        print(f"\n🎉 Phase 5: Finalizing audiobook conversion...")
        
        # Clean up temporary files and resources
        try:
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                print("🗑️ Cleaned up temporary upload file")
            
            if audio_generator:
                audio_generator.cleanup_model()
                print("🧹 Cleaned up XTTS neural synthesis resources")
                
        except Exception as cleanup_error:
            print(f"⚠️ Cleanup warning: {cleanup_error}")
            # Don't fail the conversion for cleanup issues
        
        # Calculate comprehensive conversion statistics
        total_conversion_time = time.time() - conversion_start_time
        successful_chapters = len(converted_audio_files)
        total_chapters = len(extracted_chapters)
        
        # Verify that we successfully converted at least some chapters
        if successful_chapters == 0:
            return jsonify({
                'success': False,
                'error': 'No chapters were successfully converted to audio',
                'code': 'NO_AUDIO_GENERATED',
                'conversion_id': conversion_id,
                'chapters_attempted': total_chapters
            }), 500
        
        # Calculate total audio file size
        total_audio_size_bytes = sum(chapter['audio_file_size_bytes'] for chapter in converted_audio_files)
        total_audio_size_mb = round(total_audio_size_bytes / (1024*1024), 2)
        
        print(f"✅ Audiobook conversion completed successfully!")
        print(f"📊 Conversion summary:")
        print(f"   Chapters converted: {successful_chapters}/{total_chapters}")
        print(f"   Total audio duration: ~{total_audio_duration:.1f} minutes")
        print(f"   Total audio size: {total_audio_size_mb:.2f} MB")
        print(f"   Total processing time: {total_conversion_time:.1f} seconds")
        
        # Prepare comprehensive response with all conversion details
        audiobook_response = {
            'success': True,
            'message': f'Successfully converted {successful_chapters} chapters from {original_filename} to audiobook',
            'conversion_id': conversion_id,
            'timestamp': datetime.now().isoformat(),
            
            # Original file information
            'source_file': {
                'original_filename': original_filename,
                'file_type': file_extension,
                'file_size_bytes': file_size,
                'file_size_mb': round(file_size / (1024*1024), 2)
            },
            
            # Comprehensive processing statistics
            'conversion_stats': {
                'total_chapters_found': total_chapters,
                'chapters_successfully_converted': successful_chapters,
                'conversion_success_rate': round((successful_chapters / total_chapters) * 100, 1),
                'total_processing_time_seconds': round(total_conversion_time, 2),
                'audio_generation_time_seconds': round(audio_conversion_time, 2),
                'chapter_extraction_time_seconds': round(extraction_time, 2),
                'total_words_processed': total_processed_words,
                'processing_efficiency_words_per_second': round(total_processed_words / total_conversion_time, 1)
            },
            
            # Complete audiobook information
            'audiobook': {
                'total_duration_minutes': round(total_audio_duration, 1),
                'total_size_bytes': total_audio_size_bytes,
                'total_size_mb': total_audio_size_mb,
                'chapters_folder': chapters_audio_folder,
                'chapter_count': successful_chapters,
                'format': 'WAV',
                'quality': 'Neural synthesis (XTTS v2)',
                'sample_rate': '24kHz'
            },
            
            # Detailed chapter information
            'chapters': converted_audio_files,
            
            # Technical processing details
            'processing_details': {
                'extraction_method': 'intelligent_chapter_detection',
                'audio_synthesis': 'XTTS_v2_neural_synthesis',
                'device_used': audio_generator.device if audio_generator else 'unknown',
                'speakers_available': len(audio_generator.available_speakers) if audio_generator else 0,
                'neural_quality_applied': True,
                'front_matter_skipped': True,
                'chapter_boundaries_detected': successful_chapters > 1
            },
            
            # User guidance for next steps
            'next_steps': {
                'download_individual_chapters': f'Access individual chapter audio files in: {chapters_audio_folder}',
                'listen_to_audiobook': 'Play the generated audio files in order to listen to your complete audiobook',
                'file_organization': 'Chapter files are numbered sequentially for easy playlist creation',
                'quality_verification': 'Listen to the first chapter to verify audio quality meets your expectations'
            }
        }
        
        print("=" * 70)
        print(f"🎧 Audiobook conversion completed for: {original_filename}")
        print(f"📁 Audio files location: {chapters_audio_folder}")
        print(f"🎵 Ready to listen to {successful_chapters} chapters!")
        
        return jsonify(audiobook_response)
        
    except Exception as e:
        print(f"❌ Enhanced conversion process failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Perform comprehensive cleanup on any failure
        cleanup_operations = []
        
        try:
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                cleanup_operations.append("Removed temporary upload file")
        except:
            pass
        
        try:
            if audio_generator:
                audio_generator.cleanup_model()
                cleanup_operations.append("Cleaned up XTTS resources")
        except:
            pass
        
        # Return comprehensive error information for debugging
        return jsonify({
            'success': False,
            'error': f'Enhanced conversion process failed: {str(e)}',
            'code': 'ENHANCED_CONVERSION_FAILED',
            'conversion_id': conversion_id,
            'processing_time_seconds': time.time() - conversion_start_time,
            'cleanup_performed': cleanup_operations,
            'troubleshooting': {
                'error_type': type(e).__name__,
                'suggestion': 'Check server logs for detailed error information',
                'common_solutions': [
                    'Verify XTTS system is properly installed',
                    'Check available disk space for audio files',
                    'Ensure GPU memory is available for neural synthesis',
                    'Try with a smaller file or fewer chapters'
                ]
            }
        }), 500

@app.route('/api/convert-audio-test', methods=['POST'])
def convert_audio_test():
    """
    Test audio conversion endpoint that converts the first chapter with word limitations.
    
    This endpoint is designed specifically for testing and development. It takes the
    results from a previous fullconvert operation and generates audio for just the
    first chapter with a configurable word limit. This allows you to verify that
    the audio generation pipeline works correctly before committing to processing
    entire books.
    
    Expected request format:
    {
        "conversion_id": "abc123def",
        "word_limit": 200,
        "chapter_number": 1
    }
    """
    try:
        print("\n🎵 Starting test audio conversion...")
        print("=" * 50)
        
        # Step 1: Parse the request data
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided',
                'code': 'NO_REQUEST_DATA'
            }), 400
        
        conversion_id = request_data.get('conversion_id')
        word_limit = request_data.get('word_limit', 200)  # Default to 200 words
        chapter_number = request_data.get('chapter_number', 1)  # Default to first chapter
        
        if not conversion_id:
            return jsonify({
                'success': False,
                'error': 'Conversion ID is required',
                'code': 'MISSING_CONVERSION_ID'
            }), 400
        
        print(f"🆔 Conversion ID: {conversion_id}")
        print(f"🎯 Word limit: {word_limit}")
        print(f"📖 Target chapter: {chapter_number}")
        
        # Step 2: Find the chapters folder for this conversion
        chapters_base_folder = app.config['CHAPTERS_FOLDER']
        
        # Look for folders containing this conversion ID
        matching_folders = []
        if os.path.exists(chapters_base_folder):
            for folder_name in os.listdir(chapters_base_folder):
                if conversion_id in folder_name:
                    matching_folders.append(os.path.join(chapters_base_folder, folder_name))
        
        if not matching_folders:
            return jsonify({
                'success': False,
                'error': f'No chapter files found for conversion ID: {conversion_id}',
                'code': 'CHAPTERS_NOT_FOUND',
                'suggestion': 'Please run /api/fullconvert first to extract chapters'
            }), 404
        
        chapters_folder = matching_folders[0]  # Use the first matching folder
        print(f"📁 Found chapters folder: {os.path.basename(chapters_folder)}")
        
        # Step 3: Find the target chapter file
        chapter_files = []
        if os.path.exists(chapters_folder):
            for filename in os.listdir(chapters_folder):
                if filename.startswith(f'Chapter_{chapter_number:02d}') and filename.endswith('.txt'):
                    chapter_files.append(filename)
        
        if not chapter_files:
            return jsonify({
                'success': False,
                'error': f'Chapter {chapter_number} not found in conversion {conversion_id}',
                'code': 'CHAPTER_NOT_FOUND',
                'available_files': os.listdir(chapters_folder) if os.path.exists(chapters_folder) else []
            }), 404
        
        target_chapter_file = chapter_files[0]  # Use the first matching chapter file
        chapter_file_path = os.path.join(chapters_folder, target_chapter_file)
        
        print(f"📄 Target chapter file: {target_chapter_file}")
        
        # Step 4: Create output folder for audio files
        audio_output_folder = os.path.join(app.config['AUDIOBOOKS_FOLDER'], f"test_{conversion_id}")
        os.makedirs(audio_output_folder, exist_ok=True)
        
        # Generate output filename
        audio_filename = f"Chapter_{chapter_number:02d}_test_{word_limit}words.wav"
        audio_output_path = os.path.join(audio_output_folder, audio_filename)
        
        print(f"🎵 Audio output: {audio_filename}")
        
        # Step 5: Initialize audio generator and convert chapter
        try:
            print(f"🎙️ Initializing audio generation system...")
            print(f"🧠 Initializing advanced neural audio generation system...")
            audio_generator = AdvancedAudiobookGenerator()

            # The conversion call remains the same, but now uses neural synthesis
            conversion_result = audio_generator.convert_chapter_to_audio(
                chapter_text_file_path=chapter_file_path,
                output_audio_path=audio_output_path,
                word_limit=word_limit,
                speaker='ana_florence'  # You can make this configurable later
            )

            # Clean up the audio generator
            audio_generator.cleanup_model()
            
            if conversion_result['success']:
                # Step 6: Prepare comprehensive response
                test_result = {
                    'success': True,
                    'message': f'Test audio conversion completed for Chapter {chapter_number}',
                    'conversion_id': conversion_id,
                    'test_parameters': {
                        'chapter_number': chapter_number,
                        'word_limit': word_limit,
                        'chapter_source_file': target_chapter_file
                    },
                    'audio_output': {
                        'filename': audio_filename,
                        'file_path': audio_output_path,
                        'folder': audio_output_folder,
                        'file_size_mb': conversion_result['audio_file_info']['file_size_mb'],
                        'estimated_duration_minutes': conversion_result['processing_stats']['estimated_audio_duration_minutes']
                    },
                    'processing_details': conversion_result['processing_stats'],
                    'next_steps': {
                        'listen_to_audio': f'Check the generated audio file: {audio_filename}',
                        'full_conversion': 'If satisfied with quality, proceed to full book conversion',
                        'adjust_settings': 'Modify word_limit or chapter_number for further testing'
                    }
                }
                
                print(f"\n🎉 Test audio conversion completed successfully!")
                print(f"🎵 Audio file created: {audio_filename}")
                print(f"📊 File size: {conversion_result['audio_file_info']['file_size_mb']:.2f} MB")
                print(f"⏱️ Estimated duration: {conversion_result['processing_stats']['estimated_audio_duration_minutes']:.1f} minutes")
                print(f"📁 Location: {audio_output_folder}")
                print("=" * 50)
                
                return jsonify(test_result)
            
            else:
                return jsonify({
                    'success': False,
                    'error': f'Audio conversion failed: {conversion_result.get("error", "Unknown error")}',
                    'code': 'AUDIO_CONVERSION_FAILED',
                    'conversion_id': conversion_id
                }), 500
        
        except Exception as audio_error:
            print(f"❌ Audio generation error: {str(audio_error)}")
            
            return jsonify({
                'success': False,
                'error': f'Audio generation failed: {str(audio_error)}',
                'code': 'AUDIO_GENERATION_ERROR',
                'conversion_id': conversion_id
            }), 500
    
    except Exception as e:
        print(f"❌ Test audio conversion failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Test conversion failed: {str(e)}',
            'code': 'TEST_CONVERSION_FAILED'
        }), 500

@app.route('/api/audio/<path:audio_path>')
def serve_audio_file(audio_path):
    """
    Serve audio files generated by the conversion process.
    
    This endpoint acts as a secure bridge between our server's file system
    and the React frontend. It takes a relative path to an audio file and
    serves it directly to the browser with appropriate headers for audio playback.
    
    The path should be relative to the audiobooks folder, for example:
    /api/audio/audiobook_20250720_212139_770b1cd6/chapters/Chapter_01_16._MY_ADOPTED_FATHER.wav
    """
    try:
        # Construct the full path to the audio file
        full_audio_path = os.path.join(app.config['AUDIOBOOKS_FOLDER'], audio_path)
        
        # Security check: ensure the path doesn't escape our audiobooks directory
        audiobooks_abs_path = os.path.abspath(app.config['AUDIOBOOKS_FOLDER'])
        requested_abs_path = os.path.abspath(full_audio_path)
        
        if not requested_abs_path.startswith(audiobooks_abs_path):
            print(f"⚠️ Security warning: Attempted path traversal blocked: {audio_path}")
            return jsonify({'error': 'Invalid file path'}), 403
        
        # Check if the file exists
        if not os.path.exists(full_audio_path):
            print(f"❌ Audio file not found: {full_audio_path}")
            return jsonify({'error': 'Audio file not found'}), 404
        
        # Determine the MIME type for proper browser handling
        if full_audio_path.endswith('.wav'):
            mimetype = 'audio/wav'
        elif full_audio_path.endswith('.mp3'):
            mimetype = 'audio/mpeg'
        else:
            mimetype = 'audio/wav'  # Default to WAV
        
        print(f"🎵 Serving audio file: {os.path.basename(full_audio_path)}")
        
        # Serve the file with appropriate headers for audio streaming
        return send_file(
            full_audio_path,
            mimetype=mimetype,
            as_attachment=False,  # Allow inline playback in browser
            download_name=os.path.basename(full_audio_path)
        )
        
    except Exception as e:
        print(f"❌ Error serving audio file: {str(e)}")
        return jsonify({'error': 'Failed to serve audio file'}), 500

@app.route('/api/trailConvert', methods=['POST'])
def trail_conversion_process():
    """
    Complete ebook-to-audiobook conversion endpoint with XTTS neural synthesis.
    
    This enhanced endpoint represents the evolution of your audiobook conversion system
    from a two-step process (extract chapters, then convert to audio) into a single,
    seamless pipeline that transforms ebooks directly into professional-quality audiobooks.
    
    Think of this as a master craftsman's workshop where raw materials (ebook files)
    are transformed through multiple specialized processes into finished products
    (complete audiobooks) - all in one continuous, carefully orchestrated operation.
    
    The process follows this comprehensive workflow:
    1. Receive and validate the uploaded ebook file
    2. Extract and organize chapters using intelligent content detection
    3. Initialize the XTTS neural synthesis system
    4. Convert each chapter to high-quality audio using neural voices
    5. Organize the audio files for easy access and download
    6. Return complete audiobook with detailed metadata and download links
    
    This approach eliminates the need for users to manage intermediate steps while
    providing them with immediate access to their complete audiobook conversion.
    """
    
    # Initialize comprehensive tracking variables for the entire conversion process
    conversion_start_time = time.time()
    conversion_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # These variables will track our progress through the complex conversion pipeline
    temp_file_path = None
    chapters_folder = None
    audio_output_folder = None
    audio_generator = None
    extracted_chapters = []
    converted_audio_files = []
    
    try:
        print("\n🎬 Starting enhanced ebook-to-audiobook conversion...")
        print("=" * 70)
        print(f"🆔 Conversion ID: {conversion_id}")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # ==========================================
        # PHASE 1: FILE RECEPTION AND VALIDATION
        # ==========================================
        
        print("\n📥 Phase 1: Processing uploaded file...")
        
        # Validate that we received a file in the request
        if 'file' not in request.files:
            print("❌ No file found in request")
            return jsonify({
                'success': False,
                'error': 'No file provided',
                'code': 'NO_FILE_UPLOADED',
                'conversion_id': conversion_id
            }), 400
        
        uploaded_file = request.files['file']
        
        if uploaded_file.filename == '':
            print("❌ Empty filename detected")
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'code': 'EMPTY_FILENAME',
                'conversion_id': conversion_id
            }), 400
        
        # Extract and validate file information
        original_filename = uploaded_file.filename
        file_extension = Path(original_filename).suffix.lower()
        supported_extensions = {'.pdf', '.epub', '.txt', '.text'}
        
        print(f"📁 Original filename: {original_filename}")
        print(f"📎 File extension: {file_extension}")
        
        if file_extension not in supported_extensions:
            print(f"❌ Unsupported file type: {file_extension}")
            return jsonify({
                'success': False,
                'error': f'Unsupported file type: {file_extension}. Supported types: PDF, EPUB, TXT',
                'code': 'UNSUPPORTED_FILE_TYPE',
                'supported_types': list(supported_extensions),
                'conversion_id': conversion_id
            }), 400
        
        # Validate file size to prevent system overload
        uploaded_file.seek(0, 2)  # Seek to end to get file size
        file_size = uploaded_file.tell()
        uploaded_file.seek(0)  # Reset to beginning for processing
        
        max_size = app.config['MAX_CONTENT_LENGTH']
        if file_size > max_size:
            print(f"❌ File too large: {file_size} bytes (max: {max_size})")
            return jsonify({
                'success': False,
                'error': f'File size ({file_size // (1024*1024)}MB) exceeds maximum allowed size ({max_size // (1024*1024)}MB)',
                'code': 'FILE_TOO_LARGE',
                'max_size_mb': max_size // (1024*1024),
                'conversion_id': conversion_id
            }), 413
        
        print(f"📊 File size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
        
        # Save the uploaded file to temporary storage for processing
        safe_filename = secure_filename(original_filename)
        temp_filename = f"{timestamp}_{conversion_id}_{safe_filename}"
        temp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        
        uploaded_file.save(temp_file_path)
        print(f"💾 Saved to temporary location: {temp_filename}")
        
        # ==========================================
        # PHASE 2: INTELLIGENT CHAPTER EXTRACTION
        # ==========================================
        
        print(f"\n📖 Phase 2: Extracting chapters with intelligent content detection...")
        
        try:
            # Initialize the chapter extraction system
            chapter_extractor = IntelligentChapterExtractor()
            extraction_start_time = time.time()
            
            print(f"🎯 Beginning intelligent extraction for {file_extension} file...")
            
            # Extract chapters using your sophisticated content detection algorithms
            extracted_chapters = chapter_extractor.extract_chapters_from_file(temp_file_path)
            
            extraction_time = time.time() - extraction_start_time
            print(f"⏱️ Chapter extraction completed in {extraction_time:.2f} seconds")
            
            if not extracted_chapters:
                raise Exception("No readable content could be extracted from the file")
            
            print(f"✅ Successfully extracted {len(extracted_chapters)} chapters")

            total_words = sum(chapter['word_count'] for chapter in extracted_chapters)
            estimated_audio_duration = total_words / (165 / 60)  # 165 words per minute

            print(f"📊 Total content: {total_words:,} words")
            print(f"⏱️ Estimated audio duration: {estimated_audio_duration:.1f} minutes")

            print(f"\n💾 Phase 3.5: Serializing chapters to individual text files...")

            try:
                # Create a dedicated folder for this conversion's chapter files
                chapters_temp_folder = os.path.join(app.config['CHAPTERS_FOLDER'], f"conversion_{timestamp}_{conversion_id}")
                os.makedirs(chapters_temp_folder, exist_ok=True)
                
                print(f"📁 Created chapter files folder: {os.path.basename(chapters_temp_folder)}")
                
                # Write each chapter to its own text file
                serialized_chapter_files = []
                serialization_start_time = time.time()
                
                for chapter in extracted_chapters:
                    # Create a safe filename for this chapter
                    chapter_number = chapter['number']
                    chapter_title = chapter['title']
                    
                    # Clean the chapter title for use in filename (remove problematic characters)
                    safe_title = "".join(c for c in chapter_title if c.isalnum() or c in (' ', '-', '_')).strip()
                    safe_title = safe_title.replace(' ', '_')[:30]  # Limit length and replace spaces
                    
                    # Construct the chapter filename
                    chapter_filename = f"Chapter_{chapter_number:02d}_{safe_title}.txt"
                    chapter_file_path = os.path.join(chapters_temp_folder, chapter_filename)
                    
                    # Write the chapter content to the file
                    try:
                        with open(chapter_file_path, 'w', encoding='utf-8') as chapter_file:
                            # Write the actual chapter content
                            chapter_file.write(chapter['content'])
                        
                        # Verify the file was created successfully
                        if os.path.exists(chapter_file_path):
                            file_size = os.path.getsize(chapter_file_path)
                            
                            # Store the file information for Phase 4
                            serialized_chapter_files.append({
                                'chapter_number': chapter_number,
                                'title': chapter_title,
                                'file_path': chapter_file_path,
                                'filename': chapter_filename,
                                'word_count': chapter['word_count'],
                                'file_size_bytes': file_size
                            })
                            
                            print(f"   ✅ Chapter {chapter_number}: {chapter_filename} ({file_size:,} bytes)")
                        
                        else:
                            print(f"   ❌ Failed to create file for Chapter {chapter_number}")
                            
                    except Exception as file_error:
                        print(f"   ❌ Error writing Chapter {chapter_number}: {str(file_error)}")
                        continue
                
                serialization_time = time.time() - serialization_start_time
                
                if not serialized_chapter_files:
                    raise Exception("No chapter files were successfully created")
                
                print(f"✅ Successfully serialized {len(serialized_chapter_files)} chapters to files")
                print(f"⏱️ Serialization completed in {serialization_time:.2f} seconds")
                print(f"📁 Chapter files location: {chapters_temp_folder}")
                
                # Update the chapters_folder variable for Phase 4 to use
                chapters_folder = chapters_temp_folder
                
            except Exception as serialization_error:
                print(f"❌ Chapter serialization failed: {str(serialization_error)}")
                
                # Clean up temporary file before returning error
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                
                return jsonify({
                    'success': False,
                    'error': f'Chapter serialization failed: {str(serialization_error)}',
                    'code': 'CHAPTER_SERIALIZATION_FAILED',
                    'conversion_id': conversion_id,
                    'chapters_extracted': len(extracted_chapters)
                }), 500
            
            # Calculate total content statistics for planning audio conversion
            total_words = sum(chapter['word_count'] for chapter in extracted_chapters)
            estimated_audio_duration = total_words / (165 / 60)  # 165 words per minute
            
            print(f"📊 Total content: {total_words:,} words")
            print(f"⏱️ Estimated audio duration: {estimated_audio_duration:.1f} minutes")
            
        except Exception as extraction_error:
            print(f"❌ Chapter extraction failed: {str(extraction_error)}")
            # Clean up temporary file before returning error
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
            return jsonify({
                'success': False,
                'error': f'Chapter extraction failed: {str(extraction_error)}',
                'code': 'EXTRACTION_FAILED',
                'conversion_id': conversion_id
            }), 500
        
        # ==========================================
        # PHASE 3: XTTS NEURAL SYNTHESIS INITIALIZATION
        # ==========================================
        
        print(f"\n🧠 Phase 3: Initializing XTTS neural synthesis system...")
        
        try:
            # Initialize the advanced neural audio generation system
            print("⏳ Loading XTTS neural network (this may take a moment)...")
            audio_generator = AdvancedAudiobookGenerator()
            
            # Verify that initialization was successful
            if not audio_generator.model_loaded:
                raise Exception("XTTS model failed to load properly")
            
            if not audio_generator.available_speakers:
                raise Exception("No speakers were discovered in the XTTS system")
            
            print(f"✅ XTTS system initialized successfully!")
            print(f"🎭 Neural synthesis ready with {len(audio_generator.available_speakers)} available speakers")
            print(f"⚡ Processing device: {audio_generator.device}")
            
            # Show some available speakers for reference
            sample_speakers = audio_generator.available_speakers[:5]
            print(f"🎤 Sample speakers: {', '.join(sample_speakers)}")


            
        except Exception as xtts_error:
            print(f"❌ XTTS initialization failed: {str(xtts_error)}")
            
            # Clean up temporary file and extracted data
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
            return jsonify({
                'success': False,
                'error': f'Neural synthesis system initialization failed: {str(xtts_error)}',
                'code': 'XTTS_INITIALIZATION_FAILED',
                'conversion_id': conversion_id,
                'troubleshooting': {
                    'possible_causes': [
                        'XTTS model download interrupted',
                        'Insufficient GPU memory',
                        'Network connectivity issues',
                        'CUDA compatibility problems'
                    ],
                    'suggestions': [
                        'Check internet connection for model download',
                        'Restart the application to retry initialization',
                        'Free up GPU memory by closing other applications',
                        'Run the XTTS diagnostic script to verify system status'
                    ]
                }
            }), 500
        
        # ==========================================
        # PHASE 4: AUDIO CONVERSION PROCESSING
        # ==========================================
        
        print(f"\n🎵 Phase 4: Converting chapters to neural audio...")
        
        # Create organized folder structure for the complete audiobook
        audio_output_folder = os.path.join(app.config['AUDIOBOOKS_FOLDER'], f"audiobook_{timestamp}_{conversion_id}")
        chapters_audio_folder = os.path.join(audio_output_folder, "chapters")
        os.makedirs(chapters_audio_folder, exist_ok=True)
        
        print(f"📁 Audio output folder: {audio_output_folder}")
        
        # Process each chapter through the complete audio conversion pipeline
        audio_conversion_start_time = time.time()
        converted_audio_files = []
        total_audio_duration = 0
        total_processed_words = 0
        
        # Use intelligent defaults for conversion parameters
        # (Since this is a file upload request, not JSON, we use defaults)
        word_limit_per_chapter = 50  # No word limit for full conversion youcanchangethis
        speaker_preference = 'female_narrator'  # Default to first available speaker
        max_chapters = 5  # Convert all chapters found youcanchangethis
        
        print(f"🎯 Conversion settings:")
        print(f"   Word limit per chapter: {word_limit_per_chapter or 'No limit'}")
        print(f"   Preferred speaker: {speaker_preference}")
        print(f"   Max chapters to convert: {max_chapters or 'All chapters'}")
        
        # Process each serialized chapter file through the neural synthesis pipeline
        chapters_to_process = serialized_chapter_files[:max_chapters] if max_chapters else serialized_chapter_files

        for chapter_index, chapter_info in enumerate(chapters_to_process):
            chapter_start_time = time.time()
            chapter_number = chapter_info['chapter_number']
            chapter_title = chapter_info['title']
            chapter_file_path = chapter_info['file_path']  # This is the key change!
            chapter_word_count = chapter_info['word_count']
            
            print(f"\n📖 Processing Chapter {chapter_number}: {chapter_title}")
            print(f"   📊 Words: {chapter_word_count:,}")
            
            try:
                temp_chapter_path = chapter_file_path
                print(f"   📄 Using serialized file: {os.path.basename(temp_chapter_path)}")
                
                # Define output path for this chapter's audio
                audio_filename = f"Chapter_{chapter_number:02d}_{secure_filename(chapter_title[:30])}.wav"
                chapter_audio_path = os.path.join(chapters_audio_folder, audio_filename)
                
                print(f"   🎵 Generating audio: {audio_filename}")
                
                # Convert this chapter to high-quality neural audio
                conversion_result = audio_generator.convert_chapter_to_audio(
                    chapter_text_file_path=temp_chapter_path,
                    output_audio_path=chapter_audio_path,
                    word_limit=word_limit_per_chapter,
                    speaker=speaker_preference
                )
                
                
                # Process the conversion results
                if conversion_result['success']:
                    chapter_processing_time = time.time() - chapter_start_time
                    
                    # Verify the audio file was created successfully
                    if os.path.exists(chapter_audio_path):
                        audio_file_size = os.path.getsize(chapter_audio_path)
                        
                        if audio_file_size > 1000:  # Ensure file has substantial content
                            # Record successful conversion details
                            chapter_audio_info = {
                                'chapter_number': chapter_number,
                                'title': chapter_title,
                                'audio_filename': audio_filename,
                                'audio_file_path': chapter_audio_path,  # Keep the full path for server use
                                # Add this new field for frontend consumption
                                'audio_url': f'/api/audio/{os.path.relpath(chapter_audio_path, app.config["AUDIOBOOKS_FOLDER"]).replace(os.sep, "/")}',
                                'original_word_count': chapter_word_count,
                                'processed_word_count': conversion_result['processing_stats']['processed_word_count'],
                                'audio_file_size_bytes': audio_file_size,
                                'audio_file_size_mb': round(audio_file_size / (1024*1024), 2),
                                'estimated_duration_minutes': conversion_result['processing_stats']['estimated_audio_duration_minutes'],
                                'processing_time_seconds': round(chapter_processing_time, 2),
                                'speaker_used': conversion_result['neural_synthesis']['speaker'],
                                'neural_quality': conversion_result['neural_synthesis']['quality_level']
                            }
                            
                            converted_audio_files.append(chapter_audio_info)
                            total_audio_duration += conversion_result['processing_stats']['estimated_audio_duration_minutes']
                            total_processed_words += conversion_result['processing_stats']['processed_word_count']
                            
                            print(f"   ✅ Conversion successful!")
                            print(f"   📊 Audio size: {chapter_audio_info['audio_file_size_mb']:.2f} MB")
                            print(f"   ⏱️ Duration: ~{chapter_audio_info['estimated_duration_minutes']:.1f} minutes")
                            print(f"   🎭 Speaker: {chapter_audio_info['speaker_used']}")
                            
                        else:
                            print(f"   ❌ Audio file too small ({audio_file_size} bytes) - conversion may have failed")
                            continue
                    else:
                        print(f"   ❌ Audio file was not created - conversion failed")
                        continue
                
                else:
                    print(f"   ❌ Conversion failed: {conversion_result.get('error', 'Unknown error')}")
                    continue
                    
            except Exception as chapter_error:
                print(f"   ❌ Chapter processing failed: {str(chapter_error)}")
                # Continue with next chapter rather than failing the entire conversion
                continue
        
        audio_conversion_time = time.time() - audio_conversion_start_time
        
        # ==========================================
        # PHASE 5: FINALIZATION AND RESPONSE PREPARATION
        # ==========================================
        
        print(f"\n🎉 Phase 5: Finalizing audiobook conversion...")
        
        # Clean up temporary files and resources
        try:
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                print("🗑️ Cleaned up temporary upload file")
            
            if audio_generator:
                audio_generator.cleanup_model()
                print("🧹 Cleaned up XTTS neural synthesis resources")
                
        except Exception as cleanup_error:
            print(f"⚠️ Cleanup warning: {cleanup_error}")
            # Don't fail the conversion for cleanup issues
        
        # Calculate comprehensive conversion statistics
        total_conversion_time = time.time() - conversion_start_time
        successful_chapters = len(converted_audio_files)
        total_chapters = len(extracted_chapters)
        
        # Verify that we successfully converted at least some chapters
        if successful_chapters == 0:
            return jsonify({
                'success': False,
                'error': 'No chapters were successfully converted to audio',
                'code': 'NO_AUDIO_GENERATED',
                'conversion_id': conversion_id,
                'chapters_attempted': total_chapters
            }), 500
        
        # Calculate total audio file size
        total_audio_size_bytes = sum(chapter['audio_file_size_bytes'] for chapter in converted_audio_files)
        total_audio_size_mb = round(total_audio_size_bytes / (1024*1024), 2)
        
        print(f"✅ Audiobook conversion completed successfully!")
        print(f"📊 Conversion summary:")
        print(f"   Chapters converted: {successful_chapters}/{total_chapters}")
        print(f"   Total audio duration: ~{total_audio_duration:.1f} minutes")
        print(f"   Total audio size: {total_audio_size_mb:.2f} MB")
        print(f"   Total processing time: {total_conversion_time:.1f} seconds")
        
        # Prepare comprehensive response with all conversion details
        audiobook_response = {
            'success': True,
            'message': f'Successfully converted {successful_chapters} chapters from {original_filename} to audiobook',
            'conversion_id': conversion_id,
            'timestamp': datetime.now().isoformat(),
            
            # Original file information
            'source_file': {
                'original_filename': original_filename,
                'file_type': file_extension,
                'file_size_bytes': file_size,
                'file_size_mb': round(file_size / (1024*1024), 2)
            },
            
            # Comprehensive processing statistics
            'conversion_stats': {
                'total_chapters_found': total_chapters,
                'chapters_successfully_converted': successful_chapters,
                'conversion_success_rate': round((successful_chapters / total_chapters) * 100, 1),
                'total_processing_time_seconds': round(total_conversion_time, 2),
                'audio_generation_time_seconds': round(audio_conversion_time, 2),
                'chapter_extraction_time_seconds': round(extraction_time, 2),
                'total_words_processed': total_processed_words,
                'processing_efficiency_words_per_second': round(total_processed_words / total_conversion_time, 1)
            },
            
            # Complete audiobook information
            'audiobook': {
                'total_duration_minutes': round(total_audio_duration, 1),
                'total_size_bytes': total_audio_size_bytes,
                'total_size_mb': total_audio_size_mb,
                'chapters_folder': chapters_audio_folder,
                'chapter_count': successful_chapters,
                'format': 'WAV',
                'quality': 'Neural synthesis (XTTS v2)',
                'sample_rate': '24kHz'
            },
            
            # Detailed chapter information
            'chapters': converted_audio_files,
            
            # Technical processing details
            'processing_details': {
                'extraction_method': 'intelligent_chapter_detection',
                'audio_synthesis': 'XTTS_v2_neural_synthesis',
                'device_used': audio_generator.device if audio_generator else 'unknown',
                'speakers_available': len(audio_generator.available_speakers) if audio_generator else 0,
                'neural_quality_applied': True,
                'front_matter_skipped': True,
                'chapter_boundaries_detected': successful_chapters > 1
            },
            
            # User guidance for next steps
            'next_steps': {
                'download_individual_chapters': f'Access individual chapter audio files in: {chapters_audio_folder}',
                'listen_to_audiobook': 'Play the generated audio files in order to listen to your complete audiobook',
                'file_organization': 'Chapter files are numbered sequentially for easy playlist creation',
                'quality_verification': 'Listen to the first chapter to verify audio quality meets your expectations'
            }
        }
        
        print("=" * 70)
        print(f"🎧 Audiobook conversion completed for: {original_filename}")
        print(f"📁 Audio files location: {chapters_audio_folder}")
        print(f"🎵 Ready to listen to {successful_chapters} chapters!")
        
        return jsonify(audiobook_response)
        
    except Exception as e:
        print(f"❌ Enhanced conversion process failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Perform comprehensive cleanup on any failure
        cleanup_operations = []
        
        try:
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                cleanup_operations.append("Removed temporary upload file")
        except:
            pass
        
        try:
            if audio_generator:
                audio_generator.cleanup_model()
                cleanup_operations.append("Cleaned up XTTS resources")
        except:
            pass
        
        # Return comprehensive error information for debugging
        return jsonify({
            'success': False,
            'error': f'Enhanced conversion process failed: {str(e)}',
            'code': 'ENHANCED_CONVERSION_FAILED',
            'conversion_id': conversion_id,
            'processing_time_seconds': time.time() - conversion_start_time,
            'cleanup_performed': cleanup_operations,
            'troubleshooting': {
                'error_type': type(e).__name__,
                'suggestion': 'Check server logs for detailed error information',
                'common_solutions': [
                    'Verify XTTS system is properly installed',
                    'Check available disk space for audio files',
                    'Ensure GPU memory is available for neural synthesis',
                    'Try with a smaller file or fewer chapters'
                ]
            }
        }), 500






if __name__ == '__main__':
    print("\n🚀 Starting AudioBook Converter Backend...")
    print("=" * 60)
    
    # Perform initial system check
    print("🔧 Performing startup system check...")
    
    # Check if all required directories exist
    directories_ok = True
    for folder_name, folder_path in [
        ('Upload', app.config['UPLOAD_FOLDER']),
        ('Chapters', app.config['CHAPTERS_FOLDER']),
        ('Audiobooks', app.config['AUDIOBOOKS_FOLDER'])
    ]:
        if os.path.exists(folder_path):
            print(f"✅ {folder_name} directory ready: {folder_path}")
        else:
            print(f"❌ {folder_name} directory missing: {folder_path}")
            directories_ok = False
    
    # Check critical libraries
    libraries_ok = True
    required_libraries = [
        ('PyPDF2', 'PDF processing'),
        ('ebooklib', 'EPUB processing'),
        ('pyttsx3', 'Text-to-speech conversion'),
        ('flask', 'Web framework'),
        ('flask_cors', 'Cross-origin requests')
    ]
    
    for lib_name, purpose in required_libraries:
        try:
            __import__(lib_name)
            print(f"✅ {lib_name} available for {purpose}")
        except ImportError:
            print(f"❌ {lib_name} missing - required for {purpose}")
            libraries_ok = False
    
    # Test TTS engine initialization
    print("🎵 Testing text-to-speech engine...")
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        if voices:
            print(f"✅ TTS engine ready with {len(voices)} available voices")
        else:
            print("⚠️ TTS engine initialized but no voices detected")
        engine.stop()
    except Exception as tts_error:
        print(f"❌ TTS engine test failed: {tts_error}")
        libraries_ok = False
    
    # Report startup status
    if directories_ok and libraries_ok:
        print("\n🎉 All systems ready for audiobook conversion!")
        print("📡 Starting Flask server...")
        print("🌐 Backend will be available at: http://localhost:5001")
        print("🔗 Health check: http://localhost:5001/health")
        print("📱 Make sure your React frontend connects to: http://localhost:5001")
        print("=" * 60)
        
        # Start the Flask development server
        app.run(host='0.0.0.0', port=5001, debug=True)
        
    else:
        print("\n❌ System startup failed!")
        print("🛠️ Please install missing dependencies:")
        print("   pip install flask flask-cors PyPDF2 ebooklib beautifulsoup4 pyttsx3")
        print("=" * 60)
