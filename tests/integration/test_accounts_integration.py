#!/usr/bin/env python3
"""
Comprehensive Integration Tests for Accounts Department
Covers end-to-end flows, negative tests, and API contract validation
"""

import requests
import json
import time
from typing import Dict, Any

# Test Configuration
BASE_URL = "http://localhost:5000"
ACCOUNTS_ADMIN = {"username": "admin_accounts", "password": "admin123"}
CUSTOMER_USER = {"username": "john_smith", "password": "customer123"}

class TestAccountsIntegration:
    """Integration tests for Accounts Department functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.session = requests.Session()
        self.test_accounts = [
            "ACC-001-2024",
            "ACC-002-2024", 
            "ACC-003-2024"
        ]
    
    def teardown_method(self):
        """Cleanup after each test method"""
        if self.session:
            self.session.close()
    
    # ==================== END-TO-END FLOW TESTS ====================
    
    def test_accounts_admin_complete_flow(self):
        """Test complete admin flow: login → dashboard → transaction → logout"""
        print("\n=== Testing Accounts Admin Complete Flow ===")
        
        # Step 1: Login
        print("1. Logging in as accounts admin...")
        response = self.session.post(f"{BASE_URL}/login", data=ACCOUNTS_ADMIN)
        assert response.status_code in [200, 302], f"Login failed: {response.status_code}"
        print("✅ Login successful")
        
        # Step 2: Access dashboard
        print("2. Accessing accounts dashboard...")
        response = self.session.get(f"{BASE_URL}/accounts_dashboard")
        assert response.status_code == 200, f"Dashboard access failed: {response.status_code}"
        print("✅ Dashboard accessible")
        
        # Step 3: Perform a deposit transaction
        print("3. Performing deposit transaction...")
        deposit_data = {
            'account_number': self.test_accounts[0],
            'amount': 1000.00,
            'currency': 'USD',
            'description': 'Integration test deposit'
        }
        response = self.session.post(f"{BASE_URL}/api/teller/deposit", json=deposit_data)
        assert response.status_code == 200, f"Deposit failed: {response.status_code}"
        result = response.json()
        assert 'message' in result, "Deposit response missing message"
        print("✅ Deposit transaction successful")
        
        # Step 4: Perform a withdrawal transaction
        print("4. Performing withdrawal transaction...")
        withdrawal_data = {
            'account_number': self.test_accounts[0],
            'amount': 500.00,
            'currency': 'USD',
            'description': 'Integration test withdrawal'
        }
        response = self.session.post(f"{BASE_URL}/api/teller/withdraw", json=withdrawal_data)
        assert response.status_code == 200, f"Withdrawal failed: {response.status_code}"
        result = response.json()
        assert 'message' in result, "Withdrawal response missing message"
        print("✅ Withdrawal transaction successful")
        
        # Step 5: Logout
        print("5. Logging out...")
        response = self.session.get(f"{BASE_URL}/logout")
        assert response.status_code in [200, 302], f"Logout failed: {response.status_code}"
        print("✅ Logout successful")
        
        print("🎉 Complete accounts admin flow test passed!")
    
    def test_customer_accounts_flow(self):
        """Test customer flow: login → dashboard → view transactions → logout"""
        print("\n=== Testing Customer Accounts Flow ===")
        
        # Step 1: Login as customer
        print("1. Logging in as customer...")
        response = self.session.post(f"{BASE_URL}/login", data=CUSTOMER_USER)
        assert response.status_code in [200, 302], f"Customer login failed: {response.status_code}"
        print("✅ Customer login successful")
        
        # Step 2: Access customer dashboard
        print("2. Accessing customer dashboard...")
        response = self.session.get(f"{BASE_URL}/customer_dashboard")
        assert response.status_code == 200, f"Customer dashboard access failed: {response.status_code}"
        print("✅ Customer dashboard accessible")
        
        # Step 3: Check if customer can access accounts dashboard (should be denied)
        print("3. Testing unauthorized access to accounts dashboard...")
        response = self.session.get(f"{BASE_URL}/accounts_dashboard")
        # Should be denied or redirected
        assert response.status_code in [302, 403, 401], f"Unauthorized access not properly handled: {response.status_code}"
        print("✅ Unauthorized access properly handled")
        
        # Step 4: Logout
        print("4. Logging out...")
        response = self.session.get(f"{BASE_URL}/logout")
        assert response.status_code in [200, 302], f"Logout failed: {response.status_code}"
        print("✅ Logout successful")
        
        print("🎉 Customer accounts flow test passed!")
    
    # ==================== NEGATIVE TESTS ====================
    
    def test_invalid_login_credentials(self):
        """Test various invalid login scenarios"""
        print("\n=== Testing Invalid Login Scenarios ===")
        
        invalid_credentials = [
            {"username": "nonexistent", "password": "wrong"},
            {"username": "admin_accounts", "password": "wrong"},
            {"username": "", "password": ""},
            {"username": "admin_accounts", "password": ""},
            {"username": "", "password": "admin123"}
        ]
        
        for i, creds in enumerate(invalid_credentials, 1):
            print(f"{i}. Testing invalid credentials: {creds['username']}/{creds['password']}")
            response = self.session.post(f"{BASE_URL}/login", data=creds)
            # Should not be successful (200 or 302)
            assert response.status_code not in [200, 302], f"Invalid login succeeded: {creds}"
            print(f"   ✅ Invalid login properly rejected")
        
        print("🎉 All invalid login scenarios handled correctly!")
    
    def test_unauthorized_api_access(self):
        """Test accessing APIs without authentication"""
        print("\n=== Testing Unauthorized API Access ===")
        
        # Test APIs that require authentication
        protected_apis = [
            "/api/teller/deposit",
            "/api/teller/withdraw", 
            "/api/teller/customer/search",
            "/api/teller/account/freeze",
            "/api/teller/currency/exchange",
            "/api/teller/wire/transfer",
            "/api/teller/fraud/report"
        ]
        
        for api in protected_apis:
            print(f"Testing unauthorized access to {api}...")
            response = self.session.post(f"{BASE_URL}{api}", json={})
            # Should be denied (401, 403, or redirect to login)
            assert response.status_code in [401, 403, 302], f"Unauthorized access to {api} not properly handled: {response.status_code}"
            print(f"   ✅ {api} properly protected")
        
        print("🎉 All APIs properly protected!")
    
    def test_invalid_transaction_data(self):
        """Test submitting invalid transaction data"""
        print("\n=== Testing Invalid Transaction Data ===")
        
        # Login first
        self.session.post(f"{BASE_URL}/login", data=ACCOUNTS_ADMIN)
        
        # Test invalid deposit data
        invalid_deposits = [
            {"account_number": "", "amount": 1000, "currency": "USD"},  # Empty account
            {"account_number": "ACC-001-2024", "amount": -1000, "currency": "USD"},  # Negative amount
            {"account_number": "ACC-001-2024", "amount": 0, "currency": "USD"},  # Zero amount
            {"account_number": "ACC-001-2024", "amount": 1000, "currency": "INVALID"},  # Invalid currency
            {"account_number": "ACC-001-2024", "amount": "not_a_number", "currency": "USD"},  # Invalid amount type
            {},  # Empty data
        ]
        
        for i, invalid_data in enumerate(invalid_deposits, 1):
            print(f"{i}. Testing invalid deposit data: {invalid_data}")
            response = self.session.post(f"{BASE_URL}/api/teller/deposit", json=invalid_data)
            # Should be rejected (400, 422, or similar)
            assert response.status_code in [400, 422, 500], f"Invalid deposit data not rejected: {response.status_code}"
            print(f"   ✅ Invalid deposit data properly rejected")
        
        print("🎉 All invalid transaction data properly handled!")
    
    # ==================== API CONTRACT TESTS ====================
    
    def test_deposit_api_contract(self):
        """Test deposit API response contract"""
        print("\n=== Testing Deposit API Contract ===")
        
        # Login first
        self.session.post(f"{BASE_URL}/login", data=ACCOUNTS_ADMIN)
        
        # Valid deposit
        valid_data = {
            'account_number': self.test_accounts[0],
            'amount': 1000.00,
            'currency': 'USD',
            'description': 'API contract test'
        }
        
        response = self.session.post(f"{BASE_URL}/api/teller/deposit", json=valid_data)
        assert response.status_code == 200, f"Valid deposit failed: {response.status_code}"
        
        # Check response structure
        data = response.json()
        required_fields = ['message', 'success']
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        assert isinstance(data['message'], str), "Message should be string"
        assert isinstance(data['success'], bool), "Success should be boolean"
        
        print("✅ Deposit API contract validated")
    
    def test_withdrawal_api_contract(self):
        """Test withdrawal API response contract"""
        print("\n=== Testing Withdrawal API Contract ===")
        
        # Login first
        self.session.post(f"{BASE_URL}/login", data=ACCOUNTS_ADMIN)
        
        # Valid withdrawal
        valid_data = {
            'account_number': self.test_accounts[0],
            'amount': 100.00,
            'currency': 'USD',
            'description': 'API contract test'
        }
        
        response = self.session.post(f"{BASE_URL}/api/teller/withdraw", json=valid_data)
        assert response.status_code == 200, f"Valid withdrawal failed: {response.status_code}"
        
        # Check response structure
        data = response.json()
        required_fields = ['message', 'success']
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        assert isinstance(data['message'], str), "Message should be string"
        assert isinstance(data['success'], bool), "Success should be boolean"
        
        print("✅ Withdrawal API contract validated")
    
    def test_customer_search_api_contract(self):
        """Test customer search API response contract"""
        print("\n=== Testing Customer Search API Contract ===")
        
        # Login first
        self.session.post(f"{BASE_URL}/login", data=ACCOUNTS_ADMIN)
        
        # Valid search
        search_data = {
            'search_value': 'John',
            'search_type': 'name'
        }
        
        response = self.session.post(f"{BASE_URL}/api/teller/customer/search", json=search_data)
        assert response.status_code == 200, f"Customer search failed: {response.status_code}"
        
        # Check response structure
        data = response.json()
        assert 'customers' in data, "Response should contain 'customers' field"
        assert isinstance(data['customers'], list), "Customers should be a list"
        
        print("✅ Customer search API contract validated")
    
    def test_exchange_rates_api_contract(self):
        """Test exchange rates API response contract"""
        print("\n=== Testing Exchange Rates API Contract ===")
        
        # Login first
        self.session.post(f"{BASE_URL}/login", data=ACCOUNTS_ADMIN)
        
        response = self.session.get(f"{BASE_URL}/api/teller/exchange/rates")
        assert response.status_code == 200, f"Exchange rates failed: {response.status_code}"
        
        # Check response structure
        data = response.json()
        assert 'rates' in data, "Response should contain 'rates' field"
        assert isinstance(data['rates'], list), "Rates should be a list"
        
        print("✅ Exchange rates API contract validated")
    
    # ==================== EDGE CASE TESTS ====================
    
    def test_concurrent_transactions(self):
        """Test handling of concurrent transactions"""
        print("\n=== Testing Concurrent Transactions ===")
        
        # Login first
        self.session.post(f"{BASE_URL}/login", data=ACCOUNTS_ADMIN)
        
        # Create multiple sessions for concurrent requests
        sessions = [requests.Session() for _ in range(3)]
        for session in sessions:
            session.post(f"{BASE_URL}/login", data=ACCOUNTS_ADMIN)
        
        # Submit concurrent deposits
        deposit_data = {
            'account_number': self.test_accounts[1],
            'amount': 100.00,
            'currency': 'USD',
            'description': 'Concurrent test'
        }
        
        responses = []
        for session in sessions:
            response = session.post(f"{BASE_URL}/api/teller/deposit", json=deposit_data)
            responses.append(response)
        
        # All should succeed (200) or be handled gracefully
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count >= 1, "At least one concurrent transaction should succeed"
        
        print(f"✅ Concurrent transactions handled: {success_count}/{len(responses)} succeeded")
    
    def test_large_amount_transactions(self):
        """Test handling of large amount transactions"""
        print("\n=== Testing Large Amount Transactions ===")
        
        # Login first
        self.session.post(f"{BASE_URL}/login", data=ACCOUNTS_ADMIN)
        
        # Test very large amounts
        large_amounts = [999999.99, 1000000.00, 999999999.99]
        
        for amount in large_amounts:
            deposit_data = {
                'account_number': self.test_accounts[2],
                'amount': amount,
                'currency': 'USD',
                'description': f'Large amount test: {amount}'
            }
            
            response = self.session.post(f"{BASE_URL}/api/teller/deposit", json=deposit_data)
            # Should either succeed or be rejected with proper error
            assert response.status_code in [200, 400, 422], f"Large amount {amount} not handled properly: {response.status_code}"
            
            if response.status_code == 200:
                print(f"   ✅ Large amount {amount} accepted")
            else:
                print(f"   ✅ Large amount {amount} properly rejected")
        
        print("🎉 Large amount transactions properly handled!")

def run_integration_tests():
    """Run all integration tests"""
    print("🚀 Starting Accounts Department Integration Tests...")
    
    test_suite = TestAccountsIntegration()
    
    # Run all test methods
    test_methods = [
        test_suite.test_accounts_admin_complete_flow,
        test_suite.test_customer_accounts_flow,
        test_suite.test_invalid_login_credentials,
        test_suite.test_unauthorized_api_access,
        test_suite.test_invalid_transaction_data,
        test_suite.test_deposit_api_contract,
        test_suite.test_withdrawal_api_contract,
        test_suite.test_customer_search_api_contract,
        test_suite.test_exchange_rates_api_contract,
        test_suite.test_concurrent_transactions,
        test_suite.test_large_amount_transactions
    ]
    
    passed = 0
    failed = 0
    
    for test_method in test_methods:
        try:
            test_suite.setup_method()
            test_method()
            passed += 1
        except Exception as e:
            print(f"❌ Test failed: {test_method.__name__} - {str(e)}")
            failed += 1
        finally:
            test_suite.teardown_method()
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All integration tests passed!")
    else:
        print(f"⚠️ {failed} tests failed. Please review the errors above.")
    
    return failed == 0

if __name__ == "__main__":
    run_integration_tests() 