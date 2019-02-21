"""Provides context for tests"""
# pylint: disable=wrong-import-position
# While it is very nice of pylint to remind me to order this correctly, that
# import cannot be at the top of this file.

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import timetracker
