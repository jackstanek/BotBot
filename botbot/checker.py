import stat, os

from botbot.problems import *

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
        self.checks = set()
        self.all_problems = list()


    def register(self, fn):
        """Add a new checking function to the set, or a list/tuple of functions."""
        if isinstance(fn, list) or isinstance(fn, tuple):
            for f in fn:
                self.checks.add(f)
        else:
            self.checks.add(fn)

    def check_tree(self, path):
        """
        Run all the checks on every file in the specified path,
        recursively. Returns a list of tuples. Each tuple contains 2
        elements: the first is the path of the file, and the second is a
        list of issues with the file at that path.
        """
        self.all_problems = list()

        for f in os.listdir(path):
            newpath = os.path.join(path, f)

            if stat.S_ISDIR(np_mode):
                self.check_tree(newpath)
            else:
                current_problems = list()
                for check in self.checks:
                    current_problems.append(check(newpath))

                self.all_problems.append((newpath, current_problems))

    def pretty_print_issues(self):
        """Print a list of issues with their fixes."""
        for p in self.all_problems:
            for m in p[1]:
                print(p[0] + ": " + m.message + " " + m.fix)

def has_permission_issues(path):
    """Check whether a given path has bad permissons."""
    mode = os.stat(path).st_mode
    if stat.S_ISDIR(mode) and not stat.S_IXGRP(mode):
        return PROB_DIR_NOT_EXEC
    else:
        if not bool(stat.S_IRGRP & mode):
            return PROB_FILE_NOT_GRPRD
        else:
            return PROB_NO_PROBLEM

def is_fastq(path):
    """Check whether a given file is a fastq file."""
    if os.path.splitext(path)[1] == ".fastq":
        return PROB_FILE_IS_FASTQ
