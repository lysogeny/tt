#!/usr/bin/env python3

import os
import time
import argparse
import subprocess
import locale
import shutil
from datetime import datetime

#import sys
#import tempfile
#import tailer

CONFIG_FILE = os.path.join(os.path.expanduser('~'), '.config', 'timetrack', 'config')

TT_FILE_NAME = 'time.txt'
TT_ARCHIVE_NAME = 'archive.txt'
TT_BACKUP_NAME = 'backup.txt'
TT_DEFAULT_DIR = os.path.join(os.path.expanduser('~'), 'Cloud', 'tt')

# Temporary?
TT_DIR = '/home/jooa/Cloud/tt'
TT_FILE = os.path.join(TT_DIR, 'time.txt')
TT_ARCHIVE = os.path.join(TT_DIR, 'archive.txt')

def format_line(line, utc=False):
    line = line.split('\t')
    try:
        line[0] = int(line[0])
    except ValueError:
        line[0] = line[0]
    else:
        method = datetime.utcfromtimestamp if utc else datetime.fromtimestamp
        line[0] = method(line[0]).strftime('%c')
    return '\t'.join(line)

class ActivityLine:
    """Activity line

    Provides several formatting options
    """
    def __init__(self):
        raise NotImplementedError


class TimeTrackingFile:
    """Abstraction for the time tracking file/folder.

    Provides all the necessary tidbits for modifying the time-tracking file
    contents.
    """
    def __init__(self, dir_name=None, file_name=None, archive_name=None,
                 verbose=True, utc=False, raw_ts=False):
        self.format = "{timestamp}\t{activity}\n"
        self.timeformat = "unix"
        self.default = "Free"
        self.utc = utc
        self.raw_ts = raw_ts
        if file_name is None and archive_name is None:
            if dir_name is None:
                dir_name = TT_DEFAULT_DIR
            self.file_name = os.path.join(dir_name, TT_FILE_NAME)
            self.archive_name = os.path.join(dir_name, TT_ARCHIVE_NAME)
            self.backup_file_name = os.path.join(dir_name, TT_BACKUP_NAME)
        else:
            self.file_name = file_name
            self.archive_name = archive_name
        self.verbose = verbose

    def __repr__(self):
        return '<TimeTrackingFile at `{}`>'.format(self.file_name)

    def append_activity_map(self, activity):
        """Appends to the time-tracking file based on a mapping"""
        line = self.format.format_map(activity)
        with open(self.file_name, 'a') as f:
            f.writelines(line)
        return format_line(line, self.utc) if not self.raw_ts else line

    def append_activity(self, activity, *args):
        """Appends activity to the time-tracking file"""
        act_map = {'timestamp': round(time.time()), 'activity': activity}
        return self.append_activity_map(act_map)

    def tail(self, n=5, *args):
        """Returns the last `n` activities, optionally in human-readable form."""
        try:
            n = int(n)
        except (TypeError, ValueError):
            n = 5
        with open(self.file_name, 'r') as f:
            # Seek to the end.
            lines = f.readlines()[-n:]
            lines = [format_line(line, self.utc) if not self.raw_ts else line for line in lines]
        return ''.join(lines)

    def sort(self, *args):
        """Sorts the list and saves it again"""
        raise NotImplementedError

    def archive(self, *args):
        """Archive old (defined by some option) activities"""
        # Implement this. Details might become apparent after a while. Currently not sure what would be a good thing for this.
        raise NotImplementedError

    def backup(self, *args):
        """Copy file to backup location"""
        try:
            shutil.copy(self.file_name, self.backup_file_name)
        except:
            response = 'Something went wrong.'
        else:
            response = 'Everything fine'
        return response

    def edit(self, editor=None, *args):
        """Opens an editor on the file"""
        if not editor:
            editor = os.environ.get('EDITOR', 'vim')
        if editor == 'vim':
            return '{} exited with status {}'.format(editor, subprocess.call([editor, self.file_name]))
        else:
            return '{} exited with status {}'.format(editor, subprocess.call([editor, self.file_name]))

    def flush(self, confirm=True, *args):
        """Removes all entries"""
        if confirm and input("Are you sure? [yN] ").lower() in ['yes', 'y']:
            open(self.file_name, 'w').close()
            return "Cleared activities"
        return "Abort"

    def insert(self, activity='Free', timestamp=round(time.time())):
        """Inserts a activity at timestamp"""
        with open(self.file_name, 'r') as f:
            content = f.readlines()
        content = [tuple(line.split('\t')) for line in content]
        content = [(int(i[0]), i[1]) for i in content]
        content.append((timestamp, activity))
        content = sorted(content)
        content_str = ''.join(['{}\t{}'.format(i[0], i[1]) for i in content])
        content_i = [index for index, line in enumerate(content) if line[0] == timestamp][0]
        content_trim = ['{}\t{}'.format(line[0], line[1]) for line in content[content_i-2:content_i+2]]
        with open(self.file_name, 'w') as f:
            f.write(content_str)
        return ''.join([format_line(line, self.utc) for line in content_trim])

    def list(self):
        with open(self.file_name, 'r') as f:
            content = [line.strip().split('\t') for line in f.readlines()]
        zipped = sorted(set(list(zip(*content))[1]))
        return os.linesep.join(zipped)


