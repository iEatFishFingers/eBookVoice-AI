"""Enhanced text parsing for eBook files with smart content detection."""
import re
import logging
from pathlib import Path
from typing import Optional, Tuple
import PyPDF2
from bs4 import BeautifulSoup

# Try to import ebooklib
try:
    import ebooklib
    from ebooklib import epub
    EPUB_SUPPORT = True
except ImportError:
    EPUB_SUPPORT = False
    
logger = logging.getLogger(__name__)

class TextParser:
    """Enhanced text parser for eBooks with smart content extraction."""
    
    def __init__(self):
        self.chapter_patterns = [
            r'^chapter\s+\d+',
            r'^\d+\.\s',
            r'^part\s+\d+',
            r'^section\s+\d+',
            r'chapter one',
            r'chapter 1',
            r'^1\s',
        ]
        
        self.header_patterns = [
            r'table of contents',
            r'contents',
            r'copyright',
            r'published by',
            r'isbn',
            r'all rights reserved',
            r'printed in',
            r'first edition',
            r'cover design',
            r'acknowledgments',
            r'about the author',
            r'also by',
            r'dedication'
        ]
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract and clean text from any supported file type."""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_extension == '.epub':
            return self._extract_from_epub(file_path)
        elif file_extension in ['.txt', '.text']:
            return self._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF with smart content detection."""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                        
                        # Log progress for large PDFs
                        if page_num > 0 and page_num % 50 == 0:
                            logger.info(f"Processed {page_num + 1} pages...")
            
            return self._clean_extracted_text(text)
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            raise
    
    def _extract_from_epub(self, file_path: str) -> str:
        """Extract text from EPUB with chapter detection."""
        if not EPUB_SUPPORT:
            raise ValueError("EPUB support not available. Please install ebooklib.")
        
        try:
            book = epub.read_epub(file_path)
            text_parts = []
            
            # Get all document items
            items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
            
            for item in items:
                try:
                    content = item.get_content().decode('utf-8')
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Remove style and script tags
                    for tag in soup(["style", "script", "meta", "link"]):
                        tag.decompose()
                    
                    # Extract text
                    item_text = soup.get_text()
                    if item_text and len(item_text.strip()) > 50:  # Skip very short sections
                        text_parts.append(item_text)
                        
                except Exception as e:
                    logger.warning(f"Failed to process EPUB item {item.file_name}: {e}")
                    continue
            
            full_text = "\n".join(text_parts)
            return self._clean_extracted_text(full_text)
            
        except Exception as e:
            logger.error(f"Failed to extract text from EPUB: {e}")
            raise
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file with encoding detection."""
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        text = file.read()
                        return self._clean_extracted_text(text)
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, try with error handling
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                text = file.read()
                return self._clean_extracted_text(text)
                
        except Exception as e:
            logger.error(f"Failed to extract text from TXT: {e}")
            raise
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean and process extracted text for audiobook conversion."""
        if not text or not text.strip():
            return ""
        
        # Find main content start
        main_content = self._find_main_content_start(text)
        
        # Clean the text
        cleaned = self._apply_text_cleaning(main_content)
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)
        
        return cleaned.strip()
    
    def _find_main_content_start(self, text: str) -> str:
        """Find where the main content starts (skip frontmatter)."""
        lines = text.split('\n')
        start_index = 0
        
        # Look for chapter markers
        for i, line in enumerate(lines):
            line_lower = line.strip().lower()
            
            # Skip empty lines
            if not line_lower:
                continue
            
            # Check for chapter patterns
            for pattern in self.chapter_patterns:
                if re.match(pattern, line_lower):
                    start_index = i
                    logger.info(f"Found main content start at line {i}: '{line.strip()}'")
                    break
            
            if start_index > 0:
                break
            
            # If we've gone too far without finding a chapter, start from beginning
            if i > 100 and start_index == 0:
                logger.info("No clear chapter start found, using full text")
                break
        
        # Skip header content if found
        filtered_lines = []
        skip_until_content = False
        
        for i in range(start_index, len(lines)):
            line = lines[i].strip()
            line_lower = line.lower()
            
            # Skip header/frontmatter sections
            if any(pattern in line_lower for pattern in self.header_patterns):
                skip_until_content = True
                continue
            
            # If we find substantial content, stop skipping
            if skip_until_content and len(line) > 50:
                skip_until_content = False
            
            if not skip_until_content:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _apply_text_cleaning(self, text: str) -> str:
        """Apply comprehensive text cleaning for TTS."""
        # Remove page numbers (standalone numbers on lines)
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Remove headers/footers (repeated patterns)
        lines = text.split('\n')
        filtered_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip very short lines that might be page numbers or artifacts
            if len(line) < 3:
                continue
            
            # Skip lines that are all caps and short (likely headers)
            if len(line) < 50 and line.isupper():
                continue
            
            # Skip lines with excessive punctuation or symbols
            punct_ratio = len(re.findall(r'[^\w\s]', line)) / len(line) if line else 0
            if punct_ratio > 0.5:
                continue
            
            filtered_lines.append(line)
        
        # Rejoin text
        text = '\n'.join(filtered_lines)
        
        # Fix common OCR/extraction errors
        text = re.sub(r'([.!?])\s*([a-z])', r'\1 \2', text)  # Fix missing spaces after punctuation
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Fix missing spaces between words
        text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)  # Fix hyphenated words split across lines
        
        # Normalize quotation marks  
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r"[''']", "'", text)
        
        # Remove excessive punctuation
        text = re.sub(r'\.{3,}', '...', text)
        text = re.sub(r'-{2,}', '—', text)
        
        return text
    
    def get_text_statistics(self, text: str) -> dict:
        """Get statistics about the extracted text."""
        if not text:
            return {'words': 0, 'characters': 0, 'paragraphs': 0}
        
        words = len(text.split())
        characters = len(text)
        paragraphs = len([p for p in text.split('\n\n') if p.strip()])
        
        return {
            'words': words,
            'characters': characters,
            'paragraphs': paragraphs,
            'estimated_reading_time_minutes': round(words / 200)  # Average reading speed
        }

# Global parser instance
text_parser = None

def get_text_parser():
    """Get the global text parser instance."""
    global text_parser
    if text_parser is None:
        text_parser = TextParser()
    return text_parser