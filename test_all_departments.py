#!/usr/bin/env python3
"""
Comprehensive test script to verify all department dashboards and functionalities
"""

import requests
import json

def test_admin_hr_dashboard():
    """Test HR Admin dashboard"""
    print("\n=== Testing HR Admin Dashboard ===")
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Login as HR admin
    login_data = {
        'username': 'admin_hr',
        'password': 'admin123'
    }
    
    response = session.post(f"{base_url}/login", data=login_data)
    if response.status_code == 200:
        print("✅ HR Admin login successful!")
        
        # Test main dashboard access
        response = session.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ HR Admin dashboard accessible!")
            
            # Check for HR-specific content
            content = response.text.lower()
            if "manage employees" in content or "hr" in content:
                print("✅ HR Admin dashboard shows HR content")
            else:
                print("⚠️ HR Admin dashboard content unclear")
        else:
            print(f"❌ HR Admin dashboard not accessible: {response.status_code}")
    else:
        print(f"❌ HR Admin login failed: {response.status_code}")

def test_accounts_dashboard():
    """Test Accounts dashboard"""
    print("\n=== Testing Accounts Dashboard ===")
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Login as accounts admin
    login_data = {
        'username': 'admin_accounts',
        'password': 'admin123'
    }
    
    response = session.post(f"{base_url}/login", data=login_data)
    if response.status_code == 200:
        print("✅ Accounts Admin login successful!")
        
        # Test accounts dashboard access
        response = session.get(f"{base_url}/accounts_dashboard")
        if response.status_code == 200:
            print("✅ Accounts dashboard accessible!")
            
            # Check for accounts-specific content
            content = response.text.lower()
            if "cash deposit" in content or "teller" in content:
                print("✅ Accounts dashboard shows teller operations")
            else:
                print("⚠️ Accounts dashboard content unclear")
        else:
            print(f"❌ Accounts dashboard not accessible: {response.status_code}")
    else:
        print(f"❌ Accounts Admin login failed: {response.status_code}")

def test_loans_dashboard():
    """Test Loans dashboard"""
    print("\n=== Testing Loans Dashboard ===")
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Login as loans admin
    login_data = {
        'username': 'admin_loans',
        'password': 'admin123'
    }
    
    response = session.post(f"{base_url}/login", data=login_data)
    if response.status_code == 200:
        print("✅ Loans Admin login successful!")
        
        # Test loans dashboard access
        response = session.get(f"{base_url}/loans_dashboard")
        if response.status_code == 200:
            print("✅ Loans dashboard accessible!")
            
            # Check for loans-specific content
            content = response.text.lower()
            if "loan applications" in content or "loans" in content:
                print("✅ Loans dashboard shows loan operations")
            else:
                print("⚠️ Loans dashboard content unclear")
        else:
            print(f"❌ Loans dashboard not accessible: {response.status_code}")
    else:
        print(f"❌ Loans Admin login failed: {response.status_code}")

def test_customer_service_dashboard():
    """Test Customer Service dashboard"""
    print("\n=== Testing Customer Service Dashboard ===")
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Login as customer service admin
    login_data = {
        'username': 'admin_customer_service',
        'password': 'admin123'
    }
    
    response = session.post(f"{base_url}/login", data=login_data)
    if response.status_code == 200:
        print("✅ Customer Service Admin login successful!")
        
        # Test customer service dashboard access
        response = session.get(f"{base_url}/customer_service_dashboard")
        if response.status_code == 200:
            print("✅ Customer Service dashboard accessible!")
            
            # Check for customer service content
            content = response.text.lower()
            if "customer" in content or "support" in content:
                print("✅ Customer Service dashboard shows customer operations")
            else:
                print("⚠️ Customer Service dashboard content unclear")
        else:
            print(f"❌ Customer Service dashboard not accessible: {response.status_code}")
    else:
        print(f"❌ Customer Service Admin login failed: {response.status_code}")

def test_teller_dashboard():
    """Test Teller dashboard"""
    print("\n=== Testing Teller Dashboard ===")
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Login as teller admin
    login_data = {
        'username': 'admin_teller',
        'password': 'admin123'
    }
    
    response = session.post(f"{base_url}/login", data=login_data)
    if response.status_code == 200:
        print("✅ Teller Admin login successful!")
        
        # Test teller dashboard access
        response = session.get(f"{base_url}/teller_dashboard")
        if response.status_code == 200:
            print("✅ Teller dashboard accessible!")
            
            # Check for teller-specific content
            content = response.text.lower()
            if "teller" in content or "cash" in content:
                print("✅ Teller dashboard shows teller operations")
            else:
                print("⚠️ Teller dashboard content unclear")
        else:
            print(f"❌ Teller dashboard not accessible: {response.status_code}")
    else:
        print(f"❌ Teller Admin login failed: {response.status_code}")

def test_audit_dashboard():
    """Test Audit dashboard"""
    print("\n=== Testing Audit Dashboard ===")
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Login as audit admin
    login_data = {
        'username': 'admin_audit',
        'password': 'admin123'
    }
    
    response = session.post(f"{base_url}/login", data=login_data)
    if response.status_code == 200:
        print("✅ Audit Admin login successful!")
        
        # Test audit dashboard access
        response = session.get(f"{base_url}/audit_dashboard")
        if response.status_code == 200:
            print("✅ Audit dashboard accessible!")
            
            # Check for audit-specific content
            content = response.text.lower()
            if "audit" in content or "compliance" in content:
                print("✅ Audit dashboard shows audit operations")
            else:
                print("⚠️ Audit dashboard content unclear")
        else:
            print(f"❌ Audit dashboard not accessible: {response.status_code}")
    else:
        print(f"❌ Audit Admin login failed: {response.status_code}")

