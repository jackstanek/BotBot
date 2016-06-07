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
        self.checked = list() # List of FileInfos with associated problems
        self.status = {
            'files': 0,
            'time': 0
        } # Information about the previous check
        self.db = sql.FileDatabase(dbpath)
        self.reporter = rep.Reporter(self, out=outpath)

    def register(self, *funcs):
        """
        Add a new checking function to the set, or a list/tuple of
        functions.
        """
        for fn in funcs:
            self.checks.add(fn)

    def build_checklist(self, path, link=False, verbose=True):
        """
        Build a list of files to check. If link is True, follow symlinks.
        """
        ignore = ig.parse_ignore_rules(ig.find_ignore_file())
        to_add = [os.path.join(path, f) for f in os.listdir(path)]

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
                elif stat.S_ISDIR(apath['mode']):
                    new = [os.path.join(apath['path'], f) for f in os.listdir(apath['path'])]
                    to_add.extend(new)
                else:
                    self.checklist.append(apath)

            # TODO: Fix these pls...
            except FileNotFoundError:
                pass
            except PermissionError:
                pass
            except OSError:
                pass

        self.status['files'] = len(self.checklist)
        if verbose:
            print('Located {0} files.'.format(self.status['files']))

    def check_all(self, path, link=False, verbose=False):
        """Check the file list generated before."""
        self.checklist = self.db.get_cached_filelist(path)
        if len(self.checklist) == 0:
            self.build_checklist(path)

        starttime = time.time()
        for finfo in self.checklist:
            self.check_file(finfo, status=verbose)
        self.status['time'] = time.time() - starttime
        self.db.store_file_problems(self.checked)

        self.reporter.write_report('generic')

    def check_file(self, finfo, status=True):
        """
        Check a file against all checkers, write status to stdout if status
        is True
        """
        for check in self.checks:
            prob = check(finfo)
            if prob is not None:
                if finfo['problems'] is None:
                    finfo['problems'] = {prob}
                else:
                    finfo['problems'].add(prob)

        finfo['lastcheck'] = int(time.time())
        self.checked.append(finfo)

        if status:
            self.reporter.write_status(40)

def is_link(path):
    """Check if the given path is a symbolic link"""
    return os.path.islink(path) or os.path.abspath(path) != os.path.realpath(path)
