#!/usr/bin/env python3
"""Objects for the timetracker `tt`"""

import io
import os
import csv
import time

class TrackingFile:
    """A single tracking file object

    This class defines a tracking file. It is pointed at a file and we can
    start from there.
    Reading and writing are supported. the with statement can be used to
    automagically read and write like this:

        >>> with TrackingFile('example.csv') as tf:
        >>>     tf.append('Work')

    __enter__ will read the file, and __exit__ will write the file. Append
    appends the 'Work' entry to the file. This construct is most useful when
    used with operations that both read and write, such as editing the file.

    A better way of defining the above behaviour would be:

        >>> tf = TrackingFile('example.csv')
        >>> tf.append('Work')
        >>> tf.write()

    This avoids a possibly costly loading of the whole file, and is best suited
    for only adding to the file.

    __{del,set,get}item__ are implemented to allow index-based manipulation of
    data. These methods call the same method on self.data.

    Formatting of data is implemented. For instance, to print the last 5 entries
    in a user readable (ISO-8601) format:

        >>> tf = TrackingFile('example.csv')
        >>> tf.read()
        >>> print(tf[-5:].format('%F %T'))

    """
    def __init__(self, file_name, dialect=None):
        self.file_name = file_name
        if not os.path.exists(self.file_name):
            raise FileNotFoundError
        self.data = []
        self.dialect = dialect
        self.loaded = False

    def __getitem__(self, key):
        self.data.__getitem__(key)

    def __setitem__(self, key, value):
        self.data.__setitem__(key, value)

    def __delitem__(self, key):
        self.data.__delitem__(key)

    def __enter__(self):
        self.read()
        return self

    def __exit__(self, *args, **kwargs):
        self.write()

    def format_data(self, ts_format):
        """Formats data with a given ts_format for timestamps.

        The format returned is the same as self.data, except timestamps are
        strings now.
        """
        return [[time.strftime(ts_format, time.gmtime(row[0])), row[1]] for row in self.data]

    def format(self, ts_format):
        """Formats data as an output file and returns it as a string.

        The output is the same as writing to a file with a given timestamp format.
        """
        formatted_data = self.format_data(ts_format)
        with io.StringIO() as output:
            writer = csv.writer(output, dialect=self.dialect)
            writer.writerows(formatted_data)
            out_string = output.getvalue()
        return out_string

    def read(self):
        """Reads file contents into self.data

        File contents are read into self.data. This happens in several steps.
        First the first 1024 bytes are read to determine the csv dialect if it
        is not already defined. Then the file is provided to csv.reader, which
        is then converted to a list.
        Finally, self.loaded is set to True to indicate that self.data contains
        the whole file and writing should replace, not append.
        """
        with open(self.file_name, 'r') as data_file:
            if not self.dialect:
                self.dialect = csv.Sniffer().sniff(data_file.read(1024))
            data_file.seek(0)
            reader = csv.reader(data_file, dialect=self.dialect)
            self.data = list(reader)
            self.loaded = True

    def write(self, ts_format='%s', file_name=None):
        """Writes self.data to a specific file using a timestamp format.

        By default it writes data to the file stored in the object, but this
        can be changed by defining file_name. ts_format defaults to '%s',
        indicating the unix epoch

        This has different effects based on self.loaded:

        If self.loaded is True, i.e. the file will be replaced with self.data.
        The contents of self.data are not cleared.

        If self.loaded is False, self.data will be appended to the file.
        The contents of self.data are then removed to avoid duplicate writes.
        """
        if not file_name:
            file_name = self.file_name
        if self.loaded:
            mode = 'w'
        else:
            mode = 'a'
        out_data = self.format_data(ts_format)
        with open(file_name, mode) as file_conn:
            writer = csv.writer(file_conn, dialect=self.dialect)
            writer.writerows(out_data)
        if not self.loaded:
            self.data = []

    def append(self, activity, timestamp=round(time.time())):
        """Appends an activity at an optionally defined timestamp.

        Appends the activity with a timestamp as a row. If no timestamp is
        provided, the current time is used.
        """
        row = [timestamp, activity]
        self.data.append(row)

class ConfigurationFile:
    """Object representing the configuration file"""
    # This needs:
    # - Optionally defined file name. If file name is missing:
    # - File resolver. Figures out what the file might be from a list of options
    # - configparser.ConfigParser
    def __init__(self, file_name=None):
        pass

    def parse(self):
        """Parses the configuration file"""

    def load(self):
        """Load the configuration file"""

class BaseCommand:
    """Object representing a command"""
    def __init__(self, config=None):
        self.config = config

    def __call__(self, *args, **kwargs):
        self.command(*args, **kwargs)

    def reconfigure(self, config):
        """Configures the command"""
        self.config = config

    def command(self, *args, **kwargs):
        """Command method of this command"""
        raise NotImplementedError

class CommandAppend(BaseCommand):
    """Appends something to the database"""
    def command(self, *args, **kwargs):
        activity = kwargs['activity']
        timestamp = kwargs['timestamp']
        with TrackingFile(self.config['target_file']) as tracking_file:
            if timestamp:
                tracking_file.append(activity, timestamp)
            else:
                tracking_file.append(activity)

class CommandEdit(BaseCommand):
    """Opens the database in an editor to allow the user to make edits"""
    def command(self, *args, **kwargs):
        pass

class CommandTail(BaseCommand):
    """Shows the last n entries of the database"""
    def command(self, *args, **kwargs):
        count = kwargs['count']
        with TrackingFile(self.config['target_file']) as tracking_file:
            tail = tracking_file.read().data[-count:]
        print(tail)

class App:
    """Object representing the Application"""
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        pass

    def run(self):
        """Runs the app"""
