"""
This file contains fixtures that can be shared across multiple test files.
"""
import os
import sys

# Add the parent directory to sys.path to ensure app can be imported in all tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
