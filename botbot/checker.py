"""Base class for checking file trees"""

import stat
import os
import time
from fnmatch import fnmatch

import py

from . import report as rep
from . import sqlcache as sql
from . import ignore as ig
from . import checkinfo as ci
from .problems import every_problem as ep

def get_username(pypath):
    from pwd import getpwuid

    st = pypath.stat()
    return getpwuid(st.uid)

class CheckerBase:
    """
    Defines a foundation for other checker objects. Allows for
    checking individual files against a list of check functions.
    """
    def __init__(self):
        self.checks = set()
        self.path = '' # Base path we're checking
        self.checked = dict() # keys: users; values: dicts with (keys:
        # problem obj; values: paths)

    def register(self, *funcs):
        """
        Add a new checking function to the set, or a list/tuple of
        functions.
        """
        for fn in funcs:
            self.checks.add(fn)

    def check_file(self, path):
        """
        Check a file against all registered checkers.
        """
        from .problems import every_problem as ep

        result = ci.CheckResult(path)
        for check in self.checks:
            result.add_problem(check(path))

        # get the username
        un = get_username(path)

        # Check if this user has any already-checked files
        if un not in self.checked.values():
            self.checked[un] = dict()

        # Otherwise, file problematic problems properly
        for prob in result.problems:
            if not self.checked.get(un).get(prob):
                self.checked[un][prob] = {path}
            else:
                self.checked.get(un).get(prob).add(path)

class OneshotChecker(CheckerBase):
    """
    Intended to run checks recursively on a given path, once. Useful
    for one-off check runs, not for daemon mode.
    """
    # checks is a set of all the checking functions this checker knows of.  All
    # checkers return a number signifying a specific problem with the
    # file specified in the path.
    def __init__(self, outpath):
        super().__init__()
        self.checks = set() # All checks to perform
        self.checklist = list() # List of FileInfos to check at some point
        self.path = None
        self.status = {
            'files': 0,
            'checked': 0,
            'time': 0,
            'probcount': 0
        } # Information about the previous check
        self.reporter = rep.OneshotReporter(self, out=outpath) # Formats and
                                                        # writes
                                                        # information

    def build_new_checklist(self, path, link=False, verbose=True, owner=None):
        """
        Build a list of files to check. If link is True, follow symlinks.
        """

        # # Try to clear out the FileInfo cache
        # self.db.clear()

        # Make the stored path object
        if isinstance(path, py.path.local):
            self.path = path
        elif isinstance(path, str):
            self.path = py.path.local(path)
        else:
            raise TypeError('Not a valid path type')

        # A stack for paths to add to the to-check-list
        to_add = [self.path.new()]

        while to_add:
            subpath = to_add.pop()

            # Ignore symlinks unless explicitly asked for
            if subpath.islink() and not link:
                continue

            # Ignore files in the ignore list
            # TODO: Reimplement

            # Check files
            if subpath.isfile():
                self.checklist.append(subpath)

            # Add directory contents to the stack
            elif subpath.isdir():
                # Do a special, but basic check here: make sure we can
                # actually access this directory.

                try:
                    try:
                        to_add.extend(subpath.listdir())

                    except py.error.Error:
                        self.checked.append(
                            ci.CheckResult(
                                subpath,
                                problems={'PROB_DIR_NOT_ACCESSIBLE'}
                            )
                        )

                except PermissionError:
                    pass

        # Update checker records
        self.status['files'] = len(self.checklist)

    def check_all(self, path, shared=False, link=False,
                  verbose=False, fmt='generic', ignore=None,
                  cached=False, force=False, me=False):
        """Pretty much do everything."""

        # Set the the UID, if necessary.
        if me:
            me = os.getuid()
        else:
            me = None

        # Start timing
        starttime = time.time()

        # Munge that path boys!
        path = os.path.expanduser(path)
        path = os.path.abspath(path)
        self.path = py.path.local(path)

        # If no cached tree exists, (or if we explicitly want to build
        # a new one) build one if we need one
        if not cached:
            # Build a checklist.
            self.build_new_checklist(path, link=link)

            # Check all the files against every check.
            while self.checklist:
                cp = self.checklist.pop()
                self.check_file(cp)

            # self.db.store_file_problems(self.checked)

        else:
            # self.checked = self.db.get_cached_results(self.path.strpath)
            pass

        # Record stats and write the report. We out!
        self.status['time'] = time.time() - starttime
        self.reporter.write_report(fmt, shared)

def is_link(path):
    """Check if the given path is a symbolic link"""
    return os.path.islink(path) or os.path.abspath(path) != os.path.realpath(path)
