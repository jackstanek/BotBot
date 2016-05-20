"""Base class for checking file trees"""

import stat
import os
import time
import sys
import math

from . import problist as pl
from . import fileinfo as fi
from . import report as rep

class Checker:
    """
    Holds a set of checks that can be run on a file to make sure that
    it's suitable for the shared directory. Runs checks recursively on a
    given path.
    """
    # checks is a set of all the checking functions this checker knows of.  All
    # checkers return a number signifying a specific problem with the
    # file specified in the path.
    def __init__(self, out=sys.stdout):
        self.checks = set() # All checks to perform
        self.checklist = list()
        self.probs = pl.ProblemList() # List of files with their issues
        self.status = {
            'cfiles': 0,
            'files': 0,
            'problems': 0,
            'starttime': 0
        } # Information about the previous check
        self.reporter = rep.ReportWriter(self, out)

    def register(self, func):
        """
        Add a new checking function to the set, or a list/tuple of
        functions.
        """
        if hasattr(func, '__call__'):
            self.checks.add(func)
        else:
            for f in list(func):
                self.checks.add(f)

    """
    Build a list of files to check. If link is True, follow symlinks.

    """
    def build_checklist(self, path, link=False, verbose=True):
        to_add = [os.path.join(path, f) for f in os.listdir(path)]
        while len(to_add) > 0:
            try:
                apath = fi.FileInfo(to_add.pop())
                if is_link(apath.path):
                    if not link:
                        continue
                    else:
                        # Check if link is broken
                        with open(apath.path, mode='r') as exists:
                            self.checklist.append(apath)
                elif stat.S_ISDIR(os.stat(apath.path).st_mode):
                    new = [os.path.join(apath.path, f) for f in os.listdir(apath.path)]
                    to_add.extend(new)
                else:
                    self.checklist.append(apath)

            except FileNotFoundError:
                self.probs.add_problem(apath, 'PROB_BROKEN_LINK')
            except PermissionError:
                self.probs.add_problem(apath, 'PROB_DIR_NOT_WRITABLE')
            except OSError:
                self.probs.add_problem(apath, 'PROB_UNKNOWN_ERROR')

        self.status['files'] = len(self.checklist)
        if verbose:
            print('Located {0} files.'.format(self.status['files']))

    def check_all(self, path, link=False, verbose=False):
        self.build_checklist(path)
        self.status['starttime'] = time.time()
        for finfo in self.checklist:
            self.check_file(finfo, status=verbose)

        self.print_summary()

    def check_file(self, finfo, status=False):
        """
        Check a file against all checkers, write status to stdout if status
        is True
        """
        for check in self.checks:
            prob = check(finfo)
            if prob is not None:
                self.probs.add_problem(finfo, prob)
                self.status['problems'] += 1
        self.status['cfiles'] += 1
        # self.status['time'] = time.time() - self.status['starttime']

        if status:
            self.write_status(40)

    def write_status(self, barlen):
        done = self.status['cfiles']
        total = self.status['files']
        perc = done / total
        filllen = math.ceil(perc * barlen)
        
        print('[{0}] {1:.0%}\r'.format(filllen * '#' + (barlen - filllen) * '-', perc), end='')
        sys.stdout.flush()

    def print_summary(self):
        """
        Print a list of issues with their fixes. Only print issues which
        are in problist, unless verbose is true, in which case print
        all messages.
        TODO: Move into ReportWriter
        """
        # Print general statistics
        self.status['time'] = time.time() - self.status['starttime']
        infostring = "Found {problems} problems over {files} files in {time:.2f} seconds."
        print(infostring.format(**self.status))
        self.reporter.write()

def is_link(path):
    """Check if the given path is a symbolic link"""
    return os.path.islink(path) or os.path.abspath(path) != os.path.realpath(path)
