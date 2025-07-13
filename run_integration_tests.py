#!/usr/bin/env python3
"""
Simple Integration Test Runner
Run this script from the project root to execute all integration tests
"""

import sys
import os

# Add the tests/integration directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests', 'integration'))

try:
    from run_integration_tests import main
    exit(main())
except ImportError as e:
    print(f"❌ Error importing integration tests: {e}")
    print("Make sure you're running this from the project root directory.")
    exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    exit(1) 