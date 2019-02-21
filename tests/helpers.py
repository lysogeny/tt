"""Helpers for the test functions"""

import tempfile
import time
import os
import random
from typing import List, Tuple

def create_example_file(content: str) -> str:
    """Creates an example file at a temporary location and returns the file name"""
    with tempfile.NamedTemporaryFile('w', delete=False) as temp:
        temp.write(content)
        return temp.name

def format_example_data(data, sep='\t') -> str:
    """Formats data in a table"""
    return os.linesep.join([sep.join((str(r) for r in row)) for row in data])

def create_random_string(length: int) -> str:
    """Creates a string of random length"""
    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    string = ''.join(random.choices(letters, k=length))
    return string

def create_random_activity(length: int, depth: int) -> str:
    """Creates an activity consisting of depth elements of given length"""
    return ':'.join([create_random_string(length) for i in range(0, depth)])

def create_example_data(length: int, activities: int) -> List[Tuple[int, str]]:
    """Creates random data of given length with given amount of activities"""
    activities = [create_random_activity(length=5, depth=random.randint(1, 4))
                  for i in range(0, activities)]
    range_ts = (0, int(time.time()))
    data = [(random.randint(range_ts[0], range_ts[1]), random.choice(activities))
            for i in range(0, length)]
    return sorted(data, key=lambda x: x[0])

def store_example_data(length: int, activities: int) -> str:
    """Creates and stores example data into tempfile.

    Returns a string with file location of the data
    """
    data = create_example_data(length, activities)
    chars = format_example_data(data)
    return create_example_file(chars)
