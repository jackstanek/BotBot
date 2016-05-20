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

    def write(self):
        """Generate a report and write to the stream"""
        outfile = sys.stdout
        if self.out is not None:
            outfile = open(self.out, mode='w')
        else:
            print('Report:\n')
            
        for prob in iter(problems.every_problem):
            if len(self.chkr.probs.files_with_problem(prob)) > 0:
                print(prob, file=outfile)
                for fileprobs in self.chkr.probs.files_with_problem(prob):
                    owner = pwd.getpwuid(fileprobs.fi.uid).pw_name
                    print('{}, owned by {}'.format(fileprobs.fi.abspath(), owner), file=outfile)

        if self.out is not None:
            outfile.close()
