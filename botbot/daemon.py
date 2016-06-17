"""Botbot daemon mode!"""

import os
import errno

import inotify.adapters
from inotify.constants import IN_CREATE, IN_ATTRIB, IN_DELETE
from .checker import Checker

_ACTIONABLE_EVENTS = (IN_CREATE, IN_ATTRIB, IN_DELETE)

class DaemonizedChecker(Checker):
    """Checker that runs in a daemon"""
    def __init__(self, path):
        super().__init__()
        self.rootpath = path
        self.watch = None

        del self.check_all
        del self.checklist, self.checked

    def init(self):
        """Attempt to get an inotify watch on the specified path"""
        try:
            self.watch = inotify.adapters.InotifyTree(self.rootpath)
        except inotify.calls.InotifyError as err:
            raise OSError('Could not initialize inotify API: {} ({})'.format(
                errno.errorcode[err.errno],
                err.errno
            ))

    def handle(self, event):
        """Recheck the file given in this event"""
        path, filename = event[2:3] # wew lad, magic numbers
        chkpath = os.path.join(path, filename)

        if is_inevent(event, 'IN_CREATE') or is_inevent(event, 'IN_MODIFY'):
            result = self.check_file(chkpath)
            self.db.store_file_problems(result)
        elif is_inevent(event, 'IN_DELETE'):
            self.db.prune(chkpath)

    def run(self):
        """Event loop which runs forever"""
        for event in self.watch.event_gen():
            if event is not None:
                self.handle(event)

def is_inevent(event, inevent):
    """
    Helper function to determine if event is the type of inotify event
    inevent
    """
    header = event[0]
    return bool(header.mask & inevent)
