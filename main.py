#!/usr/bin/env python3
"""
Tobey Finance Bank - Main Application Entry Point
A comprehensive banking management system
"""

import sys
import os
from datetime import datetime

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.cli import BankingCLI
from src.utils.database import DatabaseManager


def main():
    """Main application entry point"""
    print("=" * 50)
    print("    TOBEY FINANCE BANK - Banking Management System")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Initialize database
        db_manager = DatabaseManager()
        db_manager.initialize_database()
        
        # Start the CLI interface
        cli = BankingCLI()
        cli.run()
        
    except KeyboardInterrupt:
        print("\n\nThank you for using Tobey Finance Bank!")
        print("Goodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please contact system administrator.")
        sys.exit(1)


if __name__ == "__main__":
    main() 