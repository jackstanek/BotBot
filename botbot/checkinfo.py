"""Results of file checks"""

import time

import py

from .md5sum import get_file_hash
from .config import CONFIG

def _get_ptype(path):
    if path.islink():
        return 'link'
    elif path.isfile():
        return 'file'
    elif path.isdir():
        return 'dir'

def _is_important(path):
    exts = CONFIG.get('important', 'ext',
                      fallback='.sam, .bam')

    return path.ext in exts

class CheckResult():
    """Holds the result of a check"""

    def __init__(self, path, lastcheck=time.time()):
        self.path = path
        self.problems = set()

    def add_problem(self, probstr):
        """Add a problem to this file"""
        self.problems.add(probstr)

    def get_info_dict(self):
        """Get a dictionary fit for use with the SQL file cache"""
        def _serialize_problems():
            return ','.join(self.problems)

        path = self.path
        stat = self.path.stat()

        infodict = {
            'path': path.strpath,
            'mode': stat.mode,
            'username': stat.owner,
            'size': path.size(),
            'lastmod': path.mtime(),
            'ptype': _get_ptype(path),
            'md5sum': get_file_hash(path),
            'important': _is_important(path),
            'problems': _serialize_problems()
        }

        return infodict
