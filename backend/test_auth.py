#!/usr/bin/env python3
"""Simple test script for the authentication system."""

import requests
import json
import sys

# Test configuration
BASE_URL = 'http://localhost:5001'
TEST_EMAIL = 'test@example.com'
TEST_PASSWORD = 'testpassword123'
TEST_DISPLAY_NAME = 'Test User'

def test_auth_flow():
    """Test the complete authentication flow."""
    print("Testing eBookVoice AI Authentication System")
    print("=" * 50)
    
    # Test health check
    print("1. Testing health check...")
    try:
        response = requests.get(f'{BASE_URL}/health')
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print("❌ Health check failed")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Please start the backend with: python app.py")
        return False
    
    # Test registration
    print("\n2. Testing user registration...")
    register_data = {
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD,
        'display_name': TEST_DISPLAY_NAME
    }
    
    response = requests.post(f'{BASE_URL}/api/auth/register', 
                           json=register_data,
                           headers={'Content-Type': 'application/json'})
    
    if response.status_code == 201:
        register_result = response.json()
        if register_result['success']:
            print("✅ Registration successful")
            token = register_result['token']
            user_data = register_result['user']
            print(f"   User ID: {user_data['id']}")
            print(f"   Email: {user_data['email']}")
            print(f"   Display Name: {user_data['display_name']}")
            print(f"   Tier: {user_data['subscription_tier']}")
        else:
            print(f"❌ Registration failed: {register_result['error']}")
            return False
    else:
        print(f"❌ Registration failed with status {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    # Test login
    print("\n3. Testing user login...")
    login_data = {
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD
    }
    
    response = requests.post(f'{BASE_URL}/api/auth/login',
                           json=login_data,
                           headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200:
        login_result = response.json()
        if login_result['success']:
            print("✅ Login successful")
            token = login_result['token']
            print(f"   Token received (length: {len(token)})")
        else:
            print(f"❌ Login failed: {login_result['error']}")
            return False
    else:
        print(f"❌ Login failed with status {response.status_code}")
        return False
    
    # Test authenticated endpoint
    print("\n4. Testing authenticated endpoint...")
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(f'{BASE_URL}/api/auth/me', headers=headers)
    
    if response.status_code == 200:
        me_result = response.json()
        if me_result['success']:
            print("✅ Authenticated request successful")
            user = me_result['user']
            print(f"   Current user: {user['email']}")
        else:
            print(f"❌ Authenticated request failed: {me_result['error']}")
            return False
    else:
        print(f"❌ Authenticated request failed with status {response.status_code}")
        return False
    
    # Test invalid token
    print("\n5. Testing invalid token...")
    invalid_headers = {
        'Authorization': 'Bearer invalid-token',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(f'{BASE_URL}/api/auth/me', headers=invalid_headers)
    
    if response.status_code == 401:
        print("✅ Invalid token correctly rejected")
    else:
        print(f"❌ Invalid token not properly rejected (status: {response.status_code})")
        return False
    
    # Test conversion endpoint with auth
    print("\n6. Testing conversion endpoint with authentication...")
    response = requests.get(f'{BASE_URL}/conversions', headers=headers)
    
    if response.status_code == 200:
        conversions_result = response.json()
        if conversions_result['success']:
            print("✅ Authenticated conversion endpoint works")
            if 'user' in conversions_result:
                print(f"   User context included: {conversions_result['user']['email']}")
        else:
            print(f"❌ Conversion endpoint failed: {conversions_result['error']}")
            return False
    else:
        print(f"❌ Conversion endpoint failed with status {response.status_code}")
        return False
    
    print("\n🎉 All authentication tests passed!")
    print("\n📊 Summary:")
    print(f"   ✅ User registered: {TEST_EMAIL}")
    print(f"   ✅ JWT token generated and validated")
    print(f"   ✅ Authentication middleware working")
    print(f"   ✅ Database integration successful")
    return True

if __name__ == '__main__':
    success = test_auth_flow()
    sys.exit(0 if success else 1)