"""
Employee service for Tobey Finance Bank
"""

from typing import List, Optional, Dict
from datetime import datetime
from ..models.employee import Employee, Department, Role
from ..utils.security import SecurityManager
from ..models.audit_log import AuditLog, AuditAction

class EmployeeService:
    """Service class for employee (user/admin) operations"""
    def __init__(self, database_manager):
        self.db = database_manager
        self.security = SecurityManager()
        self.employees: Dict[str, Employee] = {}
        self._load_employees()
        self.audit_service = None  # Will be set by CLI

    def set_audit_service(self, audit_service):
        """Set audit service for logging"""
        self.audit_service = audit_service

    def _log_action(self, employee_id: str, action: AuditAction, target_type: str = "", 
                    target_id: str = "", details: str = "", success: bool = True):
        """Log an action if audit service is available"""
        if self.audit_service:
            self.audit_service.log_action(employee_id, action, target_type, target_id, details, success)

    def _load_employees(self):
        employees_data = self.db.get_all_employees()
        for emp_data in employees_data:
            emp = Employee.from_dict(emp_data)
            self.employees[emp.employee_id] = emp

    def create_employee(self, username: str, password: str, first_name: str, last_name: str, email: str, department: Department, role: Role = Role.STAFF) -> Optional[Employee]:
        if any(emp.username == username for emp in self.employees.values()):
            print("Username already exists.")
            self._log_action("system", AuditAction.CREATE_EMPLOYEE, "employee", "", f"Failed to create employee {username}", False)
            return None
        password_hash = self.security.hash_password(password).decode('utf-8')
        emp = Employee(
            username=username,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            email=email,
            department=department,
            role=role
        )
        self.db.save_employee(emp.to_dict())
        self.employees[emp.employee_id] = emp
        self._log_action("system", AuditAction.CREATE_EMPLOYEE, "employee", emp.employee_id, f"Created employee {username}")
        return emp

    def authenticate(self, username: str, password: str) -> Optional[Employee]:
        for emp in self.employees.values():
            if emp.username == username and self.security.verify_password(password, emp.password_hash.encode('utf-8')):
                emp.last_login = datetime.now()
                self.db.update_employee(emp.to_dict())
                self._log_action(emp.employee_id, AuditAction.LOGIN, "employee", emp.employee_id, f"Login successful for {username}")
                return emp
        self._log_action("system", AuditAction.LOGIN, "employee", "", f"Failed login attempt for {username}", False)
        return None

    def get_employee(self, employee_id: str) -> Optional[Employee]:
        return self.employees.get(employee_id)

    def get_all_employees(self) -> List[Employee]:
        return list(self.employees.values())

    def get_department_employees(self, department: Department) -> List[Employee]:
        return [emp for emp in self.employees.values() if emp.department == department]

    def update_employee(self, employee_id: str, **kwargs) -> bool:
        emp = self.get_employee(employee_id)
        if not emp:
            return False
        for key, value in kwargs.items():
            if hasattr(emp, key):
                setattr(emp, key, value)
        self.db.update_employee(emp.to_dict())
        return True

    def deactivate_employee(self, employee_id: str) -> bool:
        emp = self.get_employee(employee_id)
        if not emp:
            return False
        emp.is_active = False
        self.db.update_employee(emp.to_dict())
        self._log_action("system", AuditAction.DEACTIVATE_EMPLOYEE, "employee", employee_id, f"Deactivated employee {emp.username}")
        return True

    def delete_employee(self, employee_id: str) -> bool:
        emp = self.get_employee(employee_id)
        if not emp:
            return False
        username = emp.username
        if employee_id in self.employees:
            del self.employees[employee_id]
        self._log_action("system", AuditAction.DELETE_EMPLOYEE, "employee", employee_id, f"Deleted employee {username}")
        return self.db.delete_employee(employee_id)

    def change_password(self, employee_id: str, old_password: str, new_password: str) -> bool:
        emp = self.get_employee(employee_id)
        if not emp:
            return False
        if not self.security.verify_password(old_password, emp.password_hash.encode('utf-8')):
            self._log_action(employee_id, AuditAction.CHANGE_PASSWORD, "employee", employee_id, "Password change failed - wrong old password", False)
            return False
        emp.password_hash = self.security.hash_password(new_password).decode('utf-8')
        self.db.update_employee(emp.to_dict())
        self._log_action(employee_id, AuditAction.CHANGE_PASSWORD, "employee", employee_id, "Password changed successfully")
        return True

    def admin_reset_password(self, employee_id: str, new_password: str) -> bool:
        emp = self.get_employee(employee_id)
        if not emp:
            return False
        emp.password_hash = self.security.hash_password(new_password).decode('utf-8')
        self.db.update_employee(emp.to_dict())
        self._log_action("system", AuditAction.RESET_PASSWORD, "employee", employee_id, f"Password reset for {emp.username}")
        return True

    def update_role_department(self, employee_id: str, new_role: Role = None, new_department: Department = None) -> bool:
        emp = self.get_employee(employee_id)
        if not emp:
            return False
        old_role = emp.role
        old_dept = emp.department
        if new_role:
            emp.role = new_role
        if new_department:
            emp.department = new_department
        self.db.update_employee(emp.to_dict())
        self._log_action("system", AuditAction.UPDATE_EMPLOYEE, "employee", employee_id, 
                        f"Updated role from {old_role.value} to {emp.role.value}, dept from {old_dept.value} to {emp.department.value}")
        return True 

    def search_employees(self, search_term: str) -> List[Employee]:
        """Search employees by name, username, or email"""
        results = []
        search_term = search_term.lower()
        
        for emp in self.employees.values():
            if (search_term in emp.first_name.lower() or
                search_term in emp.last_name.lower() or
                search_term in emp.full_name().lower() or
                search_term in emp.username.lower() or
                search_term in emp.email.lower()):
                results.append(emp)
        
        return results

    def get_employees_by_department(self, department: Department) -> List[Employee]:
        """Get all employees in a specific department"""
        return [emp for emp in self.employees.values() if emp.department == department]

    def get_employees_by_role(self, role: Role) -> List[Employee]:
        """Get all employees with a specific role"""
        return [emp for emp in self.employees.values() if emp.role == role] 