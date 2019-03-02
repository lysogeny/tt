"""Tests for the TrackingFile object

Possibly missing tests at the moment:
    - Save can save different timezones
    - Loading can deal with different timezones
"""
#pylint: disable=invalid-name,unused-import


import unittest
import tempfile
import os
import csv
import io
import copy
from datetime import timezone, timedelta

from .context import timetracker
from . import helpers

class TestTrackingFileBase(unittest.TestCase):
    """Base for the tracking file tests.

    Ensure deletion of temporary files stored in file or files.
    """
    file = str()
    files = dict()

    def setUp(self):
        self.file = helpers.create_no_file()
        self.tf = timetracker.TrackingFile(self.file)

    def delete_files(self):
        """Deletes files from string self.file and self.files"""
        if self.file and os.path.exists(self.file):
            os.remove(self.file)
        if self.files:
            # Non-assignment of this. Nothing is returned, assignment makes no
            # sense, but pylint is yelling at me if I don't do this.
            _ = [os.remove(file_name)
                 for file_name in self.files.values()
                 if os.path.exists(file_name)]

    def tearDown(self):
        self.delete_files()

class TestTrackingFileDefaults(TestTrackingFileBase):
    """Tests default values of TrackingFile"""

    def test_loaded_false(self):
        """Checks if loaded is false by default"""
        self.assertFalse(self.tf.loaded)

    def test_dialect_empty(self):
        """Asserts that dialect is undefined by default"""
        self.assertIsNone(self.tf.dialect)

    def test_data_empty(self):
        """Assert that data is empty when loaded"""
        self.assertFalse(self.tf.data)

    def test_file_name_provided(self):
        """Assert that the file name is the one we provided"""
        self.assertEqual(self.tf.file_name, self.file)

class TestTrackingFileIndexing(TestTrackingFileBase):
    """Test Tracking File Indexing provides indexing for the self.data property.

    Indexing is tested for the tracking file.
    """

    def setUp(self):
        self.file = helpers.create_no_file()
        self.tf = timetracker.TrackingFile(self.file)
        self.tf.data = [1, 2, 3, 4, 5]

    def test_index_deletion(self):
        """Test if deletion with indexes is implemented by TrackingFile"""
        del self.tf[0]
        self.assertEqual([2, 3, 4, 5], self.tf.data)

    def test_index_selection_single(self):
        """Test if selection by index is implemented by TrackingFile"""
        self.assertEqual(1, self.tf[0])

    def test_index_selection_slice(self):
        """Test if selection by index slicing is implemented by TrackingFile"""
        self.assertEqual([1, 2, 3], self.tf[0:3])

    def test_index_replacement(self):
        """Test if replacement by index is implemented by TrackingFile"""
        self.tf[1] = 9
        self.assertEqual(9, self.tf.data[1])

class TestTrackingFileWithStatement(TestTrackingFileBase):
    """Tests if TrackingFile implements __enter__ and __exit__"""

    def setUp(self):
        self.sample_len = 10
        self.file = helpers.store_example_data(self.sample_len, 2)
        self.tf = timetracker.TrackingFile(self.file)

    def test_entry_reads(self):
        """Test if __enter__ reads data."""
        old_len = len(self.tf.data)
        self.tf.__enter__()
        new_len = len(self.tf.data)
        self.assertEqual(self.sample_len, new_len-old_len)

    def test_exit_writes(self):
        """Test if __exit__ writes data."""
        with self.tf as tf:
            tf.append('Test')
        new_len = self.sample_len + 1
        tf = timetracker.TrackingFile(self.file)
        tf.read()
        actual_len = len(tf.data)
        self.assertEqual(new_len, actual_len)

class TestTrackingFileRepr(TestTrackingFileBase):
    """Test __repr__ of TrackingFile"""
    def test_repr_contains_filename(self):
        """Assert that repr contains the filename"""
        self.assertTrue(self.file in self.tf.__repr__())

