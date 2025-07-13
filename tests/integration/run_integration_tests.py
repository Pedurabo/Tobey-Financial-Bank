#!/usr/bin/env python3
"""
Integration Test Runner
Executes all integration tests and provides comprehensive reporting
"""

import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from test_accounts_integration import TestAccountsIntegration, run_integration_tests

class IntegrationTestRunner:
    """Manages and runs integration tests with detailed reporting"""
    
    def __init__(self):
        self.test_suites = {
            "Accounts Department": TestAccountsIntegration
        }
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def run_all_tests(self):
        """Run all integration test suites"""
        print("🚀 Banking Management System - Integration Test Suite")
        print("=" * 60)
        
        self.start_time = time.time()
        
        total_passed = 0
        total_failed = 0
        
        for suite_name, test_class in self.test_suites.items():
            print(f"\n📋 Running {suite_name} Integration Tests...")
            print("-" * 50)
            
            suite_passed, suite_failed = self._run_test_suite(suite_name, test_class)
            total_passed += suite_passed
            total_failed += suite_failed
        
        self.end_time = time.time()
        
        # Generate comprehensive report
        self._generate_report(total_passed, total_failed)
        
        return total_failed == 0
    
    def _run_test_suite(self, suite_name, test_class):
        """Run a specific test suite"""
        suite = test_class()
        test_methods = [method for method in dir(suite) if method.startswith('test_')]
        
        passed = 0
        failed = 0
        suite_results = []
        
        for method_name in test_methods:
            method = getattr(suite, method_name)
            test_name = method_name.replace('test_', '').replace('_', ' ').title()
            
            try:
                # Setup
                if hasattr(suite, 'setup_method'):
                    suite.setup_method()
                
                # Run test
                method()
                passed += 1
                suite_results.append({
                    'test': test_name,
                    'status': 'PASSED',
                    'error': None
                })
                print(f"✅ {test_name}")
                
            except Exception as e:
                failed += 1
                error_msg = str(e)
                suite_results.append({
                    'test': test_name,
                    'status': 'FAILED',
                    'error': error_msg
                })
                print(f"❌ {test_name}: {error_msg}")
            
            finally:
                # Teardown
                if hasattr(suite, 'teardown_method'):
                    suite.teardown_method()
        
        self.results[suite_name] = {
            'passed': passed,
            'failed': failed,
            'total': passed + failed,
            'results': suite_results
        }
        
        print(f"\n📊 {suite_name} Results: {passed} passed, {failed} failed")
        return passed, failed
    
    def _generate_report(self, total_passed, total_failed):
        """Generate a comprehensive test report"""
        if self.start_time is None or self.end_time is None:
            duration = 0.0
        else:
            duration = self.end_time - self.start_time
        
        print("\n" + "=" * 60)
        print("📊 INTEGRATION TEST SUMMARY REPORT")
        print("=" * 60)
        
        print(f"⏱️  Total Duration: {duration:.2f} seconds")
        print(f"📈 Total Tests: {total_passed + total_failed}")
        print(f"✅ Passed: {total_passed}")
        print(f"❌ Failed: {total_failed}")
        print(f"📊 Success Rate: {(total_passed / (total_passed + total_failed) * 100):.1f}%")
        
        print("\n📋 Detailed Results by Test Suite:")
        print("-" * 40)
        
        for suite_name, result in self.results.items():
            print(f"\n{suite_name}:")
            print(f"  ✅ Passed: {result['passed']}")
            print(f"  ❌ Failed: {result['failed']}")
            print(f"  📊 Success Rate: {(result['passed'] / result['total'] * 100):.1f}%")
            
            if result['failed'] > 0:
                print("  🔍 Failed Tests:")
                for test_result in result['results']:
                    if test_result['status'] == 'FAILED':
                        print(f"    ❌ {test_result['test']}: {test_result['error']}")
        
        # Overall status
        if total_failed == 0:
            print("\n🎉 ALL INTEGRATION TESTS PASSED!")
            print("✅ The banking management system is ready for production!")
        else:
            print(f"\n⚠️  {total_failed} TESTS FAILED")
            print("🔧 Please review and fix the failing tests before proceeding.")
        
        # Save detailed report to file
        self._save_detailed_report()
    
    def _save_detailed_report(self):
        """Save detailed test results to a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"integration_test_report_{timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write("Banking Management System - Integration Test Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            if self.start_time is None or self.end_time is None:
                f.write(f"Duration: 0.00 seconds\n\n")
            else:
                f.write(f"Duration: {self.end_time - self.start_time:.2f} seconds\n\n")
            
            for suite_name, result in self.results.items():
                f.write(f"{suite_name}:\n")
                f.write(f"  Passed: {result['passed']}\n")
                f.write(f"  Failed: {result['failed']}\n")
                f.write(f"  Success Rate: {(result['passed'] / result['total'] * 100):.1f}%\n\n")
                
                for test_result in result['results']:
                    status_icon = "✅" if test_result['status'] == 'PASSED' else "❌"
                    f.write(f"  {status_icon} {test_result['test']}\n")
                    if test_result['error']:
                        f.write(f"      Error: {test_result['error']}\n")
                f.write("\n")
        
        print(f"\n📄 Detailed report saved to: {report_file}")

def main():
    """Main entry point for running integration tests"""
    try:
        runner = IntegrationTestRunner()
        success = runner.run_all_tests()
        
        if success:
            print("\n🎯 All integration tests completed successfully!")
            return 0
        else:
            print("\n⚠️  Some integration tests failed. Please review the report above.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️  Test execution interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error during test execution: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main()) 