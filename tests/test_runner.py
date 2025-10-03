"""
Test runner for all unit tests.
Runs all test modules and generates a summary report.
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import test modules
from test_file_scanner import TestFileScanner
from test_preprocessor_parser import TestPreprocessorParser
from test_validation import TestDirectiveValidator


def run_all_tests():
    """Run all test suites and return results."""
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestFileScanner))
    test_suite.addTest(unittest.makeSuite(TestPreprocessorParser))
    test_suite.addTest(unittest.makeSuite(TestDirectiveValidator))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result


def main():
    """Main entry point for test runner."""
    print("=" * 70)
    print("C++ PREPROCESSOR DIRECTIVE ANALYSIS TOOL - TEST SUITE")
    print("=" * 70)
    print()
    
    result = run_all_tests()
    
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Exception:')[-1].strip()}")
    
    # Return exit code
    return 0 if (len(result.failures) == 0 and len(result.errors) == 0) else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)