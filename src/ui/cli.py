"""
Command-line interface for Tobey Finance Bank
"""

from src.services.account_service import AccountService
from src.services.customer_service import CustomerService
from src.services.transaction_service import TransactionService
from src.services.employee_service import EmployeeService
from src.services.audit_service import AuditService
from src.models.audit_log import AuditAction
from src.utils.database import DatabaseManager
from src.models.employee import Department, Role

class BankingCLI:
    def __init__(self):
        self.db = DatabaseManager()
        self.account_service = AccountService(self.db)
        self.customer_service = CustomerService(self.db)
        self.transaction_service = TransactionService(self.db)
        self.employee_service = EmployeeService(self.db)
        self.audit_service = AuditService(self.db)
        self.employee_service.set_audit_service(self.audit_service)
        self.current_employee = None
        self._ensure_default_admins()

    def _ensure_default_admins(self):
        # Create a default admin for each department if not exists
        default_admins = [
            ("accounts_admin", "Accounts", Department.ACCOUNTS),
            ("loans_admin", "Loans", Department.LOANS),
            ("customer_admin", "Customer", Department.CUSTOMER_SERVICE),
            ("teller_admin", "Teller", Department.TELLER),
            ("audit_admin", "Audit", Department.AUDIT),
            ("it_admin", "IT", Department.IT),
            ("risk_admin", "Risk", Department.RISK),
            ("marketing_admin", "Marketing", Department.MARKETING),
            ("treasury_admin", "Treasury", Department.TREASURY),
            ("adminhr_admin", "AdminHR", Department.ADMIN_HR),
        ]
        for username, fname, dept in default_admins:
            if not any(emp.username == username for emp in self.employee_service.get_all_employees()):
                self.employee_service.create_employee(
                    username=username,
                    password="admin123",  # Default password, should be changed
                    first_name=fname,
                    last_name="Admin",
                    email=f"{username}@bank.com",
                    department=dept,
                    role=Role.ADMIN
                )

    def login(self):
        print("\n==== Employee Login ====")
        for _ in range(3):
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            emp = self.employee_service.authenticate(username, password)
            if emp:
                if not emp.is_active:
                    print("Account is deactivated. Contact Admin/HR.")
                    return False
                self.current_employee = emp
                print(f"Welcome, {emp.full_name()} ({emp.department.value}, {emp.role.value})!")
                return True
            else:
                print("Invalid credentials. Try again.")
        print("Too many failed attempts. Exiting.")
        return False

    def run(self):
        if not self.login():
            return
        while True:
            print("\n==== Tobey Finance Bank ====")
            print("1. Manage Accounts")
            print("2. Manage Customers")
            print("3. Manage Transactions")
            print("4. Change My Password")
            if self.current_employee.department == Department.ADMIN_HR and self.current_employee.role == Role.ADMIN:
                print("5. Manage Employees/Departments (Admin/HR)")
                print("6. View Audit Logs")
                print("7. Logout")
                print("8. Exit")
            else:
                print("5. Logout")
                print("6. Exit")
            choice = input("Select an option: ").strip()
            if choice == '1':
                self.manage_accounts()
            elif choice == '2':
                self.manage_customers()
            elif choice == '3':
                self.manage_transactions()
            elif choice == '4':
                self.change_my_password()
            elif choice == '5':
                if self.current_employee.department == Department.ADMIN_HR and self.current_employee.role == Role.ADMIN:
                    self.manage_employees()
                else:
                    print("Logging out...")
                    self.current_employee = None
                    if not self.login():
                        return
            elif choice == '6':
                if self.current_employee.department == Department.ADMIN_HR and self.current_employee.role == Role.ADMIN:
                    self.view_audit_logs()
                else:
                    print("Exiting Tobey Finance Bank. Goodbye!")
                    break
            elif choice == '7':
                if self.current_employee.department == Department.ADMIN_HR and self.current_employee.role == Role.ADMIN:
                    print("Logging out...")
                    self.current_employee = None
                    if not self.login():
                        return
                else:
                    print("Exiting Tobey Finance Bank. Goodbye!")
                    break
            elif choice == '8' and self.current_employee.department == Department.ADMIN_HR and self.current_employee.role == Role.ADMIN:
                print("Exiting Tobey Finance Bank. Goodbye!")
                break
            else:
                print("Invalid option. Please try again.")

    def manage_accounts(self):
        print("\n[Account Management] (Stub)")
        # Add account management logic here

    def manage_customers(self):
        print("\n[Customer Management] (Stub)")
        # Add customer management logic here

    def manage_transactions(self):
        print("\n[Transaction Management] (Stub)")
        # Add transaction management logic here

    def change_my_password(self):
        print("\n[Change My Password]")
        old_password = input("Old Password: ").strip()
        new_password = input("New Password: ").strip()
        confirm = input("Confirm New Password: ").strip()
        if new_password != confirm:
            print("Passwords do not match.")
            return
        if self.employee_service.change_password(self.current_employee.employee_id, old_password, new_password):
            print("Password changed successfully.")
        else:
            print("Failed to change password. Check your old password.")

    def manage_employees(self):
        while True:
            print("\n[Employee/Department Management]")
            print("1. List Employees")
            print("2. Add Employee")
            print("3. Deactivate Employee")
            print("4. Delete Employee")
            print("5. Reset Employee Password")
            print("6. Update Role/Department")
            print("7. Search Employees")
            print("8. View Employees by Department")
            print("9. View Employees by Role")
            print("10. Back")
            choice = input("Select an option: ").strip()
            if choice == '1':
                emps = self.employee_service.get_all_employees()
                for emp in emps:
                    print(f"{emp.employee_id}: {emp.full_name()} | {emp.username} | {emp.department.value} | {emp.role.value} | {'Active' if emp.is_active else 'Inactive'}")
            elif choice == '2':
                username = input("Username: ").strip()
                password = input("Password: ").strip()
                first_name = input("First Name: ").strip()
                last_name = input("Last Name: ").strip()
                email = input("Email: ").strip()
                print("Departments:")
                for i, dept in enumerate(Department):
                    print(f"{i+1}. {dept.value}")
                dept_choice = int(input("Select department: "))
                department = list(Department)[dept_choice-1]
                print("Roles:")
                for i, role in enumerate(Role):
                    print(f"{i+1}. {role.value}")
                role_choice = int(input("Select role: "))
                role = list(Role)[role_choice-1]
                emp = self.employee_service.create_employee(username, password, first_name, last_name, email, department, role)
                if emp:
                    print("Employee created successfully.")
            elif choice == '3':
                emp_id = input("Employee ID to deactivate: ").strip()
                if self.employee_service.deactivate_employee(emp_id):
                    print("Employee deactivated.")
                else:
                    print("Employee not found.")
            elif choice == '4':
                emp_id = input("Employee ID to delete: ").strip()
                if self.employee_service.delete_employee(emp_id):
                    print("Employee deleted.")
                else:
                    print("Employee not found.")
            elif choice == '5':
                emp_id = input("Employee ID to reset password: ").strip()
                new_password = input("New Password: ").strip()
                if self.employee_service.admin_reset_password(emp_id, new_password):
                    print("Password reset successfully.")
                else:
                    print("Employee not found.")
            elif choice == '6':
                emp_id = input("Employee ID to update: ").strip()
                print("Update Role/Department:")
                print("Roles:")
                for i, role in enumerate(Role):
                    print(f"{i+1}. {role.value}")
                role_choice = int(input("Select new role (or 0 to skip): "))
                new_role = list(Role)[role_choice-1] if role_choice > 0 else None
                print("Departments:")
                for i, dept in enumerate(Department):
                    print(f"{i+1}. {dept.value}")
                dept_choice = int(input("Select new department (or 0 to skip): "))
                new_dept = list(Department)[dept_choice-1] if dept_choice > 0 else None
                if self.employee_service.update_role_department(emp_id, new_role, new_dept):
                    print("Role/Department updated.")
                else:
                    print("Employee not found.")
            elif choice == '7':
                search_term = input("Search term: ").strip()
                results = self.employee_service.search_employees(search_term)
                if results:
                    print(f"Found {len(results)} employees:")
                    for emp in results:
                        print(f"{emp.employee_id}: {emp.full_name()} | {emp.username} | {emp.department.value} | {emp.role.value}")
                else:
                    print("No employees found.")
            elif choice == '8':
                print("Departments:")
                for i, dept in enumerate(Department):
                    print(f"{i+1}. {dept.value}")
                dept_choice = int(input("Select department: "))
                department = list(Department)[dept_choice-1]
                results = self.employee_service.get_employees_by_department(department)
                if results:
                    print(f"Employees in {department.value}:")
                    for emp in results:
                        print(f"{emp.employee_id}: {emp.full_name()} | {emp.username} | {emp.role.value}")
                else:
                    print("No employees in this department.")
            elif choice == '9':
                print("Roles:")
                for i, role in enumerate(Role):
                    print(f"{i+1}. {role.value}")
                role_choice = int(input("Select role: "))
                role = list(Role)[role_choice-1]
                results = self.employee_service.get_employees_by_role(role)
                if results:
                    print(f"Employees with role {role.value}:")
                    for emp in results:
                        print(f"{emp.employee_id}: {emp.full_name()} | {emp.username} | {emp.department.value}")
                else:
                    print("No employees with this role.")
            elif choice == '10':
                break
            else:
                print("Invalid option.")

    def view_audit_logs(self):
        while True:
            print("\n[Audit Logs]")
            print("1. View Recent Logs")
            print("2. View Employee Logs")
            print("3. View Failed Logs")
            print("4. Search Logs")
            print("5. Back")
            choice = input("Select an option: ").strip()
            if choice == '1':
                logs = self.audit_service.get_recent_logs(50)
                print("Recent Audit Logs:")
                for log in logs:
                    print(f"{log.timestamp}: {log.employee_id} | {log.action.value} | {log.details} | {'SUCCESS' if log.success else 'FAILED'}")
            elif choice == '2':
                emp_id = input("Employee ID: ").strip()
                logs = self.audit_service.get_employee_logs(emp_id, 30)
                print(f"Logs for employee {emp_id}:")
                for log in logs:
                    print(f"{log.timestamp}: {log.action.value} | {log.details} | {'SUCCESS' if log.success else 'FAILED'}")
            elif choice == '3':
                logs = self.audit_service.get_failed_logs(30)
                print("Failed Audit Logs:")
                for log in logs:
                    print(f"{log.timestamp}: {log.employee_id} | {log.action.value} | {log.details}")
            elif choice == '4':
                search_term = input("Search term: ").strip()
                logs = self.audit_service.search_logs(search_term, 30)
                print(f"Search results for '{search_term}':")
                for log in logs:
                    print(f"{log.timestamp}: {log.employee_id} | {log.action.value} | {log.details}")
            elif choice == '5':
                break
            else:
                print("Invalid option.") 