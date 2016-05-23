"""Allow BotBot to ignore files, much like a .gitignore file."""

import os
from glob import glob

def find_ignore_file():
    path = '~/.botbotignore'
    if os.path.isfile(path):
        return path
    
def parse_ignore_rules(path):
    ig = list()
    if path is not None:
        with open(path, mode='r') as ignore:
            for rule in ignore:
                ig.extend(glob(strip_comments(rule)))

    return ig

def strip_comments(line):
    return line.split('#')[0]
