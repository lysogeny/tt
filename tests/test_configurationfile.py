#!/usr/bin/env python3
"""Tests for the configuration file class

We want to check:
    - Reads
    - Fails if no file found
    - File resolver

Reading correctly is functionality of configparser and will not be tested.
"""

import os
import unittest
import configparser

from .context import timetracker
from . import helpers

class TestFileFinder(unittest.TestCase):
    """File finder Testing Tests"""
    # pylint: disable=invalid-name
    def setUp(self):
        self.files = [
            helpers.create_no_file(),
            helpers.create_no_file(),
            helpers.create_empty_file(),
            helpers.create_no_file(),
            helpers.create_empty_file(),
            helpers.create_no_file(),
            helpers.create_no_file(),
            helpers.create_no_file(),
        ]
        self.target = self.files[2]
        self.not_target = self.files[4]

    def tearDown(self):
        for file_name in self.files:
            if os.path.exists(file_name):
                os.remove(file_name)

    def test_file_finder_finds_correct_file(self):
        """Assert that the file finder finds the target file"""
        result = timetracker.file_finder(self.files)
        self.assertEqual(result, self.target)
        self.assertTrue(os.path.exists(result))

    def test_file_finder_returns_str(self):
        """Assert that the file finder returns a string"""
        result = timetracker.file_finder(self.files)
        self.assertIsInstance(result, str)

    def test_file_finder_doesnt_find_wrong_file(self):
        """Assert that the file finder finds a file that exists"""
        result = timetracker.file_finder(self.files)
        self.assertNotEqual(result, self.not_target)

    def test_file_finder_finds_existing_file(self):
        """Assert that the file finder finds a file that exists"""
        result = timetracker.file_finder(self.files)
        self.assertTrue(os.path.exists(result))

    def test_file_finder_raise_error(self):
        """Assert that file_finder raises FileNotFoundError when no files exist"""
        with self.assertRaises(FileNotFoundError):
            # the last three elements of self.files don't exist
            timetracker.file_finder(self.files[-3:])

class TestConfigLoader(unittest.TestCase):
    """Base Configuration Testing

    Test the functionality of config_loader
    - If file_name load file_name
    - if not file_name use order
    - If not order or file_name use DEFAULT_CONFIG_RESOLVE_ORDER
    """

    def test_config_loader_returns_confiparser(self):
        """Assert a configparser is returned by config_loader"""

    def test_config_parser_contains_defaults(self):
        """Assert that the configparser contains the default values passed to configparser"""

    def test_file_not_found_error_raised_suitably(self):
        """Assert that a file_finder's FileNotFoundError is raised when no file is loaded"""

    def test_file_can_be_loaded(self):
        """Test that a file can be loaded"""


#
