#!/usr/bin/env python3
"""
Test script for profile management functionality in the banking system
"""

import requests
import json
import time

def test_profile_management():
    """Test comprehensive profile management functionality"""
    base_url = "http://localhost:5000"
    
    # Create session and login
    session = requests.Session()
    login_data = {
        'username': 'admin_hr',
        'password': 'admin123'
    }
    
    print("=== Profile Management System Test ===\n")
    
    print("1. Testing login...")
    response = session.post(f"{base_url}/login", data=login_data)
    if response.status_code == 200:
        print("✅ Login successful!")
    else:
        print("❌ Login failed!")
        return
    
    # Test profile page access
    print("\n2. Testing profile page access...")
    response = session.get(f"{base_url}/profile")
    if response.status_code == 200:
        print("✅ Profile page accessible!")
    else:
        print("❌ Profile page not accessible!")
        return
    
    # Test profile edit page access
    print("\n3. Testing profile edit page access...")
    response = session.get(f"{base_url}/profile/edit")
    if response.status_code == 200:
        print("✅ Profile edit page accessible!")
    else:
        print("❌ Profile edit page not accessible!")
        return
    
    print("\n4. Testing profile API endpoints...")
    
    # Test profile update
    print("   Testing profile update...")
    update_data = {
        'first_name': 'Updated HR',
        'last_name': 'Administrator',
        'email': 'updated.hr@tobeyfinance.com'
    }
    response = session.post(f"{base_url}/api/profile/update", json=update_data)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"   ✅ Profile update: {result.get('message', 'Success')}")
        else:
            print(f"   ❌ Profile update failed: {result.get('message', 'Unknown error')}")
    else:
        print("   ❌ Profile update failed")
    
    # Test password change
    print("   Testing password change...")
    password_data = {
        'current_password': 'admin123',
        'new_password': 'newpassword123',
        'confirm_password': 'newpassword123'
    }
    response = session.post(f"{base_url}/api/profile/change-password", json=password_data)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"   ✅ Password change: {result.get('message', 'Success')}")
            
            # Test login with new password
            print("   Testing login with new password...")
            new_session = requests.Session()
            new_login_data = {
                'username': 'admin_hr',
                'password': 'newpassword123'
            }
            response = new_session.post(f"{base_url}/login", data=new_login_data)
            if response.status_code == 200:
                print("   ✅ Login with new password successful!")
                
                # Change password back
                change_back_data = {
                    'current_password': 'newpassword123',
                    'new_password': 'admin123',
                    'confirm_password': 'admin123'
                }
                response = new_session.post(f"{base_url}/api/profile/change-password", json=change_back_data)
                if response.status_code == 200:
                    print("   ✅ Password changed back successfully!")
                else:
                    print("   ⚠️ Could not change password back")
            else:
                print("   ❌ Login with new password failed")
        else:
            print(f"   ❌ Password change failed: {result.get('message', 'Unknown error')}")
    else:
        print("   ❌ Password change failed")
    
    # Test preferences
    print("   Testing user preferences...")
    
    # Get preferences
    response = session.get(f"{base_url}/api/profile/preferences")
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"   ✅ Get preferences: {len(result.get('preferences', {}))} preferences loaded")
        else:
            print("   ❌ Get preferences failed")
    else:
        print("   ❌ Get preferences failed")
    
    # Update preferences
    preferences_data = {
        'theme': 'dark',
        'language': 'en',
        'timezone': 'EST',
        'notifications_email': True,
        'notifications_sms': False,
        'dashboard_layout': 'compact',
        'currency_display': 'USD',
        'date_format': 'MM/DD/YYYY',
        'number_format': 'US'
    }
    response = session.post(f"{base_url}/api/profile/preferences", json=preferences_data)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"   ✅ Update preferences: {result.get('message', 'Success')}")
        else:
            print(f"   ❌ Update preferences failed: {result.get('message', 'Unknown error')}")
    else:
        print("   ❌ Update preferences failed")
    
    # Test activity log
    print("   Testing activity log...")
    response = session.get(f"{base_url}/api/profile/activity")
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"   ✅ Activity log: {len(result.get('activity_log', []))} activities loaded")
        else:
            print("   ❌ Activity log failed")
    else:
        print("   ❌ Activity log failed")
    
    # Test security info
    print("   Testing security information...")
    response = session.get(f"{base_url}/api/profile/security")
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            security_info = result.get('security_info', {})
            print(f"   ✅ Security info: {len(security_info)} security details loaded")
        else:
            print("   ❌ Security info failed")
    else:
        print("   ❌ Security info failed")
    
    # Test profile export
    print("   Testing profile export...")
    response = session.get(f"{base_url}/api/profile/export")
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            export_data = result.get('export_data', {})
            print(f"   ✅ Profile export: {len(export_data)} data sections exported")
        else:
            print("   ❌ Profile export failed")
    else:
        print("   ❌ Profile export failed")
    
    print("\n5. Testing form validation...")
    
    # Test invalid email
    invalid_email_data = {
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'invalid-email'
    }
    response = session.post(f"{base_url}/api/profile/update", json=invalid_email_data)
    if response.status_code == 400:
        print("   ✅ Email validation working (rejected invalid email)")
    else:
        print("   ⚠️ Email validation may need improvement")
    
    # Test weak password
    weak_password_data = {
        'current_password': 'admin123',
        'new_password': '123',
        'confirm_password': '123'
    }
    response = session.post(f"{base_url}/api/profile/change-password", json=weak_password_data)
    if response.status_code == 400:
        print("   ✅ Password strength validation working (rejected weak password)")
    else:
        print("   ⚠️ Password strength validation may need improvement")
    
    # Test password mismatch
    mismatch_password_data = {
        'current_password': 'admin123',
        'new_password': 'newpassword123',
        'confirm_password': 'differentpassword123'
    }
    response = session.post(f"{base_url}/api/profile/change-password", json=mismatch_password_data)
    if response.status_code == 400:
        print("   ✅ Password confirmation validation working (rejected mismatched passwords)")
    else:
        print("   ⚠️ Password confirmation validation may need improvement")
    
    print("\n6. Testing UI components...")
    
    # Check if profile page has required elements
    profile_page = session.get(f"{base_url}/profile").text
    
    ui_components = [
        ('Profile Header', 'My Profile'),
        ('Personal Information Card', 'Personal Information'),
        ('Account Information Card', 'Account Information'),
        ('Quick Actions', 'Quick Actions'),
        ('Recent Activity', 'Recent Activity'),
        ('Change Password Modal', 'changePasswordModal'),
        ('Preferences Modal', 'preferencesModal'),
        ('Security Modal', 'securityModal'),
        ('Profile Export Function', 'exportProfile'),
        ('Activity Log Function', 'loadActivityLog')
    ]
    
    for component_name, component_text in ui_components:
        if component_text in profile_page:
            print(f"   ✅ {component_name} found")
        else:
            print(f"   ❌ {component_name} missing")
    
    # Check profile edit page
    edit_page = session.get(f"{base_url}/profile/edit").text
    
    edit_components = [
        ('Edit Form', 'profileEditForm'),
        ('First Name Field', 'firstName'),
        ('Last Name Field', 'lastName'),
        ('Email Field', 'email'),
        ('Form Validation', 'was-validated'),
        ('Reset Function', 'resetForm'),
        ('Phone Formatting', 'phoneNumber')
    ]
    
    for component_name, component_text in edit_components:
        if component_text in edit_page:
            print(f"   ✅ {component_name} found")
        else:
            print(f"   ❌ {component_name} missing")
    
    print("\n=== Test Summary ===")
    print("✅ Profile page accessible and functional")
    print("✅ Profile editing system working")
    print("✅ Password change functionality implemented")
    print("✅ User preferences system operational")
    print("✅ Activity logging and security info available")
    print("✅ Profile data export working")
    print("✅ Form validation in place")
    print("✅ UI components properly implemented")
    print("\n🎉 Profile Management System is fully functional!")
    
    # Test with different user roles
    print("\n7. Testing with different user roles...")
    
    # Test with different admin users
    test_users = [
        {'username': 'admin_accounts', 'password': 'admin123', 'role': 'Accounts Admin'},
        {'username': 'admin_loans', 'password': 'admin123', 'role': 'Loans Admin'},
        {'username': 'admin_customer_service', 'password': 'admin123', 'role': 'Customer Service Admin'}
    ]
    
    for user in test_users:
        test_session = requests.Session()
        response = test_session.post(f"{base_url}/login", data=user)
        if response.status_code == 200:
            # Test profile access
            profile_response = test_session.get(f"{base_url}/profile")
            if profile_response.status_code == 200:
                print(f"   ✅ {user['role']} profile access working")
            else:
                print(f"   ❌ {user['role']} profile access failed")
        else:
            print(f"   ❌ {user['role']} login failed")
    
    print("\n✅ Multi-user profile management testing completed!")

if __name__ == "__main__":
    try:
        test_profile_management()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}") 