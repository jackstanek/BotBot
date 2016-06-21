"""Botbot daemon mode!"""

import os
import sys
import errno

import inotify.adapters
from inotify.constants import IN_CREATE, IN_ATTRIB, IN_DELETE
from .checker import CheckerBase
from .sqlcache import get_dbpath
from .fileinfo import FileInfo

_EVENT_MASK = IN_CREATE | IN_ATTRIB | IN_DELETE

class DaemonizedChecker(CheckerBase):
    """Checker that runs in a daemon"""
    def __init__(self, path):
        super().__init__(sys.stdout, get_dbpath())
        self.rootpath = path
        self.watch = None

    def init(self):
        """Attempt to get an inotify watch on the specified path"""
        try:
            self.watch = inotify.adapters.InotifyTree(self.rootpath,
                                                      mask=_EVENT_MASK)
        except inotify.calls.InotifyError as err:
            raise OSError('Could not initialize inotify API: {} ({})'.format(
                errno.errorcode[err.errno],
                err.errno
            ))

    def handle(self, event):
        """Recheck the file given in this event"""
        path, filename = event[2:4] # wew lad, magic numbers
        chkpath = os.path.join(path, filename)

        if is_inevent(event, IN_CREATE, IN_ATTRIB):
            result = FileInfo(chkpath)
            self.check_file(result)
            self.db.store_file_problems(result)
        elif is_inevent(event, IN_DELETE):
            self.db.prune(chkpath)

    def run(self):
        """Event loop which runs forever"""
        for event in self.watch.event_gen():
            if event is not None:
                self.handle(event)

def is_inevent(event, *inevent):
    """
    Helper function to determine if event is the type of inotify event
    inevent
    """
    header = event[0]
    mask = 0
    for ie in inevent:
        mask |= ie
    return bool(mask & header.mask)
