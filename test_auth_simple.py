#!/usr/bin/env python3
"""
Simple authentication test for Tobey Finance Bank
"""

import requests
import json

def test_login():
    """Test login functionality"""
    base_url = "http://localhost:5000"
    
    # Test login page
    print("Testing login page...")
    response = requests.get(f"{base_url}/login")
    print(f"Login page status: {response.status_code}")
    
    # Test login with HR admin credentials
    print("\nTesting login with HR admin credentials...")
    login_data = {
        'username': 'admin_hr',
        'password': 'admin123'
    }
    
    session = requests.Session()
    response = session.post(f"{base_url}/login", data=login_data)
    print(f"Login response status: {response.status_code}")
    
    # Test dashboard access
    print("\nTesting dashboard access...")
    response = session.get(f"{base_url}/")
    print(f"Dashboard status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Successfully logged in and accessed dashboard")
        return True
    else:
        print("❌ Failed to access dashboard")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    base_url = "http://localhost:5000"
    
    # Create session and login
    session = requests.Session()
    login_data = {
        'username': 'admin_hr',
        'password': 'admin123'
    }
    session.post(f"{base_url}/login", data=login_data)
    
    # Test add employee API
    print("\nTesting add employee API...")
    test_employee = {
        'username': 'test_user',
        'password': 'test123',
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com',
        'department': 'ACCOUNTS',
        'role': 'STAFF'
    }
    
    response = session.post(
        f"{base_url}/api/add_employee",
        json=test_employee,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Add employee API status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"API response: {result}")
    else:
        print(f"API error: {response.text}")

if __name__ == "__main__":
    print("=== Tobey Finance Bank Authentication Test ===\n")
    
    try:
        # Test login
        if test_login():
            # Test API endpoints
            test_api_endpoints()
        else:
            print("❌ Login failed, skipping API tests")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}") 