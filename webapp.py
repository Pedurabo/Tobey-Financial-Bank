from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify, Response
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from typing import Optional
from datetime import datetime, timedelta
from src.services.employee_service import EmployeeService
from src.utils.database import DatabaseManager
from src.models.employee import Department, Role
import os
import time
import random

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'tobeyfinancebanksecret')

# Add Content Security Policy headers
@app.after_request
def add_security_headers(response):
    # Development mode - very permissive CSP to allow all necessary functionality
    if app.debug:
        response.headers['Content-Security-Policy'] = (
            "default-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
            "https://code.jquery.com https://cdn.jsdelivr.net https://cdn.datatables.net "
            "https://cdnjs.cloudflare.com https://unpkg.com https://cdn.jsdelivr.net "
            "https://cdnjs.cloudflare.com https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' "
            "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://cdn.datatables.net "
            "https://unpkg.com; "
            "font-src 'self' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://unpkg.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "worker-src 'self' blob:; "
            "child-src 'self' blob:;"
        )
    else:
        # Production mode - more restrictive CSP
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
            "https://code.jquery.com https://cdn.jsdelivr.net https://cdn.datatables.net "
            "https://cdnjs.cloudflare.com https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' "
            "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://cdn.datatables.net "
            "https://unpkg.com; "
            "font-src 'self' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://unpkg.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
    return response

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # type: ignore

db = DatabaseManager()
employee_service = EmployeeService(db)

# Initialize default admin accounts if no employees exist
def initialize_default_accounts():
    """Create default admin accounts if no employees exist"""
    all_employees = employee_service.get_all_employees()
    if not all_employees:
        print("No employees found. Creating default admin accounts...")
        
        # Create admin accounts for each department
        default_accounts = [
            {
                'username': 'admin_hr',
                'password': 'admin123',
                'first_name': 'HR',
                'last_name': 'Administrator',
                'email': 'hr.admin@tobeyfinance.com',
                'department': Department.AdminHR,
                'role': Role.ADMIN
            },
            {
                'username': 'admin_accounts',
                'password': 'admin123',
                'first_name': 'Accounts',
                'last_name': 'Administrator',
                'email': 'accounts.admin@tobeyfinance.com',
                'department': Department.Accounts,
                'role': Role.ADMIN
            },
            {
                'username': 'admin_loans',
                'password': 'admin123',
                'first_name': 'Loans',
                'last_name': 'Administrator',
                'email': 'loans.admin@tobeyfinance.com',
                'department': Department.Loans,
                'role': Role.ADMIN
            },
            {
                'username': 'admin_customer_service',
                'password': 'admin123',
                'first_name': 'Customer Service',
                'last_name': 'Administrator',
                'email': 'customerservice.admin@tobeyfinance.com',
                'department': Department.CustomerService,
                'role': Role.ADMIN
            },
            {
                'username': 'admin_teller',
                'password': 'admin123',
                'first_name': 'Teller',
                'last_name': 'Administrator',
                'email': 'teller.admin@tobeyfinance.com',
                'department': Department.Teller,
                'role': Role.ADMIN
            },
            {
                'username': 'admin_audit',
                'password': 'admin123',
                'first_name': 'Audit',
                'last_name': 'Administrator',
                'email': 'audit.admin@tobeyfinance.com',
                'department': Department.Audit,
                'role': Role.ADMIN
            },
            {
                'username': 'admin_it',
                'password': 'admin123',
                'first_name': 'IT',
                'last_name': 'Administrator',
                'email': 'it.admin@tobeyfinance.com',
                'department': Department.IT,
                'role': Role.ADMIN
            },
            {
                'username': 'admin_risk',
                'password': 'admin123',
                'first_name': 'Risk',
                'last_name': 'Administrator',
                'email': 'risk.admin@tobeyfinance.com',
                'department': Department.Risk,
                'role': Role.ADMIN
            },
            {
                'username': 'admin_marketing',
                'password': 'admin123',
                'first_name': 'Marketing',
                'last_name': 'Administrator',
                'email': 'marketing.admin@tobeyfinance.com',
                'department': Department.Marketing,
                'role': Role.ADMIN
            },
            {
                'username': 'admin_treasury',
                'password': 'admin123',
                'first_name': 'Treasury',
                'last_name': 'Administrator',
                'email': 'treasury.admin@tobeyfinance.com',
                'department': Department.Treasury,
                'role': Role.ADMIN
            }
        ]
        
        for account in default_accounts:
            employee_service.create_employee(
                username=account['username'],
                password=account['password'],
                first_name=account['first_name'],
                last_name=account['last_name'],
                email=account['email'],
                department=account['department'],
                role=account['role']
            )
            print(f"Created admin account: {account['username']} (Password: {account['password']})")
        
        print("\nDefault admin accounts created successfully!")
        print("You can now log in with any of these accounts:")
        for account in default_accounts:
            print(f"  Username: {account['username']}, Password: {account['password']}")

# Initialize default accounts when app starts
initialize_default_accounts()

# Helper to get enum from name or value
def get_enum_value(enum_class, value):
    try:
        return enum_class[value]
    except (KeyError, ValueError):
        for member in enum_class:
            if member.value == value:
                return member
    raise ValueError(f"Invalid value for {enum_class.__name__}: {value}")

class WebEmployee(UserMixin):
    def __init__(self, employee):
        self.employee = employee
        self.id = employee.employee_id
        self.username = employee.username
        self.role = employee.role
        self.department = employee.department
        self._is_active = employee.is_active
        self.full_name = employee.full_name()

    def get_id(self):
        return self.id
    
    @property
    def is_active(self):
        return self._is_active

@login_manager.user_loader
def load_user(user_id):
    emp = employee_service.get_employee(user_id)
    if emp:
        return WebEmployee(emp)
    return None

@app.template_filter('commafy')
def commafy(value):
    try:
        return "{:,}".format(int(value))
    except Exception:
        return value

@app.route('/test')
def test_modal():
    return render_template('test_modal.html')

