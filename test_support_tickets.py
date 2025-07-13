#!/usr/bin/env python3
"""
Test script to verify Support Tickets functionality
"""

import requests
import json

def test_support_tickets():
    """Test Support Tickets functionality"""
    base_url = "http://localhost:5000"
    
    # Create session and login
    session = requests.Session()
    login_data = {
        'username': 'admin_customer_service',
        'password': 'admin123'
    }
    
    print("=== Testing Support Tickets Functionality ===\n")
    
    # Test login
    print("1. Testing login...")
    response = session.post(f"{base_url}/login", data=login_data)
    print(f"Login response: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Login successful!")
        
        # Test GET /api/support_tickets
        print("\n2. Testing GET /api/support_tickets...")
        response = session.get(f"{base_url}/api/support_tickets")
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                tickets = data.get('tickets', [])
                print(f"✅ Found {len(tickets)} support tickets")
                for ticket in tickets:
                    print(f"   - Ticket {ticket['id']}: {ticket['customer_name']} ({ticket['status']})")
            else:
                print("❌ API returned success=False")
        else:
            print("❌ GET /api/support_tickets failed")
        
        # Test GET specific ticket
        print("\n3. Testing GET /api/support_tickets/T001...")
        response = session.get(f"{base_url}/api/support_tickets/T001")
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                ticket = data.get('ticket')
                print(f"✅ Ticket details loaded: {ticket['id']} - {ticket['customer_name']}")
                print(f"   Status: {ticket['status']}, Priority: {ticket['priority']}")
            else:
                print("❌ API returned success=False")
        else:
            print("❌ GET specific ticket failed")
        
        # Test POST new ticket
        print("\n4. Testing POST /api/support_tickets (create new ticket)...")
        new_ticket = {
            'customer_id': 'C004',
            'customer_name': 'Test Customer',
            'issue_type': 'technical_support',
            'priority': 'medium',
            'description': 'Test ticket created via API'
        }
        
        response = session.post(f"{base_url}/api/support_tickets", json=new_ticket)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ New ticket created successfully!")
                print(f"   Ticket ID: {data.get('ticket', {}).get('id')}")
            else:
                print("❌ API returned success=False")
        else:
            print("❌ POST new ticket failed")
        
        # Test PUT update ticket status
        print("\n5. Testing PUT /api/support_tickets/T001 (update status)...")
        update_data = {
            'status': 'in_progress',
            'notes': 'Status updated via API test'
        }
        
        response = session.put(f"{base_url}/api/support_tickets/T001", json=update_data)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Ticket status updated successfully!")
                print(f"   New status: {data.get('status')}")
            else:
                print("❌ API returned success=False")
        else:
            print("❌ PUT update ticket failed")
        
        # Test dashboard access
        print("\n6. Testing customer service dashboard access...")
        response = session.get(f"{base_url}/customer_service_dashboard")
        print(f"Dashboard status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Customer service dashboard accessible!")
            
            # Check for Support Tickets button
            if "Support Ticket" in response.text:
                print("✅ Support Ticket button found on dashboard")
            else:
                print("❌ Support Ticket button not found")
                
            # Check for View Tickets button
            if "View Tickets" in response.text:
                print("✅ View Tickets button found on dashboard")
            else:
                print("❌ View Tickets button not found")
                
        else:
            print("❌ Customer service dashboard not accessible")
            
    else:
        print("❌ Login failed!")
        print(f"Response: {response.text}")

def test_support_tickets_ui():
    """Test Support Tickets UI elements"""
    base_url = "http://localhost:5000"
    
    session = requests.Session()
    login_data = {
        'username': 'admin_customer_service',
        'password': 'admin123'
    }
    
    print("\n=== Testing Support Tickets UI Elements ===\n")
    
    # Login
    response = session.post(f"{base_url}/login", data=login_data)
    if response.status_code != 200:
        print("❌ Login failed for UI testing")
        return
    
    # Test dashboard page
    response = session.get(f"{base_url}/customer_service_dashboard")
    if response.status_code == 200:
        content = response.text
        
        # Check for Support Tickets modal
        if "supportTicketsModal" in content:
            print("✅ Support Tickets modal found")
        else:
            print("❌ Support Tickets modal not found")
            
        # Check for Ticket Details modal
        if "ticketDetailsModal" in content:
            print("✅ Ticket Details modal found")
        else:
            print("❌ Ticket Details modal not found")
            
        # Check for Update Ticket Status modal
        if "updateTicketStatusModal" in content:
            print("✅ Update Ticket Status modal found")
        else:
            print("❌ Update Ticket Status modal not found")
            
        # Check for JavaScript functions
        if "openSupportTicketsModal" in content:
            print("✅ openSupportTicketsModal function found")
        else:
            print("❌ openSupportTicketsModal function not found")
            
        if "viewTicket" in content:
            print("✅ viewTicket function found")
        else:
            print("❌ viewTicket function not found")
            
        if "updateTicketStatus" in content:
            print("✅ updateTicketStatus function found")
        else:
            print("❌ updateTicketStatus function not found")
            
        if "submitTicketStatusUpdate" in content:
            print("✅ submitTicketStatusUpdate function found")
        else:
            print("❌ submitTicketStatusUpdate function not found")
            
        # Check for timeline CSS
        if "timeline" in content:
            print("✅ Timeline CSS styles found")
        else:
            print("❌ Timeline CSS styles not found")
            
    else:
        print("❌ Dashboard not accessible for UI testing")

if __name__ == "__main__":
    try:
        test_support_tickets()
        test_support_tickets_ui()
        print("\n=== Support Tickets Testing Complete ===")
        print("\nTo test the UI manually:")
        print("1. Go to http://localhost:5000")
        print("2. Login with admin_customer_service / admin123")
        print("3. Click 'View Tickets' button")
        print("4. Test viewing ticket details and updating status")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}") 