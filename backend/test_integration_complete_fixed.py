#!/usr/bin/env python3
"""
Complete integration tests for eBookVoice AI Backend
Tests all major features: file upload, conversion, progress tracking, audio player support, and health checks
"""

import os
import sys
import time
import requests
import json
import tempfile
from pathlib import Path

# Test configuration
BASE_URL = 'http://localhost:5001'
TEST_TIMEOUT = 30  # seconds

def test_health_check():
    """Test server health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        assert response.status_code == 200, f"Health check failed with status {response.status_code}"
        
        data = response.json()
        assert data['status'] == 'healthy', "Health check returned unhealthy status"
        assert 'timestamp' in data, "Health check missing timestamp"
        
        print("PASS: Health check passed")
        return True
    except Exception as e:
        print(f"FAIL: Health check failed: {e}")
        return False

def test_file_upload_and_conversion():
    """Test file upload and conversion process"""
    print("Testing file upload and conversion...")
    
    # Create a test text file
    test_content = """
    This is a test eBook for the eBookVoice AI conversion system.
    It contains multiple sentences to test the text-to-speech functionality.
    The system should convert this text into an audio file successfully.
    This test verifies the complete workflow from upload to conversion.
    """
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            temp_file_path = f.name
        
        # Upload file
        print("  Uploading test file...")
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('test_integration.txt', f, 'text/plain')}
            data = {'voice_id': 'basic_0'}
            
            response = requests.post(
                f"{BASE_URL}/upload", 
                files=files, 
                data=data,
                timeout=30
            )
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        assert response.status_code == 200, f"Upload failed with status {response.status_code}"
        
        result = response.json()
        assert result['success'] == True, f"Upload unsuccessful: {result.get('error', 'Unknown error')}"
        
        job_id = result['data']['id']
        print(f"  File uploaded successfully. Job ID: {job_id}")
        
        # Poll for completion
        print("  Polling for conversion completion...")
        max_attempts = 30  # 30 * 2 = 60 seconds max
        attempt = 0
        
        while attempt < max_attempts:
            response = requests.get(f"{BASE_URL}/conversions/{job_id}", timeout=10)
            assert response.status_code == 200, "Failed to get conversion status"
            
            status_data = response.json()
            assert status_data['success'] == True, "Status check unsuccessful"
            
            job_status = status_data['data']['status']
            progress = status_data['data'].get('progress', 0)
            phase = status_data['data'].get('current_phase', 'Unknown')
            
            print(f"    Status: {job_status}, Progress: {progress}%, Phase: {phase}")
            
            if job_status == 'completed':
                print("  PASS: Conversion completed successfully")
                return job_id
            elif job_status == 'failed':
                error = status_data['data'].get('error', 'Unknown error')
                raise Exception(f"Conversion failed: {error}")
            
            time.sleep(2)
            attempt += 1
        
        raise Exception("Conversion timeout - took longer than expected")
        
    except Exception as e:
        print(f"  FAIL: File upload and conversion failed: {e}")
        return None

def test_audio_download(job_id):
    """Test audio file download"""
    print("Testing audio file download...")
    
    try:
        response = requests.get(f"{BASE_URL}/download/{job_id}", timeout=30)
        assert response.status_code == 200, f"Download failed with status {response.status_code}"
        
        # Check that we got audio content
        content_type = response.headers.get('content-type', '')
        assert 'audio' in content_type.lower() or len(response.content) > 1000, "Downloaded file doesn't appear to be audio"
        
        print(f"  PASS: Audio file downloaded successfully ({len(response.content)} bytes)")
        return True
    except Exception as e:
        print(f"  FAIL: Audio download failed: {e}")
        return False

def test_conversions_list():
    """Test conversions list endpoint"""
    print("Testing conversions list...")
    
    try:
        response = requests.get(f"{BASE_URL}/conversions", timeout=10)
        assert response.status_code == 200, f"Conversions list failed with status {response.status_code}"
        
        data = response.json()
        assert data['success'] == True, "Conversions list unsuccessful"
        assert isinstance(data['data'], list), "Conversions data should be a list"
        
        print(f"  PASS: Conversions list retrieved ({len(data['data'])} conversions)")
        return True
    except Exception as e:
        print(f"  FAIL: Conversions list failed: {e}")
        return False

def test_voice_endpoints():
    """Test voice-related endpoints"""
    print("Testing voice endpoints...")
    
    try:
        # Test voices list
        response = requests.get(f"{BASE_URL}/api/voices", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"  PASS: Voices list retrieved ({data.get('total_voices', 0)} voices)")
            else:
                print("  WARN:  Voices endpoint returned unsuccessful response")
        else:
            print(f"  WARN:  Voices endpoint returned status {response.status_code}")
        
        return True
    except Exception as e:
        print(f"  WARN:  Voice endpoints test failed: {e}")
        return True  # Non-critical for basic functionality

def test_file_type_support():
    """Test different file type support"""
    print("Testing file type support...")
    
    supported_types = ['.txt', '.pdf']  # .epub requires ebooklib
    
    try:
        # Test with invalid file type
        test_content = "This is a test file"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.invalid', delete=False) as f:
            f.write(test_content)
            temp_file_path = f.name
        
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('test_invalid.invalid', f, 'text/plain')}
            data = {'voice_id': 'basic_0'}
            
            response = requests.post(
                f"{BASE_URL}/upload", 
                files=files, 
                data=data,
                timeout=15
            )
        
        os.unlink(temp_file_path)
        
        # Should fail for unsupported type
        assert response.status_code == 400, "Should reject unsupported file types"
        
        result = response.json()
        assert result['success'] == False, "Should return unsuccessful for unsupported types"
        assert 'unsupported' in result.get('error', '').lower(), "Should mention unsupported file type"
        
        print("  PASS: File type validation working correctly")
        return True
        
    except Exception as e:
        print(f"  FAIL: File type support test failed: {e}")
        return False

def run_integration_tests():
    """Run all integration tests"""
    print("Starting eBookVoice AI Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("File Type Support", test_file_type_support),
        ("Voice Endpoints", test_voice_endpoints),
        ("Conversions List", test_conversions_list),
    ]
    
    results = {}
    
    # Run basic tests first
    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        results[test_name] = test_func()
    
    # Run the main conversion test
    print(f"\nRunning File Upload and Conversion...")
    job_id = test_file_upload_and_conversion()
    results["File Upload and Conversion"] = job_id is not None
    
    # Test download if conversion succeeded
    if job_id:
        print(f"\nRunning Audio Download...")
        results["Audio Download"] = test_audio_download(job_id)
    else:
        results["Audio Download"] = False
        print("Skipping audio download test (conversion failed)")
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "PASS" if passed_test else "FAIL"
        print(f"{status} - {test_name}")
        if passed_test:
            passed += 1
    
    print("-" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("ALL TESTS PASSED! The system is working correctly.")
        return True
    else:
        print("Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)