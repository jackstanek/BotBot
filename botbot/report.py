"""Generate a report about file errors"""

import os
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
        self.out = out # Can be a path or sys.stdout

    def write_report_to_file(self, fmt):
        """Write a report with the specified format function"""
        if self.out == sys.stdout:
            fmt(self.out)
        else:
            with open(self.out, mode='w') as outfile:
                fmt(outfile)

    def write_generic_report(self, out):
        """Generate a standard report and write to the stream"""
        for prob in iter(problems.every_problem):
            if len(self.chkr.probs.files_with_problem(prob)) > 0:
                print('{}'.format(*problems.every_problem[prob].message), file=out)
                for fileprobs in self.chkr.probs.files_with_problem(prob):
                    owner = pwd.getpwuid(fileprobs.fi.uid).pw_name

                    if fileprobs.fi.uid == os.getuid():
                        start, end = '\t\033[1;37m', '\033[0m'
                        if out == sys.stdout:
                            print('{}{}{}, owned by you'.format(start, fileprobs.fi.path, end))
                        else:
                            print('{}, owned by you'.format(fileprobs.fi.path))
                    else:
                        print('{}, owned by {}'.format(os.path.abspath(fileprobs.fi.path), owner))

    def write_user_sorted_report(self, out):
        """Write a report that is sorted by user."""
        pass
