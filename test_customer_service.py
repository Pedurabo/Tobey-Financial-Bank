#!/usr/bin/env python3
"""
Test script to check customer service dashboard functionality
"""

import requests
import json

def test_customer_service_dashboard():
    """Test customer service dashboard functionality"""
    base_url = "http://localhost:5000"
    
    # Create session and login as customer service admin
    session = requests.Session()
    login_data = {
        'username': 'admin_customer_service',
        'password': 'admin123'
    }
    
    print("Testing customer service login...")
    response = session.post(f"{base_url}/login", data=login_data)
    print(f"Login response: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Login successful!")
        
        # Test main dashboard access
        print("\nTesting main dashboard access...")
        response = session.get(f"{base_url}/")
        print(f"Dashboard status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Main dashboard accessible!")
            
            # Check if "Manage Customers" button is present
            if "Manage Customers" in response.text:
                print("✅ 'Manage Customers' button found in dashboard")
            else:
                print("❌ 'Manage Customers' button not found")
                
        else:
            print("❌ Main dashboard not accessible")
            
        # Test customer service dashboard access
        print("\nTesting customer service dashboard access...")
        response = session.get(f"{base_url}/customer_service_dashboard")
        print(f"Customer service dashboard status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Customer service dashboard accessible!")
            
            # Check if customer service dashboard contains expected content
            if "Customer Service Dashboard" in response.text:
                print("✅ Customer service dashboard contains correct title")
            else:
                print("❌ Customer service dashboard missing title")
                
            if "Customer Registry" in response.text:
                print("✅ Customer service dashboard contains customer registry")
            else:
                print("❌ Customer service dashboard missing customer registry")
                
        else:
            print("❌ Customer service dashboard not accessible")
            print(f"Response: {response.text[:200]}")
    else:
        print("❌ Login failed!")
        print(f"Response: {response.text}")

def test_customer_api():
    """Test customer API endpoints"""
    base_url = "http://localhost:5000"
    
    # Create session and login
    session = requests.Session()
    login_data = {
        'username': 'admin_customer_service',
        'password': 'admin123'
    }
    
    print("\n=== Testing Customer API ===")
    response = session.post(f"{base_url}/login", data=login_data)
    
    if response.status_code == 200:
        # Test GET customers API
        print("\nTesting GET /api/customers...")
        response = session.get(f"{base_url}/api/customers")
        print(f"API status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ API returned {len(data.get('customers', []))} customers")
            else:
                print("❌ API returned error")
        else:
            print("❌ API request failed")
    else:
        print("❌ Login failed for API test")

if __name__ == "__main__":
    print("=== Customer Service Dashboard Test ===\n")
    
    try:
        test_customer_service_dashboard()
        test_customer_api()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}") 