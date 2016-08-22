"""Results of file checks"""

import time

import py

from .md5sum import get_file_hash
from .config import CONFIG

def _is_important(path):
    exts = CONFIG.get('important', 'ext',
                      fallback='.sam, .bam')

    return path.ext in exts

class CheckResult():
    """Holds the result of a check"""

    def __init__(self, path, lastcheck=time.time(), problems=None, md5sum=None):
        if isinstance(path, str):
            self.path = py.path.local(path)
        elif isinstance(path, py.path.local):
            self.path = path

        self.lastcheck = lastcheck

        self.problems = set()
        if problems:
            if isinstance(problems, str):
                self.decode_probstr(problems)
            elif isinstance(problems, set):
                self.problems = problems
            else:
                raise TypeError('problems must be a set or a str')

        self.md5sum = md5sum

    def add_problem(self, probstr):
        """Add a problem to this file"""
        if probstr:
            self.problems.add(probstr)

    def serialize_problems(self):
        """Turn a set of problems from the CheckResult into a string"""
        return ','.join(self.problems)

    def decode_probstr(self, probstr):
        """Decode a problem string"""
        self.problems = set(probstr.split(','))
