#!/usr/bin/env python3
"""
Test runner for the Climate Assistant RAG System
"""
import sys
import os
import unittest
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def run_tests():
    """Run all tests in the tests directory"""
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = backend_dir / 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)
