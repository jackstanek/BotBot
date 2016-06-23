"""Base class for checking file trees"""

import stat
import os
import time
from fnmatch import fnmatch

from . import fileinfo as fi
from . import report as rep
from . import sqlcache as sql
from . import ignore as ig

class CheckerBase:
    """
    Defines a foundation for other checker objects. Allows for
    checking individual files against a list of check functions.
    """
    def __init__(self, dbpath):
        self.checks = set()
        self.db = sql.FileDatabase(dbpath) # Information about
                                           # previous check, updated
                                           # after every check
        self.path = '' # Base path we're checking
        self.checked = [] # List of checked files

    def register(self, *funcs):
        """
        Add a new checking function to the set, or a list/tuple of
        functions.
        """
        for fn in funcs:
            self.checks.add(fn)

    def check_file(self, finfo):
        """
        Check a file against all checkers, write status to stdout if status
        is True
        """
        for check in self.checks:
            prob = check(finfo)
            if prob is not None:
                finfo['problems'].add(prob)

        finfo['lastcheck'] = int(time.time())

    def process_checked_file(self, result):
        """
        Helper function to record that a file was checked and to increment
        the counter.
        """
        self.checked.append(result)

class OneshotChecker(CheckerBase):
    """
    Intended to run checks recursively on a given path, once. Useful
    for one-off check runs, not for daemon mode.
    """
    # checks is a set of all the checking functions this checker knows of.  All
    # checkers return a number signifying a specific problem with the
    # file specified in the path.
    def __init__(self, outpath, dbpath):
        super().__init__(dbpath)
        self.checks = set() # All checks to perform
        self.checklist = list() # List of FileInfos to check at some point
        self.status = {
            'files': 0,
            'checked': 0,
            'time': 0,
            'probcount': 0
        } # Information about the previous check
        self.reporter = rep.OneshotReporter(self, out=outpath) # Formats and
                                                        # writes
                                                        # information

    def build_new_checklist(self, path, link=False, verbose=True):
        """
        Build a list of files to check. If link is True, follow symlinks.
        """
        self.path = path
        to_add = [path] # Acts like a stack, this does

        checklist = []

        while len(to_add) > 0:
            try:
                apath = fi.FileInfo(to_add.pop(), link=link)
                # If this path is a directory, push all files and
                # subdirectories to the stack
                if apath['isdir']:
                    new = [os.path.join(apath['path'], f) for f in os.listdir(apath['path'])]
                    to_add.extend(new)
                else:
                    # Otherwise just add that file to the checklist
                    checklist.append(apath)

            except FileNotFoundError as err:
                # This likely means that when we tried to stat the
                # file, the file was actually a dangling symlink
                apath['problems'] = {'PROB_BROKEN_LINK'}
                self.checked.append(apath)
            except PermissionError as err:
                # We couldn't read the file or directory because
                # permissions were wrong
                apath['problems'] = {'PROB_DIR_NOT_ACCESSIBLE'}
                self.checked.append(apath)
            except OSError as err:
                # Probably a dangling link again.
                apath['problems'] = {'PROB_BROKEN_LINK'}
                self.checked.append(apath)

        # Update checker records
        self.checklist = checklist
        self.status['files'] = len(self.checklist)

    def update_checklist(self, cached, link=False, verbose=True):
        """
        Take a cached list of files to check and make a list of
        directories and files that need to be rechecked. A file is
        rechecked if its last check time is earlier than its last change.
        """

        prunelist = []
        recheck = []
        for finfo in cached:
            try:
                # If the ctime of the given file is later than the
                # last check, the file needs to be rechecked.
                recent = fi.FileInfo(finfo['path'])
                if recent['lastmod'] > finfo['lastcheck']:
                    if recent['isfile']:
                        recent['problems'] = set() # We'll regenerate
                                                   # the list later.
                        recheck.append(recent)
                    else:
                        path = recent['path']

                        # Add all the paths to the recheck list
                        try:
                            for f in os.listdir(path):
                                self.checklist.append(fi.FileInfo(f))
                        except PermissionError:
                            # Probably means we can't execute this
                            # directory. (although we probably should
                            # abolish capital punishment anyway)
                            recent['problems'] = {'PROB_DIR_NOT_ACCESSIBLE'}
                            self.checked.append(recent)
                else:
                    # The file's in the same condition as its last
                    # check. Don't recheck it pls
                    self.checked.append(finfo)

            except FileNotFoundError:
                # Cached path no longer exists, prune it bb
                prunelist.append(finfo)

        self.db.prune(*prunelist)

        # Update that shizznik
        self.checklist = recheck
        self.status['files'] = len(self.checklist)

    def populate_checklist(self, force=False):
        """Populate the list of files to check"""
        # Get a list of files from last time
        checklist = self.db.get_cached_filelist(self.path)

        # Recheck if explicitly stated or if we have no cached files
        if force or len(checklist) == 0:
            self.build_new_checklist(self.path)
        else:
            # Otherwise, see if we need to recheck any files
            self.status['probcount'] = len(checklist)
            self.update_checklist(checklist)

        def remove_ignored(fi, ignore):
            """Check if a file matches a pattern from the ignore file"""
            fn = os.path.basename(fi['path'])
            # Check each file against every ignore rule. Return True
            # for matching files.
            for rule in ignore:
                if fnmatch(fn, rule):
                    print('Ignoring {}...'.format(fn))
                    return False
            return True
        # Remove ignored files and move to object
        ignore = ig.parse_ignore_rules(ig.find_ignore_file())
        self.checklist = [fi for fi in self.checklist if remove_ignored(fi, ignore)]

    def check_all(self, path, shared=False, link=False,
                  verbose=False, fmt='generic', ignore=None,
                  cached=False, force=False):
        """Pretty much do everything."""

        # Start timing
        starttime = time.time()

        # Munge that path boys!
        path = os.path.abspath(path)
        path = os.path.expanduser(path)
        self.path = path

        # If no cached tree exists, (or if we explicitly want to build
        # a new one) build one if we need one
        if not cached:
            # Build the checklist
            self.populate_checklist(force=force)

            # Check all the files against every check.
            for finfo in self.checklist:
                if finfo['isfile']:
                    self.check_file(finfo)
                    self.process_checked_file(finfo)
                    if verbose:
                        pass
            self.db.store_file_problems(*self.checked)

        # Record stats and write the report. We out!
        self.status['time'] = time.time() - starttime
        self.reporter.write_report(fmt, shared)

    def process_checked_file(self, finfo):
        super().process_checked_file(finfo)
        self.status['probcount'] += len(result['problems'])
        self.status['checked'] += 1

def is_link(path):
    """Check if the given path is a symbolic link"""
    return os.path.islink(path) or os.path.abspath(path) != os.path.realpath(path)
