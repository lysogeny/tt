"""Tests for helper test functions"""

import os
import unittest
import random
from . import helpers

class TestCreateExampleFile(unittest.TestCase):
    """Tests create_example_file

    Mostly tests if a file is created, a string is returned, and the file can
    be read and is the correct contents.
    """
    def setUp(self):
        self.file_name = helpers.create_example_file(self.__doc__)

    def test_can_create_file(self):
        """Tests if a string is returned"""
        self.assertIsInstance(self.file_name, str)

    def test_file_exists(self):
        """Tests if the file created exists"""
        self.assertTrue(os.path.exists(self.file_name))

    def test_file_reads(self):
        """Tests if the file has the contents we wrote"""
        with open(self.file_name, 'r') as test_file:
            content = test_file.read()
            self.assertTrue(content == self.__doc__)

    def tearDown(self):
        os.remove(self.file_name)

class TestFormatExampleData(unittest.TestCase):
    """Tests formatting of example data"""

    def test_single_row(self):
        """Tests if a single row is correctly formatted"""
        should_string = "abc\tdef"
        in_data = [("abc", "def")]
        is_string = helpers.format_example_data(in_data)
        self.assertEqual(should_string, is_string)

    def test_two_row(self):
        """Tests if a single row is correctly formatted"""
        should_string = "abc\tdef" + os.linesep + "ghi\tjkl"
        data = [("abc", "def"),
                ("ghi", "jkl")]
        is_string = helpers.format_example_data(data)
        self.assertEqual(should_string, is_string)

    def test_mixed_type_rows(self):
        """Tests if a mixed-row types are correctly formatted"""
        should_string = "abc\tdef" + os.linesep + "123\t456"
        data = [("abc", "def"),
                (123, 456)]
        is_string = helpers.format_example_data(data)
        self.assertEqual(should_string, is_string)

    def test_mixed_type_columns(self):
        """Tests if a mixed-column types are correctly formatted"""
        should_string = "123\tabc" + os.linesep + "789\txyz"
        data = [(123, "abc"),
                (789, "xyz")]
        is_string = helpers.format_example_data(data)
        self.assertEqual(should_string, is_string)

    def test_alternate_sep(self):
        """Tests if a alternate separators work"""
        should_string = "abc def"
        data = [("abc", "def")]
        is_string = helpers.format_example_data(data, sep=' ')
        self.assertEqual(should_string, is_string)

class TestCreateRandomString(unittest.TestCase):
    """Test creation of random strings"""

    def test_string(self):
        """Tests if create_random_string returns a string"""
        string = helpers.create_random_string(10)
        self.assertIsInstance(string, str)

    def test_string_length1(self):
        """Tests if create_random_string returns length 1 string"""
        length = 1
        string = helpers.create_random_string(length)
        self.assertEqual(len(string), length)

    def test_string_length100(self):
        """Tests if create_random_string returns length 100 string"""
        length = 100
        string = helpers.create_random_string(length)
        self.assertEqual(len(string), length)

    def test_string_length1000(self):
        """Tests if create_random_string returns length 100 string"""
        length = 1000
        string = helpers.create_random_string(length)
        self.assertEqual(len(string), length)

    def test_string_length0(self):
        """Tests if create_random_string returns length 0 string with zero input"""
        length = 0
        string = helpers.create_random_string(length)
        self.assertEqual(len(string), length)

    def test_string_length_minus1(self):
        """Tests if create_random_string returns length 0 string with negative input"""
        length = -1
        string = helpers.create_random_string(length)
        self.assertEqual(len(string), 0)

class TestCreateRandomActivity(unittest.TestCase):
    """Tests creation of random activities

    Mostly tests if correct lengths are created for a couple of sample cases.
    """

    def test_depth_1(self):
        """Tests if depth 1 length 10 is 10 long"""
        depth = 1
        length = 10
        activity = helpers.create_random_activity(length=length, depth=depth)
        self.assertEqual(len(activity), length)

    def test_depth_2(self):
        """Tests if depth 2 length 10 is correct length long"""
        depth = 2
        length = 10
        activity = helpers.create_random_activity(length=length, depth=depth)
        self.assertEqual(len(activity), length*depth + depth - 1)

    def test_depth_20(self):
        """Tests if depth 20 length 10 is correct length long"""
        depth = 20
        length = 10
        activity = helpers.create_random_activity(length=length, depth=depth)
        self.assertEqual(len(activity), length*depth + depth - 1)

    def test_depth_0(self):
        """Tests if depth 0 length 10 is empty string"""
        depth = 0
        length = 10
        activity = helpers.create_random_activity(length=length, depth=depth)
        self.assertEqual(activity, '')

class TestCreateExampleData(unittest.TestCase):
    """Tests creation of sample data sets

    Tests if data is ordered, correct length and has a correct amount of activities.
    """

    def test_data_len_10(self):
        """Tests creation of length 10 data is length 10"""
        length = 10
        activities = 5
        result = helpers.create_example_data(length, activities)
        self.assertEqual(length, len(result))

    def test_data_len_100(self):
        """Tests creation of length 100 data is length 100"""
        length = 100
        activities = 5
        result = helpers.create_example_data(length, activities)
        self.assertEqual(length, len(result))

    def test_data_order(self):
        """Tests if timestamps are ordered

        Note that due to RNG this test may very well succeed even if timestamps
        are not being ordered. We will mitigate this by generating a very large data set.
        """
        length = 10000
        activities = 12
        result = helpers.create_example_data(length, activities)
        times = [r[0] for r in result]
        self.assertEqual(times, sorted(times))

    def test_correct_activity_count(self):
        """Tests if correct amount of activities are created

        Note that due to RNG this might fail while actually not being broken.
        We mitigate this by creating a very large set and making this very unlikely.
        """
        length = 10000
        activities = 12
        result = helpers.create_example_data(length, activities)
        acts = {r[1] for r in result}
        self.assertEqual(len(acts), activities)

class TestStoreExampleData(unittest.TestCase):
    """Tests storing sample data sets"""

    def setUp(self):
        """Create a sample file"""
        random.seed(0)
        self.test_file = helpers.store_example_data(500, 10) # 500 entries of 10 distinct activities
        random.seed(0)
        self.test_data = helpers.create_example_data(500, 10)
        self.test_content = helpers.format_example_data(self.test_data)

    def test_file_exists(self):
        """Tests that the file exists"""
        self.assertTrue(os.path.exists(self.test_file))

    def test_file_contents(self):
        """Tests that the file has the correct contents"""
        with open(self.test_file, 'r') as test:
            content = test.read()
        self.assertEqual(content, self.test_content)

    def tearDown(self):
        os.remove(self.test_file)
