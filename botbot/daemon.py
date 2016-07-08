"""Botbot daemon mode!"""

import os
import sys
import errno

import inotify.adapters
from inotify.constants import *
from .checker import CheckerBase
from .sqlcache import get_dbpath
from .report import DaemonReporter
from . import fileinfo
from .config import CONFIG

_EVENT_MASK = IN_CREATE | IN_ATTRIB | IN_DELETE | IN_MOVED_FROM | IN_MOVED_TO
_RECHECK_MASK = IN_CREATE | IN_ATTRIB | IN_MOVED_TO
_PRUNE_MASK = IN_MOVED_FROM | IN_DELETE

class DaemonizedChecker(CheckerBase):
    """Checker that runs in a daemon"""
    def __init__(self, path):
        super().__init__(get_dbpath())
        self.rootpath = path
        self.watch = None
        self.handle_hook = [] # Callbacks for event handling
        self.reporter = DaemonReporter(self)

    def add_event_handler(self, func, mask=(IN_ATTRIB | IN_CREATE)):
        """
        Helper function to add an event handler callback. The function
        runs if the event mask matches the mask given in mask.
        """
        self.handle_hook.append((func, mask))

    def init(self, *event_handlers):
        """
        Attempt to get an inotify watch on the specified path. Add event
        handler callbacks to the inotify hook
        """
        try:
            self.watch = inotify.adapters.InotifyTree(self.rootpath,
                                                      mask=_EVENT_MASK)
        except inotify.calls.InotifyError as err:
            raise OSError('Could not initialize inotify API: {} ({})'.format(
                errno.errorcode[err.errno],
                err.errno
            ))

        for h in event_handlers:
            func, mask = h
            self.add_event_handler(func, mask)

    def handle(self, event):
        """Recheck the file given in this event"""
        path, filename = event[2:4] # wew lad, magic numbers
        mask = event[0].mask
        chkpath = os.path.join(path, filename)

        for handler in self.handle_hook:
            func, hmask = handler
            if bool(hmask & mask):
                func(chkpath)

    def run(self):
        """Event loop which runs the daemon forever"""
        # Grace period in minutes
        graceperiod = CONFIG.get('email', 'grace',
                                 fallback=10)

        for event in self.watch.event_gen():
            if event is not None:
                self.handle(event)

    def check_all(self):
        """Alias for DaemonizedChecker.run()"""
        self.run()

    def check_file(self, path):
        f = fileinfo.FileInfo(path)
        super().check_file(f)

        self.process_checked_file(f)

    def process_checked_file(self, result):
        self.db.store_file_problems(result)

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
