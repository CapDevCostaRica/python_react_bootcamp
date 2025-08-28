"""
Pytest configuration file for the dnd project tests.
"""
import sys
import os

# Get the absolute path to the src directory
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '..', 'src')
sys.path.insert(0, src_path)

# Also add the project root to handle any other imports
project_root = os.path.join(current_dir, '..', '..', '..')
sys.path.insert(0, project_root)
