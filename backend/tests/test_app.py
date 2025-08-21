import pytest
import json
import tempfile
import os
from pathlib import Path
import sys

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, conversion_jobs

@pytest.fixture
def client():
    """Create test client."""
    app = create_app('testing')
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def sample_txt_file():
    """Create a temporary text file for testing."""
    content = "This is a test eBook content for the conversion system."
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)

class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test health endpoint returns 200 and correct structure."""
        response = client.get('/health')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert data['service'] == 'eBookVoice AI Converter'

class TestFileUpload:
    """Test file upload and conversion functionality."""
    
    def test_upload_no_file(self, client):
        """Test upload endpoint with no file."""
        response = client.post('/upload')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'No file provided' in data['error']
    
    def test_upload_empty_filename(self, client):
        """Test upload endpoint with empty filename."""
        data = {'file': (None, '')}
        response = client.post('/upload', data=data)
        
        assert response.status_code == 400
        
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'No file selected' in response_data['error']
    
    def test_upload_unsupported_file_type(self, client):
        """Test upload endpoint with unsupported file type."""
        data = {'file': (tempfile.NamedTemporaryFile(suffix='.mp3'), 'test.mp3')}
        response = client.post('/upload', data=data)
        
        assert response.status_code == 400
        
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'Unsupported file type' in response_data['error']
    
    def test_upload_valid_txt_file(self, client, sample_txt_file):
        """Test upload endpoint with valid text file."""
        with open(sample_txt_file, 'rb') as f:
            data = {'file': (f, 'test.txt')}
            response = client.post('/upload', data=data)
        
        assert response.status_code == 200
        
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert 'data' in response_data
        
        job_data = response_data['data']
        assert 'id' in job_data
        assert job_data['fileName'] == 'test.txt'
        assert job_data['title'] == 'test'
        assert job_data['status'] == 'pending'
        assert job_data['progress'] == 0

class TestConversionStatus:
    """Test conversion status endpoints."""
    
    def test_get_nonexistent_conversion(self, client):
        """Test getting status of non-existent conversion."""
        response = client.get('/conversions/nonexistent-id')
        
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'not found' in data['error']
    
    def test_get_all_conversions_empty(self, client):
        """Test getting all conversions when none exist."""
        # Clear any existing jobs
        conversion_jobs.clear()
        
        response = client.get('/conversions')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data'] == []

class TestDownload:
    """Test audio file download functionality."""
    
    def test_download_nonexistent_job(self, client):
        """Test downloading from non-existent job."""
        response = client.get('/download/nonexistent-id')
        
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'not found' in data['error']

class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_complete_upload_workflow(self, client, sample_txt_file):
        """Test complete upload and status check workflow."""
        # Upload file
        with open(sample_txt_file, 'rb') as f:
            data = {'file': (f, 'integration_test.txt')}
            upload_response = client.post('/upload', data=data)
        
        assert upload_response.status_code == 200
        upload_data = json.loads(upload_response.data)
        job_id = upload_data['data']['id']
        
        # Check status
        status_response = client.get(f'/conversions/{job_id}')
        assert status_response.status_code == 200
        
        status_data = json.loads(status_response.data)
        assert status_data['success'] is True
        assert status_data['data']['id'] == job_id
        
        # Check in all conversions list
        all_response = client.get('/conversions')
        assert all_response.status_code == 200
        
        all_data = json.loads(all_response.data)
        assert any(job['id'] == job_id for job in all_data['data'])

if __name__ == '__main__':
    pytest.main([__file__, '-v'])