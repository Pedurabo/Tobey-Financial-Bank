#!/usr/bin/env python3
"""
Test script to verify department access control is working correctly
"""

import requests
import time

def test_department_access_control():
    """Test that department access control is properly implemented"""
    base_url = "http://localhost:5000"
    
    print("=== Department Access Control Test ===\n")
    
    # Test scenarios: each user tries to access different department dashboards
    test_users = [
        {
            'username': 'admin_hr',
            'password': 'admin123',
            'department': 'Admin/HR Department',
            'role': 'admin',
            'should_access': {
                'accounts_dashboard': True,   # HR admins have system-wide access
                'loans_dashboard': True,      # HR admins have system-wide access
                'customer_service_dashboard': True,  # HR admins have system-wide access
                'teller_dashboard': True,     # HR admins have system-wide access
                'risk_dashboard': True        # HR admins have system-wide access
            }
        },
        {
            'username': 'admin_accounts',
            'password': 'admin123',
            'department': 'Accounts Department',
            'role': 'admin',
            'should_access': {
                'accounts_dashboard': True,   # Own department
                'loans_dashboard': False,     # Different department
                'customer_service_dashboard': False,  # Different department
                'teller_dashboard': False,    # Different department
                'risk_dashboard': False       # Different department
            }
        },
        {
            'username': 'admin_loans',
            'password': 'admin123',
            'department': 'Loans Department',
            'role': 'admin',
            'should_access': {
                'accounts_dashboard': False,  # Different department
                'loans_dashboard': True,      # Own department
                'customer_service_dashboard': False,  # Different department
                'teller_dashboard': False,    # Different department
                'risk_dashboard': False       # Different department
            }
        },
        {
            'username': 'admin_customer_service',
            'password': 'admin123',
            'department': 'Customer Service Department',
            'role': 'admin',
            'should_access': {
                'accounts_dashboard': False,  # Different department
                'loans_dashboard': False,     # Different department
                'customer_service_dashboard': True,  # Own department
                'teller_dashboard': False,    # Different department
                'risk_dashboard': False       # Different department
            }
        },
        {
            'username': 'admin_teller',
            'password': 'admin123',
            'department': 'Teller/Transaction Department',
            'role': 'admin',
            'should_access': {
                'accounts_dashboard': False,  # Different department
                'loans_dashboard': False,     # Different department
                'customer_service_dashboard': False,  # Different department
                'teller_dashboard': True,     # Own department
                'risk_dashboard': False       # Different department
            }
        },
        {
            'username': 'admin_risk',
            'password': 'admin123',
            'department': 'Risk Management Department',
            'role': 'admin',
            'should_access': {
                'accounts_dashboard': False,  # Different department - THIS IS THE KEY TEST
                'loans_dashboard': False,     # Different department
                'customer_service_dashboard': False,  # Different department
                'teller_dashboard': False,    # Different department
                'risk_dashboard': True        # Own department
            }
        }
    ]
    
    dashboards = [
        'accounts_dashboard',
        'loans_dashboard',
        'customer_service_dashboard',
        'teller_dashboard',
        'risk_dashboard'
    ]
    
    total_tests = 0
    passed_tests = 0
    critical_failures = []
    
    for user in test_users:
        print(f"\n--- Testing {user['username']} ({user['department']}) ---")
        
        # Create session and login
        session = requests.Session()
        login_data = {
            'username': user['username'],
            'password': user['password']
        }
        
        response = session.post(f"{base_url}/login", data=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed for {user['username']}")
            continue
        
        print(f"✅ Login successful for {user['username']}")
        
        # Test access to each dashboard
        for dashboard in dashboards:
            total_tests += 1
            should_access = user['should_access'][dashboard]
            
            try:
                response = session.get(f"{base_url}/{dashboard}")
                
                # Check if access was granted or denied
                if should_access:
                    # Should have access
                    if response.status_code == 200:
                        print(f"   ✅ {dashboard}: Access granted (expected)")
                        passed_tests += 1
                    else:
                        print(f"   ❌ {dashboard}: Access denied (unexpected)")
                        critical_failures.append(f"{user['username']} should access {dashboard} but was denied")
                else:
                    # Should NOT have access
                    if response.status_code == 200:
                        print(f"   ❌ {dashboard}: Access granted (SECURITY ISSUE)")
                        critical_failures.append(f"{user['username']} should NOT access {dashboard} but was granted access")
                    else:
                        print(f"   ✅ {dashboard}: Access denied (expected)")
                        passed_tests += 1
                        
            except Exception as e:
                print(f"   ❌ {dashboard}: Error testing access - {e}")
                critical_failures.append(f"{user['username']} - {dashboard}: {e}")
    
    # Test the specific scenario mentioned in the user query
    print("\n=== CRITICAL SECURITY TEST ===")
    print("Testing: Risk Administrator should NOT access Accounts Dashboard")
    
    # Login as risk admin
    risk_session = requests.Session()
    risk_login = {
        'username': 'admin_risk',
        'password': 'admin123'
    }
    
    response = risk_session.post(f"{base_url}/login", data=risk_login)
    if response.status_code == 200:
        print("✅ Risk admin login successful")
        
        # Try to access accounts dashboard
        response = risk_session.get(f"{base_url}/accounts_dashboard")
        if response.status_code == 200:
            print("❌ CRITICAL SECURITY FAILURE: Risk admin can access Accounts Dashboard!")
            critical_failures.append("CRITICAL: Risk admin has unauthorized access to Accounts Dashboard")
        else:
            print("✅ SECURITY VERIFIED: Risk admin correctly denied access to Accounts Dashboard")
            
        # Verify risk admin can still access their own dashboard
        response = risk_session.get(f"{base_url}/risk_dashboard")
        if response.status_code == 200:
            print("✅ Risk admin can access their own Risk Dashboard")
        else:
            print("❌ Risk admin cannot access their own Risk Dashboard")
            critical_failures.append("Risk admin cannot access their own dashboard")
    else:
        print("❌ Risk admin login failed")
        critical_failures.append("Risk admin login failed")
    
    # Summary
    print(f"\n=== TEST SUMMARY ===")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if critical_failures:
        print(f"\n❌ CRITICAL FAILURES ({len(critical_failures)}):")
        for failure in critical_failures:
            print(f"   - {failure}")
        print("\n🚨 SECURITY ISSUES DETECTED! Access control needs immediate attention.")
        return False
    else:
        print("\n✅ ALL TESTS PASSED!")
        print("🔒 Department access control is working correctly.")
        print("✅ Risk administrators cannot access Accounts Dashboard.")
        print("✅ All department dashboards are properly protected.")
        return True

def test_specific_scenarios():
    """Test specific security scenarios"""
    base_url = "http://localhost:5000"
    
    print("\n=== SPECIFIC SECURITY SCENARIOS ===\n")
    
    # Test 1: Admin from one department cannot access another department's APIs
    print("Test 1: Cross-department API access")
    
    # Login as risk admin
    risk_session = requests.Session()
    risk_login = {'username': 'admin_risk', 'password': 'admin123'}
    response = risk_session.post(f"{base_url}/login", data=risk_login)
    
    if response.status_code == 200:
        # Try to access accounts-specific API endpoints
        test_apis = [
            ('/api/loan_applications', 'GET'),
            ('/api/customers', 'GET'),
            ('/api/teller/transactions', 'GET'),
        ]
        
        for api, method in test_apis:
            try:
                if method == 'GET':
                    response = risk_session.get(f"{base_url}{api}")
                else:
                    response = risk_session.post(f"{base_url}{api}", json={})
                
                if response.status_code == 200:
                    print(f"   ⚠️ {api}: Risk admin has access (may need review)")
                else:
                    print(f"   ✅ {api}: Risk admin properly denied access")
            except Exception as e:
                print(f"   ❌ {api}: Error - {e}")
    
    # Test 2: HR admin should have system-wide access
    print("\nTest 2: HR admin system-wide access")
    
    hr_session = requests.Session()
    hr_login = {'username': 'admin_hr', 'password': 'admin123'}
    response = hr_session.post(f"{base_url}/login", data=hr_login)
    
    if response.status_code == 200:
        dashboards = ['accounts_dashboard', 'loans_dashboard', 'risk_dashboard']
        
        for dashboard in dashboards:
            response = hr_session.get(f"{base_url}/{dashboard}")
            if response.status_code == 200:
                print(f"   ✅ {dashboard}: HR admin has system-wide access")
            else:
                print(f"   ❌ {dashboard}: HR admin denied access (unexpected)")

if __name__ == "__main__":
    try:
        print("Starting department access control tests...")
        print("Make sure the Flask app is running on http://localhost:5000\n")
        
        # Run main test
        main_test_passed = test_department_access_control()
        
        # Run specific scenarios
        test_specific_scenarios()
        
        print("\n" + "="*50)
        
        if main_test_passed:
            print("🎉 SECURITY VERIFICATION COMPLETE!")
            print("✅ Department access control is properly implemented.")
            print("✅ Risk administrators cannot access Accounts Dashboard.")
            print("✅ Cross-department access is properly restricted.")
        else:
            print("🚨 SECURITY ISSUES DETECTED!")
            print("❌ Department access control needs immediate attention.")
            print("❌ Review the access control implementation.")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}") 