def main():
    """Main function, called when not loaded as lib"""
    locale.setlocale(locale.LC_TIME, '') # Fixes an issue around not correctly using the locale

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', dest='verbose',
                        help='increased verbosity',
                        default=False, action='store_true')
    parser.add_argument('-a', '--archive', dest='archive',
                        help='automatically archive older entries',
                        default=False, action='store_true')
    parser.add_argument('-c', '--config', dest='config_file', metavar='FILE',
                        default=CONFIG_FILE,
                        help='configuration file to load in place of defaults')
    parser.add_argument('-d', '--dir', dest='tt_dir', metavar='DIR',
                        default=TT_DEFAULT_DIR,
                        help='directory to load files from')
    parser.add_argument('-u', '--utc', dest='utc', help='print time in UTC', 
                        default=False, action='store_true')
    parser.add_argument('-r', '--raw', dest='raw', help='do not format timestamps', 
                        default=False, action='store_true')
    parser.add_argument('command', nargs='?', 
                        help="command to perform on the file")
                        #choices=['do','tail','show','append','new','backup','vi','edit','visual','flush','t','a','e'])
    # I think the sanest thing would be to load a different subclass of ttf
    # depending on `command`. The arguments to command are then parsed by that
    # object, somehow so that tt ignores any commands that are not part of it's
    # own part?
    parser.add_argument('args', nargs='*', help="further arguments passed to command")
    args = parser.parse_args()

    if args.verbose:
        print(args)

    ttf = TimeTrackingFile(args.tt_dir, verbose=args.verbose, utc=args.utc, raw_ts=args.raw)

    #default_command = ttf.tail
    lookup_dict = {
        'list': ttf.list,
        'insert': ttf.insert,
        'do': ttf.append_activity,
        'tail': ttf.tail,
        'show': ttf.tail,
        'append': ttf.append_activity,
        'new': ttf.append_activity,
        'backup': ttf.backup,
        'edit': ttf.edit,
        'vi': ttf.edit,
        'visual': ttf.edit,
        'flush': ttf.flush,
        't': ttf.tail,
        'a': ttf.append_activity,
        'add': ttf.append_activity,
        'e': ttf.edit,
        None: ttf.tail,
    }
    try:
        command = lookup_dict[args.command]
    except KeyError:
        #command = default_command
        result = ttf.append_activity(*([args.command]+args.args))
    else:
        result = command(*args.args)
    print(str(result).strip())

if __name__ == '__main__':
    main()


