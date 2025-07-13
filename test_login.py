#!/usr/bin/env python3
"""
Test script to debug login issues
"""

import requests
import json

def test_login():
    """Test login functionality"""
    base_url = "http://localhost:5000"
    
    # Test if server is running
    try:
        response = requests.get(f"{base_url}/login", timeout=5)
        print(f"Server status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Flask app is running.")
        return False
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return False
    
    # Test login with HR admin credentials
    print("\nTesting login with HR admin credentials...")
    login_data = {
        'username': 'admin_hr',
        'password': 'admin123'
    }
    
    session = requests.Session()
    try:
        response = session.post(f"{base_url}/login", data=login_data, timeout=10)
        print(f"Login response status: {response.status_code}")
        print(f"Response URL: {response.url}")
        
        if response.status_code == 200:
            if "dashboard" in response.url or "Logged in successfully" in response.text:
                print("✅ Login successful!")
                return True
            else:
                print("❌ Login failed - redirected to login page")
                print(f"Response text preview: {response.text[:200]}...")
                return False
        else:
            print(f"❌ Login failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return False

def test_other_credentials():
    """Test other admin credentials"""
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    test_credentials = [
        ('admin_accounts', 'admin123'),
        ('admin_loans', 'admin123'),
        ('admin_customer_service', 'admin123'),
        ('admin_teller', 'admin123'),
        ('admin_audit', 'admin123'),
        ('admin_it', 'admin123'),
        ('admin_risk', 'admin123'),
        ('admin_marketing', 'admin123'),
        ('admin_treasury', 'admin123'),
    ]
    
    print("\nTesting other admin credentials...")
    for username, password in test_credentials:
        try:
            response = session.post(f"{base_url}/login", data={'username': username, 'password': password}, timeout=5)
            if response.status_code == 200 and ("dashboard" in response.url or "Logged in successfully" in response.text):
                print(f"✅ {username}: Login successful")
            else:
                print(f"❌ {username}: Login failed")
        except Exception as e:
            print(f"❌ {username}: Error - {e}")

if __name__ == "__main__":
    print("=== Tobey Finance Bank Login Test ===\n")
    
    if test_login():
        print("\n✅ Login test passed!")
    else:
        print("\n❌ Login test failed!")
        test_other_credentials() 