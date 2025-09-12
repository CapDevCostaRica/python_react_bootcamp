#!/usr/bin/env python3
"""
Test runner
"""
import subprocess
import sys
import os

def run_tests():
    test_file = os.path.join(os.path.dirname(__file__), "test_shipments.py")
    
    cmd = [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("All tests passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print("Some tests failed!")
        return e.returncode

if __name__ == "__main__":
    sys.exit(run_tests())

