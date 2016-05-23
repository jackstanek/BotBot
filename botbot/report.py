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
        self.out = out

    def write_generic_report(self):
        """Generate a standard report and write to the stream"""
        outfile = sys.stdout
        if self.out is not None:
            outfile = open(self.out, mode='w')

        for prob in iter(problems.every_problem):
            if len(self.chkr.probs.files_with_problem(prob)) > 0:
                print('\n{}'.format(problems.every_problem[prob].message), file=outfile)
                for fileprobs in self.chkr.probs.files_with_problem(prob):
                    owner = pwd.getpwuid(fileprobs.fi.uid).pw_name

                    if fileprobs.fi.uid == os.getuid():
                        start, end = '\t\033[1;37m', '\033[0m'
                        print('{}{}{}, owned by you'.format(start, fileprobs.fi.path, end))
                    else:
                        print('{}'.format(os.path.abspath(fileprobs.fi.path)))

        outfile.close()
