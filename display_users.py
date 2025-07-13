#!/usr/bin/env python3
"""
Display all available users in the banking system
"""

import json
from datetime import datetime

def display_users():
    """Display all users in a formatted table"""
    
    try:
        with open('data/employees.json', 'r') as f:
            users = json.load(f)
        
        print("=" * 80)
        print("🏦 TOBEY FINANCE BANK - ALL AVAILABLE USERS")
        print("=" * 80)
        
        # Group users by role
        admins = [u for u in users if u['role'] == 'admin']
        staff = [u for u in users if u['role'] == 'staff']
        customers = [u for u in users if u['role'] == 'customer']
        
        print(f"\n👑 ADMIN USERS ({len(admins)} users)")
        print("-" * 80)
        print(f"{'Username':<25} {'Department':<30} {'Email':<35}")
        print("-" * 80)
        for user in admins:
            print(f"{user['username']:<25} {user['department']:<30} {user['email']:<35}")
        
        print(f"\n👥 STAFF USERS ({len(staff)} users)")
        print("-" * 80)
        print(f"{'Username':<25} {'Department':<30} {'Email':<35}")
        print("-" * 80)
        for user in staff:
            print(f"{user['username']:<25} {user['department']:<30} {user['email']:<35}")
        
        print(f"\n💳 CUSTOMER USERS ({len(customers)} users)")
        print("-" * 80)
        print(f"{'Username':<20} {'Name':<25} {'Account':<15} {'Balance':<12} {'Type':<10}")
        print("-" * 80)
        for user in customers:
            name = f"{user['first_name']} {user['last_name']}"
            account = user.get('account_number', 'N/A')
            balance = f"${user.get('account_balance', 0):,.2f}"
            account_type = user.get('account_type', 'N/A')
            print(f"{user['username']:<20} {name:<25} {account:<15} {balance:<12} {account_type:<10}")
        
        print("\n" + "=" * 80)
        print("🔑 DEFAULT PASSWORD FOR ALL USERS: admin123")
        print("=" * 80)
        
        print(f"\n📊 SUMMARY:")
        print(f"   • Total Users: {len(users)}")
        print(f"   • Admin Users: {len(admins)}")
        print(f"   • Staff Users: {len(staff)}")
        print(f"   • Customer Users: {len(customers)}")
        
        print(f"\n🌐 LOGIN URL: http://localhost:5000/login")
        print(f"📱 CUSTOMER SERVICE DASHBOARD: http://localhost:5000/customer_service_dashboard")
        
        print("\n" + "=" * 80)
        print("💡 QUICK LOGIN EXAMPLES:")
        print("   • Customer Service Admin: admin_customer_service / admin123")
        print("   • Regular Customer: john_smith / admin123")
        print("   • HR Admin: admin_hr / admin123")
        print("   • Accounts Admin: admin_accounts / admin123")
        print("=" * 80)
        
    except FileNotFoundError:
        print("❌ Error: employees.json file not found!")
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON in employees.json file!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    display_users() 