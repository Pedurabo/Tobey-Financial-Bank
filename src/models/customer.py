"""
Customer model for Tobey Finance Bank
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum
import uuid


class CustomerStatus(Enum):
    """Customer status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BLACKLISTED = "blacklisted"


@dataclass
class Customer:
    """Customer model for the bank"""
    
    customer_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    date_of_birth: Optional[datetime] = None
    status: CustomerStatus = CustomerStatus.ACTIVE
    created_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    kyc_verified: bool = False
    risk_level: str = "low"  # low, medium, high
    accounts: List[str] = field(default_factory=list)  # List of account numbers
    
    def __post_init__(self):
        """Validate customer data after initialization"""
        if not self.first_name or not self.last_name:
            raise ValueError("First name and last name are required")
        if self.email and '@' not in self.email:
            raise ValueError("Invalid email format")
        if self.risk_level not in ['low', 'medium', 'high']:
            raise ValueError("Risk level must be low, medium, or high")
    
    @property
    def full_name(self) -> str:
        """Get customer's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def add_account(self, account_number: str) -> bool:
        """Add an account to the customer's account list"""
        if account_number not in self.accounts:
            self.accounts.append(account_number)
            self.last_updated = datetime.now()
            return True
        return False
    
    def remove_account(self, account_number: str) -> bool:
        """Remove an account from the customer's account list"""
        if account_number in self.accounts:
            self.accounts.remove(account_number)
            self.last_updated = datetime.now()
            return True
        return False
    
    def is_active(self) -> bool:
        """Check if customer is active"""
        return self.status == CustomerStatus.ACTIVE
    
    def can_open_account(self) -> bool:
        """Check if customer can open new accounts"""
        return (self.is_active() and 
                self.kyc_verified and 
                self.status != CustomerStatus.BLACKLISTED)
    
    def update_kyc_status(self, verified: bool) -> None:
        """Update KYC verification status"""
        self.kyc_verified = verified
        self.last_updated = datetime.now()
    
    def update_risk_level(self, risk_level: str) -> bool:
        """Update customer risk level"""
        if risk_level in ['low', 'medium', 'high']:
            self.risk_level = risk_level
            self.last_updated = datetime.now()
            return True
        return False
    
    def to_dict(self) -> dict:
        """Convert customer to dictionary"""
        return {
            'customer_id': self.customer_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'status': self.status.value,
            'created_date': self.created_date.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'kyc_verified': self.kyc_verified,
            'risk_level': self.risk_level,
            'accounts': self.accounts
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Customer':
        """Create customer from dictionary"""
        data['status'] = CustomerStatus(data['status'])
        data['created_date'] = datetime.fromisoformat(data['created_date'])
        data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        if data.get('date_of_birth'):
            data['date_of_birth'] = datetime.fromisoformat(data['date_of_birth'])
        return cls(**data) 