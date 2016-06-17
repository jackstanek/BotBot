"""Base class for checking file trees"""

import stat
import os
import time
from fnmatch import fnmatch

from . import fileinfo as fi
from . import report as rep
from . import sqlcache as sql

class Checker:
    """
    Holds a set of checks that can be run on a file to make sure that
    it's suitable for the shared directory. Runs checks recursively on a
    given path.
    """
    # checks is a set of all the checking functions this checker knows of.  All
    # checkers return a number signifying a specific problem with the
    # file specified in the path.
    def __init__(self, outpath, dbpath):
        self.checks = set() # All checks to perform
        self.checklist = list() # List of FileInfos to check at some point
        self.checked = list()
        self.status = {
            'files': 0,
            'checked': 0,
            'time': 0,
            'probcount': 0
        } # Information about the previous check
        self.db = sql.FileDatabase(dbpath)
        self.reporter = rep.Reporter(self, out=outpath)
        self.path = ''

    def register(self, *funcs):
        """
        Add a new checking function to the set, or a list/tuple of
        functions.
        """
        for fn in funcs:
            self.checks.add(fn)

    def build_new_checklist(self, path, link=False, verbose=True):
        """
        Build a list of files to check. If link is True, follow symlinks.
        """
        to_add = [path]

        checklist = []

        while len(to_add) > 0:
            try:
                apath = fi.FileInfo(to_add.pop(), link=link)
                if apath['isdir']:
                    new = [os.path.join(apath['path'], f) for f in os.listdir(apath['path'])]
                    to_add.extend(new)
                else:
                    checklist.append(apath)

            except FileNotFoundError as err:
                apath['problems'] = {'PROB_BROKEN_LINK'}
                self.checked.append(apath)
            except PermissionError as err:
                apath['problems'] = {'PROB_DIR_NOT_ACCESSIBLE'}
                self.checked.append(apath)
            except OSError as err:
                apath['problems'] = {'PROB_BROKEN_LINK'}
                self.checked.append(apath)

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
                recent = fi.FileInfo(finfo['path'])
                if recent['lastmod'] > finfo['lastcheck']:
                    if recent['isfile']:
                        recent['problems'] = None
                        recheck.append(recent)
                    else:
                        path = recent['path']

                        # Add all the paths to recheck
                        try:
                            for f in os.listdir(path):
                                self.checklist.append(fi.FileInfo(f))
                        except PermissionError:
                            recent['problems'] = {'PROB_DIR_NOT_ACCESSIBLE'}
                            self.checked.append(recent)
                else:
                    self.checked.append(finfo)

            except FileNotFoundError:
                # Cached path no longer exists
                prunelist.append(finfo)

        self.db.prune(*prunelist)

        self.checklist = recheck
        self.status['files'] = len(self.checklist)

    def check_all(self, path, shared=False, link=False,
                  verbose=False, fmt='generic', ignore=None,
                  cached=False, force=False):
        """Pretty much do everything."""
        def remove_ignored(fi, ignore):
            """Remove files if they're in the ignore file"""
            fn = os.path.basename(fi['path'])
            for rule in ignore:
                if fnmatch(fn, rule):
                    print('Ignoring {}...'.format(fn))
                    return False
            return True

        """Check the file list generated before."""
        # Start timing
        starttime = time.time()

        # Munge that path boys!
        path = os.path.abspath(path)
        path = os.path.expanduser(path)
        self.path = path

        # Get a list of files
        checklist = self.db.get_cached_filelist(path)

        # If no cached tree exists, build one if we need one
        if not cached:
            if force or len(checklist) == 0:
                self.build_new_checklist(path)
            else:
                # Otherwise, see if we need to recheck any files
                self.status['probcount'] = len(checklist)
                self.update_checklist(checklist)

        # Remove ignored files
        self.checklist = [fi for fi in self.checklist if remove_ignored(fi, ignore)]

        if not cached:
            for finfo in self.checklist:
                if finfo['isfile']:
                    finfo['lastcheck'] = int(time.time())
                    result = self.check_file(finfo, status=verbose)
                    self.process_checked_file(result)
            self.db.store_file_problems(*self.checked)

        self.status['time'] = time.time() - starttime
        self.reporter.write_report(fmt, shared)

    def check_file(self, finfo, status=False):
        """
        Check a file against all checkers, write status to stdout if status
        is True
        """
        result = dict(finfo)
        for check in self.checks:
            prob = check(finfo)
            if prob is not None:
                if result['problems'] is None:
                    result['problems'] = {prob}
                else:
                    result['problems'].add(prob)
                    self.status['probcount'] += 1

        if status:
            self.reporter.write_status(40)

        return result

    def process_checked_file(self, result):
        self.checked.append(result)
        self.status['checked'] += 1

def is_link(path):
    """Check if the given path is a symbolic link"""
    return os.path.islink(path) or os.path.abspath(path) != os.path.realpath(path)
