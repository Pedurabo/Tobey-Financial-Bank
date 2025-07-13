#!/usr/bin/env python3
"""
Quick test to verify customer dashboard fixes
"""

import requests
import time

def test_customer_dashboard():
    """Test customer dashboard access and functionality"""
    base_url = "http://localhost:5000"
    
    print("=== Testing Customer Dashboard Fixes ===\n")
    
    # Test 1: Login as customer
    print("1. Testing customer login...")
    session = requests.Session()
    login_data = {
        'username': 'john_smith',
        'password': 'password123'
    }
    
    response = session.post(f"{base_url}/login", data=login_data)
    if response.status_code == 200:
        print("✅ Customer login successful!")
    else:
        print("❌ Customer login failed!")
        return
    
    # Test 2: Access customer dashboard
    print("\n2. Testing customer dashboard access...")
    response = session.get(f"{base_url}/customer_dashboard")
    if response.status_code == 200:
        print("✅ Customer dashboard accessible!")
        
        # Check for key elements
        content = response.text
        if "Welcome back" in content:
            print("✅ Welcome message present")
        else:
            print("❌ Welcome message missing")
            
        if "Quick Actions" in content:
            print("✅ Quick Actions section present")
        else:
            print("❌ Quick Actions section missing")
            
        if "Transfer Money" in content:
            print("✅ Transfer Money button present")
        else:
            print("❌ Transfer Money button missing")
            
        if "Recent Transactions" in content:
            print("✅ Recent Transactions section present")
        else:
            print("❌ Recent Transactions section missing")
            
    else:
        print(f"❌ Customer dashboard not accessible: {response.status_code}")
    
    # Test 3: Check for template errors
    print("\n3. Checking for template errors...")
    if "TypeError" not in response.text and "NoneType" not in response.text:
        print("✅ No template formatting errors")
    else:
        print("❌ Template formatting errors detected")
    
    print("\n=== Test Complete ===")
    print("If all tests passed, the customer dashboard should be working properly!")
    print("You can now visit http://localhost:5000/login and log in as john_smith")

if __name__ == "__main__":
    try:
        test_customer_dashboard()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}") 