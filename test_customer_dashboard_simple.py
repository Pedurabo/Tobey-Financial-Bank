#!/usr/bin/env python3
"""
Simple test for customer dashboard
"""

import requests
import time

def test_customer_dashboard():
    """Test customer dashboard access"""
    base_url = "http://localhost:5000"
    
    print("=== Testing Customer Dashboard ===\n")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/login")
        print(f"✅ Server is running (Status: {response.status_code})")
    except:
        print("❌ Server is not running")
        return
    
    # Test 2: Login as customer
    print("\n2. Testing customer login...")
    session = requests.Session()
    login_data = {
        'username': 'john_smith',
        'password': 'password123'
    }
    
    response = session.post(f"{base_url}/login", data=login_data)
    print(f"Login response: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Login successful!")
        
        # Test 3: Access customer dashboard
        print("\n3. Testing customer dashboard access...")
        response = session.get(f"{base_url}/customer_dashboard")
        print(f"Dashboard status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Customer dashboard accessible!")
            print(f"Response length: {len(response.text)}")
            
            # Check for key content
            if "Welcome back" in response.text:
                print("✅ Welcome message found")
            else:
                print("❌ Welcome message missing")
                
            if "Quick Actions" in response.text:
                print("✅ Quick Actions section found")
            else:
                print("❌ Quick Actions section missing")
                
            if "Transfer Money" in response.text:
                print("✅ Transfer Money button found")
            else:
                print("❌ Transfer Money button missing")
                
        else:
            print("❌ Customer dashboard not accessible")
            print(f"Response: {response.text[:500]}")
    else:
        print("❌ Login failed!")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_customer_dashboard() 