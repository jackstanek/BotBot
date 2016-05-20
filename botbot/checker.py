"""Base class for checking file trees"""

import stat
import os
import time
import sys

from botbot import problist as pl

class Checker:
    """
    Holds a set of checks that can be run on a file to make sure that
    it's suitable for the shared directory. Runs checks recursively on a
    given path.
    """
    # checks is a set of all the checking functions this checker knows of.  All
    # checkers return a number signifying a specific problem with the
    # file specified in the path.
    def __init__(self):
        self.checks = set() # All checks to perform
        self.probs = pl.ProblemList() # List of files with their issues
        self.info = {
            'files': 0,
            'problems': 0,
            'time': 0
        } # Information about the previous check

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

    def check_tree(self, path, link=False, verbose=True):
        """
        Run all the checks on every file in the specified path,
        recursively. Returns a list of tuples. Each tuple contains 2
        elements: the first is the path of the file, and the second is
        a list of issues with the file at that path. If link is True,
        follow symlinks.
        """
        path = os.path.abspath(path)
        start = path # Currently unused, could be used to judge depth
        to_check = [path]
        extime = time.time()

        while len(to_check) > 0:
            chk_path = to_check.pop()
            try:
                if not link and is_link(chk_path):
                    continue
                elif stat.S_ISDIR(os.stat(chk_path).st_mode):
                    new = [os.path.join(chk_path, f) for f in os.listdir(chk_path)]
                    to_check.extend(new)
                else:
                    self.check_file(chk_path)

                self.info['time'] = time.time() - extime

            except FileNotFoundError:
                self.probs.add_problem(chk_path, 'PROB_BROKEN_LINK')
            except PermissionError:
                self.probs.add_problem(chk_path, 'PROB_DIR_NOT_WRITABLE')

            if verbose:
                self.write_status()

    def check_file(self, chk_path):
        """Check a file against all checkers"""
        for check in self.checks:
            prob = check(chk_path)
            if prob is not None:
                self.probs.add_problem(chk_path, prob)
                self.info['problems'] += 1

        self.info['files'] += 1

    def write_status(self):
        infostring = "Found {problems} problems over {files} files in {time:.2f} seconds.\r"
        print(infostring.format(**self.info), end='')
        sys.stdout.flush()

    def pretty_print_issues(self, verbose):
        """
        Print a list of issues with their fixes. Only print issues which
        are in problist, unless verbose is true, in which case print
        all messages.
        TODO: Move into ReportWriter
        """
        # Print general statistics
        infostring = "Found {problems} problems over {files} files in {time:.2f} seconds."
        print(infostring.format(**self.info))

def is_link(path):
    """Check if the given path is a symbolic link"""
    return os.path.islink(path) or os.path.abspath(path) != os.path.realpath(path)
