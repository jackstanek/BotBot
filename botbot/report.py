"""Generate a report about file errors"""

import os
import sys
import math
from pkg_resources import resource_exists, resource_filename

from jinja2 import Environment, FileSystemLoader

from . import problems

class Reporter():
    def __init__(self, chkr, out=sys.stdout):
        self.chkr = chkr
        self.out = out

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

    def get_template_filename(self, name):
        parts = str(name).split('.')
        if parts[len(parts) - 1] == 'txt':
            return name
        else:
            return '.'.join(parts + ['txt'])

    def write_report(self, fmt, shared, attr='problems'):
        """Write the summary of what transpired."""
        def prune_shared_probs(fl):
            """Remove shared problem listings"""
            shared_probs = ('PROB_DIR_NOT_WRITABLE',
                            'PROB_FILE_NOT_GRPRD',
                            'PROB_FILE_NOT_GRPEXEC',
                            'PROB_DIR_NOT_WRITABLE',
                            'PROB_DIR_NOT_ACCESSIBLE')
            for key in fl.keys():
                if key in shared_probs:
                    fl[key] = []

        def prune_empty_listings(fl):
            """Return a new dictionary with empty listings removed"""
            new = dict()
            for key, value in fl.items():
                if len(value) > 0:
                    new[key] = value
            return new

        tmpname = self.get_template_filename(fmt)
        tmp_respath = os.path.join('resources', 'templates')
        if resource_exists(__package__, tmp_respath):
            env = Environment(
                loader=FileSystemLoader(resource_filename(__package__, tmp_respath)),
                trim_blocks=True
            )

            if self.chkr.status['probcount'] > 0:
                filelist = self.chkr.db.get_files_by_attribute(self.chkr.path, attr, shared=shared)

                # Prune
                if not shared:
                    prune_shared_probs(filelist)
                filelist = prune_empty_listings(filelist)

                tempgen = env.get_template(tmpname).generate({
                    'attr': attr,
                    'values': filelist,
                    'status': self.chkr.status
                })

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

        else:
            raise FileNotFoundError('No such report format')
