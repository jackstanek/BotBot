"""Base class for checking file trees"""

import stat
import os
import time

from . import problems

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
        self.all_problems = list() # List of files with their issues
        self.info = {
            'files': 0,
            'problems': 0,
            'time': 0
        } # Information about the previous check

    def register(self, func):
        """Add a new checking function to the set, or a list/tuple of functions."""
        if hasattr(func, '__call__'):
            self.checks.add(func)
        else:
            for f in list(func):
                self.checks.add(f)

    def check_tree(self, path):
        """
        Run all the checks on every file in the specified path,
        recursively. Returns a list of tuples. Each tuple contains 2
        elements: the first is the path of the file, and the second is
        a list of issues with the file at that path. If link is True,
        follow symlinks.

        """
        path = os.path.abspath(path)
        to_check = [path]
        extime = time.time()
        while True:
            if len(to_check) == 0:
                self.info['time'] = time.time() - extime
                return
            else:
                chk_path = to_check.pop()
                try:
                    if stat.S_ISDIR(os.stat(chk_path).st_mode):
                        for f in os.listdir(chk_path):
                            to_check.append(os.path.join(chk_path, f))
                    else:
                        self.check_file(chk_path)

                except FileNotFoundError:
                    self.all_problems.append([chk_path, [problems.PROB_BROKEN_LINK]])
                except PermissionError:
                    self.all_problems.append([chk_path, [problems.PROB_DIR_NOT_WRITABLE]])

    def check_file(self, chk_path):
        """Check a file against all checkers"""
        curr = set()
        for check in self.checks:
            curr.add(check(chk_path))

        self.all_problems.append((chk_path, curr))
        self.info['problems'] += len(curr) - 1
        self.info['files'] += 1

    def pretty_print_issues(self, verbose):
        """
        Print a list of issues with their fixes. Only print issues which
        are in problist, unless verbose is true, in which case print
        all messages.

        """
        for prob in self.all_problems:
            for mess in prob[1]:
                if verbose:
                    print(prob[0] + ": " + mess.message + " " + mess.fix)
                # else:
                #     if m != problems.PROB_NO_PROBLEM:
                #         print(p[0] + ": " + m.message + " " + m.fix)

        infostring = "Found {problems} problems over {files} files in {time:f} seconds."
        print(infostring.format(**self.info))

def is_link(path):
    """Check if the given path is a symbolic link"""
    return os.path.islink(path) or os.path.abspath(path) != os.path.realpath(path)
