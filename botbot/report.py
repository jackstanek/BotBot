"""Generate a report about file errors"""

import sys
import shutil
import pwd

from . import problems

class ReportWriter():
    def __init__(self, chkr, out):
        """
        pl is a ProblemList. If out is None, write to stdout. Otherwise,
        write to the file whose path is specified in out.
        """
        self.chkr = chkr
        self.out = out
        if out is sys.stdout:
            self.width = shutil.get_terminal_size().columns
        else:
            self.width = None

    def write(self):
        """Generate a report and write to the stream"""
        for prob in iter(problems.every_problem.keys()):
            print(prob)
            for fileprobs in self.chkr.probs.files_with_problem(prob):
                owner = pwd.getpwuid(fileprobs.fi.uid).pw_name
                print('{}, owned by {}'.format(fileprobs.fi.path, owner))
