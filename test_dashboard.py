#!/usr/bin/env python3
"""
Test script to check dashboard functionality
"""

import requests
import json

def test_dashboard():
    """Test dashboard functionality"""
    base_url = "http://localhost:5000"
    
    # Create session and login
    session = requests.Session()
    login_data = {
        'username': 'admin_hr',
        'password': 'admin123'
    }
    
    print("Testing login...")
    response = session.post(f"{base_url}/login", data=login_data)
    print(f"Login response: {response.status_code}")
    
    if response.status_code == 200:
        print("Login successful!")
        
        # Test dashboard access
        print("\nTesting dashboard access...")
        response = session.get(f"{base_url}/")
        print(f"Dashboard status: {response.status_code}")
        print(f"Response length: {len(response.text)}")
        
        if response.status_code == 200:
            print("✅ Dashboard accessible!")
            
            # Check if dashboard contains expected content
            if "Tobey Finance Bank" in response.text:
                print("✅ Dashboard contains bank branding")
            else:
                print("❌ Dashboard missing bank branding")
                
            if "Total Employees" in response.text:
                print("✅ Dashboard contains employee statistics")
            else:
                print("❌ Dashboard missing employee statistics")
                
            if "HR Management" in response.text:
                print("✅ Dashboard contains HR management section")
            else:
                print("❌ Dashboard missing HR management section")
                
        else:
            print("❌ Dashboard not accessible")
            print(f"Response: {response.text[:200]}")
    else:
        print("❌ Login failed!")
        print(f"Response: {response.text}")

def test_department_access():
    """Test department-specific dashboard access"""
    base_url = "http://localhost:5000"
    
    # Test different department logins
    departments = [
        ('admin_hr', 'Admin/HR Department'),
        ('admin_accounts', 'Accounts Department'),
        ('admin_loans', 'Loans Department'),
        ('admin_customer_service', 'Customer Service Department')
    ]
    
    print("\n=== Testing Department Access ===")
    
    for username, department in departments:
        print(f"\nTesting {department} access...")
        session = requests.Session()
        login_data = {'username': username, 'password': 'admin123'}
        
        response = session.post(f"{base_url}/login", data=login_data)
        if response.status_code == 200:
            dashboard_response = session.get(f"{base_url}/")
            if dashboard_response.status_code == 200:
                print(f"✅ {department}: Dashboard accessible")
            else:
                print(f"❌ {department}: Dashboard not accessible")
        else:
            print(f"❌ {department}: Login failed")

if __name__ == "__main__":
    print("=== Dashboard Functionality Test ===\n")
    
    try:
        test_dashboard()
        test_department_access()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}") 