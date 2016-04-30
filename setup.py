#!/usr/bin/env python3

from distutils.core import setup

setup(name='BotBot',
      version='0.0.3',
      description='Laboratory computational resource management',
      author='Jack Stanek',
      author_email='stane064@umn.edu',
      url='http://github.com/jackstanek/BotBot',
      scripts=['botbot/cli/botbot'],
      packages=['botbot'],
)