class TestTrackingFileFormatData(TestTrackingFileBase):
    """Test the format_data method of TrackingFile.

    Assert that: elements at index 0 are converted to a string and in the
    correct format
    """

    def setUp(self):
        self.file = helpers.create_no_file()
        self.tf = timetracker.TrackingFile(self.file)
        self.tf.data.append([0, 'Work'])

    def test_formats_to_string(self):
        """Assert that objects at index 0 are strings"""
        out = self.tf.format_data('%F %T')
        self.assertIsInstance(list(out)[0][0], str)

    def test_format_is_correct(self):
        """Assert that the format returned is correct, i.e. the correct libraries are used."""
        out = self.tf.format_data('%F %T', timezone.utc)
        self.assertEqual(list(out)[0][0], '1970-01-01 00:00:00')

    def test_format_other_timezone_works(self):
        """Assert that the format returned is correct with a different timezone"""
        cet = timezone(timedelta(hours=1))
        out = self.tf.format_data('%F %T', cet)
        self.assertEqual(list(out)[0][0], '1970-01-01 01:00:00')

class TestTrackingFileFormat(TestTrackingFileBase):
    """Test the format method of TrackingFile"""

    def setUp(self):
        self.len = 15
        self.file = helpers.store_example_data(self.len, 3)
        self.tf = timetracker.TrackingFile(self.file)

    def test_format_returns_str(self):
        """Assert that the object returned by format is a string"""
        self.assertIsInstance(self.tf.format('%F %T'), str)

    def test_format_returns_non_empty(self):
        """Assert that the string returned is not zero-length"""
        with self.tf as tf:
            self.assertNotEqual(0, len(tf.format('%F %T', timezone.utc)))

    def test_format_creates_tabs(self):
        """Assert that the string returned by format has the correct amount of tab chars

        Tab chars are the default for the helpers for test. As the test data is
        created by the helpers, this should be fine.
        """
        with self.tf as tf:
            string = tf.format('%F %T', timezone.utc)
        self.assertEqual(self.len, string.count('\t'))
        # How do I do this?

    def test_format_sample_data(self):
        """Check the behaviour with sample data

        Tests that the format is correct in the UTC timezone.
        """
        sample_data = [
            [0, 'Free'],
            [946684800, 'Work'],
            [1074689100, 'Fun']
        ]
        self.tf.dialect = timetracker.Dialect
        self.tf.data = sample_data
        string = self.tf.format('%F %T', timezone.utc)
        should_string = '1970-01-01 00:00:00\tFree\n'\
                        '2000-01-01 00:00:00\tWork\n'\
                        '2004-01-21 12:45:00\tFun\n'
        self.assertEqual(string, should_string)

    def test_format_chooses_dialect_if_missing(self):
        """Assert that csv dialect is excel_tab with os.linesep if it is not defined."""
        self.tf.read()
        self.tf.dialect = None
        self.tf.format('%Y-%m-%d %H:%M:%S %z')

class TestTrackingFileRead(TestTrackingFileBase):
    """Test Tracking File Class can read files.

    Verify that:
    - Files can be read (self.data is not-empty)
    - self.loaded is set to true afterwards
    - self.dialect is defined after reading.
    - dialect is unmodified if already defined
    - Files are correctly loaded (with non-random example data)
    """

    def setUp(self):
        self.len = 10
        self.file = helpers.store_example_data(self.len, 12)
        self.tf = timetracker.TrackingFile(self.file)

    def test_file_can_be_read(self):
        """Test if a file that does not exist is created"""
        self.tf.read()
        self.assertTrue(self.tf.data)

    def test_file_reading_reads_correct_length(self):
        """Assert that the file reads the correct length of data"""
        self.tf.read()
        self.assertEqual(self.len, len(self.tf.data))

    def test_reading_sets_loaded(self):
        """Test if a file that does not exist is created"""
        self.tf.read()
        self.assertTrue(self.tf.loaded)

    def test_reading_defines_dialect(self):
        """Test if a file that does not exist is created"""
        self.tf.read()
        self.assertTrue(self.tf.dialect)

    def test_reading_loads_time_as_int_when_int(self):
        """Assert that times are loaded as integers"""
        self.tf.read()
        self.assertIsInstance(self.tf.data[0][0], int)

    def test_data_loads_correctly(self):
        """Assert that the data gets loaded correctly

        This is not very thorough, mainly because making more tests would end
        up testing the csv module and not my code.
        """
        test_string = "0\tFree\n1\tTest\n2\tAmazing\n"
        expected = [
            [0, "Free"],
            [1, "Test"],
            [2, "Amazing"]
        ]
        with open(self.file, 'w') as f:
            f.write(test_string)
        self.tf.read()
        self.assertEqual(self.tf.data, expected)

    def test_huge_file_loads(self):
        """Assert that large files can still be read"""
        len_file = 10000 # We want a big file, not a file so large that the tests will take forever
        file_name = helpers.store_example_data(len_file, 10)
        self.files['large'] = file_name
        tf = timetracker.TrackingFile(file_name)
        tf.read()
        self.assertEqual(len(tf.data), len_file)

