#!/usr/bin/env python3
"""
Test template rendering
"""

import requests

def test_template():
    """Test template rendering"""
    base_url = "http://localhost:5000"
    
    print("=== Testing Template Rendering ===\n")
    
    # Login as customer
    session = requests.Session()
    login_data = {
        'username': 'john_smith',
        'password': 'password123'
    }
    
    response = session.post(f"{base_url}/login", data=login_data)
    if response.status_code == 200:
        print("✅ Login successful!")
        
        # Get customer dashboard
        response = session.get(f"{base_url}/customer_dashboard")
        if response.status_code == 200:
            print("✅ Dashboard accessible!")
            
            content = response.text
            
            # Check for template structure
            print("\n=== Template Structure ===")
            print(f"Contains DOCTYPE: {'<!DOCTYPE html>' in content}")
            print(f"Contains <html>: {'<html' in content}")
            print(f"Contains <head>: {'<head' in content}")
            print(f"Contains <body>: {'<body' in content}")
            print(f"Contains Bootstrap: {'bootstrap' in content.lower()}")
            print(f"Contains jQuery: {'jquery' in content.lower()}")
            
            # Check for specific sections
            print("\n=== Content Sections ===")
            print(f"Contains 'Welcome back': {'Welcome back' in content}")
            print(f"Contains 'Quick Actions': {'Quick Actions' in content}")
            print(f"Contains 'Transfer Money': {'Transfer Money' in content}")
            print(f"Contains 'Recent Transactions': {'Recent Transactions' in content}")
            print(f"Contains 'Your Cards': {'Your Cards' in content}")
            
            # Show the actual HTML structure
            print("\n=== HTML Structure ===")
            lines = content.split('\n')
            for i, line in enumerate(lines[:20]):  # First 20 lines
                print(f"{i+1:2d}: {line.strip()}")
            
            print("\n=== Last 10 lines ===")
            for i, line in enumerate(lines[-10:]):
                print(f"{len(lines)-10+i+1:2d}: {line.strip()}")
                
        else:
            print(f"❌ Dashboard not accessible: {response.status_code}")
    else:
        print("❌ Login failed!")

if __name__ == "__main__":
    test_template() 