"""
Transaction service for Tobey Finance Bank
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta

from ..models.transaction import Transaction, TransactionType, TransactionStatus


class TransactionService:
    """Service class for transaction operations"""
    
    def __init__(self, database_manager):
        self.db = database_manager
        self.transactions: Dict[str, Transaction] = {}
        self._load_transactions()
    
    def _load_transactions(self):
        """Load transactions from database"""
        transactions_data = self.db.get_all_transactions()
        for transaction_data in transactions_data:
            transaction = Transaction.from_dict(transaction_data)
            self.transactions[transaction.transaction_id] = transaction
    
    def create_transaction(self, account_number: str, transaction_type: TransactionType,
                          amount: float, description: str = "", 
                          target_account: str = None) -> Optional[Transaction]:
        """Create a new transaction"""
        try:
            transaction = Transaction(
                account_number=account_number,
                transaction_type=transaction_type,
                amount=amount,
                description=description,
                target_account=target_account
            )
            
            # Save to database
            self.db.save_transaction(transaction.to_dict())
            self.transactions[transaction.transaction_id] = transaction
            
            return transaction
        except Exception as e:
            print(f"Error creating transaction: {e}")
            return None
    
    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Get transaction by ID"""
        return self.transactions.get(transaction_id)
    
    def get_account_transactions(self, account_number: str, 
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> List[Transaction]:
        """Get all transactions for an account"""
        transactions = []
        
        for transaction in self.transactions.values():
            if transaction.account_number == account_number:
                # Filter by date if provided
                if start_date and transaction.timestamp < start_date:
                    continue
                if end_date and transaction.timestamp > end_date:
                    continue
                transactions.append(transaction)
        
        # Sort by timestamp (newest first)
        transactions.sort(key=lambda x: x.timestamp, reverse=True)
        return transactions
    
    def get_transactions_by_type(self, transaction_type: TransactionType) -> List[Transaction]:
        """Get all transactions of a specific type"""
        return [transaction for transaction in self.transactions.values()
                if transaction.transaction_type == transaction_type]
    
    def get_transactions_by_status(self, status: TransactionStatus) -> List[Transaction]:
        """Get all transactions with a specific status"""
        return [transaction for transaction in self.transactions.values()
                if transaction.status == status]
    
    def get_transactions_by_date_range(self, start_date: datetime, 
                                     end_date: datetime) -> List[Transaction]:
        """Get all transactions within a date range"""
        transactions = []
        
        for transaction in self.transactions.values():
            if start_date <= transaction.timestamp <= end_date:
                transactions.append(transaction)
        
        # Sort by timestamp (newest first)
        transactions.sort(key=lambda x: x.timestamp, reverse=True)
        return transactions
    
    def get_recent_transactions(self, days: int = 30) -> List[Transaction]:
        """Get recent transactions from the last N days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return self.get_transactions_by_date_range(start_date, end_date)
    
    def process_transaction(self, transaction_id: str) -> bool:
        """Process a pending transaction"""
        transaction = self.get_transaction(transaction_id)
        if not transaction:
            return False
        
        return transaction.process()
    
    def cancel_transaction(self, transaction_id: str) -> bool:
        """Cancel a pending transaction"""
        transaction = self.get_transaction(transaction_id)
        if not transaction:
            return False
        
        return transaction.cancel()
    
    def get_transaction_summary(self, account_number: str, 
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> dict:
        """Get transaction summary for an account"""
        transactions = self.get_account_transactions(account_number, start_date, end_date)
        
        summary = {
            'total_transactions': len(transactions),
            'total_deposits': 0.0,
            'total_withdrawals': 0.0,
            'total_transfers': 0.0,
            'total_fees': 0.0,
            'completed_transactions': 0,
            'failed_transactions': 0,
            'pending_transactions': 0
        }
        
        for transaction in transactions:
            if transaction.transaction_type == TransactionType.DEPOSIT:
                summary['total_deposits'] += transaction.amount
            elif transaction.transaction_type == TransactionType.WITHDRAWAL:
                summary['total_withdrawals'] += transaction.amount
            elif transaction.transaction_type == TransactionType.TRANSFER:
                summary['total_transfers'] += transaction.amount
            elif transaction.transaction_type == TransactionType.FEE:
                summary['total_fees'] += transaction.amount
            
            if transaction.status == TransactionStatus.COMPLETED:
                summary['completed_transactions'] += 1
            elif transaction.status == TransactionStatus.FAILED:
                summary['failed_transactions'] += 1
            elif transaction.status == TransactionStatus.PENDING:
                summary['pending_transactions'] += 1
        
        return summary
    
    def search_transactions(self, search_term: str) -> List[Transaction]:
        """Search transactions by description or reference number"""
        results = []
        search_term = search_term.lower()
        
        for transaction in self.transactions.values():
            if (search_term in transaction.description.lower() or
                (transaction.reference_number and search_term in transaction.reference_number.lower())):
                results.append(transaction)
        
        return results
    
    def get_transaction_statistics(self) -> dict:
        """Get overall transaction statistics"""
        total_transactions = len(self.transactions)
        completed_transactions = len(self.get_transactions_by_status(TransactionStatus.COMPLETED))
        failed_transactions = len(self.get_transactions_by_status(TransactionStatus.FAILED))
        pending_transactions = len(self.get_transactions_by_status(TransactionStatus.PENDING))
        
        total_amount = sum(t.amount for t in self.transactions.values() 
                          if t.status == TransactionStatus.COMPLETED)
        
        return {
            'total_transactions': total_transactions,
            'completed_transactions': completed_transactions,
            'failed_transactions': failed_transactions,
            'pending_transactions': pending_transactions,
            'success_rate': (completed_transactions / total_transactions * 100) if total_transactions > 0 else 0,
            'total_amount_processed': total_amount
        } 