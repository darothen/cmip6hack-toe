#!/usr/bin/env python
from setuptools import setup, find_packages
from datetime import datetime

# Use a date-stamp format for versioning
now = datetime.now()
VERSION = now.strftime("%Y-%m-%d")

NAME = 'cmip6hack-toe'
LICENSE = 'MIT'
AUTHOR = 'Daniel Rothenberg'
AUTHOR_EMAIL = 'daniel@danielrothenberg.com'

setup(
    name=NAME,
    version=VERSION,
    license=LICENSE,
    author=AUTHOR, author_email=AUTHOR_EMAIL,
    package_dir={'': 'src'},
    scripts=[],
)
