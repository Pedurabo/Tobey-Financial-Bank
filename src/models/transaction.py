"""
Transaction model for Tobey Finance Bank
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum
import uuid


class TransactionType(Enum):
    """Transaction types"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    FEE = "fee"
    INTEREST = "interest"


class TransactionStatus(Enum):
    """Transaction status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Transaction:
    """Transaction model for the bank"""
    
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4())[:16])
    account_number: str = ""
    transaction_type: TransactionType = TransactionType.DEPOSIT
    amount: float = 0.0
    currency: str = "USD"
    description: str = ""
    status: TransactionStatus = TransactionStatus.PENDING
    timestamp: datetime = field(default_factory=datetime.now)
    reference_number: Optional[str] = None
    target_account: Optional[str] = None  # For transfers
    fee: float = 0.0
    balance_after: Optional[float] = None
    
    def __post_init__(self):
        """Validate transaction data after initialization"""
        if self.amount <= 0:
            raise ValueError("Transaction amount must be positive")
        if not self.account_number:
            raise ValueError("Account number is required")
        if self.transaction_type == TransactionType.TRANSFER and not self.target_account:
            raise ValueError("Target account required for transfers")
    
    def process(self) -> bool:
        """Process the transaction"""
        if self.status != TransactionStatus.PENDING:
            return False
        
        # Simulate transaction processing
        if self.transaction_type in [TransactionType.DEPOSIT, TransactionType.TRANSFER]:
            self.status = TransactionStatus.COMPLETED
        elif self.transaction_type == TransactionType.WITHDRAWAL:
            # Check if sufficient balance (this would be done in account service)
            self.status = TransactionStatus.COMPLETED
        else:
            self.status = TransactionStatus.COMPLETED
        
        return True
    
    def cancel(self) -> bool:
        """Cancel the transaction"""
        if self.status == TransactionStatus.PENDING:
            self.status = TransactionStatus.CANCELLED
            return True
        return False
    
    def get_total_amount(self) -> float:
        """Get total amount including fees"""
        return self.amount + self.fee
    
    def is_completed(self) -> bool:
        """Check if transaction is completed"""
        return self.status == TransactionStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if transaction failed"""
        return self.status == TransactionStatus.FAILED
    
    def to_dict(self) -> dict:
        """Convert transaction to dictionary"""
        return {
            'transaction_id': self.transaction_id,
            'account_number': self.account_number,
            'transaction_type': self.transaction_type.value,
            'amount': self.amount,
            'currency': self.currency,
            'description': self.description,
            'status': self.status.value,
            'timestamp': self.timestamp.isoformat(),
            'reference_number': self.reference_number,
            'target_account': self.target_account,
            'fee': self.fee,
            'balance_after': self.balance_after
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        """Create transaction from dictionary"""
        data['transaction_type'] = TransactionType(data['transaction_type'])
        data['status'] = TransactionStatus(data['status'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data) 