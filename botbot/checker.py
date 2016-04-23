import stat, os

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
        self.checks = set()
        self.all_problems = list()


    def register(self, fn):
        """Add a new checking function to the set, or a list/tuple of functions."""
        if hasattr(fn, '__call__'):
            self.checks.add(fn)
        else:
            for f in list(fn):
                self.checks.add(f)

    def check_tree(self, path):
        """
        Run all the checks on every file in the specified path,
        recursively. Returns a list of tuples. Each tuple contains 2
        elements: the first is the path of the file, and the second is a
        list of issues with the file at that path.
        """
        mode = os.stat(path).st_mode

        for f in os.listdir(path):
            newpath = os.path.join(path, f)
            np_mode = os.stat(newpath).st_mode

            if stat.S_ISDIR(np_mode):
                self.check_tree(newpath)
            else:
                current_problems = set()
                for check in self.checks:
                    p = check(newpath)
                    current_problems.add(p)

                self.all_problems.append((newpath, current_problems))

        # Note: this section removes the residual dummy errors
        # from files that have other errors. It adds another O(n)
        # loop where we could have done it in that previous loop,
        # so we should probably optimize it at some point.
        for prob in self.all_problems:
            prob_set = prob[1]
            n = len(prob_set)
            if problems.PROB_NO_PROBLEM in prob[1] and n > 1:
                prob[1].remove(problems.PROB_NO_PROBLEM)


    def pretty_print_issues(self, verbose):
        """Print a list of issues with their fixes."""
        for p in self.all_problems:
            for m in p[1]:
                if (verbose):
                    print(p[0] + ": " + m.message + " " + m.fix)
                else:
                    if m != problems.PROB_NO_PROBLEM:
                        print(p[0] + ": " + m.message + " " + m.fix)

def has_permission_issues(path):
    """Check whether a given path has bad permissons."""
    mode = os.stat(path).st_mode
    if stat.S_ISDIR(mode) and not stat.S_IXGRP(mode):
        return problems.PROB_DIR_NOT_EXEC
    else:
        if not bool(stat.S_IRGRP & mode):
            return problems.PROB_FILE_NOT_GRPRD
        else:
            return problems.PROB_NO_PROBLEM

def is_fastq(path):
    """Check whether a given file is a fastq file."""
    if os.path.splitext(path)[1] == ".fastq":
        if not os.path.islink(path):
            return problems.PROB_FILE_IS_FASTQ

    return problems.PROB_NO_PROBLEM
