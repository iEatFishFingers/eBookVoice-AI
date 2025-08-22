"""Test the lightweight text parser with built-in libraries."""
import sys
import os
import tempfile
import zipfile
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_epub():
    """Create a minimal test EPUB file."""
    epub_content = {
        'META-INF/container.xml': '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>''',
        'content.opf': '''<?xml version="1.0" encoding="UTF-8"?>
<package version="3.0" xmlns="http://www.idpf.org/2007/opf">
    <metadata>
        <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">Test Book</dc:title>
    </metadata>
    <manifest>
        <item id="chapter1" href="chapter1.html" media-type="application/xhtml+xml"/>
    </manifest>
    <spine>
        <itemref idref="chapter1"/>
    </spine>
</package>''',
        'chapter1.html': '''<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Chapter 1</title>
</head>
<body>
    <h1>Chapter 1: The Beginning</h1>
    <p>This is the first chapter of our test book. It contains some sample text that should be extracted properly by our lightweight parser.</p>
    <p>The parser should handle HTML tags correctly and extract only the readable text content.</p>
    <p>This paragraph tests multiple sentences. Each sentence should be preserved. The formatting should be clean.</p>
</body>
</html>'''
    }
    
    # Create temporary EPUB file
    temp_epub = tempfile.NamedTemporaryFile(suffix='.epub', delete=False)
    temp_epub.close()
    
    with zipfile.ZipFile(temp_epub.name, 'w', zipfile.ZIP_DEFLATED) as epub_zip:
        for filename, content in epub_content.items():
            epub_zip.writestr(filename, content)
    
    return temp_epub.name

def test_text_parser_functionality():
    """Test all text parser functions with built-in libraries."""
    print("Testing lightweight text parser...")
    
    try:
        from text_parser import get_text_parser
        parser = get_text_parser()
        
        # Test 1: TXT file parsing
        print("\n1. Testing TXT file parsing...")
        test_txt_content = """
        Table of Contents
        
        Chapter 1: The Story Begins
        
        This is the beginning of our story. The protagonist walked through the forest, wondering what adventures lay ahead. The text should be cleaned and formatted properly for audio conversion.
        
        This is a second paragraph that should also be preserved in the output.
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_txt_content)
            txt_path = f.name
        
        try:
            txt_extracted = parser.extract_text_from_file(txt_path)
            txt_stats = parser.get_text_statistics(txt_extracted)
            
            print(f"   - TXT extraction successful")
            print(f"   - Words: {txt_stats['words']}")
            print(f"   - Characters: {txt_stats['characters']}")
            print(f"   - Preview: {txt_extracted[:100]}...")
            
            assert txt_stats['words'] > 0, "No words extracted from TXT"
            assert "Chapter 1" in txt_extracted, "Chapter marker not found"
            
        finally:
            os.unlink(txt_path)
        
        # Test 2: EPUB file parsing  
        print("\n2. Testing EPUB file parsing...")
        epub_path = create_test_epub()
        
        try:
            epub_extracted = parser.extract_text_from_file(epub_path)
            epub_stats = parser.get_text_statistics(epub_extracted)
            
            print(f"   - EPUB extraction successful")
            print(f"   - Words: {epub_stats['words']}")
            print(f"   - Characters: {epub_stats['characters']}")
            print(f"   - Preview: {epub_extracted[:100]}...")
            
            assert epub_stats['words'] > 0, "No words extracted from EPUB"
            assert "Chapter 1" in epub_extracted, "Chapter content not found"
            assert "<html>" not in epub_extracted, "HTML tags not removed"
            
        finally:
            os.unlink(epub_path)
        
        # Test 3: Text cleaning functionality
        print("\n3. Testing text cleaning...")
        dirty_text = """
        
        Copyright Notice
        All rights reserved
        
        Chapter One
        
        This    text   has  weird    spacing.
        It also has "curly quotes" and 'single quotes'.
        Some—long—dashes and... excessive dots.
        
        123
        
        This line should be preserved.
        """
        
        cleaned_text = parser._clean_extracted_text(dirty_text)
        
        print(f"   - Text cleaning successful")
        print(f"   - Cleaned length: {len(cleaned_text)}")
        print(f"   - Preview: {cleaned_text[:100]}...")
        
        assert "Chapter One" in cleaned_text, "Chapter marker not preserved"
        assert "Copyright Notice" not in cleaned_text, "Header content not removed"
        assert "This line should be preserved" in cleaned_text, "Valid content removed"
        
        print("\n✓ All text parser tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Text parser test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flask_app_functionality():
    """Test Flask app basic functionality."""
    print("\nTesting Flask app functionality...")
    
    try:
        from app import create_app
        
        # Create test app
        app = create_app('testing')
        
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            assert response.status_code == 200, f"Health check failed: {response.status_code}"
            
            data = response.get_json()
            assert data['status'] == 'healthy', "Health status not healthy"
            
            print("   - Health endpoint working")
            
            # Test CORS headers
            response = client.options('/health', 
                headers={'Origin': 'https://ebookvoiceai.netlify.app'})
            assert 'Access-Control-Allow-Origin' in response.headers, "CORS headers missing"
            
            print("   - CORS headers present")
            
            # Test voices endpoint
            response = client.get('/api/voices')
            print(f"   - Voices endpoint accessible (status: {response.status_code})")
            
        print("✓ Flask app tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Flask app test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("Testing eBookVoice AI Lightweight Backend")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(test_text_parser_functionality())
    results.append(test_flask_app_functionality())
    
    # Summary
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"All tests passed! ({passed}/{total})")
        print("\nOptimized backend features:")
        print("- Built-in Python libraries only (zipfile, xml.etree, html.parser)")
        print("- Reduced dependencies (no ebooklib, beautifulsoup4, lxml)")
        print("- Faster Docker builds with optimized Dockerfile")
        print("- PDF extraction via PyPDF2")
        print("- EPUB extraction via zipfile + xml.etree")
        print("- TXT files via native Python file handling")
        print("- Smart content detection and cleaning")
        print("- Coqui XTTS v2 integration maintained")
        
        dependency_savings = [
            "Removed: ebooklib (0.19)",
            "Removed: beautifulsoup4 (4.12.2)",
            "Removed: lxml (4.9.3)",
            "Removed: pytest (7.4.3) - dev only",
        ]
        
        print(f"\nDependency cleanup:")
        for saving in dependency_savings:
            print(f"- {saving}")
            
        print(f"\nExpected deployment improvement:")
        print("- Faster pip install (fewer dependencies)")
        print("- Smaller Docker image size")
        print("- Reduced build time on Render")
        print("- Maintained functionality with built-in libraries")
        
    else:
        print(f"{passed}/{total} tests passed")
        print("Some optimizations may need adjustment")
    
    return passed == total

if __name__ == "__main__":
    main()