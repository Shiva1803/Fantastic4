"""
Pytest configuration for backend tests.
"""

import sys
import os

# Add parent directory to path so 'backend' module can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
