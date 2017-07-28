#!/usr/bin/env python3

import os
import io
import re

from setuptools import setup

def read(*names, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name='BotBot',
    version=find_version('src', 'botbot', '__init__.py'),
    description='Laboratory computational resource management',
    author='Jack Stanek',
    author_email='stane064@umn.edu',
    url='http://github.com/jackstanek/BotBot',
    package_dir={'': 'src'},
    packages=['botbot']
)
