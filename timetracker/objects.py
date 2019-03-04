#!/usr/bin/env python3
"""Objects for the timetracker `tt`"""

import io
import os
import csv
import time
from datetime import datetime
from datetime import timezone
import configparser

DEFAULT_HUMAN_DATETIME = '%Y-%m-%d %H:%M:%S %z'

DEFAULT_CONFIG = {
    'user': {
        'file':'/etc/tt/tt.conf',
    },
}
DEFAULT_CONFIG_RESOLVE_ORDER = (
    # XDG dirs first
    '/home/{}/.config/tt/tt.conf',
    '/home/{}/.config/tt.conf',
    '/home/{}/.tt/tt.conf',
    '/etc/tt/tt.conf',
    '/etc/tt.conf',
)

class Dialect(csv.Dialect):
    #pylint: disable=too-few-public-methods
    """CSV dialect based loosely on excel_tab"""
    delimiter = '\t'
    doublequote = True
    lineterminator = os.linesep
    quotechar = '"'
    quoting = 0
    skipinitialspace = False

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
        self.data = []
        self.dialect = dialect
        self.loaded = False

    def __getitem__(self, key):
        return self.data.__getitem__(key)

    def __setitem__(self, key, value):
        self.data.__setitem__(key, value)

    def __delitem__(self, key):
        self.data.__delitem__(key)

    def __enter__(self):
        self.read()
        return self

    def __exit__(self, *args, **kwargs):
        self.write()

    def __repr__(self):
        return '<{} at `{}`>'.format(type(self).__name__, self.file_name)

    def format_data(self, ts_format: str, tz_info=None):
        """Generator formatting data with a given ts_format for timestamps.

        Requires a ts_format, which is a format understood by strftime.
        tz_info can be used to override the system's timezone.
        The format returned is the same as self.data, except timestamps are
        strings now.
        """
        for row in self.data:
            time_data = datetime.fromtimestamp(row[0], tz=tz_info).strftime(ts_format)
            yield [time_data, *row[1:]]

    def format(self, ts_format: str, tz_info=None):
        """Formats data as an output file and returns it as a string.

        See format_data for more.
        The output is the same as writing to a file with a given timestamp format.
        If no self.dialect is set, the dialect is set to excel_tab with lineterminator = os.linesep
        """
        if not self.dialect:
            # This part should basically never be hit in real-world applications.
            dialect = Dialect
        else:
            dialect = self.dialect
        if not tz_info:
            tz_info = timezone.utc
        formatted_data = self.format_data(ts_format, tz_info)
        with io.StringIO() as output:
            writer = csv.writer(output, dialect=dialect)
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

        time_format is one of the following:
        - 'unix' indicating a unix timestamp, the default option
        - a string that can be used with strptime
        """
        with open(self.file_name, 'r') as data_file:
            if not self.dialect:
                self.dialect = csv.Sniffer().sniff(data_file.read(1024))
            data_file.seek(0)
            reader = csv.reader(data_file, dialect=self.dialect)
            self.data = list(reader)
            self.loaded = True
            self.data = [[int(row[0]), *row[1:]] for row in self.data]

    def write(self):
        """Writes self.data back to the file

        Writes the data into the file (self.file_name). For saving files elsewhere, see save
        This has different effects based on self.loaded:

        If self.loaded is True, i.e. the file will be replaced with self.data.
        The contents of self.data are not cleared.

        If self.loaded is False, self.data will be appended to the file.
        The contents of self.data are then removed to avoid duplicate writes.
        """
        if self.loaded:
            mode = 'w'
        else:
            mode = 'a'
        if not self.dialect and os.path.exists(self.file_name):
            # No dialect exists, but we can determine it from the file
            with open(self.file_name, 'r') as file_conn:
                sample = file_conn.read(1024)
                dialect = csv.Sniffer().sniff(sample)
        elif not self.dialect and not os.path.exists(self.file_name):
            # No dialect, and no way of guessing. Go back to defaults.
            # The default dialect is excel_tab with os specific lineseps.
            dialect = Dialect
        else:
            # The dialect exists
            dialect = self.dialect
        with open(self.file_name, mode) as file_conn:
            # Write
            writer = csv.writer(file_conn, dialect=dialect)
            writer.writerows(self.data)
        if not self.loaded:
            self.data = [] # clear data to avoid duplicate appends
        if not self.dialect:
            self.dialect = dialect # set dialect if not already set.

    def save(self, file_name, ts_format=DEFAULT_HUMAN_DATETIME, tz_info=None):
        """Save human-readable data to file specified

        Save data to file file_name.
        Optionally accept changed ts_format or tz_info
        """
        if not tz_info:
            tz_info = timezone.utc
        write_data = self.format(ts_format, tz_info)
        with open(file_name, 'w') as connection:
            connection.write(write_data)

    def load(self, file_name, ts_format=DEFAULT_HUMAN_DATETIME, tz_info=None):
        """Loads human-readable data from specified file

        Optionally change of ts_format and tz_data are possible"""
        if not os.path.exists(file_name):
            raise FileNotFoundError('The file you are trying to load does not exist')
        if not tz_info:
            tz_info = timezone.utc
        with open(file_name, 'r') as connection:
            this_dialect = csv.Sniffer().sniff(connection.read(1024))
            connection.seek(0)
            reader = csv.reader(connection, dialect=this_dialect)
            data = list(reader)
            data = [[int(datetime.strptime(row[0], ts_format).timestamp()), *row[1:]]
                    for row in data]
            self.data = data
    def append(self, activity: str, timestamp=round(time.time())):
        """Appends an activity at an optionally defined timestamp.

        Appends the activity with a timestamp as a row. If no timestamp is
        provided, the current time is used.
        """
        row = [timestamp, activity]
        self.data.append(row)

    @property
    def timestamp(self):
        """Timestamps from data"""
        return [row[0] for row in self.data]

    @property
    def activity(self):
        """Activities from data"""
        return [row[1] for row in self.data]


def file_finder(order: list):
    """Try out files in order. Return first hit. Raise FileNotFoundError if None."""
    if not order:
        raise FileNotFoundError('No file found')
    elif os.path.exists(order[0]):
        return order[0]
    else:
        return file_finder(order[1:])

def config_loader(file_name: str = None, order: list = None, defaults: dict = None):
    """Finds a configuration file from order or file_name

    If file_name is given, it will try to load file_name. If file_name is
    missing, but order is given, it will use file_finder to find the first file.
    if file_name and order are missing it will use DEFAULT_CONFIG_RESOLVE_ORDER
    to find a suitable file
    """
    if not defaults:
        defaults = DEFAULT_CONFIG
    if not file_name:
        if not order:
            order = DEFAULT_CONFIG_RESOLVE_ORDER
        file_name = file_finder(order)
    config = configparser.RawConfigParser()
    config.read_dict(defaults)
    config.read(file_name)
    return config

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
