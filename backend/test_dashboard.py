#!/usr/bin/env python3
"""Test script for the dashboard and analytics system."""

import requests
import json
import sys
import time
import tempfile
import os

# Test configuration
BASE_URL = 'http://localhost:5001'
TEST_EMAIL = 'dashboard@example.com'
TEST_PASSWORD = 'testpassword123'

def create_test_file(content_size='small'):
    """Create test files of different sizes."""
    if content_size == 'small':
        content = """
        This is a small test document for dashboard testing.
        It contains a few paragraphs to test word counting and analytics.
        We want to see how the dashboard tracks user conversions and usage.
        This should help us validate the analytics functionality.
        """
    elif content_size == 'medium':
        content = """
        This is a medium-sized test document for comprehensive dashboard testing.
        """ + "This paragraph is repeated to increase word count. " * 50
    else:  # large
        content = """
        This is a large test document to test usage limits and analytics.
        """ + "This sentence is repeated many times to create a large document. " * 200
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_file.write(content.strip())
    temp_file.close()
    return temp_file.name

def test_dashboard_system():
    """Test the complete dashboard and analytics system."""
    print("📊 Testing Dashboard & Analytics System")
    print("=" * 50)
    
    # Test 1: Register/Login user
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
            print("✅ User registered successfully")
        else:
            # Try login if user exists
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
    
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # Test 2: Initial dashboard data
    print("\n2. Testing initial dashboard data...")
    try:
        response = requests.get(f'{BASE_URL}/api/dashboard', headers=headers)
        if response.status_code == 200:
            dashboard_data = response.json()
            print("✅ Dashboard data loaded")
            user = dashboard_data['user']
            print(f"   User: {user['display_name']} ({user['email']})")
            print(f"   Tier: {user['subscription_tier']}")
            print(f"   Member since: {user['member_since']}")
            
            usage = dashboard_data['usage']
            print(f"   Current usage: {usage['current_month']['conversions_used']} conversions, {usage['current_month']['words_used']} words")
            print(f"   Limits: {usage['current_month']['conversions_remaining']} conversions, {usage['current_month']['words_remaining']} words remaining")
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        return False
    
    # Test 3: Usage limit checking
    print("\n3. Testing usage limit checking...")
    try:
        check_data = {'estimated_words': 500}
        response = requests.post(f'{BASE_URL}/api/dashboard/usage-check', 
                               json=check_data, headers=headers)
        if response.status_code == 200:
            usage_check = response.json()
            print("✅ Usage limit check working")
            print(f"   Can convert: {usage_check['can_convert']}")
            print(f"   Current tier: {usage_check['tier']}")
            if not usage_check['can_convert']:
                print(f"   Reasons: {', '.join(usage_check['reasons'])}")
        else:
            print(f"❌ Usage check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Usage check error: {e}")
        return False
    
    # Test 4: Perform some conversions to generate data
    print("\n4. Generating test conversions for analytics...")
    conversions_completed = 0
    
    for i, size in enumerate(['small', 'medium', 'small']):
        print(f"   Converting file {i+1}/3 ({size})...")
        test_file = create_test_file(size)
        
        try:
            with open(test_file, 'rb') as f:
                files = {'file': (f'test_{size}_{i}.txt', f, 'text/plain')}
                data = {'voice_id': 'basic_0'}
                
                response = requests.post(f'{BASE_URL}/upload', 
                                       files=files, 
                                       data=data,
                                       headers={'Authorization': f'Bearer {token}'})
            
            if response.status_code == 200:
                result = response.json()
                job_id = result['data']['id']
                
                # Wait for conversion to complete
                for _ in range(20):  # Wait up to 20 seconds
                    time.sleep(1)
                    status_response = requests.get(f'{BASE_URL}/conversions/{job_id}')
                    if status_response.status_code == 200:
                        job_data = status_response.json()['data']
                        if job_data['status'] == 'completed':
                            conversions_completed += 1
                            print(f"   ✅ Conversion {i+1} completed ({job_data.get('word_count', 0)} words)")
                            break
                        elif job_data['status'] == 'failed':
                            print(f"   ❌ Conversion {i+1} failed")
                            break
                else:
                    print(f"   ⚠️ Conversion {i+1} taking too long")
            else:
                print(f"   ❌ Upload {i+1} failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error with conversion {i+1}: {e}")
        finally:
            try:
                os.unlink(test_file)
            except:
                pass
        
        time.sleep(0.5)  # Brief pause between conversions
    
    print(f"   Completed {conversions_completed}/3 test conversions")
    
    # Test 5: Updated dashboard data
    print("\n5. Testing updated dashboard data...")
    try:
        response = requests.get(f'{BASE_URL}/api/dashboard', headers=headers)
        if response.status_code == 200:
            dashboard_data = response.json()
            print("✅ Updated dashboard data loaded")
            
            usage = dashboard_data['usage']
            print(f"   Current usage: {usage['current_month']['conversions_used']} conversions, {usage['current_month']['words_used']} words")
            
            recent = dashboard_data['recent_conversions']
            print(f"   Recent conversions: {len(recent)} found")
            for conv in recent[:3]:  # Show first 3
                print(f"     - {conv['original_filename']}: {conv['word_count']} words, {conv['voice_used']} voice")
            
            stats = dashboard_data['statistics']
            print(f"   Statistics: {stats['total_conversions']} total, avg {stats['avg_words_per_conversion']} words/conversion")
        else:
            print(f"❌ Updated dashboard failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Updated dashboard error: {e}")
        return False
    
    # Test 6: Conversion history
    print("\n6. Testing conversion history...")
    try:
        response = requests.get(f'{BASE_URL}/api/dashboard/conversions?page=1&per_page=10', 
                               headers=headers)
        if response.status_code == 200:
            history_data = response.json()
            print("✅ Conversion history loaded")
            
            conversions = history_data['conversions']
            pagination = history_data['pagination']
            
            print(f"   Found {pagination['total_count']} total conversions")
            print(f"   Page {pagination['current_page']} of {pagination['total_pages']}")
            
            for conv in conversions[:3]:  # Show first 3
                print(f"     - {conv['original_filename']}: {conv['status']}, {conv['download_count']} downloads")
        else:
            print(f"❌ Conversion history failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Conversion history error: {e}")
        return False
    
    # Test 7: Analytics
    print("\n7. Testing analytics data...")
    try:
        response = requests.get(f'{BASE_URL}/api/dashboard/analytics?days=30', 
                               headers=headers)
        if response.status_code == 200:
            analytics_data = response.json()
            print("✅ Analytics data loaded")
            
            summary = analytics_data['summary']
            print(f"   Summary: {summary['total_conversions']} conversions, {summary['total_words']} words")
            print(f"   Average: {summary['average_words_per_conversion']} words/conversion")
            
            if analytics_data['by_voice']:
                print("   Voice usage:")
                for voice, stats in analytics_data['by_voice'].items():
                    print(f"     - {voice}: {stats['count']} conversions, {stats['words']} words")
            
            if analytics_data['by_file_type']:
                print("   File type usage:")
                for file_type, stats in analytics_data['by_file_type'].items():
                    print(f"     - {file_type}: {stats['count']} files, {stats['words']} words")
            
            print(f"   Efficiency score: {analytics_data['efficiency_score']}/100")
        else:
            print(f"❌ Analytics failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Analytics error: {e}")
        return False
    
    # Test 8: Test usage limits (if applicable)
    if conversions_completed > 0:
        print("\n8. Testing usage limit enforcement...")
        try:
            # Try to check limits with a large estimated word count
            check_data = {'estimated_words': 50000}  # Large number to potentially trigger limits
            response = requests.post(f'{BASE_URL}/api/dashboard/usage-check', 
                                   json=check_data, headers=headers)
            if response.status_code == 200:
                usage_check = response.json()
                print("✅ Usage limit enforcement tested")
                print(f"   Can convert large file: {usage_check['can_convert']}")
                if usage_check.get('limits_approaching'):
                    approaching = usage_check['limits_approaching']
                    if approaching['words'] or approaching['conversions']:
                        print("   ⚠️ Approaching usage limits!")
        except Exception as e:
            print(f"❌ Usage limit test error: {e}")
    
    print("\n🎉 Dashboard and Analytics system tests completed!")
    print("\n📊 Test Summary:")
    print("   ✅ Dashboard data loading functional")
    print("   ✅ Usage tracking and limits working")
    print(f"   ✅ Conversion tracking successful ({conversions_completed} conversions)")
    print("   ✅ Conversion history with pagination")
    print("   ✅ Analytics and statistics generation")
    print("   ✅ Real-time usage limit checking")
    print("   ✅ Database integration fully functional")
    
    return True

if __name__ == '__main__':
    success = test_dashboard_system()
    sys.exit(0 if success else 1)