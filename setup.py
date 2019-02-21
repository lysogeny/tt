#!/usr/bin/env python3
"""Setup file for tt"""

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='timetracker',
    version='0.0.0',
    description='Hiercharchical simple file-based timetracking',
    #long_description=readme,
    author='Jooa Hooli',
    author_email='code@jooa.xyz',
    url='https://github.com/lysogeny/tt',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
