"""Generate a report about file errors"""

import sys
import math
import pkg_resources as pkgr

from jinja2 import Template, Environment, FileSystemLoader

class Reporter():
    def __init__(self, chkr, template, out=sys.stdout):
        self.chkr = chkr
        self.template = template
        self.out = out

    def write_status(self, barlen):
        """Write where we're at"""
        done = self.chkr.status['cfiles']
        total = self.chkr.status['files']
        perc = done / total
        filllen = math.ceil(perc * barlen)

        print('[{0}] {1:.0%}\r'.format(filllen * '#' + (barlen - filllen) * '-', perc), end='')
        sys.stdout.flush()

    def write_report(self):
        """Write the summary of what transpired."""
        # Jinja2, hoo-whee!
        pass
