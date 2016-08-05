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

    def __init__(self, path, lastcheck=time.time(), probstr=None):
        self.path = path
        self.lastcheck = lastcheck
        if probstr:
            self.decode_probstr(probstr)
        else:
            self.problems = set()

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
