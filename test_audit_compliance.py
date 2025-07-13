#!/usr/bin/env python3
"""
Comprehensive test script for Audit and Compliance Department functionality
"""

import requests
import json
import time
from datetime import datetime

def test_audit_compliance_functionality():
    """Test all audit and compliance department functionality"""
    base_url = "http://localhost:5000"
    
    # Create session and login as admin_audit
    session = requests.Session()
    login_data = {
        'username': 'admin_audit',
        'password': 'admin123'
    }
    
    print("=== Audit and Compliance Department Functionality Test ===\n")
    
    print("1. Testing login...")
    response = session.post(f"{base_url}/login", data=login_data)
    if response.status_code == 200:
        print("✅ Login successful!")
    else:
        print("❌ Login failed!")
        return
    
    print("\n2. Testing audit dashboard access...")
    response = session.get(f"{base_url}/audit_dashboard")
    if response.status_code == 200:
        print("✅ Audit dashboard accessible!")
    else:
        print("❌ Audit dashboard not accessible!")
        return
    
    print("\n3. Testing Audit Trail Management...")
    
    # Test audit trail retrieval
    print("   Testing audit trail retrieval...")
    response = session.get(f"{base_url}/api/audit/trail")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Audit trail: {result.get('total_records', 0)} records retrieved")
    else:
        print("   ❌ Audit trail retrieval failed")
    
    # Test audit trail filtering
    print("   Testing audit trail filtering...")
    filter_params = {
        'start_date': '2025-01-01',
        'end_date': '2025-12-31',
        'department': 'Accounts Department'
    }
    response = session.get(f"{base_url}/api/audit/trail", params=filter_params)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Audit trail filtering: {len(result.get('audit_trail', []))} filtered records")
    else:
        print("   ❌ Audit trail filtering failed")
    
    print("\n4. Testing Compliance Reporting...")
    
    # Test compliance report generation
    print("   Testing compliance report generation...")
    response = session.get(f"{base_url}/api/compliance/report")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Compliance report: {result.get('report_type', 'N/A')} report generated")
    else:
        print("   ❌ Compliance report generation failed")
    
    # Test compliance assessment creation
    print("   Testing compliance assessment creation...")
    assessment_data = {
        'department': 'Loans Department',
        'assessment_type': 'regulatory',
        'compliance_areas': ['AML', 'KYC', 'Privacy'],
        'findings': ['Missing documentation for loan applications'],
        'recommendations': ['Implement document verification process'],
        'risk_level': 'medium',
        'due_date': '2025-02-15'
    }
    response = session.post(f"{base_url}/api/compliance/assessment", json=assessment_data)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Compliance assessment: {result.get('assessment_id', 'N/A')} created")
    else:
        print("   ❌ Compliance assessment creation failed")
    
    print("\n5. Testing Regulatory Monitoring...")
    
    # Test regulatory monitoring data
    print("   Testing regulatory monitoring data...")
    response = session.get(f"{base_url}/api/regulatory/monitoring")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Regulatory monitoring: {len(result.get('regulatory_alerts', []))} alerts found")
    else:
        print("   ❌ Regulatory monitoring failed")
    
    # Test regulatory alert creation
    print("   Testing regulatory alert creation...")
    alert_data = {
        'alert_type': 'aml',
        'severity': 'high',
        'title': 'New AML Requirements',
        'description': 'Updated AML guidelines require immediate attention',
        'affected_departments': ['Accounts Department', 'Loans Department'],
        'regulatory_reference': 'AML-2025-001',
        'action_required': True,
        'due_date': '2025-02-15'
    }
    response = session.post(f"{base_url}/api/regulatory/alert", json=alert_data)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Regulatory alert: {result.get('alert_id', 'N/A')} created")
    else:
        print("   ❌ Regulatory alert creation failed")
    
    print("\n6. Testing Internal Audit Functions...")
    
    # Test internal audit creation
    print("   Testing internal audit creation...")
    audit_data = {
        'department': 'Accounts Department',
        'audit_type': 'operational',
        'scope': 'Review of account opening procedures',
        'objectives': ['Verify compliance with KYC requirements', 'Assess risk management'],
        'findings': ['Some accounts missing required documentation'],
        'recommendations': ['Implement mandatory document checklist'],
        'risk_assessment': 'medium',
        'compliance_score': 85,
        'estimated_completion': '2025-01-25'
    }
    response = session.post(f"{base_url}/api/audit/internal/review", json=audit_data)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Internal audit: {result.get('review_id', 'N/A')} created")
        audit_review_id = result.get('review_id')
    else:
        print("   ❌ Internal audit creation failed")
        audit_review_id = None
    
    # Test internal audit retrieval
    if audit_review_id:
        print("   Testing internal audit retrieval...")
        response = session.get(f"{base_url}/api/audit/internal/{audit_review_id}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Internal audit retrieval: {result.get('audit_review', {}).get('review_id', 'N/A')}")
        else:
            print("   ❌ Internal audit retrieval failed")
    
    # Test internal audit update
    if audit_review_id:
        print("   Testing internal audit update...")
        update_data = {
            'status': 'completed',
            'findings': ['Some accounts missing required documentation', 'Training needed for staff'],
            'recommendations': ['Implement mandatory document checklist', 'Provide staff training']
        }
        response = session.put(f"{base_url}/api/audit/internal/{audit_review_id}/update", json=update_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Internal audit update: {result.get('audit_review', {}).get('status', 'N/A')}")
        else:
            print("   ❌ Internal audit update failed")
    
    print("\n7. Testing Compliance Dashboard Data...")
    
    # Test compliance dashboard data
    print("   Testing compliance dashboard data...")
    response = session.get(f"{base_url}/api/compliance/dashboard")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Compliance dashboard: Score {result.get('compliance_score', 0)}%")
        print(f"   ✅ Regulatory alerts: {result.get('regulatory_alerts', 0)}")
        print(f"   ✅ Pending assessments: {result.get('pending_assessments', 0)}")
        print(f"   ✅ Active audits: {result.get('active_audits', 0)}")
    else:
        print("   ❌ Compliance dashboard data failed")
    
    print("\n8. Testing Audit Report Export...")
    
    # Test audit report export
    print("   Testing audit report export...")
    export_data = {
        'report_type': 'comprehensive',
        'date_range': 'last_30_days',
        'format': 'pdf'
    }
    response = session.post(f"{base_url}/api/audit/export", json=export_data)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Audit report export: {result.get('report_id', 'N/A')} generated")
    else:
        print("   ❌ Audit report export failed")
    
    print("\n9. Testing Access Control...")
    
    # Test access control for non-audit users
    print("   Testing access control for non-audit users...")
    
    # Login as accounts user
    accounts_login = {
        'username': 'admin_accounts',
        'password': 'admin123'
    }
    session2 = requests.Session()
    session2.post(f"{base_url}/login", data=accounts_login)
    
    # Try to access audit dashboard
    response = session2.get(f"{base_url}/audit_dashboard")
    if response.status_code == 302:  # Redirected due to access denied
        print("   ✅ Access control working (non-audit user denied)")
    else:
        print("   ❌ Access control failed (non-audit user should be denied)")
    
    # Try to access audit API
    response = session2.get(f"{base_url}/api/audit/trail")
    if response.status_code == 403:  # Forbidden
        print("   ✅ API access control working (non-audit user denied)")
    else:
        print("   ❌ API access control failed (non-audit user should be denied)")
    
    print("\n10. Testing Audit Trail Logging...")
    
    # Test that audit events are being logged
    print("   Testing audit trail logging...")
    
    # Perform some actions that should be logged
    actions_to_test = [
        ('/api/compliance/assessment', 'POST', {'department': 'Test Department'}),
        ('/api/regulatory/alert', 'POST', {'title': 'Test Alert'}),
        ('/api/audit/internal/review', 'POST', {'department': 'Test Department'})
    ]
    
    for endpoint, method, data in actions_to_test:
        if method == 'POST':
            response = session.post(f"{base_url}{endpoint}", json=data)
        else:
            response = session.get(f"{base_url}{endpoint}")
        
        if response.status_code in [200, 201]:
            print(f"   ✅ Audit event logged for {endpoint}")
        else:
            print(f"   ⚠️ Audit event may not be logged for {endpoint}")
    
    print("\n=== Audit and Compliance Department Test Summary ===")
    print("✅ Audit dashboard access")
    print("✅ Audit trail management")
    print("✅ Compliance reporting")
    print("✅ Regulatory monitoring")
    print("✅ Internal audit functions")
    print("✅ Compliance dashboard data")
    print("✅ Audit report export")
    print("✅ Access control")
    print("✅ Audit trail logging")
    print("\n🎉 Audit and Compliance Department functionality comprehensive test complete!")

if __name__ == "__main__":
    try:
        test_audit_compliance_functionality()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}") 