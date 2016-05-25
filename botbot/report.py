"""Generate a report about file errors"""

import os
import sys
import math
from pkg_resources import resource_exists, resource_filename

from jinja2 import Template, Environment, FileSystemLoader

class Reporter():
    def __init__(self, chkr, out=sys.stdout):
        self.chkr = chkr
        self.out = out

    def write_status(self, barlen):
        """Write where we're at"""
        done = self.chkr.status['cfiles']
        total = self.chkr.status['files']
        perc = done / total
        filllen = math.ceil(perc * barlen)

        print('[{0}] {1:.0%}\r'.format(filllen * '#' + (barlen - filllen) * '-', perc), end='')
        if perc == 1:
            print('\n', end='')
        sys.stdout.flush()

    def get_template_filename(self, name):
        parts = str(name).split('.')
        if parts[len(parts) - 1] == 'txt':
            return name
        else:
            return '.'.join(parts + ['txt'])

    def write_report(self, fmt):
        """Write the summary of what transpired."""
        tmpname = self.get_template_filename(fmt)
        if resource_exists(__package__, os.path.join('templates', tmpname)):
            env = Environment(
                loader=FileSystemLoader(resource_filename(__package__, 'templates'))
            )

            if self.chkr.probs.probcount() > 0:
                tempgen = env.get_template(tmpname).generate({
                    'probs': self.chkr.probs.files_by_problem(),
                    'probcount': self.chkr.probs.probcount(),
                    'time': self.chkr.status['time']
                })

                if self.out != sys.stdout:
                    print('Writing report to {}.'.format(self.out))
                    out = open(self.out, mode='w')
                else:
                    print('Report:')
                    out = sys.stdout

                for line in tempgen:
                    print(line, file=out, end='')

                print('', file=out)
                out.close()

            else:
                print('No problems here!')

        else:
            raise FileNotFoundError('No such report format')
