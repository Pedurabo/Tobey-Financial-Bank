"""
Account model for Tobey Finance Bank
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum
import uuid


class AccountType(Enum):
    """Account types available in the bank"""
    SAVINGS = "savings"
    CHECKING = "checking"
    FIXED_DEPOSIT = "fixed_deposit"
    CURRENT = "current"


class AccountStatus(Enum):
    """Account status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CLOSED = "closed"


@dataclass
class Account:
    """Bank account model"""
    
    account_number: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    customer_id: str = ""
    account_type: AccountType = AccountType.SAVINGS
    balance: float = 0.0
    currency: str = "USD"
    status: AccountStatus = AccountStatus.ACTIVE
    created_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    interest_rate: float = 0.02  # 2% default interest rate
    overdraft_limit: float = 0.0
    minimum_balance: float = 0.0
    
    def __post_init__(self):
        """Validate account data after initialization"""
        if self.balance < 0:
            raise ValueError("Account balance cannot be negative")
        if self.interest_rate < 0 or self.interest_rate > 1:
            raise ValueError("Interest rate must be between 0 and 1")
    
    def deposit(self, amount: float) -> bool:
        """Deposit money into the account"""
        if amount <= 0:
            return False
        if self.status != AccountStatus.ACTIVE:
            return False
        
        self.balance += amount
        self.last_updated = datetime.now()
        return True
    
    def withdraw(self, amount: float) -> bool:
        """Withdraw money from the account"""
        if amount <= 0:
            return False
        if self.status != AccountStatus.ACTIVE:
            return False
        
        available_balance = self.balance + self.overdraft_limit
        if amount > available_balance:
            return False
        
        self.balance -= amount
        self.last_updated = datetime.now()
        return True
    
    def transfer(self, amount: float, target_account: 'Account') -> bool:
        """Transfer money to another account"""
        if self.withdraw(amount):
            if target_account.deposit(amount):
                return True
            else:
                # Rollback if deposit fails
                self.deposit(amount)
        return False
    
    def calculate_interest(self) -> float:
        """Calculate interest for the account"""
        if self.account_type == AccountType.SAVINGS:
            return self.balance * self.interest_rate
        return 0.0
    
    def is_active(self) -> bool:
        """Check if account is active"""
        return self.status == AccountStatus.ACTIVE
    
    def get_available_balance(self) -> float:
        """Get available balance including overdraft"""
        return self.balance + self.overdraft_limit
    
    def to_dict(self) -> dict:
        """Convert account to dictionary"""
        return {
            'account_number': self.account_number,
            'customer_id': self.customer_id,
            'account_type': self.account_type.value,
            'balance': self.balance,
            'currency': self.currency,
            'status': self.status.value,
            'created_date': self.created_date.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'interest_rate': self.interest_rate,
            'overdraft_limit': self.overdraft_limit,
            'minimum_balance': self.minimum_balance
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Account':
        """Create account from dictionary"""
        data['account_type'] = AccountType(data['account_type'])
        data['status'] = AccountStatus(data['status'])
        data['created_date'] = datetime.fromisoformat(data['created_date'])
        data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        return cls(**data) 