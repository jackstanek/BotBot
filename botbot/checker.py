"""Base class for checking file trees"""

import stat
import os
import time

from . import fileinfo as fi
from . import report as rep
from . import ignore as ig
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
        ignore = ig.parse_ignore_rules(ig.find_ignore_file())
        to_add = [path]

        checklist = []

        while len(to_add) > 0:
            try:
                apath = fi.FileInfo(to_add.pop(), link=link)
                if apath['path'] in ignore:
                    continue # Ignore this file

                if is_link(apath['path']):
                    if not link:
                        continue
                    else:
                        to_add.append(apath['path'])
                elif apath['isdir']:
                    new = [os.path.join(apath['path'], f) for f in os.listdir(apath['path'])]
                    to_add.extend(new)

                checklist.append(apath)

            # TODO: Fix these...
            except FileNotFoundError:
                pass
            except PermissionError:
                pass
            except OSError:
                pass

        self.checklist = checklist
        self.status['files'] = len(self.checklist)

        if verbose:
            print('Located {0} files.'.format(self.status['files']))

    def update_checklist(self, cached, link=False, verbose=True):
        """
        Take a cached list of files to check and make a list of
        directories and files that need to be rechecked. A file is
        rechecked if its last check time is earlier than its last change.
        """
        if verbose:
            print('Found {} cached paths.'.format(len(cached)))

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
                        new = [
                            fi.FileInfo(p) for p in os.listdir(path)
                            if p not in (f['path'] for f in self.checked)
                        ] # Try to remove duplicates

                        recheck.extend(new)
                else:
                    self.checked.append(finfo)

            except FileNotFoundError:
                # Cached path no longer exists
                prunelist.append(finfo)

        if verbose:
            print('Pruning {} files.'.format(len(prunelist)))
        self.db.prune(prunelist)

        self.checklist = list(recheck)
        self.status['files'] = len(self.checklist)
        if verbose:
            print('Found {} paths to recheck.'.format(self.status['files']))

    def check_all(self, path, link=False, verbose=False):
        """Check the file list generated before."""
        # Start timing
        starttime = time.time()

        path = os.path.abspath(path)
        path = os.path.expanduser(path)
        self.path = path

        checklist = self.db.get_cached_filelist(path)
        if len(checklist) == 0:
            self.build_new_checklist(path)
        else:
            self.status['probcount'] = len(checklist)
            self.update_checklist(checklist)

        for finfo in self.checklist:
            if finfo['isfile']:
                self.check_file(finfo, status=verbose)
            finfo['lastcheck'] = int(time.time())

        self.db.store_file_problems(self.checked)

        self.status['time'] = time.time() - starttime
        # self.reporter.write_report('generic')
        print(self.checked)

    def check_file(self, finfo, status=True):
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

        self.checked.append(result)
        self.status['checked'] += 1

        if status:
            self.reporter.write_status(40)

def is_link(path):
    """Check if the given path is a symbolic link"""
    return os.path.islink(path) or os.path.abspath(path) != os.path.realpath(path)
