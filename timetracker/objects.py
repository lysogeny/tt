#!/usr/bin/env python3
"""Objects for the timetracker `tt`"""

import os
import csv
import time

class NotConnectedError(BaseException):
    """Error raised when file object is not connected"""

class TrackingFile:
    """A single tracking file object"""
    def __init__(self, file_name, dialect=None, mode=None):
        self.file_name = file_name
        if not os.path.exists(self.file_name):
            raise FileNotFoundError
        self.data = None
        self.file = None
        self.reader = None
        self.dialect = dialect
        self.mode = mode
        # We enter by opening a file connection in read mode.
        # We figure out what dialect it is
        # And then create a csv reader object from that.
        # This way we don't have to read the file if we don't need it. But we
        # keep the connection around should we choose to read it.

    def connect(self, mode='r'):
        """Connect to the file

        This opens self.file_name in self.mode, and if self.dialect is None,
        will guess the dialect A csv reader is then opened and made available
        as self.reader.
        """
        self.mode = mode
        self.file = open(self.file_name, self.mode)
        if not self.dialect:
            self.dialect = csv.Sniffer().sniff(self.file.read(1024))
        self.file.seek(0)
        self.reader = csv.reader(self.file, dialect=self.dialect)

    def __enter__(self):
        self.connect()
        # Just connect
        return self

    def __exit__(self, *args, **kwargs):
        if self.data:
            # Only write if we have something in data.
            self.write()
        self.file.__exit__(*args, **kwargs)

    def read(self):
        """Reads into self.data

        This is done by storing a list of self.reader in self.data.
        Thus you first need to connect to the file.
        Will raise an Error if self.reader is None
        """
        if self.reader:
            self.data = list(self.reader)
        else:
            raise NotConnectedError("Are you sure the file is connected?")

    def write(self):
        """Writes self.data to the file

        Be careful as this will overwrite the file.
        Will do nothing if self.data is implied False
        """
        if self.data:
            with open(self.file_name, 'w') as file_conn:
                writer = csv.writer(file_conn, dialect=self.dialect)
                writer.writerows(self.data)

    def close(self):
        """Closes the file connection"""
        self.file.close()
        self.reader = None

    def append(self, activity, timestamp=round(time.time())):
        """Appends something to file"""
        row = (timestamp, activity)
        if self.data:
            self.data.append(row)
        with open(self.file_name, 'a') as file_conn:
            writer = csv.writer(file_conn, dialect=self.dialect)
            writer.writerow(row)

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
