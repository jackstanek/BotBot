"""Generate a report about file errors"""

import os
import sys
import math
from pkg_resources import resource_exists, resource_filename

from jinja2 import Environment, FileSystemLoader

from . import problems

_DEFAULT_RES_PATH = os.path.join('resources', 'templates')
_GENERIC_REPORT_NAME = 'generic.txt'
_ENV_REPORT_NAME = 'env.txt'

class ReporterBase():
    def __init__(self, chkr):
        self.chkr = chkr

    def write_status(self, barlen):
        """Write where we're at"""
        done = self.chkr.status['checked']
        total = self.chkr.status['files']
        perc = done / total
        filllen = math.ceil(perc * barlen)

        print('[{0}] {1:.0%}\r'.format(filllen * '#' + (barlen - filllen) * '-', perc), end='')
        if perc == 1:
            print('\n', end='')
        sys.stdout.flush()

    def _get_template_filename(self, name):
        """Find the filename of a template. Can be a filename or just a name."""
        parts = str(name).split('.')
        if parts[len(parts) - 1] == 'txt':
            return name
        else:
            return '.'.join(parts + ['txt'])

    def _get_supporting_prob_info(self, probid):
        return problems.every_problem.get(probid)

    def _get_env(self, template):
        tmppath = os.path.join(_DEFAULT_RES_PATH,
                               self._get_template_filename(template))
        if resource_exists(__package__, tmppath):
            return Environment(
                loader=FileSystemLoader(resource_filename(__package__, _DEFAULT_RES_PATH)),
                trim_blocks=True
            )
        else:
            raise FileNotFoundError('No such template')

class OneshotReporter(ReporterBase):
    """Does one-off reports after one-off checks"""
    def __init__(self, chkr, out=sys.stdout):
        super().__init__(chkr)
        self.out = out

    def _should_print_report(self, filelist):
        for values in filelist.values():
            if values:
                return True
        return False

    def write_report(self, fmt, shared, attr='problems'):
        # print(self.chkr.checked)
        for user, probs in self.chkr.checked.items():
            if probs:
                print(user.pw_gecos)
                for prob, files in probs.items():
                    print('\t' + prob)
                    for f in files:
                        print('\t\t' + str(f))

class DaemonReporter(ReporterBase):
    """Reports issues in daemon mode"""
    def __init__(self, chkr):
        super().__init__(chkr)

    def write_report(self):
        """
        Continuously report. (Note: this implementation is temporary until
        email gets working.)
        """
        #TODO: implement emailing!

        queue = self.chkr.checked
        while queue:
            finfo = queue.pop()
            print("{} -- {}".format(finfo['path'], ', '.join(finfo['problems'])))

class EnvReporter(ReporterBase):
    """Reports environment issues"""
    def __init__(self, chkr, out=sys.stdout):
        """Constructor for the EnvReporter"""
        self.out = out
        self.chkr = chkr

    def write_report(self):
        """Write a report on environment variables"""
        env = self._get_env(_ENV_REPORT_NAME)

        if self.chkr.problems:
            tempgen = env.get_template(_ENV_REPORT_NAME).generate(
                problist=[(self._get_supporting_prob_info(p[0]), p[1])
                          for p in self.chkr.problems]
            )

            if self.out != sys.stdout:
                print('Writing report to {}.'.format(self.out))
                out = open(self.out, mode='w')
            else:
                print('Report:')
                out = sys.stdout

            for line in tempgen:
                print(line, file=out, end='')

            print('\n', file=out, end='')
            out.close()

        else:
            print('No problems here!')
