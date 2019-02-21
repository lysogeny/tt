#!/usr/bin/env python3
"""Objects for the timetracker `tt`"""

import os
import csv

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

    def append(self, row):
        """Appends something to file"""
        if self.data:
            self.data.append(row)
        with open(self.file_name, 'a') as file_conn:
            writer = csv.writer(file_conn, dialect=self.dialect)
            writer.writerow(row)

class TrackingDataBase:
    """Object representing the Tracking Database and possible operations

    Consists of several tracking file objects
    Makes things available in there and implements __enter__ and __exit__
    """
    def __init__(self, dir_name, timefile_name='time.txt',
                 archivefile_name='archive.txt'):
        self.dir_name = dir_name
        if not os.path.isdir(self.dir_name):
            raise FileNotFoundError
        self.timefile_name = os.path.join(self.dir_name, timefile_name)
        self.archivefile_name = os.path.join(self.dir_name, archivefile_name)
        self.data = None
        self.dialect = None

    def read(self):
        """Parses a file from database into data, guessing dialect if not defined already."""
        with open(self.timefile_name, 'r') as timefile:
            # csv.Sniffer can deduce formats
            # We first use Sniffer to deduce the format
            # Then we read it with the identified format
            if not self.dialect:
                # But only do this if self.dialect is None
                self.dialect = csv.Sniffer().sniff(timefile.read(1024)) # determine dialect
                timefile.seek(0) # return to start of file
            reader = csv.reader(timefile, dialect=self.dialect)
            self.data = list(reader)

    def write(self):
        """Writes data"""
        with open(self.timefile_name, 'w') as timefile:
            writer = csv.writer(timefile, dialect=self.dialect)
            writer.write(self.data)

    def archive(self):
        """Archives entries"""

    def __enter__(self):
        self.read()
        return self

    def __exit__(self, exception, value, traceback):
        if self.data:
            # If we have a non-None self.data, we have probably read the file
            # and done things to it. We should write at that point.
            self.write()

#def command_action(method):
#    """Decorator for making an action a command"""
#    def inner_function(file_name):
#        def innerest_function(self, *args, **kwargs):
#            with TrackingFile(file_name) as data:
#                method(self, data, *args, **kwargs)
#        return innerest_function
#    return inner_function
#
#class BaseCommand:
#    """A command base"""
#    file_name = None
#
#    def __init__(self, file_name=None):
#        if file_name:
#            self.file_name = file_name
#
#    @command_action(file_name)
#    def action(self, obj, *args, **kwargs):
#        """Action performed by this command"""
#        raise NotImplementedError
#
#    def help(self):
#        """Prints help for this command"""
#        print(self.__doc__)
#
#
#class Append(BaseCommand):
#    """Append something to the thing"""
#    def action(self, obj, *args, **kwargs):
#        obj.append(*args, **kwargs)
#
#class App:
#    """The time tracking application
#
#    Provides: Switching
#    """
#
#    def __init__(self, database):
#        self.config = None
#        self.database = database
