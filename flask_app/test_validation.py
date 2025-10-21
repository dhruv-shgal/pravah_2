#!/usr/bin/env python3
"""
Test script for validation functions
"""

import requests
import json

def test_email_validation():
    """Test email validation API"""
    print("🧪 Testing Email Validation")
    print("-" * 30)
    
    test_emails = [
        ("test@gmail.com", True),
        ("invalid-email", False),
        ("test@nonexistentdomain12345.com", False),
        ("user@example.com", False),  # Might be valid format but domain check
        ("", False)
    ]
    
    for email, expected in test_emails:
        try:
            response = requests.post('http://localhost:5000/api/validate-email', 
                                   json={'email': email})
            result = response.json()
            status = "✅" if result['valid'] == expected else "❌"
            print(f"{status} {email}: {result['message']}")
        except Exception as e:
            print(f"❌ {email}: Error - {e}")

def test_password_validation():
    """Test password validation API"""
    print("\n🧪 Testing Password Validation")
    print("-" * 30)
    
    test_passwords = [
        ("Password123!", True),
        ("password", False),  # No uppercase, number, special char
        ("PASSWORD123!", False),  # No lowercase
        ("Password!", False),  # No number
        ("Password123", False),  # No special char
        ("Pass1!", False),  # Too short
        ("", False)
    ]
    
    for password, expected in test_passwords:
        try:
            response = requests.post('http://localhost:5000/api/validate-password', 
                                   json={'password': password})
            result = response.json()
            status = "✅" if result['valid'] == expected else "❌"
            print(f"{status} '{password}': {result['message']}")
        except Exception as e:
            print(f"❌ '{password}': Error - {e}")

def test_username_validation():
    """Test username validation API"""
    print("\n🧪 Testing Username Validation")
    print("-" * 30)
    
    test_usernames = [
        ("newuser123", True),
        ("ab", False),  # Too short
        ("", False),  # Empty
        ("validuser", True)
    ]
    
    for username, expected in test_usernames:
        try:
            response = requests.post('http://localhost:5000/api/validate-username', 
                                   json={'username': username})
            result = response.json()
            status = "✅" if result['valid'] == expected else "❌"
            print(f"{status} '{username}': {result['message']}")
        except Exception as e:
            print(f"❌ '{username}': Error - {e}")

def test_user_id_validation():
    """Test user ID validation API"""
    print("\n🧪 Testing User ID Validation")
    print("-" * 30)
    
    test_user_ids = [
        ("new_user_123", True),
        ("ab", False),  # Too short
        ("", False),  # Empty
        ("valid_user_id", True)
    ]
    
    for user_id, expected in test_user_ids:
        try:
            response = requests.post('http://localhost:5000/api/validate-user-id', 
                                   json={'user_id': user_id})
            result = response.json()
            status = "✅" if result['valid'] == expected else "❌"
            print(f"{status} '{user_id}': {result['message']}")
        except Exception as e:
            print(f"❌ '{user_id}': Error - {e}")

def test_duplicate_prevention():
    """Test that duplicates are prevented"""
    print("\n🧪 Testing Duplicate Prevention")
    print("-" * 30)
    
    # This would need existing users to test properly
    # For now, just test the API endpoints work
    
    try:
        response = requests.get('http://localhost:5000/api/users')
        if response.status_code == 200:
            users_data = response.json()
            print(f"✅ Found {users_data['count']} existing users")
            
            if users_data['count'] > 0:
                # Test with existing user data
                first_user = users_data['users'][0]
                
                # Test duplicate email
                response = requests.post('http://localhost:5000/api/validate-email', 
                                       json={'email': first_user['email']})
                result = response.json()
                if not result['valid']:
                    print(f"✅ Duplicate email correctly rejected: {first_user['email']}")
                else:
                    print(f"❌ Duplicate email not detected: {first_user['email']}")
                
                # Test duplicate username
                response = requests.post('http://localhost:5000/api/validate-username', 
                                       json={'username': first_user['username']})
                result = response.json()
                if not result['valid']:
                    print(f"✅ Duplicate username correctly rejected: {first_user['username']}")
                else:
                    print(f"❌ Duplicate username not detected: {first_user['username']}")
        else:
            print("❌ Could not fetch users list")
            
    except Exception as e:
        print(f"❌ Error testing duplicates: {e}")

if __name__ == "__main__":
    print("🔍 PRAVAH Validation Testing")
    print("=" * 40)
    print("Make sure Flask app is running on port 5000")
    print()
    
    try:
        # Test if server is running
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Flask server is running")
            print()
            
            test_email_validation()
            test_password_validation()
            test_username_validation()
            test_user_id_validation()
            test_duplicate_prevention()
            
            print("\n✅ Validation testing complete!")
            
        else:
            print("❌ Flask server not responding properly")
            
    except requests.exceptions.ConnectionError:
        print("❌ Flask server not running on port 5000")
        print("Please start: cd flask_app && python app.py")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n📋 Validation Rules Summary:")
    print("📧 Email: Valid format + domain exists + unique")
    print("🔒 Password: 8+ chars + uppercase + lowercase + number + special char")
    print("👤 Username: 3+ chars + unique")
    print("🆔 User ID: 3+ chars + unique")