"""Allow BotBot to ignore files, much like a .gitignore file."""

import os
from glob import glob

def find_ignore_file():
    path = os.path.expanduser('~/.botbotignore')
    if os.path.isfile(path):
        return path

def parse_ignore_rules(path):
    ig = list()
    if path is not None:
        with open(path, mode='r') as ignore:
            for line in ignore:
                ig.append(strip_comments(line).strip())
    return ig

def strip_comments(line):
    return line.split('#')[0]
