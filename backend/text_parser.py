"""Lightweight text parsing for eBook files using built-in Python libraries."""
import re
import logging
import zipfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional, Tuple
import PyPDF2

logger = logging.getLogger(__name__)

class HTMLTextExtractor(HTMLParser):
    """Simple HTML text extractor using built-in html.parser."""
    
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.skip_tags = {'style', 'script', 'meta', 'link', 'head', 'title'}
        self.current_tag = None
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag.lower()
        
    def handle_endtag(self, tag):
        self.current_tag = None
        
    def handle_data(self, data):
        if self.current_tag not in self.skip_tags:
            text = data.strip()
            if text:
                self.text_parts.append(text)
    
    def get_text(self):
        return ' '.join(self.text_parts)

class TextParser:
    """Lightweight text parser using built-in Python libraries."""
    
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
        """Extract text from PDF using PyPDF2."""
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
        """Extract text from EPUB using built-in zipfile and xml.etree."""
        try:
            text_parts = []
            
            with zipfile.ZipFile(file_path, 'r') as epub_zip:
                # Find content files
                content_files = []
                
                # First, try to find the content.opf file to get the reading order
                opf_files = [f for f in epub_zip.namelist() if f.endswith('.opf')]
                
                if opf_files:
                    # Parse OPF file to get content order
                    opf_content = epub_zip.read(opf_files[0]).decode('utf-8', errors='ignore')
                    content_files = self._parse_opf_for_content_files(opf_content, epub_zip)
                
                if not content_files:
                    # Fallback: find all HTML/XHTML files
                    content_files = [f for f in epub_zip.namelist() 
                                   if f.endswith(('.html', '.xhtml', '.htm')) and not f.startswith('META-INF/')]
                
                # Extract text from content files
                for file_name in content_files:
                    try:
                        content = epub_zip.read(file_name).decode('utf-8', errors='ignore')
                        text = self._extract_html_text(content)
                        
                        if text and len(text.strip()) > 50:  # Skip very short sections
                            text_parts.append(text)
                            
                    except Exception as e:
                        logger.warning(f"Failed to process EPUB file {file_name}: {e}")
                        continue
            
            full_text = "\n\n".join(text_parts)
            return self._clean_extracted_text(full_text)
            
        except Exception as e:
            logger.error(f"Failed to extract text from EPUB: {e}")
            raise
    
    def _parse_opf_for_content_files(self, opf_content: str, epub_zip: zipfile.ZipFile) -> list:
        """Parse OPF file to get ordered content files."""
        try:
            # Remove namespace prefixes for simpler parsing
            opf_content = re.sub(r'xmlns[^=]*="[^"]*"', '', opf_content)
            opf_content = re.sub(r'<([^>\s]+:)', r'<', opf_content)
            opf_content = re.sub(r'</([^>\s]+:)', r'</', opf_content)
            
            root = ET.fromstring(opf_content)
            
            # Find manifest items
            manifest_items = {}
            for item in root.findall('.//item'):
                item_id = item.get('id')
                href = item.get('href')
                if item_id and href:
                    manifest_items[item_id] = href
            
            # Find spine order
            spine_items = []
            for itemref in root.findall('.//itemref'):
                idref = itemref.get('idref')
                if idref in manifest_items:
                    spine_items.append(manifest_items[idref])
            
            # Filter to existing HTML/XHTML files
            content_files = []
            for href in spine_items:
                # Handle relative paths
                full_paths = [f for f in epub_zip.namelist() if f.endswith(href)]
                if full_paths:
                    content_files.append(full_paths[0])
            
            return content_files
            
        except Exception as e:
            logger.warning(f"Failed to parse OPF file: {e}")
            return []
    
    def _extract_html_text(self, html_content: str) -> str:
        """Extract text from HTML using built-in html.parser."""
        try:
            extractor = HTMLTextExtractor()
            extractor.feed(html_content)
            return extractor.get_text()
        except Exception as e:
            logger.warning(f"HTML parsing failed, using regex fallback: {e}")
            # Fallback: simple regex-based HTML tag removal
            text = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<[^>]+>', '', text)
            text = re.sub(r'&[a-zA-Z0-9#]+;', ' ', text)  # Remove HTML entities
            return text
    
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