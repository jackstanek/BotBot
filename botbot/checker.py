import stat, os

from . import problems, checks

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

    def check_tree(self, path, link=False):
        """
        Run all the checks on every file in the specified path,
        recursively. Returns a list of tuples. Each tuple contains 2
        elements: the first is the path of the file, and the second is
        a list of issues with the file at that path. If link is True,
        follow symlinks.

        """
        path = os.path.abspath(path)
        to_check = [path]
        while (True):
            if len(to_check) == 0:
                return
            else:
                chk_path = to_check.pop()
                try:
                    if stat.S_ISDIR(os.stat(chk_path).st_mode):
                        for f in os.listdir(chk_path):
                            to_check.append(os.path.join(chk_path, f))
                    else:
                        curr = set()
                        for check in self.checks:
                            curr.add(check(chk_path))

                        self.all_problems.append([chk_path, curr])
                except FileNotFoundError:
                    self.all_problems.append([chk_path, [problems.PROB_BROKEN_LINK]])
                except PermissionError:
                    self.all_problems.append([chk_path, [problems.PROB_DIR_NOT_WRITABLE]])

    def pretty_print_issues(self, verbose):
        """
        Print a list of issues with their fixes. Only print issues which
        are in problist, unless verbose is true, in which case print
        all messages.

        """
        for p in self.all_problems:
            for m in p[1]:
                if (verbose):
                    print(p[0] + ": " + m.message + " " + m.fix)
                else:
                    if m != problems.PROB_NO_PROBLEM:
                        print(p[0] + ": " + m.message + " " + m.fix)

def is_link(path):
    return (os.path.islink(path) and os.path.abspath(path) == os.path.realpath(path))
