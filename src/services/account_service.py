"""
Account service for Tobey Finance Bank
"""

from typing import List, Optional, Dict
from datetime import datetime
import uuid

from ..models.account import Account, AccountType, AccountStatus
from ..models.transaction import Transaction, TransactionType, TransactionStatus


class AccountService:
    """Service class for account operations"""
    
    def __init__(self, database_manager):
        self.db = database_manager
        self.accounts: Dict[str, Account] = {}
        self._load_accounts()
    
    def _load_accounts(self):
        """Load accounts from database"""
        accounts_data = self.db.get_all_accounts()
        for account_data in accounts_data:
            account = Account.from_dict(account_data)
            self.accounts[account.account_number] = account
    
    def create_account(self, customer_id: str, account_type: AccountType, 
                      initial_balance: float = 0.0) -> Optional[Account]:
        """Create a new account"""
        try:
            account = Account(
                customer_id=customer_id,
                account_type=account_type,
                balance=initial_balance
            )
            
            # Save to database
            self.db.save_account(account.to_dict())
            self.accounts[account.account_number] = account
            
            return account
        except Exception as e:
            print(f"Error creating account: {e}")
            return None
    
    def get_account(self, account_number: str) -> Optional[Account]:
        """Get account by account number"""
        return self.accounts.get(account_number)
    
    def get_customer_accounts(self, customer_id: str) -> List[Account]:
        """Get all accounts for a customer"""
        return [account for account in self.accounts.values() 
                if account.customer_id == customer_id]
    
    def deposit(self, account_number: str, amount: float, 
                description: str = "Deposit") -> bool:
        """Deposit money into account"""
        account = self.get_account(account_number)
        if not account:
            return False
        
        if account.deposit(amount):
            # Create transaction record
            transaction = Transaction(
                account_number=account_number,
                transaction_type=TransactionType.DEPOSIT,
                amount=amount,
                description=description,
                balance_after=account.balance
            )
            
            # Save transaction
            self.db.save_transaction(transaction.to_dict())
            
            # Update account in database
            self.db.update_account(account.to_dict())
            
            return True
        return False
    
    def withdraw(self, account_number: str, amount: float, 
                 description: str = "Withdrawal") -> bool:
        """Withdraw money from account"""
        account = self.get_account(account_number)
        if not account:
            return False
        
        if account.withdraw(amount):
            # Create transaction record
            transaction = Transaction(
                account_number=account_number,
                transaction_type=TransactionType.WITHDRAWAL,
                amount=amount,
                description=description,
                balance_after=account.balance
            )
            
            # Save transaction
            self.db.save_transaction(transaction.to_dict())
            
            # Update account in database
            self.db.update_account(account.to_dict())
            
            return True
        return False
    
    def transfer(self, from_account: str, to_account: str, 
                 amount: float, description: str = "Transfer") -> bool:
        """Transfer money between accounts"""
        source_account = self.get_account(from_account)
        target_account = self.get_account(to_account)
        
        if not source_account or not target_account:
            return False
        
        if source_account.transfer(amount, target_account):
            # Create transaction records
            debit_transaction = Transaction(
                account_number=from_account,
                transaction_type=TransactionType.TRANSFER,
                amount=amount,
                description=f"Transfer to {to_account}",
                target_account=to_account,
                balance_after=source_account.balance
            )
            
            credit_transaction = Transaction(
                account_number=to_account,
                transaction_type=TransactionType.TRANSFER,
                amount=amount,
                description=f"Transfer from {from_account}",
                target_account=from_account,
                balance_after=target_account.balance
            )
            
            # Save transactions
            self.db.save_transaction(debit_transaction.to_dict())
            self.db.save_transaction(credit_transaction.to_dict())
            
            # Update accounts in database
            self.db.update_account(source_account.to_dict())
            self.db.update_account(target_account.to_dict())
            
            return True
        return False
    
    def get_account_balance(self, account_number: str) -> Optional[float]:
        """Get account balance"""
        account = self.get_account(account_number)
        return account.balance if account else None
    
    def get_account_statement(self, account_number: str, 
                             start_date: datetime = None, 
                             end_date: datetime = None) -> List[Transaction]:
        """Get account statement with transactions"""
        transactions = self.db.get_account_transactions(account_number, start_date, end_date)
        return [Transaction.from_dict(t) for t in transactions]
    
    def close_account(self, account_number: str) -> bool:
        """Close an account"""
        account = self.get_account(account_number)
        if not account:
            return False
        
        if account.balance != 0:
            return False  # Cannot close account with non-zero balance
        
        account.status = AccountStatus.CLOSED
        account.last_updated = datetime.now()
        
        # Update account in database
        self.db.update_account(account.to_dict())
        
        return True
    
    def calculate_interest(self, account_number: str) -> float:
        """Calculate interest for an account"""
        account = self.get_account(account_number)
        if not account:
            return 0.0
        
        return account.calculate_interest()
    
    def apply_interest(self, account_number: str) -> bool:
        """Apply interest to account"""
        account = self.get_account(account_number)
        if not account:
            return False
        
        interest_amount = account.calculate_interest()
        if interest_amount > 0:
            return self.deposit(account_number, interest_amount, "Interest Credit")
        
        return True 