class TestTrackingFileWrite(TestTrackingFileBase):
    """Test the write method of TrackingFile

    This is very stateful. Some things to consider: self.loaded affects this
    heavily.
    Options should also change the behaviour

    We should generally assert that:
    - A file which does not exist is created
    - providing a file_name creates a different file
    - ts_format works
    - Written timestamps make sense

    specifically if self.loaded:
    - The file is overwritten
    - self.data is not emptied

    if not self.loaded:
    - The file is apppended to
    - self.data is cleared
    """

    def setUp(self):
        self.len = 10
        self.files['empty'] = helpers.create_no_file()
        self.files['exists'] = helpers.store_example_data(self.len, 2)
        self.files['alternate'] = helpers.create_no_file()
        self.tf_empty = timetracker.TrackingFile(self.files['empty'])
        self.tf = timetracker.TrackingFile(self.files['exists'])

    def test_creates_file(self):
        """Assert that creation of file happens when it doesn't exist"""
        self.tf_empty.append('Hello')
        self.tf_empty.write()
        self.assertTrue(os.path.exists(self.files['empty']))

    def test_data_overwritten_when_loaded(self):
        """Assert that data being loaded will cause the file to be overwritten"""
        with self.tf as tf:
            tf.data = [tf.data[0]]
            # Reduce the data to the first element
        self.tf.read()
        self.assertEqual(len(self.tf.data), 1)

    def test_ensure_final_linesep(self):
        """Assert that a final linesep is added

        This might seem a strange thing to test, but I had some issues with
        missing final lineseps.
        """
        self.tf.write()
        with open(self.files['exists'], 'r') as f:
            content = f.read()
        self.assertTrue(content.endswith(os.linesep))

    def test_data_appended_when_not_loaded(self):
        """Assert that data is appended when file is not loaded"""
        self.tf.append('Free')
        self.tf.write()
        self.tf.read()
        self.assertEqual(len(self.tf.data), self.len+1)

class TestTrackingFileAppend(TestTrackingFileBase):
    """Test that append appends data to the data"""

    def test_append_appends(self):
        """Assert that append appends things to the data"""
        old_data = copy.deepcopy(self.tf.data)
        self.tf.append('Hello', 0)
        self.assertEqual(self.tf.data, old_data + [[0, 'Hello']])

    def test_append_does_no_file(self):
        """Assert that append does not create a file"""
        self.tf.append('Hello')
        self.assertFalse(os.path.exists(self.file))