@app.route('/')
@login_required
def dashboard():
    # Redirect customers to their dashboard
    if current_user.role == Role.CUSTOMER:
        return redirect(url_for('customer_dashboard'))
    
    # Get dashboard statistics
    all_employees = employee_service.get_all_employees()
    active_employees = [emp for emp in all_employees if emp.is_active]
    departments = set(emp.department for emp in all_employees)
    
    # Mock data for missing template variables
    dashboard_data = {
        'employee_count': len(all_employees),
        'active_employees': len(active_employees),
        'department_count': len(departments),
        'recent_logins': len([emp for emp in all_employees if emp.last_login]),
        'active_accounts': 2847,  # Mock data
        'recent_activities': [
            {
                'timestamp': '2025-07-13 19:03:27',
                'user': 'admin_teller',
                'action': 'Login',
                'details': 'User logged in successfully'
            },
            {
                'timestamp': '2025-07-13 19:02:25',
                'user': 'admin_teller',
                'action': 'Dashboard Access',
                'details': 'Accessed main dashboard'
            },
            {
                'timestamp': '2025-07-13 19:01:20',
                'user': 'admin_teller',
                'action': 'Login',
                'details': 'User logged in successfully'
            }
        ]
    }
    
    return render_template('dashboard.html', user=current_user, **dashboard_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Login attempt: username={username}")  # Debug log
        emp = employee_service.authenticate(username, password)
        print(f"Authentication result: {emp is not None}")  # Debug log
        if emp:
            print(f"Employee found: {emp.username}, role: {emp.role.value}, dept: {emp.department.value}")  # Debug log
        if emp and emp.is_active:
            print(f"Login successful for {username}")  # Debug log
            web_emp = WebEmployee(emp)
            print(f"WebEmployee created: {web_emp.get_id()}")  # Debug log
            login_user(web_emp)
            print(f"User logged in: {current_user.is_authenticated if hasattr(current_user, 'is_authenticated') else 'N/A'}")  # Debug log
            flash('Logged in successfully.', 'success')
            
            # Redirect teller users to teller dashboard
            if emp.department == Department.Teller:
                return redirect(url_for('teller_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            print(f"Login failed for {username}")  # Debug log
            flash('Invalid credentials or inactive account.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    user_profile = {
        'employee_id': current_user.id,
        'username': current_user.username,
        'full_name': current_user.full_name,
        'first_name': current_user.employee.first_name,
        'last_name': current_user.employee.last_name,
        'email': current_user.employee.email,
        'department': current_user.department.value,
        'role': current_user.role.value,
        'is_active': current_user.is_active,
        'created_date': current_user.employee.created_date,
        'last_login': current_user.employee.last_login,
        'account_number': current_user.employee.account_number,
        'account_balance': current_user.employee.account_balance,
        'account_type': current_user.employee.account_type
    }
    
    # Get login history and activity
    activity_log = [
        {'date': '2025-01-15 08:30:00', 'action': 'Login', 'ip': '192.168.1.100', 'status': 'Success'},
        {'date': '2025-01-14 17:45:00', 'action': 'Password Change', 'ip': '192.168.1.100', 'status': 'Success'},
        {'date': '2025-01-14 09:15:00', 'action': 'Login', 'ip': '192.168.1.100', 'status': 'Success'},
        {'date': '2025-01-13 16:20:00', 'action': 'Profile Update', 'ip': '192.168.1.100', 'status': 'Success'},
        {'date': '2025-01-13 08:00:00', 'action': 'Login', 'ip': '192.168.1.100', 'status': 'Success'}
    ]
    
    return render_template('profile.html', user=current_user, profile=user_profile, activity_log=activity_log)

@app.route('/profile/edit')
@login_required
def edit_profile():
    """Edit profile page"""
    user_profile = {
        'employee_id': current_user.id,
        'username': current_user.username,
        'first_name': current_user.employee.first_name,
        'last_name': current_user.employee.last_name,
        'email': current_user.employee.email,
        'department': current_user.department.value,
        'role': current_user.role.value
    }
    
    return render_template('profile_edit.html', user=current_user, profile=user_profile)

# Profile Management API Endpoints
@app.route('/api/profile/update', methods=['POST'])
@login_required
def api_update_profile():
    """Update user profile information"""
    data = request.get_json()
    
    # Get current employee
    employee = employee_service.get_employee(current_user.id)
    if not employee:
        return jsonify({'success': False, 'message': 'Employee not found'}), 404
    
    # Update allowed fields
    if 'first_name' in data and data['first_name'].strip():
        employee.first_name = data['first_name'].strip()
    
    if 'last_name' in data and data['last_name'].strip():
        employee.last_name = data['last_name'].strip()
    
    if 'email' in data and data['email'].strip():
        # Validate email format
        if '@' not in data['email']:
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400
        employee.email = data['email'].strip()
    
    try:
        # Save to database
        db.update_employee(employee.to_dict())
        
        # Update employees cache
        employee_service.employees[employee.employee_id] = employee
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'profile': {
                'first_name': employee.first_name,
                'last_name': employee.last_name,
                'email': employee.email,
                'full_name': employee.full_name()
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating profile: {str(e)}'}), 500

@app.route('/api/profile/change-password', methods=['POST'])
@login_required
def api_change_password():
    """Change user password"""
    data = request.get_json()
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    
    if not all([current_password, new_password, confirm_password]):
        return jsonify({'success': False, 'message': 'All password fields are required'}), 400
    
    if new_password != confirm_password:
        return jsonify({'success': False, 'message': 'New passwords do not match'}), 400
    
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters long'}), 400
    
    # Get current employee
    employee = employee_service.get_employee(current_user.id)
    if not employee:
        return jsonify({'success': False, 'message': 'Employee not found'}), 404
    
    # Verify current password
    from src.utils.security import SecurityManager
    security = SecurityManager()
    
    if not security.verify_password(current_password, employee.password_hash.encode('utf-8')):
        return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400
    
    try:
        # Hash new password
        new_password_hash = security.hash_password(new_password).decode('utf-8')
        employee.password_hash = new_password_hash
        
        # Save to database
        db.update_employee(employee.to_dict())
        
        # Update employees cache
        employee_service.employees[employee.employee_id] = employee
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error changing password: {str(e)}'}), 500

@app.route('/api/profile/preferences', methods=['GET', 'POST'])
@login_required
def api_user_preferences():
    """Get or update user preferences"""
    if request.method == 'GET':
        # Get user preferences (stored in session for now, could be in database)
        preferences = session.get('user_preferences', {
            'theme': 'light',
            'language': 'en',
            'timezone': 'UTC',
            'notifications_email': True,
            'notifications_sms': False,
            'dashboard_layout': 'default',
            'currency_display': 'USD',
            'date_format': 'MM/DD/YYYY',
            'number_format': 'US'
        })
        
        return jsonify({
            'success': True,
            'preferences': preferences
        })
    
    elif request.method == 'POST':
        data = request.get_json()
        
        # Get current preferences
        preferences = session.get('user_preferences', {})
        
        # Update preferences
        allowed_preferences = [
            'theme', 'language', 'timezone', 'notifications_email', 
            'notifications_sms', 'dashboard_layout', 'currency_display',
            'date_format', 'number_format'
        ]
        
        for key, value in data.items():
            if key in allowed_preferences:
                preferences[key] = value
        
        # Save preferences to session
        session['user_preferences'] = preferences
        
        return jsonify({
            'success': True,
            'message': 'Preferences updated successfully',
            'preferences': preferences
        })

@app.route('/api/profile/activity', methods=['GET'])
@login_required
def api_user_activity():
    """Get user activity log"""
    # Mock activity data - in real system, this would come from audit logs
    activity_log = [
        {
            'id': 1,
            'timestamp': '2025-01-15 08:30:00',
            'action': 'Login',
            'details': 'Successful login from 192.168.1.100',
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'status': 'Success'
        },
        {
            'id': 2,
            'timestamp': '2025-01-14 17:45:00',
            'action': 'Password Change',
            'details': 'Password changed successfully',
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'status': 'Success'
        },
        {
            'id': 3,
            'timestamp': '2025-01-14 09:15:00',
            'action': 'Login',
            'details': 'Successful login from 192.168.1.100',
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'status': 'Success'
        },
        {
            'id': 4,
            'timestamp': '2025-01-13 16:20:00',
            'action': 'Profile Update',
            'details': 'Profile information updated',
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'status': 'Success'
        },
        {
            'id': 5,
            'timestamp': '2025-01-13 08:00:00',
            'action': 'Login',
            'details': 'Successful login from 192.168.1.100',
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'status': 'Success'
        }
    ]
    
    return jsonify({
        'success': True,
        'activity_log': activity_log
    })

@app.route('/api/profile/security', methods=['GET'])
@login_required
def api_security_info():
    """Get user security information"""
    employee = employee_service.get_employee(current_user.id)
    if not employee:
        return jsonify({'success': False, 'message': 'Employee not found'}), 404
    
    security_info = {
        'last_password_change': '2025-01-14 17:45:00',  # Mock data
        'login_attempts_today': 3,
        'failed_login_attempts': 0,
        'account_locked': False,
        'two_factor_enabled': False,
        'security_questions_set': True,
        'last_login_ip': '192.168.1.100',
        'active_sessions': 1,
        'account_creation_date': employee.created_date.isoformat() if employee.created_date else None,
        'last_activity': employee.last_login.isoformat() if employee.last_login else None
    }
    
    return jsonify({
        'success': True,
        'security_info': security_info
    })

@app.route('/api/profile/export', methods=['GET'])
@login_required
def api_export_profile():
    """Export user profile data"""
    employee = employee_service.get_employee(current_user.id)
    if not employee:
        return jsonify({'success': False, 'message': 'Employee not found'}), 404
    
    # Prepare export data
    export_data = {
        'profile_export': {
            'export_date': datetime.now().isoformat(),
            'employee_id': employee.employee_id,
            'username': employee.username,
            'full_name': employee.full_name(),
            'email': employee.email,
            'department': employee.department.value,
            'role': employee.role.value,
            'account_creation_date': employee.created_date.isoformat() if employee.created_date else None,
            'last_login': employee.last_login.isoformat() if employee.last_login else None,
            'is_active': employee.is_active
        },
        'preferences': session.get('user_preferences', {}),
        'note': 'This export contains your personal data as stored in our system.'
    }
    
    return jsonify({
        'success': True,
        'message': 'Profile data exported successfully',
        'export_data': export_data
    })

@app.route('/manage_employees')
@login_required
def manage_employees():
    if not (current_user.role.value == 'admin' and current_user.department.value == 'Admin/HR Department'):
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('dashboard'))
    
    employees = employee_service.get_all_employees()
    return render_template('manage_employees.html', employees=employees)

@app.route('/audit_logs')
@login_required
def audit_logs():
    if not (current_user.role.value == 'admin' and current_user.department.value == 'Admin/HR Department'):
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('dashboard'))
    
    # This would need audit service integration
    return render_template('audit_logs.html')

@app.route('/accounts_dashboard')
@login_required
def accounts_dashboard():
    """Accounts Department Dashboard with banking functionality"""
    # Only allow Accounts Department users OR HR admins (system-wide access)
    if not (current_user.department.value == 'Accounts Department' or 
            (current_user.department.value == 'Admin/HR Department' and current_user.role.value == 'admin')):
        flash('Access denied. Only Accounts Department personnel can access this page.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get accounts statistics
    all_employees = employee_service.get_all_employees()
    accounts_employees = [emp for emp in all_employees if emp.department.value == 'Accounts Department']
    
    dashboard_data = {
        'total_accounts': len(accounts_employees),
        'active_accounts': len([emp for emp in accounts_employees if emp.is_active]),
        'pending_transactions': 15,  # Mock data
        'total_balance': 2500000,   # Mock data
        'daily_transactions': 45     # Mock data
    }
    
    return render_template('accounts_dashboard.html', user=current_user, **dashboard_data)

@app.route('/customer_dashboard')
@login_required
def customer_dashboard():
    """Customer Dashboard with banking functionality"""
    # Only allow customers
    if not current_user.role.value == 'customer':
        flash('Access denied. Only customers can access this page.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get customer data
    customer = employee_service.get_employee(current_user.id)
    # Mock data for demonstration
    accounts = [
        {'type': 'Checking', 'number': '1234567890', 'balance': 15234.55, 'currency': 'USD', 'status': 'Active'},
        {'type': 'Savings', 'number': '9876543210', 'balance': 3200.00, 'currency': 'USD', 'status': 'Active'}
    ]
    cards = [
        {'type': 'Visa Debit', 'number': '**** 1234', 'expiry': '12/26', 'status': 'Active'},
        {'type': 'Mastercard Credit', 'number': '**** 5678', 'expiry': '08/25', 'status': 'Blocked'}
    ]
    loans = [
        {'id': 'LN001', 'type': 'Personal Loan', 'amount': 10000.0, 'status': 'Active', 'balance': 7500.0, 'emi': 250.0, 'next_due': '2025-08-01'}
    ]
    payees = [
        {'name': 'Jane Doe', 'account': '111122223333', 'bank': 'Bank of America'},
        {'name': 'Electric Company', 'account': '555566667777', 'bank': 'Utility Bank'}
    ]
    recent_transactions = [
        {'date': '2025-07-13', 'account': '1234567890', 'type': 'Deposit', 'amount': 2000.0, 'description': 'Paycheck', 'balance': 15234.55},
        {'date': '2025-07-12', 'account': '1234567890', 'type': 'Withdrawal', 'amount': -100.0, 'description': 'ATM Withdrawal', 'balance': 13234.55},
        {'date': '2025-07-11', 'account': '9876543210', 'type': 'Transfer', 'amount': 500.0, 'description': 'Transfer from Checking', 'balance': 3200.00},
        {'date': '2025-07-10', 'account': '1234567890', 'type': 'Payment', 'amount': -75.0, 'description': 'Electricity Bill', 'balance': 13434.55}
    ]
    all_transactions = recent_transactions + [
        {'date': '2025-07-09', 'account': '1234567890', 'type': 'Deposit', 'amount': 1000.0, 'description': 'Gift', 'balance': 12000.00},
        {'date': '2025-07-08', 'account': '9876543210', 'type': 'Withdrawal', 'amount': -50.0, 'description': 'ATM Withdrawal', 'balance': 3150.00}
    ]
    profile = {
        'name': f'{customer.first_name} {customer.last_name}',
        'email': customer.email,
        'phone': '+1-555-123-4567',
        'address': '123 Main St, Springfield, USA',
        'last_login': customer.last_login
    }
    support_tickets = [
        {'id': 'T001', 'subject': 'Card not working', 'status': 'Open', 'created': '2025-07-10'},
        {'id': 'T002', 'subject': 'Loan statement request', 'status': 'Closed', 'created': '2025-06-20'}
    ]
    notifications = [
        {'type': 'alert', 'message': 'Low balance on Savings account', 'date': '2025-07-12'},
        {'type': 'reminder', 'message': 'Loan EMI due soon', 'date': '2025-07-15'}
    ]
    analytics = {
        'monthly_spending': 1200.0,
        'monthly_income': 2000.0,
        'category_breakdown': {'Food': 300, 'Utilities': 200, 'Shopping': 400, 'Other': 300},
        'savings_goal': {'target': 5000, 'current': 3200}
    }
    return render_template('customer_dashboard.html',
        customer=customer,
        accounts=accounts,
        cards=cards,
        loans=loans,
        payees=payees,
        recent_transactions=recent_transactions,
        all_transactions=all_transactions,
        profile=profile,
        support_tickets=support_tickets,
        notifications=notifications,
        analytics=analytics
    )

@app.route('/customer_dashboard_v2')
@login_required
def customer_dashboard_v2():
    """Modern customer dashboard with real-life banking features"""
    if current_user.role != Role.CUSTOMER:
        flash('Access denied. This dashboard is for customers only.', 'error')
        return redirect(url_for('dashboard'))

    # Realistic mock data
    customer = employee_service.get_employee(current_user.id)
    accounts = [
        {'type': 'Checking', 'number': '1234567890', 'balance': 15234.55, 'currency': 'USD', 'status': 'Active'},
        {'type': 'Savings', 'number': '9876543210', 'balance': 3200.00, 'currency': 'USD', 'status': 'Active'}
    ]
    recent_transactions = [
        {'date': '2025-07-13', 'account': '1234567890', 'type': 'Deposit', 'amount': 2000.0, 'description': 'Paycheck', 'balance': 15234.55},
        {'date': '2025-07-12', 'account': '1234567890', 'type': 'Withdrawal', 'amount': -100.0, 'description': 'ATM Withdrawal', 'balance': 13234.55},
        {'date': '2025-07-11', 'account': '9876543210', 'type': 'Transfer', 'amount': 500.0, 'description': 'Transfer from Checking', 'balance': 3200.00},
        {'date': '2025-07-10', 'account': '1234567890', 'type': 'Payment', 'amount': -75.0, 'description': 'Electricity Bill', 'balance': 13434.55}
    ]
    cards = [
        {'type': 'Visa Debit', 'number': '**** 1234', 'expiry': '12/26', 'status': 'Active'},
        {'type': 'Mastercard Credit', 'number': '**** 5678', 'expiry': '08/25', 'status': 'Blocked'}
    ]
    loans = [
        {'id': 'LN001', 'type': 'Personal Loan', 'amount': 10000.0, 'status': 'Active', 'balance': 7500.0, 'emi': 250.0, 'next_due': '2025-08-01'}
    ]
    payees = [
        {'name': 'Jane Doe', 'account': '111122223333', 'bank': 'Bank of America'},
        {'name': 'Electric Company', 'account': '555566667777', 'bank': 'Utility Bank'}
    ]
    support_tickets = [
        {'id': 'T001', 'subject': 'Card not working', 'status': 'Open', 'created': '2025-07-10'},
        {'id': 'T002', 'subject': 'Loan statement request', 'status': 'Closed', 'created': '2025-06-20'}
    ]
    profile = {
        'name': f'{customer.first_name} {customer.last_name}',
        'email': customer.email,
        'phone': '+1-555-123-4567',
        'address': '123 Main St, Springfield, USA',
        'last_login': customer.last_login
    }
    return render_template('customer_dashboard_v2.html',
        customer=customer,
        accounts=accounts,
        recent_transactions=recent_transactions,
        cards=cards,
        loans=loans,
        payees=payees,
        support_tickets=support_tickets,
        profile=profile
    )

# Customer API Endpoints
@app.route('/api/customer/transfer', methods=['POST'])
@login_required
def api_customer_transfer():
    """Process customer money transfer"""
    if current_user.role != Role.CUSTOMER:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    recipient_account = data.get('recipient_account')
    recipient_name = data.get('recipient_name')
    amount = data.get('amount')
    description = data.get('description', '')
    
    if not all([recipient_account, recipient_name, amount]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Mock transfer processing
    return jsonify({
        'success': True,
        'message': f'Successfully transferred ${amount:.2f} to {recipient_name}',
        'transaction_id': f'TXN{int(time.time())}'
    })

@app.route('/api/customer/deposit', methods=['POST'])
@login_required
def api_customer_deposit():
    """Process customer deposit"""
    if current_user.role != Role.CUSTOMER:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    amount = data.get('amount')
    source = data.get('source')
    description = data.get('description', '')
    
    if not all([amount, source]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Mock deposit processing
    return jsonify({
        'success': True,
        'message': f'Successfully deposited ${amount:.2f}',
        'transaction_id': f'DEP{int(time.time())}'
    })

@app.route('/api/customer/withdraw', methods=['POST'])
@login_required
def api_customer_withdraw():
    """Process customer withdrawal"""
    if current_user.role != Role.CUSTOMER:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    amount = data.get('amount')
    method = data.get('method')
    description = data.get('description', '')
    
    if not all([amount, method]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Mock withdrawal processing
    return jsonify({
        'success': True,
        'message': f'Successfully withdrew ${amount:.2f}',
        'transaction_id': f'WTH{int(time.time())}'
    })

@app.route('/api/customer/loan/apply', methods=['POST'])
@login_required
def api_customer_loan_apply():
    """Submit customer loan application"""
    if current_user.role != Role.CUSTOMER:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    loan_type = data.get('loan_type')
    amount = data.get('amount')
    term = data.get('term')
    purpose = data.get('purpose')
    monthly_income = data.get('monthly_income')
    additional_info = data.get('additional_info', '')
    
    if not all([loan_type, amount, term, purpose, monthly_income]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Mock loan application processing
    application_id = f'LOAN{int(time.time())}'
    return jsonify({
        'success': True,
        'message': 'Loan application submitted successfully!',
        'application_id': application_id,
        'status': 'pending'
    })

@app.route('/api/customer/support/ticket', methods=['POST'])
@login_required
def api_customer_support_ticket():
    """Submit customer support ticket"""
    if current_user.role != Role.CUSTOMER:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    category = data.get('category')
    priority = data.get('priority')
    subject = data.get('subject')
    description = data.get('description')
    contact_preference = data.get('contact_preference', 'email')
    
    if not all([category, priority, subject, description]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Mock support ticket processing
    ticket_id = f'T{int(time.time())}'
    return jsonify({
        'success': True,
        'message': 'Support ticket submitted successfully!',
        'ticket_id': ticket_id,
        'status': 'open'
    })

@app.route('/api/customer/statement/generate', methods=['POST'])
@login_required
def api_customer_generate_statement():
    """Generate customer bank statement"""
    if current_user.role != Role.CUSTOMER:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    from_date = data.get('from_date')
    to_date = data.get('to_date')
    format_type = data.get('format', 'pdf')
    
    if not all([from_date, to_date]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Mock statement generation
    statement_id = f'STMT{int(time.time())}'
    return jsonify({
        'success': True,
        'message': 'Statement generated successfully!',
        'statement_id': statement_id,
        'download_url': f'/api/customer/statement/download/{statement_id}'
    })

@app.route('/api/customer/card/add', methods=['POST'])
@login_required
def api_customer_add_card():
    """Add new card for customer"""
    if current_user.role != Role.CUSTOMER:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    card_type = data.get('card_type')
    account_type = data.get('account_type')
    limit = data.get('limit')
    
    if not all([card_type, account_type, limit]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Mock card addition
    card_id = f'CARD{int(time.time())}'
    return jsonify({
        'success': True,
        'message': 'New card added successfully!',
        'card_id': card_id,
        'estimated_delivery': '7-10 business days'
    })

# Loan Processing API Endpoints
@app.route('/api/loan_applications', methods=['GET'])
@login_required
def api_get_loan_applications():
    """Get all loan applications"""
    if not (current_user.department.value == 'Loans Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    # Mock loan applications data
    applications = [
        {
            'id': 'L001', 'customer_name': 'John Smith', 'customer_email': 'john.smith@email.com',
            'amount': 25000, 'type': 'Personal', 'term': 36, 'interest_rate': 8.5,
            'status': 'Pending', 'application_date': '2024-01-15', 'purpose': 'Home renovation',
            'monthly_payment': 790, 'total_payment': 28440, 'credit_score': 720
        },
        {
            'id': 'L002', 'customer_name': 'Sarah Johnson', 'customer_email': 'sarah.j@email.com',
            'amount': 150000, 'type': 'Mortgage', 'term': 240, 'interest_rate': 4.2,
            'status': 'Approved', 'application_date': '2024-01-10', 'purpose': 'Home purchase',
            'monthly_payment': 920, 'total_payment': 220800, 'credit_score': 780
        },
        {
            'id': 'L003', 'customer_name': 'Mike Davis', 'customer_email': 'mike.davis@email.com',
            'amount': 50000, 'type': 'Business', 'term': 60, 'interest_rate': 6.8,
            'status': 'Under Review', 'application_date': '2024-01-12', 'purpose': 'Business expansion',
            'monthly_payment': 990, 'total_payment': 59400, 'credit_score': 690
        },
        {
            'id': 'L004', 'customer_name': 'Lisa Wilson', 'customer_email': 'lisa.w@email.com',
            'amount': 75000, 'type': 'Auto', 'term': 72, 'interest_rate': 5.5,
            'status': 'Approved', 'application_date': '2024-01-08', 'purpose': 'Vehicle purchase',
            'monthly_payment': 1220, 'total_payment': 87840, 'credit_score': 750
        },
        {
            'id': 'L005', 'customer_name': 'David Brown', 'customer_email': 'david.brown@email.com',
            'amount': 30000, 'type': 'Personal', 'term': 48, 'interest_rate': 9.2,
            'status': 'Rejected', 'application_date': '2024-01-05', 'purpose': 'Debt consolidation',
            'monthly_payment': 750, 'total_payment': 36000, 'credit_score': 650
        }
    ]
    
    return jsonify({'success': True, 'applications': applications})

@app.route('/api/loan_application/<loan_id>', methods=['GET'])
@login_required
def api_get_loan_application(loan_id):
    """Get specific loan application details"""
    if not (current_user.department.value == 'Loans Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    # Mock loan application data
    application = {
        'id': loan_id,
        'customer_name': 'John Smith',
        'customer_email': 'john.smith@email.com',
        'customer_phone': '+1-555-0123',
        'customer_address': '123 Main St, City, State 12345',
        'amount': 25000,
        'type': 'Personal',
        'term': 36,
        'interest_rate': 8.5,
        'status': 'Pending',
        'application_date': '2024-01-15',
        'purpose': 'Home renovation',
        'monthly_payment': 790,
        'total_payment': 28440,
        'credit_score': 720,
        'income': 75000,
        'employment': 'Software Engineer',
        'employer': 'Tech Corp',
        'documents': [
            {'name': 'ID Document', 'status': 'Verified'},
            {'name': 'Income Statement', 'status': 'Pending'},
            {'name': 'Bank Statements', 'status': 'Verified'},
            {'name': 'Credit Report', 'status': 'Verified'}
        ],
        'notes': [
            {'date': '2024-01-15', 'user': 'admin_loans', 'note': 'Application received'},
            {'date': '2024-01-16', 'user': 'admin_loans', 'note': 'Documents under review'},
            {'date': '2024-01-17', 'user': 'admin_loans', 'note': 'Credit check completed'}
        ]
    }
    
    return jsonify({'success': True, 'application': application})

# Customer Service API Endpoints
@app.route('/api/customers', methods=['GET'])
@login_required
def api_get_customers():
    """Get all customers"""
    if not (current_user.department.value == 'Customer Service Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    # Mock customers data
    customers = [
        {
            'id': 'C001', 'name': 'John Smith', 'email': 'john.smith@email.com',
            'phone': '+1-555-0123', 'account_number': 'ACC001234', 'balance': 25000,
            'status': 'active', 'account_type': 'savings', 'created_date': '2023-01-15',
            'last_activity': '2024-01-15', 'address': '123 Main St, City, State 12345'
        },
        {
            'id': 'C002', 'name': 'Sarah Johnson', 'email': 'sarah.j@email.com',
            'phone': '+1-555-0124', 'account_number': 'ACC001235', 'balance': 150000,
            'status': 'active', 'account_type': 'checking', 'created_date': '2023-02-10',
            'last_activity': '2024-01-14', 'address': '456 Oak Ave, City, State 12345'
        },
        {
            'id': 'C003', 'name': 'Mike Davis', 'email': 'mike.davis@email.com',
            'phone': '+1-555-0125', 'account_number': 'ACC001236', 'balance': 50000,
            'status': 'pending', 'account_type': 'business', 'created_date': '2024-01-12',
            'last_activity': '2024-01-13', 'address': '789 Pine Rd, City, State 12345'
        },
        {
            'id': 'C004', 'name': 'Lisa Wilson', 'email': 'lisa.w@email.com',
            'phone': '+1-555-0126', 'account_number': 'ACC001237', 'balance': 75000,
            'status': 'active', 'account_type': 'premium', 'created_date': '2023-03-08',
            'last_activity': '2024-01-12', 'address': '321 Elm St, City, State 12345'
        },
        {
            'id': 'C005', 'name': 'David Brown', 'email': 'david.brown@email.com',
            'phone': '+1-555-0127', 'account_number': 'ACC001238', 'balance': 30000,
            'status': 'inactive', 'account_type': 'savings', 'created_date': '2023-04-05',
            'last_activity': '2024-01-10', 'address': '654 Maple Dr, City, State 12345'
        }
    ]
    
    return jsonify({'success': True, 'customers': customers})

@app.route('/api/customers', methods=['POST'])
@login_required
def api_create_customer():
    """Create new customer"""
    if not (current_user.department.value == 'Customer Service Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        
        # Mock customer creation
        new_customer = {
            'id': f'C{str(len(data) + 1).zfill(3)}',
            'name': f"{data.get('first_name', '')} {data.get('last_name', '')}",
            'email': data.get('email'),
            'phone': data.get('phone'),
            'account_number': f"ACC{str(int(time.time())).zfill(6)}",
            'balance': 0,
            'status': 'active',
            'account_type': data.get('account_type'),
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'last_activity': datetime.now().strftime('%Y-%m-%d'),
            'address': data.get('address')
        }
        
        return jsonify({
            'success': True,
            'message': 'Customer created successfully',
            'customer': new_customer
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/customers/<customer_id>', methods=['GET'])
@login_required
def api_get_customer(customer_id):
    """Get specific customer details"""
    if not (current_user.department.value == 'Customer Service Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    # Mock customer data
    customer = {
        'id': customer_id,
        'name': 'John Smith',
        'email': 'john.smith@email.com',
        'phone': '+1-555-0123',
        'address': '123 Main St, City, State 12345',
        'account_number': 'ACC001234',
        'balance': 25000,
        'status': 'active',
        'account_type': 'savings',
        'created_date': '2023-01-15',
        'last_activity': '2024-01-15',
        'transactions': [
            {'date': '2024-01-15', 'type': 'deposit', 'amount': 1000, 'description': 'Salary deposit'},
            {'date': '2024-01-14', 'type': 'withdrawal', 'amount': -500, 'description': 'ATM withdrawal'},
            {'date': '2024-01-13', 'type': 'transfer', 'amount': -200, 'description': 'Online transfer'},
            {'date': '2024-01-12', 'type': 'deposit', 'amount': 2500, 'description': 'Check deposit'}
        ],
        'loans': [
            {'id': 'L001', 'type': 'Personal', 'amount': 25000, 'status': 'active', 'balance': 15000},
            {'id': 'L002', 'type': 'Auto', 'amount': 15000, 'status': 'paid', 'balance': 0}
        ]
    }
    
    return jsonify({'success': True, 'customer': customer})

@app.route('/api/bank_statement', methods=['POST'])
@login_required
def api_generate_bank_statement():
    """Generate bank statement for customer"""
    if not (current_user.department.value == 'Customer Service Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        customer_id = data.get('customer_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        format_type = data.get('format', 'pdf')
        
        # Mock statement generation
        statement_data = {
            'customer_id': customer_id,
            'start_date': start_date,
            'end_date': end_date,
            'format': format_type,
            'transactions': [
                {'date': '2024-01-15', 'description': 'Salary deposit', 'amount': 1000, 'balance': 25000},
                {'date': '2024-01-14', 'description': 'ATM withdrawal', 'amount': -500, 'balance': 24000},
                {'date': '2024-01-13', 'description': 'Online transfer', 'amount': -200, 'balance': 24500},
                {'date': '2024-01-12', 'description': 'Check deposit', 'amount': 2500, 'balance': 24700}
            ]
        }
        
        return jsonify({
            'success': True,
            'message': 'Bank statement generated successfully',
            'statement': statement_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/process_loan', methods=['POST'])
@login_required
def api_process_loan():
    """Process loan application (approve/reject)"""
    if not (current_user.department.value == 'Loans Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        loan_id = data.get('loan_id')
        action = data.get('action')  # 'approve' or 'reject'
        notes = data.get('notes', '')
        
        # Mock processing
        if action == 'approve':
            return jsonify({
                'success': True, 
                'message': f'Loan {loan_id} approved successfully',
                'status': 'Approved'
            })
        elif action == 'reject':
            return jsonify({
                'success': True, 
                'message': f'Loan {loan_id} rejected',
                'status': 'Rejected'
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid action'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/add_loan_note', methods=['POST'])
@login_required
def api_add_loan_note():
    """Add note to loan application"""
    if not (current_user.department.value == 'Loans Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        loan_id = data.get('loan_id')
        note = data.get('note')
        
        # Mock note addition
        return jsonify({
            'success': True,
            'message': f'Note added to loan {loan_id}',
            'note': {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'user': current_user.username,
                'note': note
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/loan_analytics', methods=['GET'])
@login_required
def api_loan_analytics():
    """Get loan analytics data"""
    if not (current_user.department.value == 'Loans Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    analytics = {
        'total_applications': 1250,
        'approved_loans': 890,
        'rejected_loans': 210,
        'pending_loans': 150,
        'total_disbursed': 15000000,
        'average_processing_time': 3.2,  # days
        'approval_rate': 71.2,  # percentage
        'monthly_trends': [
            {'month': 'Jan', 'applications': 45, 'approvals': 38, 'amount': 2200000},
            {'month': 'Feb', 'applications': 52, 'approvals': 44, 'amount': 2500000},
            {'month': 'Mar', 'applications': 48, 'approvals': 41, 'amount': 2400000},
            {'month': 'Apr', 'applications': 55, 'approvals': 47, 'amount': 2800000},
            {'month': 'May', 'applications': 61, 'approvals': 52, 'amount': 3100000},
            {'month': 'Jun', 'applications': 58, 'approvals': 49, 'amount': 2900000}
        ],
        'loan_types': [
            {'type': 'Personal', 'count': 450, 'amount': 5400000, 'approval_rate': 75},
            {'type': 'Mortgage', 'count': 320, 'amount': 6400000, 'approval_rate': 68},
            {'type': 'Business', 'count': 280, 'amount': 2800000, 'approval_rate': 72},
            {'type': 'Auto', 'count': 200, 'amount': 400000, 'approval_rate': 80}
        ]
    }
    
    return jsonify({'success': True, 'analytics': analytics})

# Enhanced Loan API Endpoints
@app.route('/api/loans/apply', methods=['POST'])
@login_required
def api_apply_loan():
    """Submit a new loan application"""
    if not (current_user.department.value == 'Loans Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'})
        
        # Generate a unique application ID
        import uuid
        application_id = str(uuid.uuid4())[:8].upper()
        
        # In a real application, you would save this to a database
        # For now, we'll just return success
        return jsonify({
            'success': True, 
            'message': 'Loan application submitted successfully',
            'application_id': application_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/loans/<loan_id>', methods=['GET'])
@login_required
def api_get_loan_details(loan_id):
    """Get detailed information about a specific loan"""
    if not (current_user.department.value == 'Loans Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        # Mock loan data - in a real app, this would come from database
        loan_data = {
            'id': loan_id,
            'customer': 'John Doe',
            'email': 'john.doe@email.com',
            'phone': '+1-555-0123',
            'address': '123 Main St, City, State 12345',
            'amount': 25000,
            'type': 'Personal',
            'status': 'Pending',
            'income': 75000,
            'creditScore': 720,
            'purpose': 'Home renovation project',
            'term': 36,
            'interestRate': 8.5
        }
        
        return jsonify({'success': True, 'loan': loan_data})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/loans/<loan_id>/process', methods=['POST'])
@login_required
def api_process_loan_application(loan_id):
    """Process a loan application (approve/reject)"""
    if not (current_user.department.value == 'Loans Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'})
        
        action = data.get('action')
        notes = data.get('notes', '')
        priority = data.get('priority', 'normal')
        
        # In a real application, you would update the loan status in database
        # For now, we'll just return success
        return jsonify({
            'success': True,
            'message': f'Loan {loan_id} {action}d successfully',
            'action': action,
            'notes': notes
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Customer Service API Endpoints
@app.route('/api/support_tickets', methods=['GET'])
@login_required
def api_get_support_tickets():
    """Get all support tickets"""
    if not (current_user.department.value == 'Customer Service Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    # Mock support tickets data
    tickets = [
        {
            'id': 'T001', 'customer_id': 'C001', 'customer_name': 'John Smith',
            'issue_type': 'account_access', 'priority': 'high', 'status': 'open',
            'description': 'Cannot access online banking', 'created_date': '2024-01-15',
            'assigned_to': 'admin_customer_service', 'last_updated': '2024-01-15'
        },
        {
            'id': 'T002', 'customer_id': 'C002', 'customer_name': 'Sarah Johnson',
            'issue_type': 'transaction_issue', 'priority': 'medium', 'status': 'in_progress',
            'description': 'Transaction not showing in account', 'created_date': '2024-01-14',
            'assigned_to': 'admin_customer_service', 'last_updated': '2024-01-15'
        },
        {
            'id': 'T003', 'customer_id': 'C003', 'customer_name': 'Mike Davis',
            'issue_type': 'loan_inquiry', 'priority': 'low', 'status': 'resolved',
            'description': 'Loan application status inquiry', 'created_date': '2024-01-13',
            'assigned_to': 'admin_customer_service', 'last_updated': '2024-01-14'
        }
    ]
    
    return jsonify({'success': True, 'tickets': tickets})

@app.route('/api/support_tickets', methods=['POST'])
@login_required
def api_create_support_ticket():
    """Create new support ticket"""
    if not (current_user.department.value == 'Customer Service Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        
        # Mock ticket creation
        new_ticket = {
            'id': f'T{str(int(time.time())).zfill(3)}',
            'customer_id': data.get('customer_id'),
            'customer_name': data.get('customer_name', 'Unknown'),
            'issue_type': data.get('issue_type'),
            'priority': data.get('priority'),
            'status': 'open',
            'description': data.get('description'),
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'assigned_to': current_user.username,
            'last_updated': datetime.now().strftime('%Y-%m-%d')
        }
        
        return jsonify({
            'success': True,
            'message': 'Support ticket created successfully',
            'ticket': new_ticket
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/support_tickets/<ticket_id>', methods=['GET'])
@login_required
def api_get_support_ticket(ticket_id):
    """Get specific support ticket details"""
    if not (current_user.department.value == 'Customer Service Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    # Mock ticket details
    ticket_details = {
        'id': ticket_id,
        'customer_id': 'C001',
        'customer_name': 'John Smith',
        'issue_type': 'account_access',
        'priority': 'high',
        'status': 'open',
        'description': 'Cannot access online banking portal. Getting error message when trying to log in.',
        'created_date': '2024-01-15',
        'assigned_to': 'admin_customer_service',
        'last_updated': '2024-01-15',
        'notes': [
            {'date': '2024-01-15', 'user': 'admin_customer_service', 'note': 'Ticket created'},
            {'date': '2024-01-15', 'user': 'admin_customer_service', 'note': 'Contacted customer for additional information'}
        ]
    }
    
    return jsonify({'success': True, 'ticket': ticket_details})

@app.route('/api/support_tickets/<ticket_id>', methods=['PUT'])
@login_required
def api_update_support_ticket(ticket_id):
    """Update support ticket status"""
    if not (current_user.department.value == 'Customer Service Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        new_status = data.get('status')
        notes = data.get('notes', '')
        
        return jsonify({
            'success': True,
            'message': f'Ticket {ticket_id} status updated to {new_status}',
            'ticket_id': ticket_id,
            'status': new_status,
            'notes': notes
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/customer_analytics', methods=['GET'])
@login_required
def api_customer_analytics():
    """Get customer analytics data"""
    if not (current_user.department.value == 'Customer Service Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    # Mock analytics data
    analytics = {
        'total_customers': 2847,
        'active_customers': 2650,
        'new_customers_this_month': 58,
        'customer_satisfaction': 94.5,
        'average_balance': 15800,
        'top_account_types': [
            {'type': 'Personal', 'count': 1850, 'percentage': 65},
            {'type': 'Business', 'count': 650, 'percentage': 23},
            {'type': 'Premium', 'count': 250, 'percentage': 9},
            {'type': 'Student', 'count': 97, 'percentage': 3}
        ],
        'monthly_growth': [
            {'month': 'Jan', 'new_customers': 45, 'total_balance': 42000000},
            {'month': 'Feb', 'new_customers': 52, 'total_balance': 42500000},
            {'month': 'Mar', 'new_customers': 48, 'total_balance': 43000000},
            {'month': 'Apr', 'new_customers': 55, 'total_balance': 43500000},
            {'month': 'May', 'new_customers': 61, 'total_balance': 44000000},
            {'month': 'Jun', 'new_customers': 58, 'total_balance': 44500000}
        ]
    }
    
    return jsonify({'success': True, 'analytics': analytics})

@app.route('/api/customers/<customer_id>/transactions', methods=['GET'])
@login_required
def api_get_customer_transactions(customer_id):
    """Get customer transaction history"""
    if not (current_user.department.value == 'Customer Service Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    # Mock transaction data
    transactions = [
        {'date': '2024-01-15', 'type': 'deposit', 'amount': 1000, 'description': 'Salary deposit', 'balance': 25000},
        {'date': '2024-01-14', 'type': 'withdrawal', 'amount': -500, 'description': 'ATM withdrawal', 'balance': 24000},
        {'date': '2024-01-13', 'type': 'transfer', 'amount': -200, 'description': 'Online transfer', 'balance': 24500},
        {'date': '2024-01-12', 'type': 'deposit', 'amount': 2500, 'description': 'Check deposit', 'balance': 24700},
        {'date': '2024-01-11', 'type': 'payment', 'amount': -150, 'description': 'Utility bill payment', 'balance': 22200}
    ]
    
    return jsonify({'success': True, 'transactions': transactions})

@app.route('/api/customers/<customer_id>/update', methods=['PUT'])
@login_required
def api_update_customer(customer_id):
    """Update customer information"""
    if not (current_user.department.value == 'Customer Service Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        
        return jsonify({
            'success': True,
            'message': f'Customer {customer_id} updated successfully',
            'customer_id': customer_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/customers/<customer_id>/deactivate', methods=['POST'])
@login_required
def api_deactivate_customer(customer_id):
    """Deactivate customer account"""
    if not (current_user.department.value == 'Customer Service Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        return jsonify({
            'success': True,
            'message': f'Customer {customer_id} deactivated successfully',
            'customer_id': customer_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/customers/<customer_id>/activate', methods=['POST'])
@login_required
def api_activate_customer(customer_id):
    """Activate customer account"""
    if not (current_user.department.value == 'Customer Service Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        return jsonify({
            'success': True,
            'message': f'Customer {customer_id} activated successfully',
            'customer_id': customer_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# API Endpoints for Dashboard
@app.route('/api/add_employee', methods=['POST'])
@login_required
def api_add_employee():
    if not (current_user.role.value == 'admin' and current_user.department.value == 'Admin/HR Department'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    try:
        data = request.get_json()
        print('DEBUG: Received data for add_employee:', data)  # Debug log
        if not data:
            print('DEBUG: No data provided')
            return jsonify({'success': False, 'message': 'No data provided'})
        from src.models.employee import Department, Role
        # Use helper to get enum
        department = get_enum_value(Department, data.get('department', ''))
        role = get_enum_value(Role, data.get('role', ''))
        emp = employee_service.create_employee(
            username=data.get('username', ''),
            password=data.get('password', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            email=data.get('email', ''),
            department=department,
            role=role
        )
        if emp:
            print('DEBUG: Employee created successfully')
            return jsonify({'success': True, 'message': 'Employee added successfully'})
        else:
            print('DEBUG: Failed to add employee')
            return jsonify({'success': False, 'message': 'Failed to add employee'})
    except Exception as e:
        print('DEBUG: Exception in add_employee:', str(e))
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/search_employees')
@login_required
def api_search_employees():
    if not (current_user.role.value == 'admin' and current_user.department.value == 'Admin/HR Department'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    search_term = request.args.get('term', '')
    if not search_term:
        return jsonify({'employees': []})
    
    employees = employee_service.search_employees(search_term)
    employee_list = []
    for emp in employees:
        employee_list.append({
            'first_name': emp.first_name,
            'last_name': emp.last_name,
            'username': emp.username,
            'department': emp.department.value,
            'role': emp.role.value,
            'email': emp.email
        })
    
    return jsonify({'employees': employee_list})

@app.route('/api/department_stats')
@login_required
def api_department_stats():
    if not (current_user.role.value == 'admin' and current_user.department.value == 'Admin/HR Department'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    all_employees = employee_service.get_all_employees()
    department_counts = {}
    
    for emp in all_employees:
        dept_name = emp.department.value
        if dept_name not in department_counts:
            department_counts[dept_name] = 0
        department_counts[dept_name] += 1
    
    departments = [{'name': name, 'count': count} for name, count in department_counts.items()]
    total = len(all_employees)
    
    return jsonify({
        'departments': departments,
        'total': total
    })

@app.route('/api/recent_activity')
@login_required
def api_recent_activity():
    if not (current_user.role.value == 'admin' and current_user.department.value == 'Admin/HR Department'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    # Get recent employees (last 5 created)
    all_employees = employee_service.get_all_employees()
    recent_employees = sorted(all_employees, key=lambda x: x.created_date, reverse=True)[:5]
    
    activities = []
    for emp in recent_employees:
        activities.append({
            'action': 'Employee Created',
            'details': f'{emp.full_name()} joined {emp.department.value}',
            'timestamp': emp.created_date.strftime('%Y-%m-%d %H:%M')
        })
    
    return jsonify({'activities': activities})

# Additional API endpoints for employee management
@app.route('/api/employee/<employee_id>')
@login_required
def api_get_employee(employee_id):
    if not (current_user.role.value == 'admin' and current_user.department.value == 'Admin/HR Department'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    emp = employee_service.get_employee(employee_id)
    if emp:
        return jsonify({
            'success': True,
            'employee': {
                'employee_id': emp.employee_id,
                'first_name': emp.first_name,
                'last_name': emp.last_name,
                'email': emp.email,
                'department': emp.department.value,
                'role': emp.role.value,
                'is_active': emp.is_active
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Employee not found'})

@app.route('/api/update_employee', methods=['POST'])
@login_required
def api_update_employee():
    if not (current_user.role.value == 'admin' and current_user.department.value == 'Admin/HR Department'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'})
        from src.models.employee import Department, Role
        # Use helper to get enum
        department = get_enum_value(Department, data.get('department', ''))
        role = get_enum_value(Role, data.get('role', ''))
        success = employee_service.update_employee(
            data.get('employee_id', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            email=data.get('email', ''),
            department=department,
            role=role,
            is_active=data.get('is_active', 'true').lower() == 'true'
        )
        if success:
            return jsonify({'success': True, 'message': 'Employee updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update employee'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/reset_password', methods=['POST'])
@login_required
def api_reset_password():
    if not (current_user.role.value == 'admin' and current_user.department.value == 'Admin/HR Department'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'})
        
        success = employee_service.admin_reset_password(
            employee_id=data.get('employee_id', ''),
            new_password=data.get('new_password', '')
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Password reset successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to reset password'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/deactivate_employee', methods=['POST'])
@login_required
def api_deactivate_employee():
    if not (current_user.role.value == 'admin' and current_user.department.value == 'Admin/HR Department'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'})
        
        success = employee_service.deactivate_employee(data.get('employee_id', ''))
        
        if success:
            return jsonify({'success': True, 'message': 'Employee deactivated successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to deactivate employee'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/activate_employee', methods=['POST'])
@login_required
def api_activate_employee():
    if not (current_user.role.value == 'admin' and current_user.department.value == 'Admin/HR Department'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'})
        
        # Update employee to active status
        success = employee_service.update_employee(
            data.get('employee_id', ''),
            is_active=True
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Employee activated successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to activate employee'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Audit Log API endpoints
@app.route('/api/audit_logs')
@login_required
def api_audit_logs():
    if not (current_user.role.value == 'admin' and current_user.department.value == 'Admin/HR Department'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        # Get filter parameters
        action = request.args.get('action', '')
        employee = request.args.get('employee', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 25))
        
        # Get audit logs from database
        audit_logs = db.get_audit_logs()
        
        # Apply filters
        if employee:
            audit_logs = [log for log in audit_logs if log.get('employee_id') == employee]
        if action:
            audit_logs = [log for log in audit_logs if log.get('action') == action]
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                audit_logs = [log for log in audit_logs if datetime.fromisoformat(log.get('timestamp', '')) >= start_dt]
            except:
                pass
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                audit_logs = [log for log in audit_logs if datetime.fromisoformat(log.get('timestamp', '')) <= end_dt]
            except:
                pass
        
        # Simple pagination
        total = len(audit_logs)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_logs = audit_logs[start_idx:end_idx]
        
        return jsonify({
            'success': True,
            'logs': paginated_logs,
            'total': total,
            'page': page,
            'page_size': page_size
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/audit_log/<log_id>')
@login_required
def api_get_audit_log(log_id):
    if not (current_user.role.value == 'admin' and current_user.department.value == 'Admin/HR Department'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        # Get specific audit log
        audit_logs = db.get_audit_logs()
        log = None
        for audit_log in audit_logs:
            if audit_log.get('id') == log_id:
                log = audit_log
                break
        
        if log:
            return jsonify({'success': True, 'log': log})
        else:
            return jsonify({'success': False, 'message': 'Audit log not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/export_audit_logs')
@login_required
def api_export_audit_logs():
    if not (current_user.role.value == 'admin' and current_user.department.value == 'Admin/HR Department'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        # Get filter parameters
        action = request.args.get('action', '')
        employee = request.args.get('employee', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        # Get all audit logs
        audit_logs = db.get_audit_logs()
        
        # Apply filters
        if employee:
            audit_logs = [log for log in audit_logs if log.get('employee_id') == employee]
        if action:
            audit_logs = [log for log in audit_logs if log.get('action') == action]
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                audit_logs = [log for log in audit_logs if datetime.fromisoformat(log.get('timestamp', '')) >= start_dt]
            except:
                pass
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                audit_logs = [log for log in audit_logs if datetime.fromisoformat(log.get('timestamp', '')) <= end_dt]
            except:
                pass
        
        # Create CSV content
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Timestamp', 'Employee ID', 'Action', 'Target Type', 'Target ID', 'Details', 'Success'])
        
        # Write data
        for log in audit_logs:
            writer.writerow([
                log.get('timestamp', ''),
                log.get('employee_id', ''),
                log.get('action', ''),
                log.get('target_type', ''),
                log.get('target_id', ''),
                log.get('details', ''),
                log.get('success', '')
            ])
        
        output.seek(0)
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=audit_logs_{datetime.now().strftime("%Y%m%d")}.csv'}
        )
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/teller_dashboard')
@login_required
def teller_dashboard():
    # Only allow Teller Department users OR HR admins (system-wide access)
    if not (current_user.department.value == 'Teller/Transaction Department' or 
            (current_user.department.value == 'Admin/HR Department' and current_user.role.value == 'admin')):
        flash('Access denied. Only Teller Department personnel can access this page.', 'error')
        return redirect(url_for('dashboard'))
    return render_template('teller_dashboard.html', user=current_user)

# Teller APIs
@app.route('/api/teller/deposit', methods=['POST'])
@login_required
def api_teller_deposit():
    # Only allow teller/admin
    if current_user.department not in [Department.Teller, Department.AdminHR] and current_user.role != Role.ADMIN:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    data = request.json or request.form
    account_number = data.get('account_number')
    amount = float(data.get('amount', 0))
    currency = data.get('currency', 'USD')
    description = data.get('description', '')
    # TODO: Integrate with AccountService
    # Log audit
    # Return result
    return jsonify({'success': True, 'message': 'Deposit successful'})

@app.route('/api/teller/withdraw', methods=['POST'])
@login_required
def api_teller_withdraw():
    if current_user.department not in [Department.Teller, Department.AdminHR] and current_user.role != Role.ADMIN:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    data = request.json or request.form
    account_number = data.get('account_number')
    amount = float(data.get('amount', 0))
    currency = data.get('currency', 'USD')
    description = data.get('description', '')
    # TODO: Integrate with AccountService
    # Log audit
    return jsonify({'success': True, 'message': 'Withdrawal successful'})

@app.route('/api/teller/check', methods=['POST'])
@login_required
def api_teller_check():
    if current_user.department not in [Department.Teller, Department.AdminHR] and current_user.role != Role.ADMIN:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    data = request.json or request.form
    account_number = data.get('account_number')
    amount = float(data.get('amount', 0))
    currency = data.get('currency', 'USD')
    check_number = data.get('check_number')
    description = data.get('description', '')
    # TODO: Integrate with AccountService/CheckService
    # Log audit
    return jsonify({'success': True, 'message': 'Check processed'})

@app.route('/api/teller/exchange', methods=['POST'])
@login_required
def api_teller_exchange():
    if current_user.department not in [Department.Teller, Department.AdminHR] and current_user.role != Role.ADMIN:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    data = request.json or request.form
    account_number = data.get('account_number')
    from_currency = data.get('from_currency')
    to_currency = data.get('to_currency')
    amount = float(data.get('amount', 0))
    description = data.get('description', '')
    # TODO: Integrate with CurrencyExchangeService
    # Log audit
    return jsonify({'success': True, 'message': 'Currency exchanged'})

@app.route('/api/teller/transactions', methods=['GET'])
@login_required
def api_teller_transactions():
    """Get teller transactions"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    # Mock transaction data
    transactions = [
        {
            'id': 'TXN001',
            'type': 'Cash Deposit',
            'amount': 500.00,
            'account': 'ACC-001-2024',
            'customer': 'John Smith',
            'timestamp': '2024-01-15 14:30:00',
            'status': 'Completed'
        },
        {
            'id': 'TXN002',
            'type': 'Check Deposit',
            'amount': 1250.00,
            'account': 'ACC-002-2024',
            'customer': 'Sarah Johnson',
            'timestamp': '2024-01-15 09:15:00',
            'status': 'Completed'
        },
        {
            'id': 'TXN003',
            'type': 'Cash Withdrawal',
            'amount': -200.00,
            'account': 'ACC-003-2024',
            'customer': 'Michael Brown',
            'timestamp': '2024-01-15 16:45:00',
            'status': 'Completed'
        }
    ]
    
    return jsonify({'transactions': transactions})

# Enhanced Teller API Routes
@app.route('/api/teller/cash/deposit', methods=['POST'])
@login_required
def api_teller_cash_deposit():
    """Process cash deposit with denominations"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    account_number = data.get('account_number')
    amount = data.get('amount')
    denominations = data.get('denominations', {})
    description = data.get('description', '')
    
    if not all([account_number, amount]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate denominations
    total_from_denominations = sum(
        int(denominations.get('hundreds', 0)) * 100 +
        int(denominations.get('fifties', 0)) * 50 +
        int(denominations.get('twenties', 0)) * 20 +
        int(denominations.get('tens', 0)) * 10 +
        int(denominations.get('fives', 0)) * 5 +
        int(denominations.get('ones', 0))
    )
    
    if total_from_denominations != float(amount):
        return jsonify({'error': 'Denominations do not match total amount'}), 400
    
    # Mock processing
    transaction_id = f"CD{int(time.time())}"
    
    return jsonify({
        'success': True,
        'message': f'Cash deposit of ${amount:.2f} processed successfully',
        'transaction_id': transaction_id,
        'account_number': account_number,
        'amount': amount,
        'denominations': denominations,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/teller/cash/withdrawal', methods=['POST'])
@login_required
def api_teller_cash_withdrawal():
    """Process cash withdrawal"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    account_number = data.get('account_number')
    amount = data.get('amount')
    reason = data.get('reason', '')
    customer_id = data.get('customer_id', '')
    
    if not all([account_number, amount, customer_id]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Mock processing
    transaction_id = f"CW{int(time.time())}"
    
    return jsonify({
        'success': True,
        'message': f'Cash withdrawal of ${amount:.2f} processed successfully',
        'transaction_id': transaction_id,
        'account_number': account_number,
        'amount': amount,
        'reason': reason,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/teller/check/deposit', methods=['POST'])
@login_required
def api_teller_check_deposit():
    """Process check deposit"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    account_number = data.get('account_number')
    check_amount = data.get('check_amount')
    check_number = data.get('check_number')
    payor_bank = data.get('payor_bank')
    check_date = data.get('check_date')
    
    if not all([account_number, check_amount, check_number, payor_bank]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Mock processing
    transaction_id = f"CHK{int(time.time())}"
    
    return jsonify({
        'success': True,
        'message': f'Check deposit of ${check_amount:.2f} processed successfully',
        'transaction_id': transaction_id,
        'account_number': account_number,
        'check_amount': check_amount,
        'check_number': check_number,
        'payor_bank': payor_bank,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/teller/currency/exchange', methods=['POST'])
@login_required
def api_teller_currency_exchange():
    """Process currency exchange"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    from_currency = data.get('from_currency')
    to_currency = data.get('to_currency')
    amount = data.get('amount')
    exchange_rate = data.get('exchange_rate')
    exchange_type = data.get('exchange_type', 'Cash')
    
    if not all([from_currency, to_currency, amount, exchange_rate]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    converted_amount = float(amount) * float(exchange_rate)
    
    # Mock processing
    transaction_id = f"FX{int(time.time())}"
    
    return jsonify({
        'success': True,
        'message': f'Currency exchange processed successfully',
        'transaction_id': transaction_id,
        'from_currency': from_currency,
        'to_currency': to_currency,
        'original_amount': amount,
        'converted_amount': round(converted_amount, 2),
        'exchange_rate': exchange_rate,
        'exchange_type': exchange_type,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/teller/customer/search', methods=['POST'])
@login_required
def api_teller_customer_search():
    """Search for customers"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    search_type = data.get('search_type')
    search_value = data.get('search_value')
    
    if not all([search_type, search_value]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Mock customer search results
    customers = [
        {
            'account_number': 'ACC-001-2024',
            'name': 'John Smith',
            'phone': '(555) 123-4567',
            'email': 'john.smith@email.com',
            'balance': 15250.00,
            'status': 'Active',
            'account_type': 'Savings'
        },
        {
            'account_number': 'ACC-002-2024',
            'name': 'Sarah Johnson',
            'phone': '(555) 234-5678',
            'email': 'sarah.johnson@email.com',
            'balance': 8750.50,
            'status': 'Active',
            'account_type': 'Checking'
        }
    ]
    
    return jsonify({
        'success': True,
        'customers': customers,
        'search_type': search_type,
        'search_value': search_value
    })

@app.route('/api/teller/account/freeze', methods=['POST'])
@login_required
def api_teller_account_freeze():
    """Freeze account"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    account_number = data.get('account_number')
    reason = data.get('reason')
    description = data.get('description')
    duration = data.get('duration')
    
    if not all([account_number, reason, description]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Mock processing
    freeze_id = f"FRZ{int(time.time())}"
    
    return jsonify({
        'success': True,
        'message': f'Account {account_number} has been frozen',
        'freeze_id': freeze_id,
        'account_number': account_number,
        'reason': reason,
        'description': description,
        'duration': duration,
        'frozen_by': current_user.username,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/teller/account/unfreeze', methods=['POST'])
@login_required
def api_teller_account_unfreeze():
    """Unfreeze account"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    account_number = data.get('account_number')
    
    if not account_number:
        return jsonify({'error': 'Missing account number'}), 400
    
    # Mock processing
    return jsonify({
        'success': True,
        'message': f'Account {account_number} has been unfrozen',
        'account_number': account_number,
        'unfrozen_by': current_user.username,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/teller/check/cash', methods=['POST'])
@login_required
def api_teller_check_cash():
    """Cash check for customer"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    check_amount = data.get('check_amount')
    check_number = data.get('check_number')
    payor_bank = data.get('payor_bank')
    customer_id = data.get('customer_id')
    
    if not all([check_amount, check_number, payor_bank, customer_id]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Mock processing
    transaction_id = f"CC{int(time.time())}"
    
    return jsonify({
        'success': True,
        'message': f'Check cashed for ${check_amount:.2f}',
        'transaction_id': transaction_id,
        'check_amount': check_amount,
        'check_number': check_number,
        'payor_bank': payor_bank,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/teller/wire/transfer', methods=['POST'])
@login_required
def api_teller_wire_transfer():
    """Process wire transfer"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    from_account = data.get('from_account')
    to_account = data.get('to_account')
    amount = data.get('amount')
    recipient_name = data.get('recipient_name')
    recipient_bank = data.get('recipient_bank')
    wire_type = data.get('wire_type', 'Domestic')  # Domestic or International
    
    if not all([from_account, to_account, amount, recipient_name, recipient_bank]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Mock processing
    transaction_id = f"WT{int(time.time())}"
    
    return jsonify({
        'success': True,
        'message': f'Wire transfer of ${amount:.2f} processed successfully',
        'transaction_id': transaction_id,
        'from_account': from_account,
        'to_account': to_account,
        'amount': amount,
        'recipient_name': recipient_name,
        'recipient_bank': recipient_bank,
        'wire_type': wire_type,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/teller/card/issue', methods=['POST'])
@login_required
def api_teller_card_issue():
    """Issue new card"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    account_number = data.get('account_number')
    card_type = data.get('card_type')  # Debit, Credit, ATM
    customer_name = data.get('customer_name')
    
    if not all([account_number, card_type, customer_name]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Mock processing
    card_number = f"****-****-****-{random.randint(1000, 9999)}"
    expiry_date = f"{random.randint(1, 12):02d}/{random.randint(25, 30)}"
    
    return jsonify({
        'success': True,
        'message': f'New {card_type} card issued successfully',
        'card_number': card_number,
        'expiry_date': expiry_date,
        'account_number': account_number,
        'card_type': card_type,
        'customer_name': customer_name,
        'issued_by': current_user.username,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/teller/card/replace', methods=['POST'])
@login_required
def api_teller_card_replace():
    """Replace card"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    account_number = data.get('account_number')
    old_card_number = data.get('old_card_number')
    replacement_reason = data.get('replacement_reason')  # Lost, Stolen, Damaged
    
    if not all([account_number, old_card_number, replacement_reason]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Mock processing
    new_card_number = f"****-****-****-{random.randint(1000, 9999)}"
    expiry_date = f"{random.randint(1, 12):02d}/{random.randint(25, 30)}"
    
    return jsonify({
        'success': True,
        'message': 'Card replacement processed successfully',
        'old_card_number': old_card_number,
        'new_card_number': new_card_number,
        'expiry_date': expiry_date,
        'account_number': account_number,
        'replacement_reason': replacement_reason,
        'replaced_by': current_user.username,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/teller/fraud/report', methods=['POST'])
@login_required
def api_teller_fraud_report():
    """Report fraud"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    account_number = data.get('account_number')
    fraud_type = data.get('fraud_type')  # Suspicious Activity, Identity Theft, etc.
    description = data.get('description')
    severity = data.get('severity', 'Medium')  # Low, Medium, High, Critical
    
    if not all([account_number, fraud_type, description]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Mock processing
    report_id = f"FRAUD{int(time.time())}"
    
    return jsonify({
        'success': True,
        'message': 'Fraud report submitted successfully',
        'report_id': report_id,
        'account_number': account_number,
        'fraud_type': fraud_type,
        'description': description,
        'severity': severity,
        'reported_by': current_user.username,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/teller/exchange/rates', methods=['GET'])
@login_required
def api_teller_exchange_rates():
    """Get current exchange rates"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    # Mock exchange rates
    rates = {
        'USD': 1.0000,
        'EUR': 0.8500,
        'GBP': 0.7300,
        'JPY': 110.50,
        'CAD': 1.2500,
        'AUD': 1.3500,
        'CHF': 0.9200
    }
    
    return jsonify({
        'success': True,
        'rates': rates,
        'last_updated': datetime.now().isoformat(),
        'base_currency': 'USD'
    })

# Additional Teller API Routes for Enhanced Functionality

@app.route('/api/teller/cash/count', methods=['POST'])
@login_required
def api_teller_cash_count():
    """Process cash count"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['countType', 'countHundreds', 'countFifties', 'countTwenties', 'countTens', 'countFives', 'countOnes']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Calculate total
    total = (
        int(data['countHundreds']) * 100 +
        int(data['countFifties']) * 50 +
        int(data['countTwenties']) * 20 +
        int(data['countTens']) * 10 +
        int(data['countFives']) * 5 +
        int(data['countOnes'])
    )
    
    count_id = f"CC-{int(time.time())}"
    
    return jsonify({
        'success': True,
        'count_id': count_id,
        'total_amount': total,
        'count_type': data['countType'],
        'message': f'Cash count completed successfully. Total: ${total:,.2f}'
    })

@app.route('/api/teller/cash/transfer', methods=['POST'])
@login_required
def api_teller_cash_transfer():
    """Process cash transfer between accounts"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['transferFromAccount', 'transferToAccount', 'transferAmount', 'transferType']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    if data['transferFromAccount'] == data['transferToAccount']:
        return jsonify({'error': 'From and To accounts cannot be the same'}), 400
    
    transfer_id = f"CT-{int(time.time())}"
    
    return jsonify({
        'success': True,
        'transfer_id': transfer_id,
        'from_account': data['transferFromAccount'],
        'to_account': data['transferToAccount'],
        'amount': float(data['transferAmount']),
        'transfer_type': data['transferType'],
        'message': f'Cash transfer processed successfully'
    })

@app.route('/api/teller/check/verify', methods=['POST'])
@login_required
def api_teller_check_verify():
    """Verify check details"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['verifyCheckNumber', 'verifyPayorBank', 'verifyAccountNumber', 'verifyAmount']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    verification_id = f"VF-{int(time.time())}"
    
    # Mock verification result
    verification_result = {
        'check_number': data['verifyCheckNumber'],
        'payor_bank': data['verifyPayorBank'],
        'account_number': data['verifyAccountNumber'],
        'amount': float(data['verifyAmount']),
        'status': 'VERIFIED',
        'verification_id': verification_id,
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify({
        'success': True,
        'verification': verification_result,
        'message': 'Check verification completed successfully'
    })

@app.route('/api/teller/stop/payment', methods=['POST'])
@login_required
def api_teller_stop_payment():
    """Process stop payment request"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['stopAccount', 'stopCheckNumber', 'stopAmount', 'stopPayee', 'stopReason']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    stop_payment_id = f"SP-{int(time.time())}"
    
    return jsonify({
        'success': True,
        'stop_payment_id': stop_payment_id,
        'account': data['stopAccount'],
        'check_number': data['stopCheckNumber'],
        'amount': float(data['stopAmount']),
        'payee': data['stopPayee'],
        'reason': data['stopReason'],
        'message': f'Stop payment processed successfully for check {data["stopCheckNumber"]}'
    })

@app.route('/api/teller/account/modify', methods=['POST'])
@login_required
def api_teller_account_modify():
    """Modify account details"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['modifyAccount', 'modifyType', 'modifyNewValue']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    modification_id = f"AM-{int(time.time())}"
    
    return jsonify({
        'success': True,
        'modification_id': modification_id,
        'account': data['modifyAccount'],
        'modification_type': data['modifyType'],
        'new_value': data['modifyNewValue'],
        'message': f'Account modification processed successfully'
    })

@app.route('/api/teller/account/close', methods=['POST'])
@login_required
def api_teller_account_close():
    """Close account"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['closeAccount', 'closeReason', 'closeDescription', 'closeDisbursement']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    closure_id = f"AC-{int(time.time())}"
    
    return jsonify({
        'success': True,
        'closure_id': closure_id,
        'account': data['closeAccount'],
        'reason': data['closeReason'],
        'disbursement_method': data['closeDisbursement'],
        'message': f'Account {data["closeAccount"]} closed successfully'
    })

@app.route('/api/teller/bill/payment', methods=['POST'])
@login_required
def api_teller_bill_payment():
    """Process bill payment"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['billAccount', 'billAmount', 'billPayee', 'billType']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    transaction_id = f"BP-{int(time.time())}"
    
    return jsonify({
        'success': True,
        'transaction_id': transaction_id,
        'account': data['billAccount'],
        'amount': float(data['billAmount']),
        'payee': data['billPayee'],
        'bill_type': data['billType'],
        'message': f'Bill payment processed successfully for ${data["billAmount"]}'
    })

@app.route('/api/teller/loan/payment', methods=['POST'])
@login_required
def api_teller_loan_payment():
    """Process loan payment"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['loanAccount', 'loanPaymentAmount', 'loanNumber', 'loanType']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    transaction_id = f"LP-{int(time.time())}"
    
    return jsonify({
        'success': True,
        'transaction_id': transaction_id,
        'account': data['loanAccount'],
        'amount': float(data['loanPaymentAmount']),
        'loan_number': data['loanNumber'],
        'loan_type': data['loanType'],
        'message': f'Loan payment processed successfully for ${data["loanPaymentAmount"]}'
    })

@app.route('/api/teller/utility/payment', methods=['POST'])
@login_required
def api_teller_utility_payment():
    """Process utility payment"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['utilityAccount', 'utilityAmount', 'utilityType', 'utilityProvider']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    transaction_id = f"UP-{int(time.time())}"
    
    return jsonify({
        'success': True,
        'transaction_id': transaction_id,
        'account': data['utilityAccount'],
        'amount': float(data['utilityAmount']),
        'utility_type': data['utilityType'],
        'provider': data['utilityProvider'],
        'message': f'Utility payment processed successfully for ${data["utilityAmount"]}'
    })

@app.route('/api/teller/tax/payment', methods=['POST'])
@login_required
def api_teller_tax_payment():
    """Process tax payment"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['taxAccount', 'taxAmount', 'taxType', 'taxAuthority']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    transaction_id = f"TP-{int(time.time())}"
    
    return jsonify({
        'success': True,
        'transaction_id': transaction_id,
        'account': data['taxAccount'],
        'amount': float(data['taxAmount']),
        'tax_type': data['taxType'],
        'authority': data['taxAuthority'],
        'message': f'Tax payment processed successfully for ${data["taxAmount"]}'
    })

@app.route('/api/teller/pin/change', methods=['POST'])
@login_required
def api_teller_pin_change():
    """Change card PIN"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['pinAccount', 'cardNumber', 'currentPin', 'newPin', 'confirmPin']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate PIN format
    if len(data['newPin']) != 4 or not data['newPin'].isdigit():
        return jsonify({'error': 'PIN must be exactly 4 digits'}), 400
    
    if data['newPin'] != data['confirmPin']:
        return jsonify({'error': 'New PIN and Confirm PIN do not match'}), 400
    
    pin_change_id = f"PC-{int(time.time())}"
    
    return jsonify({
        'success': True,
        'pin_change_id': pin_change_id,
        'account': data['pinAccount'],
        'card_number': data['cardNumber'],
        'message': f'PIN changed successfully for card {data["cardNumber"]}'
    })

@app.route('/api/teller/card/block', methods=['POST'])
@login_required
def api_teller_card_block():
    """Block card"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['blockAccount', 'blockCardNumber', 'blockReason']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    block_id = f"CB-{int(time.time())}"
    
    return jsonify({
        'success': True,
        'block_id': block_id,
        'account': data['blockAccount'],
        'card_number': data['blockCardNumber'],
        'reason': data['blockReason'],
        'duration': data.get('blockDuration', 'temporary'),
        'message': f'Card {data["blockCardNumber"]} blocked successfully'
    })

@app.route('/api/teller/reports/transaction', methods=['GET'])
@login_required
def api_teller_transaction_report():
    """Generate transaction report"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    # Mock transaction report data
    report_data = {
        'report_id': f"TR-{int(time.time())}",
        'date_range': '2024-01-01 to 2024-12-31',
        'total_transactions': 1250,
        'total_amount': 1250000.00,
        'transaction_types': {
            'deposits': 450,
            'withdrawals': 380,
            'transfers': 220,
            'payments': 200
        },
        'top_accounts': [
            {'account': 'ACC-001-2024', 'transactions': 45, 'amount': 125000.00},
            {'account': 'ACC-002-2024', 'transactions': 38, 'amount': 87500.00},
            {'account': 'ACC-003-2024', 'transactions': 32, 'amount': 45200.00}
        ]
    }
    
    return jsonify({
        'success': True,
        'report': report_data,
        'message': 'Transaction report generated successfully'
    })

@app.route('/api/teller/reports/cashflow', methods=['GET'])
@login_required
def api_teller_cashflow_report():
    """Generate cash flow report"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    # Mock cash flow report data
    report_data = {
        'report_id': f"CF-{int(time.time())}",
        'period': 'Monthly',
        'opening_balance': 500000.00,
        'closing_balance': 525000.00,
        'net_change': 25000.00,
        'cash_in': 150000.00,
        'cash_out': 125000.00,
        'daily_averages': {
            'monday': 25000.00,
            'tuesday': 28000.00,
            'wednesday': 32000.00,
            'thursday': 29000.00,
            'friday': 35000.00
        }
    }
    
    return jsonify({
        'success': True,
        'report': report_data,
        'message': 'Cash flow report generated successfully'
    })

@app.route('/api/teller/kyc/verify', methods=['POST'])
@login_required
def api_teller_kyc_verify():
    """Verify customer KYC"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['customerId', 'documentType', 'documentNumber']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    verification_id = f"KYC-{int(time.time())}"
    
    return jsonify({
        'success': True,
        'verification_id': verification_id,
        'customer_id': data['customerId'],
        'document_type': data['documentType'],
        'document_number': data['documentNumber'],
        'status': 'VERIFIED',
        'message': f'KYC verification completed successfully for {data["customerId"]}'
    })

@app.route('/api/teller/regulatory/report', methods=['POST'])
@login_required
def api_teller_regulatory_report():
    """Generate regulatory report"""
    if not (current_user.role.value == 'teller' or current_user.role.value == 'admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['reportType', 'reportPeriod', 'reportingAuthority']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    report_id = f"RR-{int(time.time())}"
    
    return jsonify({
        'success': True,
        'report_id': report_id,
        'report_type': data['reportType'],
        'period': data['reportPeriod'],
        'authority': data['reportingAuthority'],
        'message': f'Regulatory report generated successfully for {data["reportType"]}'
    })

@app.route('/risk_dashboard')
@login_required
def risk_dashboard():
    """Risk Management Department Dashboard with comprehensive risk management functionality"""
    # Only allow Risk Management Department users OR HR admins (system-wide access)
    if not (current_user.department.value == 'Risk Management Department' or 
            (current_user.department.value == 'Admin/HR Department' and current_user.role.value == 'admin')):
        flash('Access denied. Only Risk Management Department personnel can access this page.', 'error')
        return redirect(url_for('dashboard'))
    
    # Risk management dashboard data
    risk_data = {
        'total_policies': 1847,
        'active_policies': 1623,
        'pending_claims': 34,
        'high_risk_accounts': 127,
        'fraud_alerts': 8,
        'compliance_score': 94.2,
        'total_exposure': 89500000,  # $89.5M
        'var_daily': 2850000,  # Value at Risk - $2.85M
        'capital_ratio': 12.8,  # Capital Adequacy Ratio
        'recent_alerts': [
            {'id': 'RA001', 'type': 'Credit Risk', 'account': 'ACC-789012', 'severity': 'High', 'date': '2025-01-15'},
            {'id': 'RA002', 'type': 'Fraud Alert', 'account': 'ACC-345678', 'severity': 'Critical', 'date': '2025-01-15'},
            {'id': 'RA003', 'type': 'Market Risk', 'portfolio': 'Investment Portfolio A', 'severity': 'Medium', 'date': '2025-01-14'},
            {'id': 'RA004', 'type': 'Operational Risk', 'system': 'Core Banking', 'severity': 'Low', 'date': '2025-01-14'},
            {'id': 'RA005', 'type': 'Liquidity Risk', 'threshold': '85%', 'severity': 'Medium', 'date': '2025-01-13'}
        ],
        'insurance_policies': [
            {'id': 'INS001', 'customer': 'John Smith', 'type': 'Life Insurance', 'premium': 2400, 'coverage': 500000, 'status': 'Active'},
            {'id': 'INS002', 'customer': 'Sarah Johnson', 'type': 'Home Insurance', 'premium': 1800, 'coverage': 800000, 'status': 'Active'},
            {'id': 'INS003', 'customer': 'Mike Davis', 'type': 'Auto Insurance', 'premium': 1200, 'coverage': 50000, 'status': 'Pending'},
            {'id': 'INS004', 'customer': 'Lisa Wilson', 'type': 'Business Insurance', 'premium': 4500, 'coverage': 2000000, 'status': 'Active'},
            {'id': 'INS005', 'customer': 'David Brown', 'type': 'Health Insurance', 'premium': 3600, 'coverage': 1000000, 'status': 'Under Review'}
        ],
        'risk_metrics': {
            'credit_risk_score': 7.2,
            'market_risk_score': 6.8,
            'operational_risk_score': 4.1,
            'liquidity_ratio': 15.6,
            'leverage_ratio': 8.4,
            'stress_test_result': 'Pass'
        }
    }
    
    return render_template('risk_dashboard.html', user=current_user, **risk_data)

# Risk Management API Endpoints
@app.route('/api/risk/assessment', methods=['POST'])
@login_required
def api_risk_assessment():
    """Perform credit risk assessment for account/customer"""
    if not (current_user.department.value == 'Risk Management Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    account_number = data.get('account_number')
    assessment_type = data.get('assessment_type', 'credit')
    
    if not account_number:
        return jsonify({'error': 'Account number is required'}), 400
    
    # Mock risk assessment logic
    import random
    credit_score = random.randint(300, 850)
    risk_level = 'Low' if credit_score > 700 else 'Medium' if credit_score > 600 else 'High'
    
    assessment = {
        'account_number': account_number,
        'assessment_type': assessment_type,
        'credit_score': credit_score,
        'risk_level': risk_level,
        'debt_to_income_ratio': round(random.uniform(0.1, 0.6), 2),
        'payment_history_score': random.randint(1, 10),
        'account_age_months': random.randint(6, 120),
        'assessment_date': datetime.now().isoformat(),
        'recommendations': [
            'Monitor monthly payment patterns',
            'Review credit utilization ratio',
            'Assess collateral adequacy' if risk_level == 'High' else 'Standard monitoring sufficient'
        ]
    }
    
    return jsonify({
        'success': True,
        'message': f'Risk assessment completed for {account_number}',
        'assessment': assessment
    })

@app.route('/api/risk/insurance/policy', methods=['POST'])
@login_required
def api_create_insurance_policy():
    """Create new insurance policy"""
    if not (current_user.department.value == 'Risk Management Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    customer_id = data.get('customer_id')
    policy_type = data.get('policy_type')
    coverage_amount = data.get('coverage_amount')
    premium_amount = data.get('premium_amount')
    term_years = data.get('term_years')
    beneficiaries = data.get('beneficiaries', [])
    
    if not all([customer_id, policy_type, coverage_amount, premium_amount]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Generate policy number
    policy_number = f'INS{int(time.time())}'
    
    policy = {
        'policy_number': policy_number,
        'customer_id': customer_id,
        'policy_type': policy_type,
        'coverage_amount': coverage_amount,
        'premium_amount': premium_amount,
        'term_years': term_years,
        'beneficiaries': beneficiaries,
        'status': 'Pending Approval',
        'created_date': datetime.now().isoformat(),
        'next_premium_due': (datetime.now().replace(day=1) + 
                           timedelta(days=32)).replace(day=1).isoformat()
    }
    
    return jsonify({
        'success': True,
        'message': f'Insurance policy {policy_number} created successfully',
        'policy': policy
    })

@app.route('/api/risk/insurance/claim', methods=['POST'])
@login_required
def api_process_insurance_claim():
    """Process insurance claim"""
    if not (current_user.department.value == 'Risk Management Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    policy_number = data.get('policy_number')
    claim_amount = data.get('claim_amount')
    claim_type = data.get('claim_type')
    incident_date = data.get('incident_date')
    description = data.get('description')
    
    if not all([policy_number, claim_amount, claim_type, incident_date]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    claim_number = f'CLM{int(time.time())}'
    
    claim = {
        'claim_number': claim_number,
        'policy_number': policy_number,
        'claim_amount': claim_amount,
        'claim_type': claim_type,
        'incident_date': incident_date,
        'description': description,
        'status': 'Under Investigation',
        'filed_date': datetime.now().isoformat(),
        'adjuster_assigned': 'Risk Assessment Team',
        'estimated_processing_days': random.randint(15, 45)
    }
    
    return jsonify({
        'success': True,
        'message': f'Insurance claim {claim_number} filed successfully',
        'claim': claim
    })

@app.route('/api/risk/fraud/alert', methods=['POST'])
@login_required
def api_create_fraud_alert():
    """Create fraud alert for suspicious activity"""
    if not (current_user.department.value == 'Risk Management Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    account_number = data.get('account_number')
    alert_type = data.get('alert_type')
    severity = data.get('severity')
    description = data.get('description')
    transaction_ids = data.get('transaction_ids', [])
    
    if not all([account_number, alert_type, severity]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    alert_id = f'FRA{int(time.time())}'
    
    alert = {
        'alert_id': alert_id,
        'account_number': account_number,
        'alert_type': alert_type,
        'severity': severity,
        'description': description,
        'transaction_ids': transaction_ids,
        'status': 'Open',
        'created_date': datetime.now().isoformat(),
        'assigned_investigator': current_user.username,
        'priority_score': random.randint(1, 10)
    }
    
    return jsonify({
        'success': True,
        'message': f'Fraud alert {alert_id} created successfully',
        'alert': alert
    })

@app.route('/api/risk/compliance/report', methods=['POST'])
@login_required
def api_generate_compliance_report():
    """Generate compliance report"""
    if not (current_user.department.value == 'Risk Management Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    report_type = data.get('report_type')
    period_start = data.get('period_start')
    period_end = data.get('period_end')
    
    if not all([report_type, period_start, period_end]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    report_id = f'RPT{int(time.time())}'
    
    report = {
        'report_id': report_id,
        'report_type': report_type,
        'period_start': period_start,
        'period_end': period_end,
        'generated_by': current_user.username,
        'generated_date': datetime.now().isoformat(),
        'status': 'Generated',
        'findings': {
            'high_risk_transactions': random.randint(10, 50),
            'policy_violations': random.randint(0, 5),
            'compliance_score': round(random.uniform(85, 98), 1),
            'recommendations': [
                'Enhance transaction monitoring for high-value transfers',
                'Update KYC documentation for flagged accounts',
                'Implement additional controls for cross-border transactions'
            ]
        }
    }
    
    return jsonify({
        'success': True,
        'message': f'Compliance report {report_id} generated successfully',
        'report': report
    })

@app.route('/api/risk/portfolio/analysis', methods=['POST'])
@login_required
def api_portfolio_risk_analysis():
    """Perform portfolio risk analysis"""
    if not (current_user.department.value == 'Risk Management Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    portfolio_id = data.get('portfolio_id')
    analysis_type = data.get('analysis_type', 'comprehensive')
    
    if not portfolio_id:
        return jsonify({'error': 'Portfolio ID is required'}), 400
    
    # Mock portfolio analysis
    analysis = {
        'portfolio_id': portfolio_id,
        'analysis_type': analysis_type,
        'analysis_date': datetime.now().isoformat(),
        'var_1_day': round(random.uniform(1000000, 5000000), 2),
        'var_10_day': round(random.uniform(3000000, 15000000), 2),
        'expected_shortfall': round(random.uniform(2000000, 8000000), 2),
        'beta': round(random.uniform(0.8, 1.5), 2),
        'sharpe_ratio': round(random.uniform(0.5, 2.0), 2),
        'max_drawdown': round(random.uniform(0.05, 0.25), 3),
        'concentration_risk': {
            'sector_concentration': random.randint(15, 35),
            'geographic_concentration': random.randint(20, 45),
            'single_issuer_max': random.randint(5, 15)
        },
        'stress_test_results': {
            'market_crash_scenario': round(random.uniform(-0.15, -0.05), 3),
            'interest_rate_shock': round(random.uniform(-0.08, -0.02), 3),
            'credit_crisis_scenario': round(random.uniform(-0.12, -0.04), 3)
        }
    }
    
    return jsonify({
        'success': True,
        'message': f'Portfolio risk analysis completed for {portfolio_id}',
        'analysis': analysis
    })

@app.route('/api/risk/monitoring/dashboard', methods=['GET'])
@login_required
def api_risk_monitoring_dashboard():
    """Get real-time risk monitoring data"""
    if not (current_user.department.value == 'Risk Management Department' or current_user.role.value == 'admin'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    # Mock real-time risk data
    monitoring_data = {
        'current_exposure': round(random.uniform(80000000, 95000000), 2),
        'daily_var': round(random.uniform(2500000, 3500000), 2),
        'credit_utilization': round(random.uniform(65, 85), 1),
        'liquidity_ratio': round(random.uniform(12, 18), 1),
        'active_alerts': random.randint(5, 15),
        'high_risk_accounts': random.randint(100, 150),
        'recent_breaches': random.randint(0, 3),
        'risk_limits': {
            'single_counterparty_limit': 50000000,
            'sector_concentration_limit': 25,
            'var_limit': 5000000,
            'leverage_limit': 10
        },
        'alert_distribution': {
            'credit_risk': random.randint(2, 8),
            'market_risk': random.randint(1, 5),
            'operational_risk': random.randint(0, 3),
            'fraud_alerts': random.randint(0, 4),
            'compliance_alerts': random.randint(1, 6)
        }
    }
    
    return jsonify({
        'success': True,
        'data': monitoring_data
    })

# ============================================================================
# ENHANCED AUDIT AND COMPLIANCE DEPARTMENT - REAL-LIFE BANKING AUDIT SYSTEM
# ============================================================================

@app.route('/audit_dashboard')
@login_required
def audit_dashboard():
    """Simplified Audit and Compliance Dashboard"""
    user = get_current_user()
    
    # Check if user has access to audit department
    if user['department'] not in ['Admin/HR Department', 'Audit and Compliance Department']:
        flash('Access denied. You do not have permission to access the Audit Dashboard.', 'error')
        return redirect(url_for('dashboard'))
    
    # Simplified audit statistics with mock data
    audit_stats = {
        'total_audit_records': 1250,
        'compliance_score': 94.5,
        'regulatory_alerts': [
            {'id': 1, 'type': 'warning', 'message': 'Quarterly compliance review due', 'date': '2025-01-20'},
            {'id': 2, 'type': 'info', 'message': 'New regulatory guidelines published', 'date': '2025-01-18'},
            {'id': 3, 'type': 'warning', 'message': 'Risk assessment update required', 'date': '2025-01-15'}
        ],
        'pending_reviews': [
            {'id': 1, 'department': 'Accounts', 'type': 'Internal Audit', 'status': 'In Progress'},
            {'id': 2, 'department': 'Loans', 'type': 'Compliance Review', 'status': 'Pending'},
            {'id': 3, 'department': 'Teller', 'type': 'Risk Assessment', 'status': 'Scheduled'}
        ],
        'risk_assessments': [
            {'id': 1, 'area': 'Credit Risk', 'score': 'Low', 'last_updated': '2025-01-15'},
            {'id': 2, 'area': 'Operational Risk', 'score': 'Medium', 'last_updated': '2025-01-10'},
            {'id': 3, 'area': 'Market Risk', 'score': 'Low', 'last_updated': '2025-01-12'}
        ],
        'compliance_reports': [
            {'id': 1, 'type': 'Quarterly Compliance', 'status': 'Completed', 'date': '2025-01-15'},
            {'id': 2, 'type': 'Annual Audit', 'status': 'In Progress', 'date': '2025-01-20'},
            {'id': 3, 'type': 'Risk Assessment', 'status': 'Pending', 'date': '2025-01-25'}
        ],
        'aml_alerts': [
            {'id': 1, 'severity': 'Medium', 'description': 'Unusual transaction pattern', 'status': 'Under Review'},
            {'id': 2, 'severity': 'Low', 'description': 'Large cash deposit', 'status': 'Resolved'},
            {'id': 3, 'severity': 'High', 'description': 'Suspicious activity detected', 'status': 'Investigation'}
        ],
        'fraud_indicators': [
            {'id': 1, 'type': 'Account Takeover', 'risk_level': 'Medium', 'status': 'Monitoring'},
            {'id': 2, 'type': 'Identity Theft', 'risk_level': 'Low', 'status': 'Resolved'},
            {'id': 3, 'type': 'Money Laundering', 'risk_level': 'High', 'status': 'Investigation'}
        ],
        'operational_risks': [
            {'id': 1, 'area': 'IT Security', 'risk_level': 'Medium', 'mitigation': 'In Progress'},
            {'id': 2, 'area': 'Data Privacy', 'risk_level': 'Low', 'mitigation': 'Completed'},
            {'id': 3, 'area': 'Business Continuity', 'risk_level': 'Low', 'mitigation': 'Planned'}
        ],
        'profit_impact_analysis': {
            'total_impact': 250000,
            'risk_adjusted_return': 8.5,
            'capital_efficiency': 92.3
        },
        'regulatory_capital_ratio': {
            'tier1_ratio': 12.5,
            'total_capital_ratio': 15.2,
            'leverage_ratio': 8.3
        },
        'credit_risk_exposure': {
            'total_exposure': 15000000,
            'non_performing_loans': 2.1,
            'provision_coverage': 125.5
        },
        'liquidity_risk_metrics': {
            'liquidity_coverage_ratio': 125.3,
            'net_stable_funding_ratio': 108.7,
            'cash_reserves': 2500000
        },
        'market_risk_indicators': {
            'var_95': 850000,
            'stress_test_result': 'Pass',
            'market_exposure': 12500000
        },
        'stress_test_results': {
            'scenario_1': 'Pass',
            'scenario_2': 'Pass',
            'scenario_3': 'Pass',
            'overall_result': 'Pass'
        }
    }
    
    return render_template('audit_dashboard.html', 
                         user=user, 
                         audit_stats=audit_stats)

# Audit Trail Management
@app.route('/api/audit/trail', methods=['GET'])
@login_required
def get_audit_trail():
    """Get comprehensive audit trail"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Audit and Compliance Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    user_filter = request.args.get('user')
    action_filter = request.args.get('action')
    department_filter = request.args.get('department')
    
    # Filter audit logs
    filtered_logs = filter_audit_logs(
        start_date=start_date,
        end_date=end_date,
        user=user_filter,
        action=action_filter,
        department=department_filter
    )
    
    return jsonify({
        'audit_trail': filtered_logs,
        'total_records': len(filtered_logs),
        'filters_applied': {
            'start_date': start_date,
            'end_date': end_date,
            'user': user_filter,
            'action': action_filter,
            'department': department_filter
        }
    })

@app.route('/api/audit/export', methods=['POST'])
@login_required
def export_audit_report():
    """Export audit report"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Audit and Compliance Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.json
    report_type = data.get('report_type', 'comprehensive')
    date_range = data.get('date_range', 'last_30_days')
    format_type = data.get('format', 'pdf')
    
    # Generate audit report
    report_data = generate_audit_report(
        report_type=report_type,
        date_range=date_range,
        format_type=format_type
    )
    
    return jsonify({
        'message': 'Audit report generated successfully',
        'report_id': report_data['report_id'],
        'download_url': f"/api/audit/download/{report_data['report_id']}",
        'report_summary': report_data['summary']
    })

# Compliance Reporting
@app.route('/api/compliance/report', methods=['GET'])
@login_required
def get_compliance_report():
    """Get compliance report"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Audit and Compliance Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    report_type = request.args.get('type', 'overall')
    department = request.args.get('department', 'all')
    
    compliance_data = generate_compliance_report(report_type, department)
    
    return jsonify({
        'compliance_report': compliance_data,
        'report_type': report_type,
        'department': department,
        'generated_at': datetime.now().isoformat()
    })

@app.route('/api/compliance/assessment', methods=['POST'])
@login_required
def create_compliance_assessment():
    """Create compliance assessment"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Audit and Compliance Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.json
    
    assessment = {
        'assessment_id': f"CA-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'assessor': user['username'],
        'department': data.get('department'),
        'assessment_type': data.get('assessment_type'),
        'compliance_areas': data.get('compliance_areas', []),
        'findings': data.get('findings', []),
        'recommendations': data.get('recommendations', []),
        'risk_level': data.get('risk_level', 'medium'),
        'status': 'pending_review',
        'created_at': datetime.now().isoformat(),
        'due_date': data.get('due_date')
    }
    
    # Save assessment
    compliance_assessments.append(assessment)
    
    # Log audit event
    log_audit_event(
        user_id=user['username'],
        action='compliance_assessment_created',
        details={
            'assessment_id': assessment['assessment_id'],
            'department': assessment['department'],
            'risk_level': assessment['risk_level']
        }
    )
    
    return jsonify({
        'message': 'Compliance assessment created successfully',
        'assessment_id': assessment['assessment_id'],
        'assessment': assessment
    })

# Regulatory Monitoring
@app.route('/api/regulatory/monitoring', methods=['GET'])
@login_required
def get_regulatory_monitoring():
    """Get regulatory monitoring data"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Audit and Compliance Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    monitoring_data = {
        'regulatory_alerts': get_regulatory_alerts(),
        'compliance_status': get_compliance_status(),
        'regulatory_updates': get_regulatory_updates(),
        'risk_indicators': get_risk_indicators(),
        'audit_schedule': get_audit_schedule()
    }
    
    return jsonify(monitoring_data)

@app.route('/api/regulatory/alert', methods=['POST'])
@login_required
def create_regulatory_alert():
    """Create regulatory alert"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Audit and Compliance Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.json
    
    alert = {
        'alert_id': f"RA-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'created_by': user['username'],
        'alert_type': data.get('alert_type'),
        'severity': data.get('severity', 'medium'),
        'title': data.get('title'),
        'description': data.get('description'),
        'affected_departments': data.get('affected_departments', []),
        'regulatory_reference': data.get('regulatory_reference'),
        'action_required': data.get('action_required', True),
        'due_date': data.get('due_date'),
        'status': 'active',
        'created_at': datetime.now().isoformat()
    }
    
    # Save alert
    regulatory_alerts.append(alert)
    
    # Log audit event
    log_audit_event(
        user_id=user['username'],
        action='regulatory_alert_created',
        details={
            'alert_id': alert['alert_id'],
            'alert_type': alert['alert_type'],
            'severity': alert['severity']
        }
    )
    
    return jsonify({
        'message': 'Regulatory alert created successfully',
        'alert_id': alert['alert_id'],
        'alert': alert
    })

# Internal Audit Functions
@app.route('/api/audit/internal/review', methods=['POST'])
@login_required
def create_internal_audit():
    """Create internal audit review"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Audit and Compliance Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.json
    
    audit_review = {
        'review_id': f"IA-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'auditor': user['username'],
        'department': data.get('department'),
        'audit_type': data.get('audit_type'),
        'scope': data.get('scope'),
        'objectives': data.get('objectives', []),
        'findings': data.get('findings', []),
        'recommendations': data.get('recommendations', []),
        'risk_assessment': data.get('risk_assessment'),
        'compliance_score': data.get('compliance_score'),
        'status': 'in_progress',
        'start_date': datetime.now().isoformat(),
        'estimated_completion': data.get('estimated_completion')
    }
    
    # Save audit review
    internal_audits.append(audit_review)
    
    # Log audit event
    log_audit_event(
        user_id=user['username'],
        action='internal_audit_created',
        details={
            'review_id': audit_review['review_id'],
            'department': audit_review['department'],
            'audit_type': audit_review['audit_type']
        }
    )
    
    return jsonify({
        'message': 'Internal audit review created successfully',
        'review_id': audit_review['review_id'],
        'audit_review': audit_review
    })

@app.route('/api/audit/internal/<review_id>', methods=['GET'])
@login_required
def get_internal_audit(review_id):
    """Get internal audit review details"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Audit and Compliance Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    # Find audit review
    audit_review = next((audit for audit in internal_audits if audit['review_id'] == review_id), None)
    
    if not audit_review:
        return jsonify({'error': 'Audit review not found'}), 404
    
    return jsonify({
        'audit_review': audit_review,
        'related_audit_logs': get_related_audit_logs(review_id)
    })

@app.route('/api/audit/internal/<review_id>/update', methods=['PUT'])
@login_required
def update_internal_audit(review_id):
    """Update internal audit review"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Audit and Compliance Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.json
    
    # Find and update audit review
    audit_review = next((audit for audit in internal_audits if audit['review_id'] == review_id), None)
    
    if not audit_review:
        return jsonify({'error': 'Audit review not found'}), 404
    
    # Update fields
    for key, value in data.items():
        if key in audit_review:
            audit_review[key] = value
    
    audit_review['last_updated'] = datetime.now().isoformat()
    audit_review['updated_by'] = user['username']
    
    # Log audit event
    log_audit_event(
        user_id=user['username'],
        action='internal_audit_updated',
        details={
            'review_id': review_id,
            'updated_fields': list(data.keys())
        }
    )
    
    return jsonify({
        'message': 'Internal audit review updated successfully',
        'audit_review': audit_review
    })

# Compliance Dashboard Data
@app.route('/api/compliance/dashboard', methods=['GET'])
@login_required
def get_compliance_dashboard_data():
    """Get compliance dashboard data"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Audit and Compliance Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    dashboard_data = {
        'compliance_score': calculate_compliance_score(),
        'regulatory_alerts': len(get_regulatory_alerts()),
        'pending_assessments': len(get_pending_compliance_assessments()),
        'active_audits': len(get_active_internal_audits()),
        'compliance_by_department': get_compliance_by_department(),
        'recent_findings': get_recent_compliance_findings(),
        'upcoming_deadlines': get_upcoming_compliance_deadlines()
    }
    
    return jsonify(dashboard_data)

# Helper functions for audit and compliance
def calculate_compliance_score():
    """Calculate overall compliance score"""
    total_checks = 25
    passed_checks = 22  # Mock data
    return round((passed_checks / total_checks) * 100, 2)

def get_regulatory_alerts():
    """Get active regulatory alerts"""
    return [
        {
            'alert_id': 'RA-20250115001',
            'title': 'New AML Requirements',
            'severity': 'high',
            'department': 'Accounts Department',
            'due_date': '2025-02-15',
            'status': 'active'
        },
        {
            'alert_id': 'RA-20250115002',
            'title': 'Updated KYC Guidelines',
            'severity': 'medium',
            'department': 'Loans Department',
            'due_date': '2025-03-01',
            'status': 'active'
        }
    ]

def get_pending_audit_reviews():
    """Get pending audit reviews"""
    return [
        {
            'review_id': 'IA-20250115001',
            'department': 'Accounts Department',
            'audit_type': 'operational',
            'status': 'pending',
            'due_date': '2025-01-20'
        }
    ]

def get_risk_assessments():
    """Get risk assessments"""
    return [
        {
            'assessment_id': 'RA-20250115001',
            'department': 'Loans Department',
            'risk_level': 'medium',
            'status': 'in_progress'
        }
    ]

def get_compliance_reports():
    """Get compliance reports"""
    return [
        {
            'report_id': 'CR-20250115001',
            'report_type': 'quarterly',
            'department': 'all',
            'status': 'completed',
            'generated_at': '2025-01-15'
        }
    ]

def filter_audit_logs(start_date=None, end_date=None, user=None, action=None, department=None):
    """Filter audit logs based on criteria"""
    filtered_logs = audit_logs.copy()
    
    if start_date:
        filtered_logs = [log for log in filtered_logs if log['timestamp'] >= start_date]
    if end_date:
        filtered_logs = [log for log in filtered_logs if log['timestamp'] <= end_date]
    if user:
        filtered_logs = [log for log in filtered_logs if user.lower() in log['user_id'].lower()]
    if action:
        filtered_logs = [log for log in filtered_logs if action.lower() in log['action'].lower()]
    if department:
        filtered_logs = [log for log in filtered_logs if department.lower() in log.get('department', '').lower()]
    
    return filtered_logs

def generate_audit_report(report_type, date_range, format_type):
    """Generate audit report"""
    report_id = f"AR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        'report_id': report_id,
        'report_type': report_type,
        'date_range': date_range,
        'format': format_type,
        'summary': {
            'total_events': len(audit_logs),
            'compliance_score': calculate_compliance_score(),
            'risk_level': 'medium'
        }
    }

def generate_compliance_report(report_type, department):
    """Generate compliance report"""
    return {
        'report_type': report_type,
        'department': department,
        'compliance_score': calculate_compliance_score(),
        'regulatory_alerts': get_regulatory_alerts(),
        'pending_assessments': get_pending_compliance_assessments(),
        'generated_at': datetime.now().isoformat()
    }

def get_pending_compliance_assessments():
    """Get pending compliance assessments"""
    return [
        {
            'assessment_id': 'CA-20250115001',
            'department': 'Loans Department',
            'assessment_type': 'regulatory',
            'status': 'pending',
            'due_date': '2025-01-25'
        }
    ]

def get_active_internal_audits():
    """Get active internal audits"""
    return [
        {
            'review_id': 'IA-20250115001',
            'department': 'Accounts Department',
            'audit_type': 'operational',
            'status': 'in_progress',
            'start_date': '2025-01-10'
        }
    ]

def get_compliance_by_department():
    """Get compliance scores by department"""
    return {
        'Accounts Department': 95.0,
        'Loans Department': 88.0,
        'Customer Service Department': 92.0,
        'Admin/HR Department': 98.0
    }

def get_recent_compliance_findings():
    """Get recent compliance findings"""
    return [
        {
            'finding_id': 'CF-20250115001',
            'department': 'Loans Department',
            'finding_type': 'regulatory',
            'severity': 'medium',
            'description': 'Missing documentation for loan applications',
            'status': 'open'
        }
    ]

def get_upcoming_compliance_deadlines():
    """Get upcoming compliance deadlines"""
    return [
        {
            'deadline_id': 'CD-20250115001',
            'title': 'Quarterly Compliance Report',
            'department': 'all',
            'due_date': '2025-01-31',
            'priority': 'high'
        }
    ]

def get_related_audit_logs(review_id):
    """Get audit logs related to a specific review"""
    return [log for log in audit_logs if review_id in log.get('details', {}).get('review_id', '')]

# Initialize audit and compliance data structures
audit_logs = []
compliance_assessments = []
regulatory_alerts = []
internal_audits = []

# ============================================================================
# REAL-LIFE BANKING AUDIT FUNCTIONS - PROFIT MAXIMIZATION & RISK MANAGEMENT
# ============================================================================

# Anti-Money Laundering (AML) Monitoring
@app.route('/api/audit/aml/monitoring', methods=['GET'])
@login_required
def get_aml_monitoring():
    """Real-time AML monitoring and suspicious activity detection"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Audit and Compliance Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    # Real-time AML analysis
    aml_analysis = perform_aml_analysis()
    
    return jsonify({
        'aml_status': aml_analysis['status'],
        'suspicious_transactions': aml_analysis['suspicious_count'],
        'high_risk_customers': aml_analysis['high_risk_customers'],
        'compliance_score': aml_analysis['compliance_score'],
        'recommendations': aml_analysis['recommendations'],
        'profit_impact': aml_analysis['profit_impact']
    })

@app.route('/api/audit/aml/investigation', methods=['POST'])
@login_required
def create_aml_investigation():
    """Create AML investigation case"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Audit and Compliance Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.json
    
    investigation = {
        'case_id': f"AML-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'investigator': user['username'],
        'customer_id': data.get('customer_id'),
        'transaction_ids': data.get('transaction_ids', []),
        'suspicious_patterns': data.get('suspicious_patterns', []),
        'risk_level': calculate_aml_risk_level(data),
        'estimated_loss_prevention': calculate_loss_prevention(data),
        'regulatory_requirements': get_aml_regulatory_requirements(),
        'investigation_priority': determine_investigation_priority(data),
        'status': 'open',
        'created_at': datetime.now().isoformat(),
        'expected_closure': calculate_investigation_timeline(data)
    }
    
    # Save investigation
    aml_investigations.append(investigation)
    
    # Log audit event
    log_audit_event(
        user_id=user['username'],
        action='aml_investigation_created',
        details={
            'case_id': investigation['case_id'],
            'risk_level': investigation['risk_level'],
            'estimated_loss_prevention': investigation['estimated_loss_prevention']
        }
    )
    
    return jsonify({
        'message': 'AML investigation created successfully',
        'case_id': investigation['case_id'],
        'investigation': investigation
    })

# Fraud Detection and Prevention
@app.route('/api/audit/fraud/detection', methods=['GET'])
@login_required
def get_fraud_detection():
    """Real-time fraud detection and prevention system"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Audit and Compliance Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    fraud_analysis = perform_fraud_analysis()
    
    return jsonify({
        'fraud_indicators': fraud_analysis['indicators'],
        'risk_score': fraud_analysis['risk_score'],
        'prevented_losses': fraud_analysis['prevented_losses'],
        'false_positive_rate': fraud_analysis['false_positive_rate'],
        'detection_accuracy': fraud_analysis['detection_accuracy'],
        'profit_protection': fraud_analysis['profit_protection'],
        'recommendations': fraud_analysis['recommendations']
    })

@app.route('/api/audit/fraud/investigation', methods=['POST'])
@login_required
def create_fraud_investigation():
    """Create fraud investigation case"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Audit and Compliance Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.json
    
    investigation = {
        'case_id': f"FRD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'investigator': user['username'],
        'fraud_type': data.get('fraud_type'),
        'affected_accounts': data.get('affected_accounts', []),
        'estimated_loss': data.get('estimated_loss', 0),
        'recovery_probability': calculate_recovery_probability(data),
        'investigation_cost': calculate_investigation_cost(data),
        'net_benefit': calculate_investigation_net_benefit(data),
        'priority_score': calculate_fraud_priority_score(data),
        'status': 'investigating',
        'created_at': datetime.now().isoformat()
    }
    
    # Save investigation
    fraud_investigations.append(investigation)
    
    return jsonify({
        'message': 'Fraud investigation created successfully',
        'case_id': investigation['case_id'],
        'investigation': investigation
    })

# Operational Risk Assessment
@app.route('/api/audit/operational/risk', methods=['GET'])
@login_required
def get_operational_risk():
    """Comprehensive operational risk assessment"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Audit and Compliance Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    risk_assessment = perform_operational_risk_assessment()
    
    return jsonify({
        'operational_risks': risk_assessment['risks'],
        'risk_appetite': risk_assessment['risk_appetite'],
        'mitigation_strategies': risk_assessment['mitigation_strategies'],
        'cost_benefit_analysis': risk_assessment['cost_benefit'],
        'profit_impact': risk_assessment['profit_impact'],
        'recommendations': risk_assessment['recommendations']
    })

# Credit Risk Monitoring
@app.route('/api/audit/credit/risk', methods=['GET'])
@login_required
def get_credit_risk_monitoring():
    """Real-time credit risk monitoring and analysis"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Audit and Compliance Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    credit_analysis = perform_credit_risk_analysis()
    
    return jsonify({
        'portfolio_quality': credit_analysis['portfolio_quality'],
        'default_probability': credit_analysis['default_probability'],
        'expected_losses': credit_analysis['expected_losses'],
        'risk_adjusted_returns': credit_analysis['risk_adjusted_returns'],
        'capital_adequacy': credit_analysis['capital_adequacy'],
        'profit_optimization': credit_analysis['profit_optimization']
    })

# Liquidity Risk Management
@app.route('/api/audit/liquidity/risk', methods=['GET'])
@login_required
def get_liquidity_risk():
    """Liquidity risk assessment and management"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Audit and Compliance Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    liquidity_analysis = perform_liquidity_risk_analysis()
    
    return jsonify({
        'liquidity_ratios': liquidity_analysis['ratios'],
        'cash_flow_projections': liquidity_analysis['cash_flow'],
        'funding_sources': liquidity_analysis['funding_sources'],
        'stress_scenarios': liquidity_analysis['stress_scenarios'],
        'optimization_opportunities': liquidity_analysis['optimization']
    })

# Market Risk Analysis
@app.route('/api/audit/market/risk', methods=['GET'])
@login_required
def get_market_risk():
    """Market risk analysis and value-at-risk calculations"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Audit and Compliance Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    market_analysis = perform_market_risk_analysis()
    
    return jsonify({
        'value_at_risk': market_analysis['var'],
        'expected_shortfall': market_analysis['expected_shortfall'],
        'sensitivity_analysis': market_analysis['sensitivity'],
        'hedging_strategies': market_analysis['hedging'],
        'profit_volatility': market_analysis['profit_volatility']
    })

# Stress Testing
@app.route('/api/audit/stress/test', methods=['POST'])
@login_required
def perform_stress_test():
    """Comprehensive stress testing for banking scenarios"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Audit and Compliance Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.json
    stress_test_results = conduct_stress_test(data)
    
    return jsonify({
        'test_id': stress_test_results['test_id'],
        'scenarios': stress_test_results['scenarios'],
        'capital_impact': stress_test_results['capital_impact'],
        'profit_impact': stress_test_results['profit_impact'],
        'risk_metrics': stress_test_results['risk_metrics'],
        'recommendations': stress_test_results['recommendations']
    })

# Regulatory Capital Compliance
@app.route('/api/audit/capital/compliance', methods=['GET'])
@login_required
def get_capital_compliance():
    """Regulatory capital adequacy and compliance monitoring"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Audit and Compliance Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    capital_analysis = analyze_regulatory_capital()
    
    return jsonify({
        'tier1_ratio': capital_analysis['tier1_ratio'],
        'total_capital_ratio': capital_analysis['total_capital_ratio'],
        'leverage_ratio': capital_analysis['leverage_ratio'],
        'compliance_status': capital_analysis['compliance_status'],
        'buffer_requirements': capital_analysis['buffer_requirements'],
        'optimization_strategies': capital_analysis['optimization']
    })

# Profit Impact Analysis
@app.route('/api/audit/profit/analysis', methods=['GET'])
@login_required
def get_profit_impact_analysis():
    """Comprehensive profit impact analysis from audit findings"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Audit and Compliance Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    profit_analysis = calculate_comprehensive_profit_impact()
    
    return jsonify({
        'revenue_protection': profit_analysis['revenue_protection'],
        'cost_savings': profit_analysis['cost_savings'],
        'risk_mitigation_value': profit_analysis['risk_mitigation'],
        'compliance_cost_avoidance': profit_analysis['compliance_savings'],
        'operational_efficiency_gains': profit_analysis['efficiency_gains'],
        'total_profit_impact': profit_analysis['total_impact'],
        'roi_from_audit': profit_analysis['audit_roi']
    })

# Real-time Monitoring Dashboard
@app.route('/api/audit/realtime/monitoring', methods=['GET'])
@login_required
def get_realtime_monitoring():
    """Real-time banking operations monitoring"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Audit and Compliance Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    monitoring_data = get_realtime_banking_metrics()
    
    return jsonify({
        'transaction_volume': monitoring_data['transaction_volume'],
        'system_performance': monitoring_data['system_performance'],
        'risk_alerts': monitoring_data['risk_alerts'],
        'compliance_status': monitoring_data['compliance_status'],
        'profit_metrics': monitoring_data['profit_metrics'],
        'operational_kpis': monitoring_data['operational_kpis']
    })

# Additional helper functions for audit and compliance
def get_compliance_status():
    """Get overall compliance status"""
    return {
        'overall_score': calculate_compliance_score(),
        'status': 'compliant' if calculate_compliance_score() >= 90 else 'needs_attention',
        'last_updated': datetime.now().isoformat()
    }

def get_regulatory_updates():
    """Get recent regulatory updates"""
    return [
        {
            'update_id': 'RU-20250115001',
            'title': 'Updated AML Guidelines',
            'effective_date': '2025-02-01',
            'impact_level': 'high',
            'affected_departments': ['Accounts Department', 'Loans Department']
        }
    ]

def get_risk_indicators():
    """Get risk indicators"""
    return {
        'operational_risk': 'medium',
        'credit_risk': 'low',
        'market_risk': 'low',
        'liquidity_risk': 'low',
        'compliance_risk': 'medium'
    }

def get_audit_schedule():
    """Get audit schedule"""
    return [
        {
            'audit_id': 'AS-20250115001',
            'department': 'Accounts Department',
            'audit_type': 'operational',
            'scheduled_date': '2025-01-20',
            'auditor': 'admin_audit',
            'status': 'scheduled'
        }
    ]

# ============================================================================
# COMPREHENSIVE REAL-LIFE BANKING AUDIT HELPER FUNCTIONS
# ============================================================================

# Initialize audit data structures
aml_investigations = []
fraud_investigations = []
stress_test_results = []
capital_analysis_cache = {}

def calculate_comprehensive_compliance_score():
    """Calculate comprehensive compliance score with real banking metrics"""
    # Basel III compliance factors
    basel_score = 85.0
    
    # AML/KYC compliance
    aml_score = 92.0
    
    # Operational risk compliance
    operational_score = 88.0
    
    # Market risk compliance
    market_score = 90.0
    
    # Credit risk compliance
    credit_score = 87.0
    
    # Liquidity risk compliance
    liquidity_score = 89.0
    
    # Weighted compliance score
    weights = {
        'basel': 0.25,
        'aml': 0.20,
        'operational': 0.15,
        'market': 0.15,
        'credit': 0.15,
        'liquidity': 0.10
    }
    
    total_score = (
        basel_score * weights['basel'] +
        aml_score * weights['aml'] +
        operational_score * weights['operational'] +
        market_score * weights['market'] +
        credit_score * weights['credit'] +
        liquidity_score * weights['liquidity']
    )
    
    return round(total_score, 2)

def get_aml_suspicious_activities():
    """Get AML suspicious activities with profit impact analysis"""
    return {
        'total_alerts': 23,
        'high_priority': 5,
        'under_investigation': 8,
        'resolved': 10,
        'false_positives': 15,
        'estimated_loss_prevention': 2500000.00,  # $2.5M prevented
        'investigation_costs': 150000.00,  # $150K costs
        'net_benefit': 2350000.00,  # $2.35M net benefit
        'compliance_score': 94.5,
        'regulatory_penalties_avoided': 500000.00  # $500K penalties avoided
    }

def get_fraud_risk_indicators():
    """Get fraud risk indicators with real-time analysis"""
    return {
        'fraud_attempts_detected': 47,
        'fraud_attempts_prevented': 42,
        'detection_rate': 89.4,  # 89.4% detection rate
        'false_positive_rate': 12.3,  # 12.3% false positives
        'prevented_losses': 1800000.00,  # $1.8M prevented
        'investigation_costs': 95000.00,  # $95K costs
        'net_savings': 1705000.00,  # $1.705M net savings
        'customer_impact_score': 8.7,  # Customer satisfaction impact
        'system_efficiency': 91.2  # System efficiency percentage
    }

def get_operational_risk_metrics():
    """Get operational risk metrics with business impact"""
    return {
        'operational_incidents': 12,
        'system_downtime_hours': 4.5,
        'revenue_impact': 85000.00,  # $85K revenue impact
        'mitigation_costs': 25000.00,  # $25K mitigation costs
        'process_efficiency': 94.2,  # 94.2% efficiency
        'employee_error_rate': 0.8,  # 0.8% error rate
        'automation_level': 87.5,  # 87.5% automated processes
        'cost_savings_potential': 320000.00,  # $320K potential savings
        'risk_appetite_utilization': 65.3  # 65.3% of risk appetite used
    }

def calculate_audit_profit_impact():
    """Calculate comprehensive audit profit impact"""
    # Revenue protection
    fraud_prevention = 1800000.00
    aml_compliance = 2500000.00
    regulatory_penalty_avoidance = 500000.00
    
    # Cost savings
    operational_efficiency = 320000.00
    process_automation = 150000.00
    error_reduction = 75000.00
    
    # Risk mitigation value
    credit_risk_mitigation = 450000.00
    market_risk_hedging = 200000.00
    liquidity_optimization = 180000.00
    
    total_impact = (
        fraud_prevention + aml_compliance + regulatory_penalty_avoidance +
        operational_efficiency + process_automation + error_reduction +
        credit_risk_mitigation + market_risk_hedging + liquidity_optimization
    )
    
    return {
        'total_profit_impact': total_impact,
        'revenue_protection': fraud_prevention + aml_compliance + regulatory_penalty_avoidance,
        'cost_savings': operational_efficiency + process_automation + error_reduction,
        'risk_mitigation': credit_risk_mitigation + market_risk_hedging + liquidity_optimization,
        'roi_percentage': 425.7,  # 425.7% ROI on audit investment
        'payback_period_months': 2.8  # 2.8 months payback period
    }

def calculate_regulatory_capital_compliance():
    """Calculate regulatory capital compliance ratios"""
    # Basel III capital ratios
    tier1_capital = 45000000.00  # $45M
    total_capital = 65000000.00  # $65M
    risk_weighted_assets = 420000000.00  # $420M
    total_assets = 850000000.00  # $850M
    
    tier1_ratio = (tier1_capital / risk_weighted_assets) * 100
    total_capital_ratio = (total_capital / risk_weighted_assets) * 100
    leverage_ratio = (tier1_capital / total_assets) * 100
    
    return {
        'tier1_ratio': round(tier1_ratio, 2),
        'total_capital_ratio': round(total_capital_ratio, 2),
        'leverage_ratio': round(leverage_ratio, 2),
        'minimum_requirements': {
            'tier1_minimum': 6.0,
            'total_capital_minimum': 8.0,
            'leverage_minimum': 3.0
        },
        'compliance_status': 'compliant' if tier1_ratio >= 6.0 and total_capital_ratio >= 8.0 and leverage_ratio >= 3.0 else 'non_compliant',
        'buffer_above_minimum': {
            'tier1_buffer': round(tier1_ratio - 6.0, 2),
            'total_capital_buffer': round(total_capital_ratio - 8.0, 2),
            'leverage_buffer': round(leverage_ratio - 3.0, 2)
        }
    }

def get_credit_risk_exposure_analysis():
    """Get comprehensive credit risk exposure analysis"""
    total_loans = 650000000.00  # $650M total loans
    non_performing_loans = 19500000.00  # $19.5M NPLs
    provisions = 12000000.00  # $12M provisions
    
    return {
        'total_exposure': total_loans,
        'non_performing_ratio': round((non_performing_loans / total_loans) * 100, 2),
        'provision_coverage': round((provisions / non_performing_loans) * 100, 2),
        'expected_losses': 8500000.00,  # $8.5M expected losses
        'unexpected_losses': 15000000.00,  # $15M unexpected losses
        'risk_adjusted_returns': 12.8,  # 12.8% RAROC
        'portfolio_quality_grade': 'B+',
        'concentration_risk': 'moderate',
        'diversification_score': 78.5
    }

def get_liquidity_risk_assessment():
    """Get liquidity risk assessment with optimization opportunities"""
    return {
        'liquidity_coverage_ratio': 125.8,  # 125.8% LCR
        'net_stable_funding_ratio': 118.3,  # 118.3% NSFR
        'cash_to_assets_ratio': 8.7,  # 8.7%
        'loan_to_deposit_ratio': 82.4,  # 82.4%
        'funding_concentration': 'low',
        'maturity_mismatch': 'acceptable',
        'stress_test_survival': '45 days',
        'optimization_potential': 45000000.00,  # $45M optimization potential
        'cost_of_funding': 2.3  # 2.3% average cost
    }

def get_market_risk_indicators():
    """Get market risk indicators with VaR calculations"""
    return {
        'value_at_risk_1day': 850000.00,  # $850K 1-day VaR
        'value_at_risk_10day': 2680000.00,  # $2.68M 10-day VaR
        'expected_shortfall': 1200000.00,  # $1.2M expected shortfall
        'interest_rate_sensitivity': 'moderate',
        'currency_exposure': 'low',
        'trading_book_var': 320000.00,  # $320K trading VaR
        'banking_book_var': 530000.00,  # $530K banking VaR
        'correlation_risk': 'managed',
        'hedging_effectiveness': 89.7  # 89.7% hedging effectiveness
    }

def get_latest_stress_test_results():
    """Get latest stress test results"""
    return {
        'test_date': '2025-01-10',
        'scenarios_tested': 5,
        'worst_case_capital_impact': -12000000.00,  # -$12M worst case
        'base_case_capital_impact': -3500000.00,  # -$3.5M base case
        'best_case_capital_impact': 2000000.00,  # +$2M best case
        'stress_survival_period': '18 months',
        'capital_adequacy_maintained': True,
        'liquidity_adequate': True,
        'operational_resilience': 'strong',
        'recovery_plan_triggered': False
    }

# Real-life banking audit analysis functions
def perform_aml_analysis():
    """Perform comprehensive AML analysis"""
    return {
        'status': 'monitoring',
        'suspicious_count': 23,
        'high_risk_customers': 45,
        'compliance_score': 94.5,
        'recommendations': [
            'Enhance transaction monitoring algorithms',
            'Increase customer due diligence frequency',
            'Implement advanced pattern recognition'
        ],
        'profit_impact': 2350000.00
    }

def perform_fraud_analysis():
    """Perform real-time fraud analysis"""
    return {
        'indicators': 47,
        'risk_score': 78.5,
        'prevented_losses': 1800000.00,
        'false_positive_rate': 12.3,
        'detection_accuracy': 89.4,
        'profit_protection': 1705000.00,
        'recommendations': [
            'Optimize fraud detection algorithms',
            'Reduce false positive rates',
            'Enhance real-time monitoring'
        ]
    }

def perform_operational_risk_assessment():
    """Perform operational risk assessment"""
    return {
        'risks': 12,
        'risk_appetite': 65.3,
        'mitigation_strategies': [
            'Process automation',
            'Employee training',
            'System redundancy'
        ],
        'cost_benefit': {
            'mitigation_cost': 25000.00,
            'potential_savings': 320000.00,
            'roi': 1280.0
        },
        'profit_impact': 295000.00,
        'recommendations': [
            'Increase automation level',
            'Implement predictive maintenance',
            'Enhance business continuity planning'
        ]
    }

def perform_credit_risk_analysis():
    """Perform credit risk analysis"""
    return {
        'portfolio_quality': 'B+',
        'default_probability': 3.2,
        'expected_losses': 8500000.00,
        'risk_adjusted_returns': 12.8,
        'capital_adequacy': 'adequate',
        'profit_optimization': {
            'pricing_optimization': 15000000.00,
            'portfolio_rebalancing': 8500000.00,
            'risk_mitigation': 450000.00
        }
    }

def perform_liquidity_risk_analysis():
    """Perform liquidity risk analysis"""
    return {
        'ratios': {
            'lcr': 125.8,
            'nsfr': 118.3,
            'loan_to_deposit': 82.4
        },
        'cash_flow': 'stable',
        'funding_sources': 'diversified',
        'stress_scenarios': 'passed',
        'optimization': {
            'funding_cost_reduction': 12000000.00,
            'liquidity_buffer_optimization': 45000000.00
        }
    }

def perform_market_risk_analysis():
    """Perform market risk analysis"""
    return {
        'var': 850000.00,
        'expected_shortfall': 1200000.00,
        'sensitivity': 'moderate',
        'hedging': {
            'effectiveness': 89.7,
            'cost': 450000.00,
            'benefit': 2800000.00
        },
        'profit_volatility': 'low'
    }

def conduct_stress_test(data):
    """Conduct comprehensive stress test"""
    test_id = f"ST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        'test_id': test_id,
        'scenarios': data.get('scenarios', ['base', 'adverse', 'severely_adverse']),
        'capital_impact': {
            'base': -3500000.00,
            'adverse': -8500000.00,
            'severely_adverse': -12000000.00
        },
        'profit_impact': {
            'base': 2000000.00,
            'adverse': -1500000.00,
            'severely_adverse': -4500000.00
        },
        'risk_metrics': {
            'capital_adequacy_maintained': True,
            'liquidity_adequate': True,
            'operational_resilience': 'strong'
        },
        'recommendations': [
            'Maintain current capital buffers',
            'Monitor market conditions closely',
            'Prepare contingency funding plans'
        ]
    }

def analyze_regulatory_capital():
    """Analyze regulatory capital requirements"""
    return calculate_regulatory_capital_compliance()

def calculate_comprehensive_profit_impact():
    """Calculate comprehensive profit impact from audit activities"""
    return {
        'revenue_protection': 4800000.00,  # $4.8M
        'cost_savings': 545000.00,  # $545K
        'risk_mitigation': 830000.00,  # $830K
        'compliance_savings': 500000.00,  # $500K
        'efficiency_gains': 320000.00,  # $320K
        'total_impact': 6995000.00,  # $6.995M
        'audit_roi': 425.7  # 425.7% ROI
    }

def get_realtime_banking_metrics():
    """Get real-time banking operation metrics"""
    return {
        'transaction_volume': {
            'daily_transactions': 45670,
            'daily_value': 125000000.00,
            'peak_hour_volume': 8750,
            'average_transaction_size': 2738.45
        },
        'system_performance': {
            'uptime': 99.97,
            'response_time_ms': 185,
            'throughput_tps': 1250,
            'error_rate': 0.03
        },
        'risk_alerts': {
            'fraud_alerts': 23,
            'aml_alerts': 15,
            'operational_alerts': 8,
            'market_risk_alerts': 3
        },
        'compliance_status': {
            'overall_score': 94.5,
            'regulatory_breaches': 0,
            'pending_reports': 2,
            'audit_findings': 5
        },
        'profit_metrics': {
            'daily_revenue': 850000.00,
            'cost_efficiency': 87.5,
            'margin_optimization': 12.8,
            'risk_adjusted_return': 15.2
        },
        'operational_kpis': {
            'customer_satisfaction': 4.7,
            'employee_productivity': 92.3,
            'process_automation': 87.5,
            'innovation_index': 78.9
        }
    }

# Helper functions for AML investigations
def calculate_aml_risk_level(data):
    """Calculate AML risk level based on transaction patterns"""
    risk_factors = {
        'transaction_amount': data.get('transaction_amount', 0),
        'frequency': data.get('frequency', 1),
        'geographic_risk': data.get('geographic_risk', 'low'),
        'customer_profile': data.get('customer_profile', 'standard')
    }
    
    # Risk scoring algorithm
    score = 0
    if risk_factors['transaction_amount'] > 10000:
        score += 25
    if risk_factors['frequency'] > 10:
        score += 20
    if risk_factors['geographic_risk'] == 'high':
        score += 30
    if risk_factors['customer_profile'] == 'high_risk':
        score += 25
    
    if score >= 70:
        return 'high'
    elif score >= 40:
        return 'medium'
    else:
        return 'low'

def calculate_loss_prevention(data):
    """Calculate estimated loss prevention from investigation"""
    base_amount = data.get('transaction_amount', 0)
    risk_multiplier = 2.5 if data.get('risk_level') == 'high' else 1.5
    return base_amount * risk_multiplier

def get_aml_regulatory_requirements():
    """Get AML regulatory requirements"""
    return [
        'Customer Due Diligence (CDD)',
        'Enhanced Due Diligence (EDD)',
        'Suspicious Activity Reporting (SAR)',
        'Currency Transaction Reporting (CTR)',
        'Beneficial Ownership Identification',
        'Ongoing Monitoring Requirements'
    ]

def determine_investigation_priority(data):
    """Determine investigation priority based on risk factors"""
    risk_level = data.get('risk_level', 'low')
    amount = data.get('transaction_amount', 0)
    
    if risk_level == 'high' and amount > 50000:
        return 'critical'
    elif risk_level == 'high' or amount > 25000:
        return 'high'
    elif risk_level == 'medium' or amount > 10000:
        return 'medium'
    else:
        return 'low'

def calculate_investigation_timeline(data):
    """Calculate expected investigation timeline"""
    priority = data.get('investigation_priority', 'medium')
    complexity = data.get('complexity', 'standard')
    
    base_days = {
        'critical': 3,
        'high': 7,
        'medium': 14,
        'low': 30
    }
    
    complexity_multiplier = {
        'simple': 0.7,
        'standard': 1.0,
        'complex': 1.5,
        'very_complex': 2.0
    }
    
    days = base_days.get(priority, 14) * complexity_multiplier.get(complexity, 1.0)
    return (datetime.now() + timedelta(days=int(days))).isoformat()

# Helper functions for fraud investigations
def calculate_recovery_probability(data):
    """Calculate probability of fraud loss recovery"""
    fraud_type = data.get('fraud_type', 'unknown')
    detection_speed = data.get('detection_speed', 'medium')
    
    base_probability = {
        'card_fraud': 0.85,
        'wire_fraud': 0.45,
        'check_fraud': 0.65,
        'identity_theft': 0.55,
        'account_takeover': 0.75
    }
    
    speed_multiplier = {
        'immediate': 1.2,
        'fast': 1.1,
        'medium': 1.0,
        'slow': 0.8,
        'very_slow': 0.6
    }
    
    probability = base_probability.get(fraud_type, 0.6) * speed_multiplier.get(detection_speed, 1.0)
    return min(probability, 0.95)  # Cap at 95%

def calculate_investigation_cost(data):
    """Calculate investigation cost based on complexity"""
    complexity = data.get('complexity', 'standard')
    estimated_loss = data.get('estimated_loss', 0)
    
    base_cost = {
        'simple': 2500,
        'standard': 5000,
        'complex': 10000,
        'very_complex': 20000
    }
    
    # Add percentage of loss amount for high-value cases
    percentage_cost = estimated_loss * 0.02 if estimated_loss > 50000 else 0
    
    return base_cost.get(complexity, 5000) + percentage_cost

def calculate_investigation_net_benefit(data):
    """Calculate net benefit of fraud investigation"""
    estimated_loss = data.get('estimated_loss', 0)
    recovery_probability = calculate_recovery_probability(data)
    investigation_cost = calculate_investigation_cost(data)
    
    expected_recovery = estimated_loss * recovery_probability
    net_benefit = expected_recovery - investigation_cost
    
    return max(net_benefit, 0)  # Don't show negative benefits

def calculate_fraud_priority_score(data):
    """Calculate fraud investigation priority score"""
    estimated_loss = data.get('estimated_loss', 0)
    net_benefit = calculate_investigation_net_benefit(data)
    customer_impact = data.get('customer_impact', 'low')
    
    # Loss amount score (0-40 points)
    loss_score = min(estimated_loss / 1000, 40)
    
    # Net benefit score (0-30 points)
    benefit_score = min(net_benefit / 1000, 30)
    
    # Customer impact score (0-30 points)
    impact_scores = {'low': 5, 'medium': 15, 'high': 25, 'critical': 30}
    impact_score = impact_scores.get(customer_impact, 5)
    
    total_score = loss_score + benefit_score + impact_score
    return round(total_score, 1)

# ============================================================================
# TREASURY DEPARTMENT - COMPREHENSIVE REAL-LIFE BANKING TREASURY MANAGEMENT
# ============================================================================

@app.route('/treasury_dashboard')
@login_required
def treasury_dashboard():
    """Comprehensive Treasury Management Dashboard with Real-Life Banking Logic"""
    # Check if user has access to treasury department
    if not (current_user.department.value == 'Treasury Department' or
            (current_user.department.value == 'Admin/HR Department' and current_user.role.value == 'admin')):
        flash('Access denied. You do not have permission to access the Treasury Dashboard.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get comprehensive treasury statistics with real-time data
    treasury_stats = {
        'total_assets': get_total_bank_assets(),
        'total_liabilities': get_total_bank_liabilities(),
        'net_interest_margin': calculate_net_interest_margin(),
        'liquidity_position': get_current_liquidity_position(),
        'investment_portfolio_value': get_investment_portfolio_value(),
        'treasury_bonds_portfolio': get_treasury_bonds_portfolio(),
        'cash_flow_forecast': get_cash_flow_forecast(),
        'funding_sources': get_funding_sources_analysis(),
        'interest_rate_exposure': get_interest_rate_exposure(),
        'alm_metrics': get_asset_liability_management_metrics(),
        'profit_optimization': calculate_treasury_profit_optimization(),
        'risk_metrics': get_treasury_risk_metrics(),
        'regulatory_ratios': get_treasury_regulatory_ratios(),
        'market_data': get_real_time_market_data()
    }
    
    return render_template('treasury_dashboard.html', 
                         user=current_user, 
                         treasury_stats=treasury_stats)

# Cash Flow Management
@app.route('/api/treasury/cashflow/forecast', methods=['GET'])
@login_required
def get_cashflow_forecast():
    """Real-time cash flow forecasting with optimization"""
    if not (current_user.department.value == 'Treasury Department' or
            (current_user.department.value == 'Admin/HR Department' and current_user.role.value == 'admin')):
        return jsonify({'error': 'Access denied'}), 403
    
    forecast_period = request.args.get('period', '30_days')
    forecast_data = generate_cashflow_forecast(forecast_period)
    
    return jsonify({
        'forecast_period': forecast_period,
        'cash_inflows': forecast_data['inflows'],
        'cash_outflows': forecast_data['outflows'],
        'net_cashflow': forecast_data['net_flow'],
        'liquidity_gaps': forecast_data['gaps'],
        'optimization_opportunities': forecast_data['optimization'],
        'funding_requirements': forecast_data['funding_needs'],
        'investment_opportunities': forecast_data['investment_ops']
    })

@app.route('/api/treasury/cashflow/optimize', methods=['POST'])
@login_required
def optimize_cashflow():
    """Optimize cash flow allocation for maximum profitability"""
    if not (current_user.department.value == 'Treasury Department' or
            (current_user.department.value == 'Admin/HR Department' and current_user.role.value == 'admin')):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.json
    optimization_result = perform_cashflow_optimization(data)
    
    return jsonify({
        'optimization_id': optimization_result['id'],
        'recommended_actions': optimization_result['actions'],
        'expected_profit_increase': optimization_result['profit_increase'],
        'risk_impact': optimization_result['risk_impact'],
        'implementation_timeline': optimization_result['timeline']
    })

# Investment Portfolio Management
@app.route('/api/treasury/investments/portfolio', methods=['GET'])
@login_required
def get_investment_portfolio():
    """Get comprehensive investment portfolio with real-time valuations"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Treasury Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    portfolio_data = get_real_time_portfolio_data()
    
    return jsonify({
        'total_portfolio_value': portfolio_data['total_value'],
        'asset_allocation': portfolio_data['allocation'],
        'performance_metrics': portfolio_data['performance'],
        'risk_metrics': portfolio_data['risk'],
        'yield_analysis': portfolio_data['yield'],
        'duration_analysis': portfolio_data['duration'],
        'credit_quality': portfolio_data['credit_quality'],
        'liquidity_profile': portfolio_data['liquidity']
    })

@app.route('/api/treasury/investments/optimize', methods=['POST'])
@login_required
def optimize_investment_portfolio():
    """Optimize investment portfolio for maximum risk-adjusted returns"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Treasury Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.json
    optimization_result = perform_portfolio_optimization(data)
    
    return jsonify({
        'optimization_id': optimization_result['id'],
        'recommended_allocation': optimization_result['allocation'],
        'expected_return': optimization_result['expected_return'],
        'risk_reduction': optimization_result['risk_reduction'],
        'profit_improvement': optimization_result['profit_improvement']
    })

# Treasury Bonds Management
@app.route('/api/treasury/bonds/portfolio', methods=['GET'])
@login_required
def get_treasury_bonds_portfolio():
    """Get treasury bonds portfolio with real-time pricing"""
    if not (current_user.department.value == 'Treasury Department' or
            (current_user.department.value == 'Admin/HR Department' and current_user.role.value == 'admin')):
        return jsonify({'error': 'Access denied'}), 403
    
    bonds_data = get_treasury_bonds_data()
    
    return jsonify({
        'total_bonds_value': bonds_data['total_value'],
        'bonds_by_maturity': bonds_data['maturity_breakdown'],
        'yield_curve_analysis': bonds_data['yield_curve'],
        'duration_risk': bonds_data['duration_risk'],
        'credit_risk': bonds_data['credit_risk'],
        'market_value_changes': bonds_data['market_changes'],
        'income_generation': bonds_data['income'],
        'hedging_effectiveness': bonds_data['hedging']
    })

@app.route('/api/treasury/bonds/trade', methods=['POST'])
@login_required
def execute_bond_trade():
    """Execute treasury bond trades with real-time pricing"""
    if not (current_user.department.value == 'Treasury Department' or
            (current_user.department.value == 'Admin/HR Department' and current_user.role.value == 'admin')):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.json
    trade_result = execute_treasury_bond_trade(data)
    
    return jsonify({
        'trade_id': trade_result['trade_id'],
        'execution_price': trade_result['price'],
        'total_cost': trade_result['total_cost'],
        'yield_to_maturity': trade_result['ytm'],
        'duration': trade_result['duration'],
        'profit_impact': trade_result['profit_impact'],
        'risk_impact': trade_result['risk_impact']
    })

# Asset-Liability Management (ALM)
@app.route('/api/treasury/alm/analysis', methods=['GET'])
@login_required
def get_alm_analysis():
    """Comprehensive Asset-Liability Management analysis"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Treasury Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    alm_data = perform_alm_analysis()
    
    return jsonify({
        'interest_rate_risk': alm_data['interest_rate_risk'],
        'liquidity_risk': alm_data['liquidity_risk'],
        'maturity_gap_analysis': alm_data['maturity_gaps'],
        'duration_gap': alm_data['duration_gap'],
        'net_interest_income_simulation': alm_data['nii_simulation'],
        'economic_value_equity': alm_data['eve'],
        'optimization_recommendations': alm_data['recommendations']
    })

@app.route('/api/treasury/alm/optimize', methods=['POST'])
@login_required
def optimize_alm():
    """Optimize Asset-Liability Management for maximum profitability"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Treasury Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.json
    optimization_result = perform_alm_optimization(data)
    
    return jsonify({
        'optimization_id': optimization_result['id'],
        'recommended_actions': optimization_result['actions'],
        'profit_improvement': optimization_result['profit_improvement'],
        'risk_reduction': optimization_result['risk_reduction'],
        'capital_efficiency': optimization_result['capital_efficiency']
    })

# Funding and Liquidity Management
@app.route('/api/treasury/funding/sources', methods=['GET'])
@login_required
def get_funding_sources():
    """Get comprehensive funding sources analysis"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Treasury Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    funding_data = analyze_funding_sources()
    
    return jsonify({
        'funding_mix': funding_data['mix'],
        'cost_analysis': funding_data['costs'],
        'maturity_profile': funding_data['maturity'],
        'concentration_risk': funding_data['concentration'],
        'optimization_opportunities': funding_data['optimization'],
        'stress_testing': funding_data['stress_results']
    })

@app.route('/api/treasury/funding/optimize', methods=['POST'])
@login_required
def optimize_funding():
    """Optimize funding mix for minimum cost and maximum stability"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Treasury Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.json
    optimization_result = optimize_funding_mix(data)
    
    return jsonify({
        'optimization_id': optimization_result['id'],
        'recommended_mix': optimization_result['mix'],
        'cost_savings': optimization_result['cost_savings'],
        'stability_improvement': optimization_result['stability'],
        'risk_impact': optimization_result['risk_impact']
    })

# Interest Rate Risk Management
@app.route('/api/treasury/interest_rate/risk', methods=['GET'])
@login_required
def get_interest_rate_risk():
    """Comprehensive interest rate risk analysis"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Treasury Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    irr_data = analyze_interest_rate_risk()
    
    return jsonify({
        'duration_analysis': irr_data['duration'],
        'gap_analysis': irr_data['gaps'],
        'sensitivity_analysis': irr_data['sensitivity'],
        'scenario_analysis': irr_data['scenarios'],
        'hedging_strategies': irr_data['hedging'],
        'profit_impact': irr_data['profit_impact']
    })

@app.route('/api/treasury/interest_rate/hedge', methods=['POST'])
@login_required
def create_interest_rate_hedge():
    """Create interest rate hedge to optimize profit and reduce risk"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Treasury Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.json
    hedge_result = create_irr_hedge(data)
    
    return jsonify({
        'hedge_id': hedge_result['hedge_id'],
        'hedge_type': hedge_result['type'],
        'notional_amount': hedge_result['notional'],
        'cost': hedge_result['cost'],
        'risk_reduction': hedge_result['risk_reduction'],
        'profit_protection': hedge_result['profit_protection']
    })

# Capital Allocation and Optimization
@app.route('/api/treasury/capital/allocation', methods=['GET'])
@login_required
def get_capital_allocation():
    """Get optimal capital allocation across business lines"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Treasury Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    allocation_data = analyze_capital_allocation()
    
    return jsonify({
        'current_allocation': allocation_data['current'],
        'optimal_allocation': allocation_data['optimal'],
        'rorac_by_business': allocation_data['rorac'],
        'capital_efficiency': allocation_data['efficiency'],
        'reallocation_opportunities': allocation_data['opportunities'],
        'profit_improvement': allocation_data['profit_improvement']
    })

@app.route('/api/treasury/capital/optimize', methods=['POST'])
@login_required
def optimize_capital_allocation():
    """Optimize capital allocation for maximum RORAC"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Treasury Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.json
    optimization_result = perform_capital_optimization(data)
    
    return jsonify({
        'optimization_id': optimization_result['id'],
        'recommended_allocation': optimization_result['allocation'],
        'rorac_improvement': optimization_result['rorac_improvement'],
        'profit_increase': optimization_result['profit_increase'],
        'risk_impact': optimization_result['risk_impact']
    })

# Real-time Market Data and Analytics
@app.route('/api/treasury/market/data', methods=['GET'])
@login_required
def get_market_data():
    """Get real-time market data for treasury operations"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Treasury Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    market_data = get_real_time_market_data()
    
    return jsonify({
        'interest_rates': market_data['rates'],
        'yield_curves': market_data['yield_curves'],
        'fx_rates': market_data['fx_rates'],
        'bond_prices': market_data['bond_prices'],
        'volatility': market_data['volatility'],
        'economic_indicators': market_data['economic_indicators']
    })

# Treasury Performance Analytics
@app.route('/api/treasury/performance/analytics', methods=['GET'])
@login_required
def get_treasury_performance():
    """Comprehensive treasury performance analytics"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Treasury Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    performance_data = analyze_treasury_performance()
    
    return jsonify({
        'net_interest_income': performance_data['nii'],
        'non_interest_income': performance_data['non_interest'],
        'funding_costs': performance_data['funding_costs'],
        'investment_returns': performance_data['investment_returns'],
        'risk_adjusted_returns': performance_data['risk_adjusted'],
        'efficiency_metrics': performance_data['efficiency'],
        'benchmarking': performance_data['benchmarks']
    })

# Treasury Reporting and Compliance
@app.route('/api/treasury/reports/generate', methods=['POST'])
@login_required
def generate_treasury_report():
    """Generate comprehensive treasury reports"""
    user = get_current_user()
    
    if user['department'] not in ['Admin/HR Department', 'Treasury Department']:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.json
    report_result = generate_treasury_report_data(data)
    
    return jsonify({
        'report_id': report_result['report_id'],
        'report_type': report_result['type'],
        'generation_status': report_result['status'],
        'download_url': report_result['download_url'],
        'summary': report_result['summary']
    })

# ============================================================================
# TREASURY DEPARTMENT HELPER FUNCTIONS - REAL-LIFE BANKING LOGIC
# ============================================================================

# Initialize treasury data structures
treasury_bonds_portfolio = []
investment_portfolio = []
funding_sources = []
alm_positions = []
interest_rate_hedges = []
treasury_trades = []

def get_total_bank_assets():
    """Get total bank assets with real-time valuation"""
    # Mock data representing real bank assets
    return {
        'total_assets': 2850000000.00,  # $2.85B total assets
        'cash_and_equivalents': 285000000.00,  # $285M cash
        'loans_gross': 1995000000.00,  # $1.995B loans
        'securities': 425000000.00,  # $425M securities
        'fixed_assets': 95000000.00,  # $95M fixed assets
        'other_assets': 50000000.00,  # $50M other
        'growth_rate': 8.5,  # 8.5% annual growth
        'asset_quality': 'A+',
        'diversification_score': 87.5
    }

def get_total_bank_liabilities():
    """Get total bank liabilities with detailed breakdown"""
    return {
        'total_liabilities': 2565000000.00,  # $2.565B total liabilities
        'deposits': 2280000000.00,  # $2.28B deposits
        'borrowings': 185000000.00,  # $185M borrowings
        'other_liabilities': 100000000.00,  # $100M other
        'equity': 285000000.00,  # $285M equity
        'leverage_ratio': 10.0,  # 10:1 leverage
        'funding_stability': 'stable',
        'cost_of_funds': 2.45  # 2.45% average cost
    }

def calculate_net_interest_margin():
    """Calculate net interest margin with optimization opportunities"""
    interest_income = 142500000.00  # $142.5M interest income
    interest_expense = 69750000.00   # $69.75M interest expense
    average_earning_assets = 2565000000.00  # $2.565B average earning assets
    
    net_interest_income = interest_income - interest_expense
    nim = (net_interest_income / average_earning_assets) * 100
    
    return {
        'net_interest_margin': round(nim, 2),
        'net_interest_income': net_interest_income,
        'interest_income': interest_income,
        'interest_expense': interest_expense,
        'optimization_potential': 15750000.00,  # $15.75M potential
        'benchmark_nim': 3.25,  # Industry benchmark
        'performance_vs_benchmark': round(nim - 3.25, 2)
    }

def get_current_liquidity_position():
    """Get current liquidity position with stress testing"""
    return {
        'cash_position': 285000000.00,  # $285M cash
        'available_credit_lines': 150000000.00,  # $150M credit lines
        'marketable_securities': 425000000.00,  # $425M marketable securities
        'total_liquidity': 860000000.00,  # $860M total liquidity
        'liquidity_ratio': 30.2,  # 30.2% liquidity ratio
        'stress_test_survival': 45,  # 45 days survival
        'optimization_opportunities': 125000000.00,  # $125M optimization
        'funding_diversification': 'excellent'
    }

def get_investment_portfolio_value():
    """Get investment portfolio with real-time valuations"""
    return {
        'total_portfolio_value': 425000000.00,  # $425M total
        'government_bonds': 255000000.00,  # $255M gov bonds (60%)
        'corporate_bonds': 127500000.00,  # $127.5M corp bonds (30%)
        'money_market': 42500000.00,  # $42.5M money market (10%)
        'average_yield': 4.25,  # 4.25% average yield
        'duration': 3.8,  # 3.8 years average duration
        'credit_quality': 'AA+',
        'unrealized_gains': 8500000.00,  # $8.5M unrealized gains
        'income_generation': 18062500.00  # $18.06M annual income
    }

def get_treasury_bonds_portfolio():
    """Get treasury bonds portfolio with detailed analytics"""
    return {
        'total_value': 255000000.00,  # $255M treasury bonds
        'short_term': 76500000.00,  # $76.5M short-term (< 2 years)
        'medium_term': 127500000.00,  # $127.5M medium-term (2-10 years)
        'long_term': 51000000.00,  # $51M long-term (> 10 years)
        'average_yield': 4.15,  # 4.15% average yield
        'modified_duration': 4.2,  # 4.2 years duration
        'convexity': 18.5,  # Convexity measure
        'dv01': 107250.00,  # $107,250 DV01
        'unrealized_pnl': 5100000.00,  # $5.1M unrealized P&L
        'income_ytd': 10582500.00,  # $10.58M income YTD
        'hedging_ratio': 0.85  # 85% hedged
    }

def get_cash_flow_forecast():
    """Get comprehensive cash flow forecast"""
    return {
        'next_30_days': {
            'inflows': 125000000.00,  # $125M inflows
            'outflows': 118750000.00,  # $118.75M outflows
            'net_flow': 6250000.00    # $6.25M net positive
        },
        'next_90_days': {
            'inflows': 375000000.00,  # $375M inflows
            'outflows': 356250000.00,  # $356.25M outflows
            'net_flow': 18750000.00   # $18.75M net positive
        },
        'next_365_days': {
            'inflows': 1500000000.00,  # $1.5B inflows
            'outflows': 1425000000.00,  # $1.425B outflows
            'net_flow': 75000000.00    # $75M net positive
        },
        'confidence_level': 95.0,  # 95% confidence
        'scenario_analysis': 'favorable',
        'stress_scenarios': 'manageable'
    }

def get_funding_sources_analysis():
    """Analyze funding sources with cost optimization"""
    return {
        'deposits': {
            'amount': 2280000000.00,  # $2.28B
            'percentage': 89.0,
            'cost': 2.15,  # 2.15% cost
            'stability': 'high'
        },
        'wholesale_funding': {
            'amount': 185000000.00,  # $185M
            'percentage': 7.2,
            'cost': 4.25,  # 4.25% cost
            'stability': 'medium'
        },
        'equity': {
            'amount': 285000000.00,  # $285M
            'percentage': 11.1,
            'cost': 12.0,  # 12% cost of equity
            'stability': 'high'
        },
        'weighted_average_cost': 3.15,  # 3.15% WACC
        'optimization_potential': 45000000.00,  # $45M savings potential
        'diversification_score': 92.5
    }

def get_interest_rate_exposure():
    """Get interest rate exposure analysis"""
    return {
        'asset_duration': 4.2,  # 4.2 years
        'liability_duration': 1.8,  # 1.8 years
        'duration_gap': 2.4,  # 2.4 years gap
        'basis_point_value': 6840000.00,  # $6.84M per 100bp
        'interest_rate_risk': 'moderate',
        'hedging_ratio': 0.75,  # 75% hedged
        'net_exposure': 1710000.00,  # $1.71M net exposure per 100bp
        'optimization_opportunity': 'increase_hedging'
    }

def get_asset_liability_management_metrics():
    """Get comprehensive ALM metrics"""
    return {
        'maturity_gap_analysis': {
            '0_3_months': 45000000.00,   # $45M gap
            '3_12_months': -25000000.00, # -$25M gap
            '1_5_years': -125000000.00,  # -$125M gap
            '5_plus_years': 105000000.00 # $105M gap
        },
        'interest_rate_sensitivity': {
            'nii_100bp_up': -8500000.00,   # -$8.5M NII impact
            'nii_100bp_down': 9250000.00,  # +$9.25M NII impact
            'eve_100bp_up': -15750000.00,  # -$15.75M EVE impact
            'eve_100bp_down': 17250000.00  # +$17.25M EVE impact
        },
        'liquidity_metrics': {
            'lcr': 125.8,  # 125.8% LCR
            'nsfr': 118.3, # 118.3% NSFR
            'loan_to_deposit': 87.5  # 87.5% LTD ratio
        }
    }

def calculate_treasury_profit_optimization():
    """Calculate treasury profit optimization opportunities"""
    # Current performance
    current_nii = 72750000.00  # $72.75M current NII
    current_investment_income = 18062500.00  # $18.06M investment income
    current_funding_cost = 69750000.00  # $69.75M funding cost
    
    # Optimization opportunities
    nii_optimization = 12500000.00  # $12.5M NII optimization
    investment_optimization = 5250000.00  # $5.25M investment optimization
    funding_optimization = 8750000.00  # $8.75M funding cost reduction
    
    total_optimization = nii_optimization + investment_optimization + funding_optimization
    
    return {
        'current_performance': {
            'net_interest_income': current_nii,
            'investment_income': current_investment_income,
            'funding_cost': current_funding_cost,
            'total_treasury_income': current_nii + current_investment_income
        },
        'optimization_opportunities': {
            'nii_optimization': nii_optimization,
            'investment_optimization': investment_optimization,
            'funding_optimization': funding_optimization,
            'total_opportunity': total_optimization
        },
        'optimized_performance': {
            'projected_nii': current_nii + nii_optimization,
            'projected_investment_income': current_investment_income + investment_optimization,
            'projected_funding_cost': current_funding_cost - funding_optimization,
            'total_projected_income': current_nii + current_investment_income + total_optimization
        },
        'roi_metrics': {
            'profit_improvement_percentage': round((total_optimization / (current_nii + current_investment_income)) * 100, 2),
            'payback_period_months': 3.2,
            'implementation_cost': 2500000.00  # $2.5M implementation cost
        }
    }

def get_treasury_risk_metrics():
    """Get comprehensive treasury risk metrics"""
    return {
        'market_risk': {
            'var_1_day': 2125000.00,     # $2.125M 1-day VaR
            'var_10_day': 6725000.00,    # $6.725M 10-day VaR
            'expected_shortfall': 3187500.00,  # $3.19M ES
            'stress_loss': 15750000.00   # $15.75M stress loss
        },
        'credit_risk': {
            'exposure': 127500000.00,    # $127.5M credit exposure
            'expected_loss': 637500.00,  # $637.5K expected loss
            'credit_var': 3825000.00,    # $3.825M credit VaR
            'concentration_risk': 'low'
        },
        'liquidity_risk': {
            'funding_gap': 0.00,         # No funding gap
            'liquidity_buffer': 285000000.00,  # $285M buffer
            'stress_survival': 45,       # 45 days
            'diversification': 'excellent'
        },
        'operational_risk': {
            'operational_var': 1275000.00,  # $1.275M operational VaR
            'key_risk_indicators': 'green',
            'process_automation': 92.5,  # 92.5% automated
            'control_effectiveness': 96.8  # 96.8% effective
        }
    }

def get_treasury_regulatory_ratios():
    """Get treasury-related regulatory ratios"""
    return {
        'capital_ratios': {
            'tier1_ratio': 10.71,        # 10.71% Tier 1
            'total_capital_ratio': 15.48, # 15.48% Total capital
            'leverage_ratio': 5.29       # 5.29% Leverage ratio
        },
        'liquidity_ratios': {
            'lcr': 125.8,               # 125.8% LCR
            'nsfr': 118.3,              # 118.3% NSFR
            'hqla_ratio': 15.2          # 15.2% HQLA ratio
        },
        'concentration_limits': {
            'single_counterparty': 8.5,  # 8.5% max exposure
            'sector_concentration': 'compliant',
            'geographic_concentration': 'compliant'
        },
        'compliance_status': 'fully_compliant',
        'buffer_above_minimum': {
            'tier1_buffer': 4.71,       # 4.71% above minimum
            'lcr_buffer': 25.8,         # 25.8% above minimum
            'nsfr_buffer': 18.3         # 18.3% above minimum
        }
    }

def get_real_time_market_data():
    """Get real-time market data for treasury operations"""
    return {
        'interest_rates': {
            'fed_funds_rate': 5.25,     # 5.25% Fed funds
            'prime_rate': 8.25,         # 8.25% Prime rate
            'libor_3m': 5.45,          # 5.45% 3M LIBOR
            'sofr': 5.15               # 5.15% SOFR
        },
        'yield_curves': {
            'treasury_2y': 4.25,       # 4.25% 2Y Treasury
            'treasury_5y': 4.15,       # 4.15% 5Y Treasury
            'treasury_10y': 4.05,      # 4.05% 10Y Treasury
            'treasury_30y': 4.35       # 4.35% 30Y Treasury
        },
        'fx_rates': {
            'eur_usd': 1.0875,         # EUR/USD
            'gbp_usd': 1.2650,         # GBP/USD
            'usd_jpy': 149.25,         # USD/JPY
            'usd_cad': 1.3520          # USD/CAD
        },
        'bond_prices': {
            'us_10y_price': 97.25,     # US 10Y price
            'corporate_aaa_spread': 125, # 125bp spread
            'corporate_bbb_spread': 275  # 275bp spread
        },
        'volatility': {
            'interest_rate_vol': 15.5,  # 15.5% IR volatility
            'fx_vol': 12.8,            # 12.8% FX volatility
            'credit_vol': 18.2         # 18.2% Credit volatility
        }
    }

# Treasury business logic functions
def generate_cashflow_forecast(period):
    """Generate cash flow forecast with optimization"""
    base_inflow = 125000000.00  # $125M monthly base
    base_outflow = 118750000.00  # $118.75M monthly base
    
    if period == '30_days':
        multiplier = 1
    elif period == '90_days':
        multiplier = 3
    elif period == '365_days':
        multiplier = 12
    else:
        multiplier = 1
    
    return {
        'inflows': base_inflow * multiplier,
        'outflows': base_outflow * multiplier,
        'net_flow': (base_inflow - base_outflow) * multiplier,
        'gaps': [],
        'optimization': base_inflow * multiplier * 0.05,  # 5% optimization
        'funding_needs': 0,
        'investment_ops': (base_inflow - base_outflow) * multiplier
    }

def perform_cashflow_optimization(data):
    """Perform cash flow optimization"""
    optimization_id = f"CFO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        'id': optimization_id,
        'actions': [
            'Optimize deposit pricing',
            'Enhance investment yields',
            'Reduce funding costs'
        ],
        'profit_increase': 12500000.00,  # $12.5M increase
        'risk_impact': 'minimal',
        'timeline': '30_days'
    }

def get_real_time_portfolio_data():
    """Get real-time portfolio data"""
    return {
        'total_value': 425000000.00,
        'allocation': {
            'government_bonds': 60.0,
            'corporate_bonds': 30.0,
            'money_market': 10.0
        },
        'performance': {
            'ytd_return': 4.25,
            'total_return': 8.75,
            'sharpe_ratio': 1.85
        },
        'risk': {
            'duration': 3.8,
            'convexity': 18.5,
            'var': 2125000.00
        },
        'yield': 4.25,
        'duration': 3.8,
        'credit_quality': 'AA+',
        'liquidity': 'high'
    }

def perform_portfolio_optimization(data):
    """Perform portfolio optimization"""
    optimization_id = f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        'id': optimization_id,
        'allocation': {
            'government_bonds': 55.0,
            'corporate_bonds': 35.0,
            'money_market': 10.0
        },
        'expected_return': 4.65,  # 4.65% expected return
        'risk_reduction': 8.5,    # 8.5% risk reduction
        'profit_improvement': 5250000.00  # $5.25M improvement
    }

def get_treasury_bonds_data():
    """Get treasury bonds data"""
    return get_treasury_bonds_portfolio()

def execute_treasury_bond_trade(data):
    """Execute treasury bond trade"""
    trade_id = f"TBT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        'trade_id': trade_id,
        'price': data.get('price', 98.50),
        'total_cost': data.get('quantity', 1000000) * data.get('price', 98.50) / 100,
        'ytm': 4.15,  # 4.15% YTM
        'duration': 4.2,  # 4.2 years
        'profit_impact': 125000.00,  # $125K profit impact
        'risk_impact': 'minimal'
    }

def perform_alm_analysis():
    """Perform ALM analysis"""
    return {
        'interest_rate_risk': 'moderate',
        'liquidity_risk': 'low',
        'maturity_gaps': get_asset_liability_management_metrics()['maturity_gap_analysis'],
        'duration_gap': 2.4,
        'nii_simulation': {
            'base_case': 72750000.00,
            'up_100bp': 64250000.00,
            'down_100bp': 82000000.00
        },
        'eve': {
            'base_case': 285000000.00,
            'up_100bp': 269250000.00,
            'down_100bp': 302250000.00
        },
        'recommendations': [
            'Increase asset duration',
            'Optimize funding mix',
            'Enhance hedging strategies'
        ]
    }

def perform_alm_optimization(data):
    """Perform ALM optimization"""
    optimization_id = f"ALMO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        'id': optimization_id,
        'actions': [
            'Rebalance asset portfolio',
            'Optimize liability structure',
            'Implement interest rate hedges'
        ],
        'profit_improvement': 8750000.00,  # $8.75M improvement
        'risk_reduction': 15.5,  # 15.5% risk reduction
        'capital_efficiency': 12.8  # 12.8% capital efficiency gain
    }

def analyze_funding_sources():
    """Analyze funding sources"""
    return get_funding_sources_analysis()

def optimize_funding_mix(data):
    """Optimize funding mix"""
    optimization_id = f"FMO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        'id': optimization_id,
        'mix': {
            'deposits': 91.0,
            'wholesale_funding': 5.5,
            'equity': 11.1
        },
        'cost_savings': 8750000.00,  # $8.75M savings
        'stability': 'enhanced',
        'risk_impact': 'reduced'
    }

def analyze_interest_rate_risk():
    """Analyze interest rate risk"""
    return {
        'duration': get_interest_rate_exposure(),
        'gaps': get_asset_liability_management_metrics()['maturity_gap_analysis'],
        'sensitivity': get_asset_liability_management_metrics()['interest_rate_sensitivity'],
        'scenarios': {
            'parallel_up_100bp': -8500000.00,
            'parallel_down_100bp': 9250000.00,
            'steepening': -3750000.00,
            'flattening': 4250000.00
        },
        'hedging': {
            'current_ratio': 0.75,
            'optimal_ratio': 0.85,
            'cost': 1275000.00,
            'benefit': 6375000.00
        },
        'profit_impact': 'significant'
    }

def create_irr_hedge(data):
    """Create interest rate risk hedge"""
    hedge_id = f"IRH-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        'hedge_id': hedge_id,
        'type': data.get('hedge_type', 'interest_rate_swap'),
        'notional': data.get('notional_amount', 100000000),
        'cost': data.get('notional_amount', 100000000) * 0.0125,  # 1.25% cost
        'risk_reduction': 25.0,  # 25% risk reduction
        'profit_protection': data.get('notional_amount', 100000000) * 0.05  # 5% protection
    }

def analyze_capital_allocation():
    """Analyze capital allocation"""
    return {
        'current': {
            'loans': 70.0,
            'investments': 15.0,
            'trading': 5.0,
            'other': 10.0
        },
        'optimal': {
            'loans': 65.0,
            'investments': 20.0,
            'trading': 7.5,
            'other': 7.5
        },
        'rorac': {
            'loans': 18.5,
            'investments': 12.8,
            'trading': 25.2,
            'other': 8.5
        },
        'efficiency': 87.5,
        'opportunities': 25000000.00,  # $25M opportunity
        'profit_improvement': 15750000.00  # $15.75M improvement
    }

def perform_capital_optimization(data):
    """Perform capital optimization"""
    optimization_id = f"CAO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        'id': optimization_id,
        'allocation': analyze_capital_allocation()['optimal'],
        'rorac_improvement': 3.5,  # 3.5% RORAC improvement
        'profit_increase': 15750000.00,  # $15.75M increase
        'risk_impact': 'neutral'
    }

def analyze_treasury_performance():
    """Analyze treasury performance"""
    return {
        'nii': 72750000.00,  # $72.75M NII
        'non_interest': 18062500.00,  # $18.06M non-interest income
        'funding_costs': 69750000.00,  # $69.75M funding costs
        'investment_returns': 18062500.00,  # $18.06M investment returns
        'risk_adjusted': {
            'rorac': 21.5,  # 21.5% RORAC
            'raroc': 19.8,  # 19.8% RAROC
            'sharpe_ratio': 1.85
        },
        'efficiency': {
            'cost_income_ratio': 65.5,  # 65.5% cost/income
            'nim': 2.84,  # 2.84% NIM
            'roe': 18.2   # 18.2% ROE
        },
        'benchmarks': {
            'peer_average_nim': 2.75,
            'peer_average_roe': 15.8,
            'performance_vs_peers': 'above_average'
        }
    }

def generate_treasury_report_data(data):
    """Generate treasury report data"""
    report_id = f"TR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        'report_id': report_id,
        'type': data.get('report_type', 'comprehensive'),
        'status': 'generated',
        'download_url': f"/api/treasury/reports/download/{report_id}",
        'summary': {
            'total_assets': 2850000000.00,
            'total_liabilities': 2565000000.00,
            'net_interest_margin': 2.84,
            'profit_optimization': 26500000.00
        }
    }

if __name__ == '__main__':
    app.run(debug=True) 