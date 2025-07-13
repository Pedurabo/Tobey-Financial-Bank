"""
Employee (User/Admin) model for Tobey Finance Bank
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum
import uuid

class Department(Enum):
    AdminHR = "Admin/HR Department"
    Accounts = "Accounts Department"
    Loans = "Loans Department"
    CustomerService = "Customer Service Department"
    Teller = "Teller/Transaction Department"
    Audit = "Audit and Compliance Department"
    IT = "IT/Technical Support Department"
    Risk = "Risk Management Department"
    Marketing = "Marketing Department"
    Treasury = "Treasury Department"
    Customer = "Customer"

class Role(Enum):
    ADMIN = "admin"
    STAFF = "staff"
    CUSTOMER = "customer"

@dataclass
class Employee:
    """Employee (user/admin) model for the bank"""
    employee_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    username: str = ""
    password_hash: str = ""  # Store hashed password
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    department: Department = Department.Accounts
    role: Role = Role.STAFF
    is_active: bool = True
    created_date: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    account_number: Optional[str] = None
    account_balance: Optional[float] = None
    account_type: Optional[str] = None

    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def to_dict(self) -> dict:
        return {
            'employee_id': self.employee_id,
            'username': self.username,
            'password_hash': self.password_hash,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'department': self.department.value,
            'role': self.role.value,
            'is_active': self.is_active,
            'created_date': self.created_date.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'account_number': self.account_number,
            'account_balance': self.account_balance,
            'account_type': self.account_type
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Employee':
        # Create a copy to avoid modifying the original
        employee_data = data.copy()
        
        # Convert enum values
        employee_data['department'] = Department(employee_data['department'])
        employee_data['role'] = Role(employee_data['role'])
        
        # Convert datetime values
        employee_data['created_date'] = datetime.fromisoformat(employee_data['created_date'])
        if employee_data.get('last_login'):
            employee_data['last_login'] = datetime.fromisoformat(employee_data['last_login'])
        
        # Handle customer fields - ensure they exist
        if 'account_number' not in employee_data:
            employee_data['account_number'] = None
        if 'account_balance' not in employee_data:
            employee_data['account_balance'] = None
        if 'account_type' not in employee_data:
            employee_data['account_type'] = None
            
        return cls(**employee_data) 