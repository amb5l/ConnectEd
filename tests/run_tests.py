#!/usr/bin/env python3
"""
Test Runner for ConnectEd Tests
"""

import unittest
import sys
import os


# Add ConnectEd package to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ConnectEd'))

# Add tests directory to path for utility imports
sys.path.insert(0, os.path.dirname(__file__))

# Import all test modules
