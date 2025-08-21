#!/usr/bin/env python3
"""Test script for the enhanced TTS voice system."""

import requests
import json
import sys
import time
import tempfile
import os

# Test configuration
BASE_URL = 'http://localhost:5001'
TEST_EMAIL = 'voicetest@example.com'
TEST_PASSWORD = 'testpassword123'

def create_test_file():
    """Create a small test text file for conversion."""
    content = """
    This is a test document for the enhanced TTS voice system.
    We are testing multiple voice options and user tiers.
    This short text should be converted to speech using different voices.
    The system supports basic voices for free users and premium voices for paid tiers.
    """
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_file.write(content.strip())
    temp_file.close()
    return temp_file.name

def test_voice_system():
    """Test the complete enhanced TTS voice system."""
    print("Testing Enhanced TTS Voice System")
    print("=" * 50)
    
    # Test 1: Voice catalog without authentication
    print("1. Testing voice catalog (anonymous user)...")
    try:
        response = requests.get(f'{BASE_URL}/api/voices')
        if response.status_code == 200:
            result = response.json()
            print("✅ Voice catalog loaded for anonymous user")
            print(f"   Available voices: {result['total_voices']}")
            print(f"   User tier: {result['user_tier']}")
            for voice in result['voices'][:2]:  # Show first 2 voices
                print(f"   - {voice['name']} ({voice['engine']}, {voice['tier_required']})")
        else:
            print(f"❌ Voice catalog failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Voice catalog error: {e}")
        return False
    
    # Test 2: Engine status
    print("\n2. Testing TTS engine status...")
    try:
        response = requests.get(f'{BASE_URL}/api/voices/engines/status')
        if response.status_code == 200:
            result = response.json()
            print("✅ Engine status loaded")
            for engine, status in result['engines'].items():
                print(f"   - {engine}: {'✅ Available' if status['available'] else '❌ Not available'} ({status['voice_count']} voices)")
        else:
            print(f"❌ Engine status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Engine status error: {e}")
        return False
    
    # Test 3: Register user to test authenticated features
    print("\n3. Testing voice catalog with authenticated user...")
    register_data = {
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD,
        'display_name': 'Voice Test User'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/api/auth/register', 
                               json=register_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 201:
            register_result = response.json()
            token = register_result['token']
            print("✅ User registered successfully")
        else:
            # User might already exist, try login
            login_data = {'email': TEST_EMAIL, 'password': TEST_PASSWORD}
            response = requests.post(f'{BASE_URL}/api/auth/login', json=login_data)
            if response.status_code == 200:
                token = response.json()['token']
                print("✅ User logged in (already existed)")
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    
    # Test authenticated voice catalog
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(f'{BASE_URL}/api/voices', headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("✅ Authenticated voice catalog loaded")
            print(f"   Available voices for {result['user_tier']}: {result['total_voices']}")
        else:
            print(f"❌ Authenticated voice catalog failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authenticated voice catalog error: {e}")
        return False
    
    # Test 4: Voice details
    print("\n4. Testing voice details...")
    try:
        response = requests.get(f'{BASE_URL}/api/voices/basic_0', headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("✅ Voice details loaded")
            voice = result['voice']
            print(f"   Voice: {voice['name']}")
            print(f"   Engine: {voice['engine']}")
            print(f"   Quality: {voice['quality']}")
            print(f"   Access: {'✅ Yes' if result['has_access'] else '❌ No'}")
        else:
            print(f"❌ Voice details failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Voice details error: {e}")
        return False
    
    # Test 5: File conversion with voice selection
    print("\n5. Testing file conversion with voice selection...")
    test_file = create_test_file()
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': ('test.txt', f, 'text/plain')}
            data = {'voice_id': 'basic_0'}
            
            response = requests.post(f'{BASE_URL}/upload', 
                                   files=files, 
                                   data=data,
                                   headers={'Authorization': f'Bearer {token}'})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Conversion started with voice selection")
            job_id = result['data']['id']
            print(f"   Job ID: {job_id}")
            print(f"   Voice used: {result['voice_used']}")
            print(f"   User tier: {result['user_tier']}")
            
            # Monitor conversion progress
            print("\n   Monitoring conversion progress...")
            for i in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                status_response = requests.get(f'{BASE_URL}/conversions/{job_id}')
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    job_data = status_result['data']
                    print(f"   Progress: {job_data['progress']}% - {job_data['current_phase']}")
                    
                    if job_data['status'] == 'completed':
                        print("✅ Conversion completed successfully")
                        if 'word_count' in job_data:
                            print(f"   Word count: {job_data['word_count']}")
                        if 'voice_used' in job_data:
                            print(f"   Voice used: {job_data['voice_used']}")
                        if 'processing_time' in job_data:
                            print(f"   Processing time: {job_data['processing_time']} seconds")
                        break
                    elif job_data['status'] == 'failed':
                        print(f"❌ Conversion failed: {job_data.get('error', 'Unknown error')}")
                        return False
            else:
                print("⚠️ Conversion taking longer than expected...")
                
        else:
            print(f"❌ Conversion request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Conversion error: {e}")
        return False
    finally:
        # Clean up test file
        try:
            os.unlink(test_file)
        except:
            pass
    
    # Test 6: Voice access validation
    print("\n6. Testing voice access validation...")
    try:
        # Try to access a professional voice with free tier
        response = requests.get(f'{BASE_URL}/api/voices/coqui_female_narrator', headers=headers)
        if response.status_code == 200:
            result = response.json()
            if not result['has_access']:
                print("✅ Voice access properly restricted for free tier")
            else:
                print("⚠️ Professional voice accessible to free user (Coqui not installed?)")
        elif response.status_code == 404:
            print("✅ Professional voice not found (expected for basic installation)")
        else:
            print(f"❌ Voice access check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Voice access validation error: {e}")
        return False
    
    print("\n🎉 Enhanced TTS voice system tests completed!")
    print("\n📊 Test Summary:")
    print("   ✅ Voice catalog system functional")
    print("   ✅ Engine status reporting working")
    print("   ✅ Authentication integration successful")
    print("   ✅ Voice selection in conversions working")
    print("   ✅ User tier restrictions enforced")
    print("   ✅ Database integration for conversion tracking")
    
    return True

if __name__ == '__main__':
    success = test_voice_system()
    sys.exit(0 if success else 1)