"""
Customer service for Tobey Finance Bank
"""

from typing import List, Optional, Dict
from datetime import datetime

from ..models.customer import Customer, CustomerStatus


class CustomerService:
    """Service class for customer operations"""
    
    def __init__(self, database_manager):
        self.db = database_manager
        self.customers: Dict[str, Customer] = {}
        self._load_customers()
    
    def _load_customers(self):
        """Load customers from database"""
        customers_data = self.db.get_all_customers()
        for customer_data in customers_data:
            customer = Customer.from_dict(customer_data)
            self.customers[customer.customer_id] = customer
    
    def create_customer(self, first_name: str, last_name: str, email: str = "",
                       phone: str = "", address: str = "") -> Optional[Customer]:
        """Create a new customer"""
        try:
            customer = Customer(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                address=address
            )
            
            # Save to database
            self.db.save_customer(customer.to_dict())
            self.customers[customer.customer_id] = customer
            
            return customer
        except Exception as e:
            print(f"Error creating customer: {e}")
            return None
    
    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get customer by ID"""
        return self.customers.get(customer_id)
    
    def get_customer_by_email(self, email: str) -> Optional[Customer]:
        """Get customer by email"""
        for customer in self.customers.values():
            if customer.email == email:
                return customer
        return None
    
    def get_all_customers(self) -> List[Customer]:
        """Get all customers"""
        return list(self.customers.values())
    
    def update_customer(self, customer_id: str, **kwargs) -> bool:
        """Update customer information"""
        customer = self.get_customer(customer_id)
        if not customer:
            return False
        
        try:
            for key, value in kwargs.items():
                if hasattr(customer, key):
                    setattr(customer, key, value)
            
            customer.last_updated = datetime.now()
            
            # Update in database
            self.db.update_customer(customer.to_dict())
            
            return True
        except Exception as e:
            print(f"Error updating customer: {e}")
            return False
    
    def delete_customer(self, customer_id: str) -> bool:
        """Delete a customer (soft delete by setting status to inactive)"""
        customer = self.get_customer(customer_id)
        if not customer:
            return False
        
        customer.status = CustomerStatus.INACTIVE
        customer.last_updated = datetime.now()
        
        # Update in database
        self.db.update_customer(customer.to_dict())
        
        return True
    
    def verify_kyc(self, customer_id: str, verified: bool = True) -> bool:
        """Verify customer KYC status"""
        customer = self.get_customer(customer_id)
        if not customer:
            return False
        
        customer.update_kyc_status(verified)
        
        # Update in database
        self.db.update_customer(customer.to_dict())
        
        return True
    
    def update_risk_level(self, customer_id: str, risk_level: str) -> bool:
        """Update customer risk level"""
        customer = self.get_customer(customer_id)
        if not customer:
            return False
        
        if customer.update_risk_level(risk_level):
            # Update in database
            self.db.update_customer(customer.to_dict())
            return True
        
        return False
    
    def add_account_to_customer(self, customer_id: str, account_number: str) -> bool:
        """Add an account to customer's account list"""
        customer = self.get_customer(customer_id)
        if not customer:
            return False
        
        if customer.add_account(account_number):
            # Update in database
            self.db.update_customer(customer.to_dict())
            return True
        
        return False
    
    def remove_account_from_customer(self, customer_id: str, account_number: str) -> bool:
        """Remove an account from customer's account list"""
        customer = self.get_customer(customer_id)
        if not customer:
            return False
        
        if customer.remove_account(account_number):
            # Update in database
            self.db.update_customer(customer.to_dict())
            return True
        
        return False
    
    def search_customers(self, search_term: str) -> List[Customer]:
        """Search customers by name or email"""
        results = []
        search_term = search_term.lower()
        
        for customer in self.customers.values():
            if (search_term in customer.first_name.lower() or
                search_term in customer.last_name.lower() or
                search_term in customer.full_name.lower() or
                search_term in customer.email.lower()):
                results.append(customer)
        
        return results
    
    def get_active_customers(self) -> List[Customer]:
        """Get all active customers"""
        return [customer for customer in self.customers.values() 
                if customer.is_active()]
    
    def get_customers_by_status(self, status: CustomerStatus) -> List[Customer]:
        """Get customers by status"""
        return [customer for customer in self.customers.values() 
                if customer.status == status] 