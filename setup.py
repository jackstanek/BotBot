#!/usr/bin/env python3

from setuptools import setup

setup(
    name='BotBot',
    version='0.0.4',
    description='Laboratory computational resource management',
    author='Jack Stanek',
    author_email='stane064@umn.edu',
    url='http://github.com/jackstanek/BotBot',
    entry_points={
        'console_scripts':[
            'botbot = botbot.botbot:main',
        ]
    },
    packages=['botbot'],
    include_package_data=True,
    install_requires=[
        'jinja2',
        'pytest'
    ]
)
