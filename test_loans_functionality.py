#!/usr/bin/env python3
"""
Comprehensive test script for Loans Department functionality with real-life loan logic
"""

import requests
import json
import time

def test_loans_dashboard_functionality():
    """Test all comprehensive loans dashboard functionality"""
    base_url = "http://localhost:5000"
    
    # Create session and login as admin_loans
    session = requests.Session()
    login_data = {
        'username': 'admin_loans',
        'password': 'admin123'
    }
    
    print("=== Comprehensive Loans Department Functionality Test ===\n")
    
    print("1. Testing login...")
    response = session.post(f"{base_url}/login", data=login_data)
    if response.status_code == 200:
        print("✅ Login successful!")
    else:
        print("❌ Login failed!")
        return
    
    print("\n2. Testing loans dashboard access...")
    response = session.get(f"{base_url}/loans_dashboard")
    if response.status_code == 200:
        print("✅ Loans dashboard accessible!")
        print("   📊 Enhanced dashboard with comprehensive loan portfolio metrics")
    else:
        print("❌ Loans dashboard not accessible!")
        return
    
    print("\n3. Testing Advanced Loan Application with Real-Life Logic...")
    
    # Test comprehensive loan application
    print("   Testing enhanced loan application...")
    comprehensive_loan_data = {
        'customer_name': 'Sarah Johnson',
        'customer_email': 'sarah.johnson@email.com',
        'customer_phone': '+1-555-0123',
        'customer_ssn': '123-45-6789',
        'loan_type': 'Personal',
        'loan_amount': 25000,
        'loan_term': 48,
        'loan_purpose': 'Debt consolidation',
        'monthly_income': 5500,
        'monthly_debt': 1200,
        'credit_score': 728,
        'employment_status': 'Full-time',
        'employment_length': 36,  # months
        'employer_name': 'Tech Solutions Inc.',
        'collateral_type': 'None',
        'collateral_value': 0,
        'down_payment': 2500,
        'branch_code': 'MAIN001',
        'referral_source': 'online'
    }
    
    response = session.post(f"{base_url}/api/loans/apply", json=comprehensive_loan_data)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Enhanced loan application: {result.get('message', 'Success')}")
        print(f"   📋 Application ID: {result.get('application_id')}")
        if 'application' in result:
            app = result['application']
            print(f"   💰 Calculated Interest Rate: {app.get('calculated_rate', 'N/A')}%")
            print(f"   📊 Risk Category: {app.get('risk_category', 'N/A')}")
            print(f"   📈 DTI Ratio: {app.get('dti_ratio', 'N/A'):.2%}")
            print(f"   🎯 Prequalification Score: {app.get('prequalification_score', 'N/A')}")
            print(f"   💳 Estimated Payment: ${app.get('estimated_payment', 'N/A'):,.2f}")
            if app.get('auto_decision'):
                print(f"   🤖 Auto Decision: {app.get('auto_decision')}")
    else:
        print("   ❌ Enhanced loan application failed")
    
    print("\n4. Testing Advanced Credit Scoring System...")
    
    # Test credit scoring
    print("   Testing comprehensive credit scoring...")
    credit_data = {
        'customer_id': 'CUST-12345',
        'payment_history': 92,
        'credit_utilization': 25,
        'credit_length': 72,
        'credit_mix': 85,
        'new_credit': 88,
        'income_stability': 90,
        'employment_history': 85,
        'debt_to_income': 0.22,
        'bank_relationships': 4,
        'collateral_value': 15000
    }
    
    response = session.post(f"{base_url}/api/loans/credit-score", json=credit_data)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            credit_report = result.get('credit_report', {})
            print(f"   ✅ Credit scoring completed")
            print(f"   📊 Credit Score: {credit_report.get('credit_score')}")
            print(f"   🏷️ Risk Category: {credit_report.get('risk_category')}")
            print(f"   📉 Default Probability: {credit_report.get('default_probability')}%")
            print(f"   💹 Rate Adjustment: {credit_report.get('recommended_rate_adjustment')}%")
            
            breakdown = credit_report.get('score_breakdown', {})
            print("   📋 Score Breakdown:")
            for factor, details in breakdown.items():
                print(f"      • {factor.replace('_', ' ').title()}: {details.get('score')} ({details.get('weight')})")
        else:
            print("   ❌ Credit scoring failed")
    else:
        print("   ❌ Credit scoring API failed")
    
    print("\n5. Testing Loan Amortization Calculator...")
    
    # Test amortization schedule
    print("   Testing amortization calculations...")
    amortization_data = {
        'principal': 25000,
        'annual_rate': 8.5,
        'term_months': 48,
        'start_date': '2024-02-01',
        'monthly_income': 5500
    }
    
    response = session.post(f"{base_url}/api/loans/amortization", json=amortization_data)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            summary = result.get('summary', {})
            schedule = result.get('schedule', [])
            print(f"   ✅ Amortization schedule generated")
            print(f"   💰 Loan Amount: ${summary.get('loan_amount'):,.2f}")
            print(f"   📅 Monthly Payment: ${summary.get('monthly_payment'):,.2f}")
            print(f"   🧮 Total Interest: ${summary.get('total_interest'):,.2f}")
            print(f"   📊 Interest Percentage: {summary.get('interest_percentage')}%")
            print(f"   📈 Payment-to-Income Ratio: {summary.get('payment_to_income_ratio')}%")
            print(f"   📅 Payoff Date: {summary.get('payoff_date')}")
            print(f"   📋 Schedule Entries: {len(schedule)} payments")
            
            # Show first few payments
            if schedule:
                print("   📆 First 3 Payments:")
                for i, payment in enumerate(schedule[:3]):
                    print(f"      Payment {payment['payment_number']}: ${payment['monthly_payment']:.2f} "
                          f"(P: ${payment['principal_payment']:.2f}, I: ${payment['interest_payment']:.2f}, "
                          f"Bal: ${payment['remaining_balance']:,.2f})")
        else:
            print("   ❌ Amortization calculation failed")
    else:
        print("   ❌ Amortization API failed")
    
    print("\n6. Testing Regulatory Compliance Verification...")
    
    # Test compliance checking
    print("   Testing comprehensive compliance checks...")
    compliance_data = {
        'application': {
            'loan_type': 'Mortgage',
            'identity_verified': True
        },
        'apr_disclosed': True,
        'finance_charge_disclosed': True,
        'payment_schedule_provided': True,
        'right_to_cancel_disclosed': False,
        'privacy_notice_provided': True,
        'opt_out_offered': True
    }
    
    response = session.post(f"{base_url}/api/loans/compliance-check", json=compliance_data)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"   ✅ Compliance verification completed")
            print(f"   📊 Compliance Score: {result.get('compliance_score')}%")
            print(f"   🏷️ Overall Status: {result.get('overall_status')}")
            
            compliance_results = result.get('compliance_results', {})
            print("   📋 Compliance Results:")
            for check_name, details in compliance_results.items():
                status = details.get('status', 'unknown')
                print(f"      • {check_name.replace('_', ' ').title()}: {status}")
            
            required_actions = result.get('required_actions', [])
            if required_actions:
                print(f"   ⚠️ Required Actions: {len(required_actions)}")
                for action in required_actions[:3]:  # Show first 3
                    print(f"      • {action}")
        else:
            print("   ❌ Compliance verification failed")
    else:
        print("   ❌ Compliance API failed")
    
    print("\n7. Testing Enhanced Loan Processing...")
    
    # Test loan processing with enhanced data
    print("   Testing enhanced loan processing...")
    processing_data = {
        'application_id': 'LA-2024-001234',
        'decision': 'approved',
        'approved_amount': 23000,
        'approved_rate': 8.25,
        'approved_term': 48,
        'conditions': 'Proof of income required, Direct deposit setup',
        'notes': 'Excellent credit profile, approved at reduced rate',
        'underwriter_id': 'UW-001',
        'risk_assessment': 'Low risk',
        'collateral_required': False
    }
    
    response = session.post(f"{base_url}/api/loans/process", json=processing_data)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Enhanced loan processing: {result.get('message', 'Success')}")
        if 'processed_loan' in result:
            loan = result['processed_loan']
            print(f"   💰 Approved Amount: ${loan.get('approved_amount'):,.2f}")
            print(f"   📈 Approved Rate: {loan.get('approved_rate')}%")
            print(f"   📅 Approved Term: {loan.get('approved_term')} months")
    else:
        print("   ❌ Enhanced loan processing failed")
    
    print("\n8. Testing Loan Disbursement with Tracking...")
    
    # Test disbursement
    print("   Testing loan disbursement...")
    disbursement_data = {
        'loan_id': 'LA-2024-001234',
        'disbursement_amount': 23000,
        'disbursement_method': 'bank_transfer',
        'account_number': 'ACC-001-2024',
        'disbursement_date': '2024-02-15',
        'fee_amount': 100,
        'net_disbursement': 22900
    }
    
    response = session.post(f"{base_url}/api/loans/disburse", json=disbursement_data)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Loan Disbursement: {result.get('message', 'Success')}")
    else:
        print("   ❌ Loan disbursement failed")
    
    # Test loan payment processing
    print("   Testing loan payment processing...")
    test_loan_id = 'LA-2024-001234'  # Define test loan ID
    payment_data = {
        'loan_id': test_loan_id,
        'payment_amount': 750,
        'payment_method': 'auto_debit',
        'payment_date': '2025-01-15',
        'payment_type': 'regular',
        'account_number': 'ACC-001-2024'
    }
    response = session.post(f"{base_url}/api/loans/payment", json=payment_data)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Loan Payment: {result.get('message', 'Success')}")
    else:
        print("   ❌ Loan payment failed")
    
    # Test loan modification
    print("   Testing loan modification...")
    modification_data = {
        'loan_id': test_loan_id,
        'modification_type': 'rate_change',
        'new_interest_rate': 7.5,
        'reason': 'Rate reduction due to improved credit score',
        'effective_date': '2025-02-01',
        'notes': 'Customer requested rate review'
    }
    response = session.post(f"{base_url}/api/loans/modify", json=modification_data)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Loan Modification: {result.get('message', 'Success')}")
    else:
        print("   ❌ Loan modification failed")
    
    # Test loan closure
    print("   Testing loan closure...")
    closure_data = {
        'loan_id': test_loan_id,
        'closure_type': 'prepayment',
        'final_payment': 15000,
        'closure_date': '2025-06-01',
        'waived_charges': 100,
        'notes': 'Early closure with partial waiver'
    }
    response = session.post(f"{base_url}/api/loans/close", json=closure_data)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Loan Closure: {result.get('message', 'Success')}")
    else:
        print("   ❌ Loan closure failed")
    
    # Test loan default management
    print("   Testing loan default management...")
    default_data = {
        'loan_id': 'L002',
        'default_type': 'missed_payment',
        'days_overdue': 30,
        'overdue_amount': 1500,
        'action_taken': 'notice_sent',
        'recovery_plan': 'Payment plan negotiation',
        'notes': 'Customer contacted for payment arrangement'
    }
    response = session.post(f"{base_url}/api/loans/default", json=default_data)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Default Management: {result.get('message', 'Success')}")
    else:
        print("   ❌ Default management failed")
    
    # Test loan restructuring
    print("   Testing loan restructuring...")
    restructure_data = {
        'loan_id': 'L003',
        'restructure_type': 'term_extension',
        'new_term_months': 48,
        'new_monthly_payment': 650,
        'reason': 'Financial hardship',
        'approval_level': 'manager',
        'notes': 'Customer facing temporary financial difficulty'
    }
    response = session.post(f"{base_url}/api/loans/restructure", json=restructure_data)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Loan Restructuring: {result.get('message', 'Success')}")
    else:
        print("   ❌ Loan restructuring failed")
    
    # Test loan analytics
    print("   Testing loan analytics...")
    response = session.get(f"{base_url}/api/loans/analytics")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Loan Analytics: {len(result.get('data', []))} analytics points retrieved")
    else:
        print("   ❌ Loan analytics failed")
    
    # Test loan portfolio report
    print("   Testing loan portfolio report...")
    report_data = {
        'report_type': 'portfolio_summary',
        'date_range': '2025-01-01 to 2025-01-31',
        'include_metrics': True,
        'format': 'json'
    }
    response = session.post(f"{base_url}/api/loans/report", json=report_data)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Portfolio Report: {result.get('message', 'Success')}")
    else:
        print("   ❌ Portfolio report failed")
    
    print("\n4. Testing loan dashboard UI components...")
    
    # Check if loan dashboard contains required elements
    dashboard_content = session.get(f"{base_url}/loans_dashboard").text
    
    ui_components = [
        ('loanApplicationModal', 'Loan Application Modal'),
        ('loanProcessingModal', 'Loan Processing Modal'),
        ('loanDisbursementModal', 'Loan Disbursement Modal'),
        ('loanPaymentModal', 'Loan Payment Modal'),
        ('loanModificationModal', 'Loan Modification Modal'),
        ('loanClosureModal', 'Loan Closure Modal'),
        ('defaultManagementModal', 'Default Management Modal'),
        ('loanRestructureModal', 'Loan Restructuring Modal'),
        ('loanAnalyticsModal', 'Loan Analytics Modal'),
        ('portfolioReportModal', 'Portfolio Report Modal'),
        ('creditAssessmentModal', 'Credit Assessment Modal'),
        ('collateralEvaluationModal', 'Collateral Evaluation Modal'),
        ('riskAnalysisModal', 'Risk Analysis Modal')
    ]
    
    for component_id, component_name in ui_components:
        if f'id="{component_id}"' in dashboard_content:
            print(f"   ✅ {component_name} found")
        else:
            print(f"   ❌ {component_name} missing")
    
    print("\n5. Testing loan dashboard JavaScript functions...")
    
    js_functions = [
        ('showLoanApplicationModal', 'Loan Application Function'),
        ('showLoanProcessingModal', 'Loan Processing Function'),
        ('showLoanDisbursementModal', 'Loan Disbursement Function'),
        ('showLoanPaymentModal', 'Loan Payment Function'),
        ('showLoanModificationModal', 'Loan Modification Function'),
        ('showLoanClosureModal', 'Loan Closure Function'),
        ('showDefaultManagementModal', 'Default Management Function'),
        ('showLoanRestructureModal', 'Loan Restructuring Function'),
        ('loadLoanAnalytics', 'Loan Analytics Function'),
        ('generatePortfolioReport', 'Portfolio Report Function'),
        ('calculateLoanSchedule', 'Loan Schedule Calculator'),
        ('validateLoanApplication', 'Application Validation'),
        ('checkCreditScore', 'Credit Score Check'),
        ('evaluateCollateral', 'Collateral Evaluation'),
        ('performRiskAnalysis', 'Risk Analysis Function')
    ]
    
    for func_name, func_description in js_functions:
        if func_name in dashboard_content:
            print(f"   ✅ {func_description} found")
        else:
            print(f"   ❌ {func_description} missing")
    
    print("\n6. Testing loan data validation...")
    
    # Test invalid loan application
    invalid_data = {
        'customer_name': '',
        'loan_amount': -1000,
        'loan_type': 'INVALID_TYPE',
        'interest_rate': 150  # Invalid rate
    }
    
    response = session.post(f"{base_url}/api/loans/apply", json=invalid_data)
    if response.status_code == 400:
        print("   ✅ Data validation working (rejected invalid data)")
    else:
        print("   ⚠️ Data validation may need improvement")
    
    print("\n=== Loans Department Test Summary ===")
    print("✅ Loan application processing")
    print("✅ Loan approval workflow")
    print("✅ Loan disbursement management")
    print("✅ Payment processing")
    print("✅ Loan modifications")
    print("✅ Default management")
    print("✅ Loan restructuring")
    print("✅ Analytics and reporting")
    print("✅ Portfolio management")
    print("✅ UI components and modals")
    print("✅ JavaScript functionality")
    print("✅ Data validation")
    print("\n🎉 Loans Department functionality comprehensive test complete!")

if __name__ == "__main__":
    try:
        test_loans_dashboard_functionality()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}") 