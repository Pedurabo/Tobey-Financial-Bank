#!/usr/bin/env python3
"""
Test script to check API endpoints
"""

import requests
import json

def test_api_endpoints():
    """Test the API endpoints"""
    base_url = "http://localhost:5000"
    
    # Test login first
    session = requests.Session()
    
    # Login
    login_data = {
        'username': 'admin_hr',
        'password': 'admin123'
    }
    
    print("Testing login...")
    response = session.post(f"{base_url}/login", data=login_data)
    print(f"Login response: {response.status_code}")
    
    if response.status_code == 200:
        print("Login successful!")
        
        # Test add employee API
        print("\nTesting add employee API...")
        employee_data = {
            'username': 'test_employee',
            'password': 'test123',
            'first_name': 'Test',
            'last_name': 'Employee',
            'email': 'test.employee@tobeyfinance.com',
            'department': 'ACCOUNTS',
            'role': 'STAFF'
        }
        
        response = session.post(
            f"{base_url}/api/add_employee",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(employee_data)
        )
        
        print(f"Add employee response: {response.status_code}")
        print(f"Response content: {response.text}")
        
        # Test search employees API
        print("\nTesting search employees API...")
        response = session.get(f"{base_url}/api/search_employees?term=test")
        print(f"Search response: {response.status_code}")
        print(f"Response content: {response.text}")
        
    else:
        print("Login failed!")

if __name__ == "__main__":
    test_api_endpoints() 