def test_risk_dashboard():
    """Test Risk Management dashboard"""
    print("\n=== Testing Risk Management Dashboard ===")
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Login as risk admin
    login_data = {
        'username': 'admin_risk',
        'password': 'admin123'
    }
    
    response = session.post(f"{base_url}/login", data=login_data)
    if response.status_code == 200:
        print("✅ Risk Admin login successful!")
        
        # Test risk dashboard access
        response = session.get(f"{base_url}/risk_dashboard")
        if response.status_code == 200:
            print("✅ Risk dashboard accessible!")
            
            # Check for risk-specific content
            content = response.text.lower()
            if "risk" in content or "assessment" in content:
                print("✅ Risk dashboard shows risk operations")
            else:
                print("⚠️ Risk dashboard content unclear")
        else:
            print(f"❌ Risk dashboard not accessible: {response.status_code}")
    else:
        print(f"❌ Risk Admin login failed: {response.status_code}")

def test_treasury_dashboard():
    """Test Treasury dashboard"""
    print("\n=== Testing Treasury Dashboard ===")
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Login as treasury admin
    login_data = {
        'username': 'admin_treasury',
        'password': 'admin123'
    }
    
    response = session.post(f"{base_url}/login", data=login_data)
    if response.status_code == 200:
        print("✅ Treasury Admin login successful!")
        
        # Test treasury dashboard access
        response = session.get(f"{base_url}/treasury_dashboard")
        if response.status_code == 200:
            print("✅ Treasury dashboard accessible!")
            
            # Check for treasury-specific content
            content = response.text.lower()
            if "treasury" in content or "cashflow" in content:
                print("✅ Treasury dashboard shows treasury operations")
            else:
                print("⚠️ Treasury dashboard content unclear")
        else:
            print(f"❌ Treasury dashboard not accessible: {response.status_code}")
    else:
        print(f"❌ Treasury Admin login failed: {response.status_code}")

def test_customer_dashboard():
    """Test Customer dashboard"""
    print("\n=== Testing Customer Dashboard ===")
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Login as customer
    login_data = {
        'username': 'john_smith',
        'password': 'admin123'
    }
    
    response = session.post(f"{base_url}/login", data=login_data)
    if response.status_code == 200:
        print("✅ Customer login successful!")
        
        # Test customer dashboard access
        response = session.get(f"{base_url}/customer_dashboard")
        if response.status_code == 200:
            print("✅ Customer dashboard accessible!")
            
            # Check for customer-specific content
            content = response.text.lower()
            if "welcome back" in content and "transfer" in content:
                print("✅ Customer dashboard shows customer operations")
            else:
                print("⚠️ Customer dashboard content unclear")
        else:
            print(f"❌ Customer dashboard not accessible: {response.status_code}")
    else:
        print(f"❌ Customer login failed: {response.status_code}")

def test_api_endpoints():
    """Test key API endpoints for each department"""
    print("\n=== Testing API Endpoints ===")
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Test with admin_hr login
    login_data = {'username': 'admin_hr', 'password': 'admin123'}
    session.post(f"{base_url}/login", data=login_data)
    
    # Test employee management API
    response = session.get(f"{base_url}/api/search_employees")
    if response.status_code == 200:
        print("✅ Employee search API working")
    else:
        print(f"❌ Employee search API failed: {response.status_code}")
    
    # Test with admin_loans login
    session = requests.Session()
    login_data = {'username': 'admin_loans', 'password': 'admin123'}
    session.post(f"{base_url}/login", data=login_data)
    
    # Test loan applications API
    response = session.get(f"{base_url}/api/loan_applications")
    if response.status_code == 200:
        print("✅ Loan applications API working")
    else:
        print(f"❌ Loan applications API failed: {response.status_code}")
    
    # Test with admin_teller login
    session = requests.Session()
    login_data = {'username': 'admin_teller', 'password': 'admin123'}
    session.post(f"{base_url}/login", data=login_data)
    
    # Test teller deposit API
    deposit_data = {
        'account_number': '1234567890',
        'amount': 1000.0,
        'currency': 'USD',
        'description': 'Test deposit'
    }
    response = session.post(f"{base_url}/api/teller/deposit", json=deposit_data)
    if response.status_code == 200:
        print("✅ Teller deposit API working")
    else:
        print(f"❌ Teller deposit API failed: {response.status_code}")

if __name__ == "__main__":
    print("=== Comprehensive Department Dashboard Test ===\n")
    
    try:
        test_admin_hr_dashboard()
        test_accounts_dashboard()
        test_loans_dashboard()
        test_customer_service_dashboard()
        test_teller_dashboard()
        test_audit_dashboard()
        test_risk_dashboard()
        test_treasury_dashboard()
        test_customer_dashboard()
        test_api_endpoints()
        
        print("\n" + "="*60)
        print("🎉 All Department Dashboard tests completed!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}") 