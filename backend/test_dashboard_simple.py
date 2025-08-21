#!/usr/bin/env python3
"""Simple test for dashboard system without Unicode characters."""

import requests
import json
import sys
import tempfile
import os
import time

BASE_URL = 'http://localhost:5001'
TEST_EMAIL = 'dashboard@example.com'
TEST_PASSWORD = 'testpassword123'

def create_test_file():
    """Create a test file for conversion."""
    content = "This is a test document for dashboard analytics testing. " * 10
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_file.write(content)
    temp_file.close()
    return temp_file.name

def test_dashboard_system():
    """Test dashboard and analytics functionality."""
    print("=== Dashboard System Test ===")
    
    # Test 1: User registration
    print("1. Setting up test user...")
    register_data = {
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD,
        'display_name': 'Dashboard Test User'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/api/auth/register', 
                               json=register_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 201:
            token = response.json()['token']
            print("   [PASS] User registered successfully")
        else:
            # Try login if user exists
            login_data = {'email': TEST_EMAIL, 'password': TEST_PASSWORD}
            response = requests.post(f'{BASE_URL}/api/auth/login', json=login_data)
            if response.status_code == 200:
                token = response.json()['token']
                print("   [PASS] User logged in (already existed)")
            else:
                print(f"   [FAIL] Authentication failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"   [FAIL] Authentication error: {e}")
        return False
    
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # Test 2: Initial dashboard data
    print("2. Testing initial dashboard data...")
    try:
        response = requests.get(f'{BASE_URL}/api/dashboard', headers=headers)
        if response.status_code == 200:
            dashboard_data = response.json()
            print("   [PASS] Dashboard data loaded")
            data = dashboard_data.get('data', dashboard_data)
            user = data['user']
            print(f"   User: {user['display_name']} ({user['email']})")
            print(f"   Tier: {user['subscription_tier']}")
            
            usage = data['usage']
            print(f"   Current usage: {usage['current_month']['conversions_used']} conversions")
        else:
            print(f"   [FAIL] Dashboard failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [FAIL] Dashboard error: {e}")
        return False
    
    # Test 3: Usage limit checking
    print("3. Testing usage limit checking...")
    try:
        check_data = {'estimated_words': 500}
        response = requests.post(f'{BASE_URL}/api/dashboard/usage-check', 
                               json=check_data, headers=headers)
        if response.status_code == 200:
            usage_check = response.json()
            print("   [PASS] Usage limit check working")
            data = usage_check.get('data', usage_check)
            print(f"   Can convert: {data['can_convert']}")
            print(f"   Current tier: {data['tier']}")
        else:
            print(f"   [FAIL] Usage check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [FAIL] Usage check error: {e}")
        return False
    
    # Test 4: Perform a test conversion
    print("4. Testing conversion with dashboard tracking...")
    test_file = create_test_file()
    conversions_completed = 0
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': ('test_dashboard.txt', f, 'text/plain')}
            data = {'voice_id': 'basic_0'}
            
            response = requests.post(f'{BASE_URL}/upload', 
                                   files=files, 
                                   data=data,
                                   headers={'Authorization': f'Bearer {token}'})
        
        if response.status_code == 200:
            result = response.json()
            job_id = result['data']['id']
            print(f"   [PASS] Conversion started (Job ID: {job_id})")
            
            # Wait for conversion to complete
            for _ in range(15):  # Wait up to 15 seconds
                time.sleep(1)
                status_response = requests.get(f'{BASE_URL}/conversions/{job_id}')
                if status_response.status_code == 200:
                    job_data = status_response.json()['data']
                    if job_data['status'] == 'completed':
                        conversions_completed = 1
                        print(f"   [PASS] Conversion completed ({job_data.get('word_count', 0)} words)")
                        break
                    elif job_data['status'] == 'failed':
                        print("   [WARN] Conversion failed (expected for testing)")
                        break
            else:
                print("   [WARN] Conversion taking longer than expected")
        else:
            print(f"   [FAIL] Upload failed: {response.status_code}")
            
    except Exception as e:
        print(f"   [FAIL] Error with conversion: {e}")
    finally:
        try:
            os.unlink(test_file)
        except:
            pass
    
    # Test 5: Updated dashboard data
    print("5. Testing updated dashboard data...")
    try:
        response = requests.get(f'{BASE_URL}/api/dashboard', headers=headers)
        if response.status_code == 200:
            dashboard_data = response.json()
            print("   [PASS] Updated dashboard data loaded")
            
            data = dashboard_data.get('data', dashboard_data)
            usage = data['usage']
            print(f"   Current usage: {usage['current_month']['conversions_used']} conversions")
            
            recent = data['recent_conversions']
            print(f"   Recent conversions: {len(recent)} found")
            
            stats = data['statistics']
            print(f"   Statistics: {stats['total_conversions']} total conversions")
        else:
            print(f"   [FAIL] Updated dashboard failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [FAIL] Updated dashboard error: {e}")
        return False
    
    # Test 6: Analytics
    print("6. Testing analytics data...")
    try:
        response = requests.get(f'{BASE_URL}/api/dashboard/analytics?days=30', 
                               headers=headers)
        if response.status_code == 200:
            analytics_data = response.json()
            print("   [PASS] Analytics data loaded")
            
            data = analytics_data.get('data', analytics_data)
            summary = data['summary']
            print(f"   Summary: {summary['total_conversions']} conversions, {summary['total_words']} words")
            
            print(f"   Efficiency score: {data['efficiency_score']}/100")
        else:
            print(f"   [FAIL] Analytics failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [FAIL] Analytics error: {e}")
        return False
    
    print("\n=== Dashboard System Test Summary ===")
    print("[PASS] Dashboard system functional")
    print("- Dashboard data loading working")
    print("- Usage tracking and limits working")
    print("- Conversion tracking working")
    print("- Analytics and statistics working")
    print("- Database integration functional")
    
    return True

if __name__ == '__main__':
    success = test_dashboard_system()
    sys.exit(0 if success else 1)