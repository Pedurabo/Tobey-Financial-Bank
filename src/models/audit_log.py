"""
Audit Log model for Tobey Finance Bank
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
import uuid

class AuditAction(Enum):
    """Types of audit actions"""
    LOGIN = "login"
    LOGOUT = "logout"
    CREATE_EMPLOYEE = "create_employee"
    UPDATE_EMPLOYEE = "update_employee"
    DELETE_EMPLOYEE = "delete_employee"
    DEACTIVATE_EMPLOYEE = "deactivate_employee"
    CHANGE_PASSWORD = "change_password"
    RESET_PASSWORD = "reset_password"
    CREATE_ACCOUNT = "create_account"
    UPDATE_ACCOUNT = "update_account"
    DELETE_ACCOUNT = "delete_account"
    CREATE_CUSTOMER = "create_customer"
    UPDATE_CUSTOMER = "update_customer"
    DELETE_CUSTOMER = "delete_customer"
    CREATE_TRANSACTION = "create_transaction"
    UPDATE_TRANSACTION = "update_transaction"
    DELETE_TRANSACTION = "delete_transaction"

@dataclass
class AuditLog:
    """Audit log entry for tracking employee actions"""
    log_id: str = field(default_factory=lambda: str(uuid.uuid4())[:16])
    employee_id: str = ""
    action: AuditAction = AuditAction.LOGIN
    target_type: str = ""  # employee, account, customer, transaction
    target_id: str = ""  # ID of the target object
    details: str = ""
    ip_address: str = ""
    user_agent: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    additional_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'log_id': self.log_id,
            'employee_id': self.employee_id,
            'action': self.action.value,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat(),
            'success': self.success,
            'additional_data': self.additional_data
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'AuditLog':
        data['action'] = AuditAction(data['action'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data) 