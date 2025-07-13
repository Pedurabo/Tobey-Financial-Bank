"""
Database manager for Tobey Finance Bank
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime


class DatabaseManager:
    """Simple database manager using JSON files"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.accounts_file = os.path.join(data_dir, "accounts.json")
        self.customers_file = os.path.join(data_dir, "customers.json")
        self.transactions_file = os.path.join(data_dir, "transactions.json")
        self.employees_file = os.path.join(data_dir, "employees.json")
        self.audit_logs_file = os.path.join(data_dir, "audit_logs.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
    
    def initialize_database(self):
        """Initialize database files if they don't exist"""
        self._ensure_file_exists(self.accounts_file)
        self._ensure_file_exists(self.customers_file)
        self._ensure_file_exists(self.transactions_file)
        self._ensure_file_exists(self.employees_file)
        self._ensure_file_exists(self.audit_logs_file)
    
    def _ensure_file_exists(self, file_path: str):
        """Ensure a JSON file exists with empty array"""
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump([], f)
    
    def _read_json_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Read JSON file and return list of dictionaries"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _write_json_file(self, file_path: str, data: List[Dict[str, Any]]):
        """Write list of dictionaries to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    # Account operations
    def save_account(self, account_data: Dict[str, Any]):
        """Save account to database"""
        accounts = self._read_json_file(self.accounts_file)
        
        # Check if account already exists
        for i, account in enumerate(accounts):
            if account.get('account_number') == account_data.get('account_number'):
                accounts[i] = account_data
                break
        else:
            accounts.append(account_data)
        
        self._write_json_file(self.accounts_file, accounts)
    
    def get_account(self, account_number: str) -> Optional[Dict[str, Any]]:
        """Get account by account number"""
        accounts = self._read_json_file(self.accounts_file)
        for account in accounts:
            if account.get('account_number') == account_number:
                return account
        return None
    
    def get_all_accounts(self) -> List[Dict[str, Any]]:
        """Get all accounts"""
        return self._read_json_file(self.accounts_file)
    
    def update_account(self, account_data: Dict[str, Any]):
        """Update account in database"""
        self.save_account(account_data)
    
    def delete_account(self, account_number: str) -> bool:
        """Delete account from database"""
        accounts = self._read_json_file(self.accounts_file)
        for i, account in enumerate(accounts):
            if account.get('account_number') == account_number:
                del accounts[i]
                self._write_json_file(self.accounts_file, accounts)
                return True
        return False
    
    # Customer operations
    def save_customer(self, customer_data: Dict[str, Any]):
        """Save customer to database"""
        customers = self._read_json_file(self.customers_file)
        
        # Check if customer already exists
        for i, customer in enumerate(customers):
            if customer.get('customer_id') == customer_data.get('customer_id'):
                customers[i] = customer_data
                break
        else:
            customers.append(customer_data)
        
        self._write_json_file(self.customers_file, customers)
    
    def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer by customer ID"""
        customers = self._read_json_file(self.customers_file)
        for customer in customers:
            if customer.get('customer_id') == customer_id:
                return customer
        return None
    
    def get_all_customers(self) -> List[Dict[str, Any]]:
        """Get all customers"""
        return self._read_json_file(self.customers_file)
    
    def update_customer(self, customer_data: Dict[str, Any]):
        """Update customer in database"""
        self.save_customer(customer_data)
    
    def delete_customer(self, customer_id: str) -> bool:
        """Delete customer from database"""
        customers = self._read_json_file(self.customers_file)
        for i, customer in enumerate(customers):
            if customer.get('customer_id') == customer_id:
                del customers[i]
                self._write_json_file(self.customers_file, customers)
                return True
        return False
    
    # Transaction operations
    def save_transaction(self, transaction_data: Dict[str, Any]):
        """Save transaction to database"""
        transactions = self._read_json_file(self.transactions_file)
        transactions.append(transaction_data)
        self._write_json_file(self.transactions_file, transactions)
    
    def get_transaction(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get transaction by transaction ID"""
        transactions = self._read_json_file(self.transactions_file)
        for transaction in transactions:
            if transaction.get('transaction_id') == transaction_id:
                return transaction
        return None
    
    def get_all_transactions(self) -> List[Dict[str, Any]]:
        """Get all transactions"""
        return self._read_json_file(self.transactions_file)
    
    def get_account_transactions(self, account_number: str, 
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get transactions for a specific account"""
        transactions = self._read_json_file(self.transactions_file)
        filtered_transactions = []
        
        for transaction in transactions:
            if transaction.get('account_number') == account_number:
                # Filter by date if provided
                if start_date or end_date:
                    transaction_date = datetime.fromisoformat(transaction.get('timestamp', ''))
                    if start_date and transaction_date < start_date:
                        continue
                    if end_date and transaction_date > end_date:
                        continue
                filtered_transactions.append(transaction)
        
        return filtered_transactions
    
    def update_transaction(self, transaction_data: Dict[str, Any]):
        """Update transaction in database"""
        transactions = self._read_json_file(self.transactions_file)
        for i, transaction in enumerate(transactions):
            if transaction.get('transaction_id') == transaction_data.get('transaction_id'):
                transactions[i] = transaction_data
                break
        
        self._write_json_file(self.transactions_file, transactions)
    
    def delete_transaction(self, transaction_id: str) -> bool:
        """Delete transaction from database"""
        transactions = self._read_json_file(self.transactions_file)
        for i, transaction in enumerate(transactions):
            if transaction.get('transaction_id') == transaction_id:
                del transactions[i]
                self._write_json_file(self.transactions_file, transactions)
                return True
        return False
    
    # Employee operations
    def save_employee(self, employee_data: Dict[str, Any]):
        """Save employee to database"""
        employees = self._read_json_file(self.employees_file)
        for i, employee in enumerate(employees):
            if employee.get('employee_id') == employee_data.get('employee_id'):
                employees[i] = employee_data
                break
        else:
            employees.append(employee_data)
        self._write_json_file(self.employees_file, employees)

    def get_employee(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Get employee by employee ID"""
        employees = self._read_json_file(self.employees_file)
        for employee in employees:
            if employee.get('employee_id') == employee_id:
                return employee
        return None

    def get_all_employees(self) -> List[Dict[str, Any]]:
        """Get all employees"""
        return self._read_json_file(self.employees_file)

    def update_employee(self, employee_data: Dict[str, Any]):
        """Update employee in database"""
        self.save_employee(employee_data)

    def delete_employee(self, employee_id: str) -> bool:
        """Delete employee from database"""
        employees = self._read_json_file(self.employees_file)
        for i, employee in enumerate(employees):
            if employee.get('employee_id') == employee_id:
                del employees[i]
                self._write_json_file(self.employees_file, employees)
                return True
        return False
    
    # Audit log operations
    def save_audit_log(self, audit_log_data: Dict[str, Any]):
        """Save audit log to database"""
        audit_logs = self._read_json_file(self.audit_logs_file)
        audit_logs.append(audit_log_data)
        self._write_json_file(self.audit_logs_file, audit_logs)

    def get_audit_logs(self, employee_id: str = None, action: str = None, 
                       start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """Get audit logs with optional filtering"""
        audit_logs = self._read_json_file(self.audit_logs_file)
        filtered_logs = []
        
        for log in audit_logs:
            # Filter by employee_id
            if employee_id and log.get('employee_id') != employee_id:
                continue
            # Filter by action
            if action and log.get('action') != action:
                continue
            # Filter by date range
            if start_date or end_date:
                log_timestamp = datetime.fromisoformat(log.get('timestamp', ''))
                if start_date and log_timestamp < start_date:
                    continue
                if end_date and log_timestamp > end_date:
                    continue
            filtered_logs.append(log)
        
        # Sort by timestamp (newest first)
        filtered_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return filtered_logs

    def get_employee_audit_logs(self, employee_id: str) -> List[Dict[str, Any]]:
        """Get all audit logs for a specific employee"""
        return self.get_audit_logs(employee_id=employee_id)
    
    # Backup and restore operations
    def backup_database(self, backup_dir: str = "backup"):
        """Create backup of all database files"""
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        files_to_backup = [
            (self.accounts_file, f"accounts_{timestamp}.json"),
            (self.customers_file, f"customers_{timestamp}.json"),
            (self.transactions_file, f"transactions_{timestamp}.json")
        ]
        
        for source_file, backup_name in files_to_backup:
            if os.path.exists(source_file):
                backup_path = os.path.join(backup_dir, backup_name)
                with open(source_file, 'r') as src, open(backup_path, 'w') as dst:
                    dst.write(src.read())
        
        print(f"Database backup created in {backup_dir}")
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        return {
            'accounts': len(self.get_all_accounts()),
            'customers': len(self.get_all_customers()),
            'transactions': len(self.get_all_transactions())
        } 