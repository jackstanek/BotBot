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

    def write_dst(self, fn):
        """
        Write the output of the report generator to the correct
        destination object. eg, if we want to write to stdout, no need
        to open a file. But open the file that we want if there is a
        file.

        """
        if self.out == sys.stdout:
            fn(self.out)
        else:
            with open(self.out) as outfile:
                fn(outfile)

    @write_dst
    def write_generic_report(self, outfile):
        """Generate a standard report and write to the stream"""
        for prob in iter(problems.every_problem):
            if len(self.chkr.probs.files_with_problem(prob)) > 0:
                print('\n{}'.format(problems.every_problem[prob].message), file=outfile)
                for fileprobs in self.chkr.probs.files_with_problem(prob):
                    owner = pwd.getpwuid(fileprobs.fi.uid).pw_name

                    if fileprobs.fi.uid == os.getuid():
                        start, end = '\t\033[1;37m', '\033[0m'
                        print('{}{}{}, owned by you'.format(start, fileprobs.fi.path, end))
                    else:
                        print('{}, owned by {}'.format(os.path.abspath(fileprobs.fi.path), owner))

        outfile.close()
