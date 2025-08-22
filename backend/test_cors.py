"""Test CORS configuration for the eBookVoice AI backend."""
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cors_configuration():
    """Test that CORS is properly configured."""
    print("Testing CORS configuration...")
    
    try:
        from app import create_app
        
        # Create test app
        app = create_app('testing')
        
        with app.test_client() as client:
            # Test preflight request (OPTIONS)
            response = client.options('/health', 
                headers={
                    'Origin': 'https://ebookvoiceai.netlify.app',
                    'Access-Control-Request-Method': 'GET',
                    'Access-Control-Request-Headers': 'Content-Type'
                })
            
            print(f"Preflight response status: {response.status_code}")
            print(f"CORS headers: {dict(response.headers)}")
            
            # Test actual request with origin
            response = client.get('/health',
                headers={
                    'Origin': 'https://ebookvoiceai.netlify.app'
                })
            
            print(f"Actual request status: {response.status_code}")
            print(f"CORS headers: {dict(response.headers)}")
            
            # Check if proper CORS headers are present
            cors_headers = [
                'Access-Control-Allow-Origin',
                'Access-Control-Allow-Methods',
                'Access-Control-Allow-Headers'
            ]
            
            has_cors = any(header in response.headers for header in cors_headers)
            
            if has_cors:
                print("✓ CORS headers are present")
                return True
            else:
                print("✗ CORS headers are missing")
                return False
            
    except Exception as e:
        print(f"✗ CORS test failed: {e}")
        return False

def main():
    """Run CORS test."""
    print("Testing eBookVoice AI CORS Configuration")
    print("=" * 40)
    
    success = test_cors_configuration()
    
    print("\n" + "=" * 40)
    if success:
        print("✓ CORS configuration appears to be working")
        print("\nThe backend should now accept requests from:")
        print("- https://ebookvoiceai.netlify.app")
        print("- http://localhost:8081 (development)")
        print("- http://localhost:19006 (development)")
    else:
        print("✗ CORS configuration needs attention")
        print("Check Flask-CORS setup and allowed origins")
    
    return success

if __name__ == "__main__":
    main()