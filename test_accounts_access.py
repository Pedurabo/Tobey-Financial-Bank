#!/usr/bin/env python3
"""
Simple test to verify accounts dashboard access
"""

import requests

def test_accounts_dashboard():
    """Test accounts dashboard access"""
    base_url = "http://localhost:5000"
    
    # Create session and login as admin_accounts
    session = requests.Session()
    login_data = {
        'username': 'admin_accounts',
        'password': 'admin123'
    }
    
    print("Testing admin_accounts login...")
    response = session.post(f"{base_url}/login", data=login_data)
    print(f"Login response: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Login successful!")
        
        # Test accounts dashboard access
        print("\nTesting accounts dashboard access...")
        response = session.get(f"{base_url}/accounts_dashboard")
        print(f"Dashboard status: {response.status_code}")
        print(f"Response length: {len(response.text)}")
        
        if response.status_code == 200:
            print("✅ Accounts dashboard accessible!")
            
            # Check for enhanced functionality
            if "Cash Operations" in response.text:
                print("✅ Enhanced cash operations found")
            else:
                print("❌ Enhanced cash operations missing")
                
            if "Check Operations" in response.text:
                print("✅ Enhanced check operations found")
            else:
                print("❌ Enhanced check operations missing")
                
            if "Account Services" in response.text:
                print("✅ Enhanced account services found")
            else:
                print("❌ Enhanced account services missing")
                
            if "Payment Services" in response.text:
                print("✅ Enhanced payment services found")
            else:
                print("❌ Enhanced payment services missing")
                
        else:
            print("❌ Accounts dashboard not accessible")
            print(f"Response: {response.text[:500]}")
    else:
        print("❌ Login failed!")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    print("=== Accounts Dashboard Access Test ===\n")
    
    try:
        test_accounts_dashboard()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}") 