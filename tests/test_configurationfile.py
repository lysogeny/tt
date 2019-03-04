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
from collections.abc import Iterable

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
        self.test_function = timetracker.file_finder
        self.test_class_result = str

    def tearDown(self):
        for file_name in self.files:
            if os.path.exists(file_name):
                os.remove(file_name)

    def test_file_finder_finds_correct_file(self):
        """Assert that the file finder finds the target file"""
        result = self.test_function(order=self.files)
        self.assertEqual(result, self.target)
        self.assertTrue(os.path.exists(result))

    def test_file_finder_returns_correct_type(self):
        """Assert that the file finder returns a string"""
        result = self.test_function(order=self.files)
        self.assertIsInstance(result, self.test_class_result)

    def test_file_finder_doesnt_find_wrong_file(self):
        """Assert that the file finder finds a file that exists"""
        result = self.test_function(order=self.files)
        self.assertNotEqual(result, self.not_target)

    def test_file_finder_finds_existing_file(self):
        """Assert that the file finder finds a file that exists"""
        result = self.test_function(order=self.files)
        self.assertTrue(os.path.exists(result))

    def test_file_finder_raise_error(self):
        """Assert that file_finder raises FileNotFoundError when no files exist"""
        with self.assertRaises(FileNotFoundError):
            # the last three elements of self.files don't exist
            self.test_function(order=self.files[-3:])

class TestConfigLoader(TestFileFinder):
    """Base Configuration Testing

    Test the functionality of config_loader
    - If file_name load file_name
    - if not file_name use order
    - If not order or file_name use DEFAULT_CONFIG_RESOLVE_ORDER
    """
    def setUp(self):
        self.files = [
            helpers.create_no_file(),
            helpers.create_no_file(),
            helpers.create_sample_config(),
            helpers.create_no_file(),
            helpers.create_sample_config(),
            helpers.create_no_file(),
            helpers.create_no_file(),
            helpers.create_no_file(),
        ]
        self.target = self.files[2]
        self.not_target = self.files[4]
        self.test_function = timetracker.config_loader
        self.test_class_result = configparser.RawConfigParser

    @unittest.skip
    def test_file_finder_finds_correct_file(self):
        """Test that the correct file is identified.

        This test does not make sense for the config_loader, as a
        different type of object is returned that does not contain any
        information about the file
        """

    @unittest.skip
    def test_file_finder_finds_existing_file(self):
        """Assert that the file finder finds a file that exists

        This test does not make sense for the config_loader, as no file handle is returned.
        """

    def test_config_parser_contains_defaults(self):
        """Assert that the configparser contains the default values passed to configparser"""
        # How do I test if the default values are contained within the
        # configparser?
        defaults = {
            'test': {
                'key': True,
                'value': 'yes',
            },
            'section2': {
                'indeed': 'no',
            },
        }
        result = self.test_function(self.target, defaults=defaults)
        self.assertEqual(result['test']['value'], 'yes')

    def test_config_parser_contains_defaults_when_file_none(self):
        """Assert that the configparser contains the default values passed to configparser"""
        # How do I test if the default values are contained within the
        # configparser?
        defaults = {
            'test': {
                'value': 'yes'
            }
        }
        result = self.test_function(self.not_target, defaults=defaults)
        self.assertEqual(result['test']['value'], 'yes')

    def test_config_parser_can_read_percent_escaped_strings(self):
        """Assert that the configparser can read percent escaped strings from the file"""
        result = self.test_function(self.target)
        self.assertEqual(result['user']['human_format'], '%Y-%m-%d %H:%M:%S')

    def test_config_parser_contains_file_values(self):
        """Assert that the file that we loaded contains the data that we were promised"""
        result = self.test_function(self.target)
        self.assertEqual(result['data']['storage'], '/tmp/tt.txt')
        self.assertEqual(result['user']['editor'], 'vim')

class TestDefaultConfigurations(unittest.TestCase):
    """Test the default values and other UPPER_CASE objects"""
    def test_default_config_is_dict_of_dict(self):
        """Assert that the default config is a dict of dicts"""
        self.assertIsInstance(timetracker.DEFAULT_CONFIG, dict)
        for value in timetracker.DEFAULT_CONFIG:
            self.assertIsInstance(timetracker.DEFAULT_CONFIG[value], dict)

    def test_default_config_resolve_order_is_iterable(self):
        """Assert that the default config resolve order is iterable"""
        self.assertIsInstance(timetracker.DEFAULT_CONFIG_RESOLVE_ORDER, Iterable)

    def test_default_human_datetime_is_str(self):
        """Assert that the default human datetime is a string"""
        self.assertIsInstance(timetracker.DEFAULT_HUMAN_DATETIME, str)


#