class TestTrackingFileSave(TestTrackingFileBase):
    """Test save method of TrackingFile object.

    Functionality expected:
        - Save will happen
    """

    def setUp(self):
        self.data = helpers.create_example_data(20, 4)
        self.file = helpers.create_no_file()
        self.tf = timetracker.TrackingFile(self.file)
        self.tf.data = self.data

    def test_save_creates_file(self):
        """Assert that creation of file happens when it does not exist"""
        self.tf.save(self.file)
        self.assertTrue(os.path.exists(self.file))

    def test_save_create_formatted_ts(self):
        """Assert that saving creates data that is equal to that created by format_data"""
        self.tf.save(self.file)
        with open(self.file, 'r') as connection:
            content = connection.read()
        self.assertEqual(content, self.tf.format('%Y-%m-%d %H:%M:%S %z'))

    def test_save_created_correct_length(self):
        """Assert that saving creates data thas has the correct length"""
        self.tf.save(self.file)
        with open(self.file, 'r') as connection:
            content = connection.read()
        self.assertEqual(len(content), len(self.tf.format('%Y-%m-%d %H:%M:%S %z')))

    def test_save_can_save_other_timezones(self):
        """Assert that save saves timestamps in different timezones"""
        cet = timezone(timedelta(hours=1))
        self.tf.save(self.file, tz_info=cet)
        with open(self.file, 'r') as connection:
            data = connection.read()
        self.assertTrue(data.split(timetracker.Dialect.delimiter)[0].endswith('+0100'))

class TestTrackingFileLoad(TestTrackingFileBase):
    """Test write method of TrackingFile"""
    def setUp(self):
        self.data = helpers.create_example_data(30, 3)
        self.file = helpers.create_example_file(helpers.format_example_data(self.data))
        self.no_file = helpers.create_no_file()
        self.files['yes'] = self.file
        self.files['no'] = self.no_file
        self.tf = timetracker.TrackingFile(self.file)

    def test_file_load_can_load(self):
        """Assert that load method does not fail if file exists"""
        with self.tf as tf:
            tf.save(self.no_file)
        self.tf.load(self.no_file)

    def test_file_load_fails_if_missing(self):
        """Assert that loading the file fails if it is missing"""
        with self.assertRaises(FileNotFoundError):
            self.tf.load(self.no_file)

    def test_file_load_correct_data(self):
        """Assert that the data loaded is correct"""
        with self.tf as tf:
            old_data = self.tf.data
            tf.save(self.no_file)
        self.tf.data = []
        self.tf.load(self.no_file)
        self.assertEqual(self.tf.data, old_data)

    def test_file_can_read_different_timezone(self):
        """Assert that timestamps in different timezones can be loaded correctly"""
        cet = timezone(timedelta(hours=1))
        with self.tf as tf:
            old_data = self.tf.data
            tf.save(self.no_file, tz_info=cet)
        self.tf.data = []
        self.tf.load(self.no_file)
        self.assertEqual(self.tf.data, old_data)

class TestTrackingFilePropertyTimestamp(TestTrackingFileBase):
    """Test that the trackingfile timestamp property is correct"""

    def setUp(self):
        self.len = 25
        self.file = helpers.store_example_data(self.len, 5)
        self.tf = timetracker.TrackingFile(self.file)

    def test_timestamp_is_correct_length(self):
        """Assert that the property has the correct length"""
        with self.tf as tf:
            self.assertEqual(len(list(tf.timestamp)), self.len)

    def test_timestamp_is_correct_type(self):
        """Assert that the property has the correct type (list)"""
        with self.tf as tf:
            self.assertIsInstance(tf.timestamp, list)

    def test_timestamp_is_correct_content(self):
        """Assert that the property has the correct contents"""
        with self.tf as tf:
            timestamp_is = tf.timestamp
            timestamp_should = list(next(zip(*tf.data)))
        self.assertEqual(timestamp_is, timestamp_should)

class TestTrackingFilePropertyActivity(TestTrackingFileBase):
    """Test that the trackingfile activity property is correct"""

    def setUp(self):
        self.len = 25
        self.file = helpers.store_example_data(self.len, 5)
        self.tf = timetracker.TrackingFile(self.file)

    def test_activity_is_correct_length(self):
        """Assert that the property has the correct length"""
        with self.tf as tf:
            self.assertEqual(len(list(tf.activity)), self.len)

    def test_activity_is_correct_type(self):
        """Assert that the property has the correct type (list)"""
        with self.tf as tf:
            self.assertIsInstance(tf.activity, list)

    def test_activity_is_correct_content(self):
        """Assert that the property has the correct contents"""
        with self.tf as tf:
            activity_is = tf.activity
            activity_should = list(list(zip(*tf.data))[1])
        self.assertEqual(activity_is, activity_should)


#
