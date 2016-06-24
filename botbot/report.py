"""Generate a report about file errors"""

import os
import sys
import math
from pkg_resources import resource_exists, resource_filename

from jinja2 import Environment, FileSystemLoader

from . import problems

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

    def get_template_filename(self, name):
        """Find the filename of a template. Can be a filename or just a name."""
        parts = str(name).split('.')
        if parts[len(parts) - 1] == 'txt':
            return name
        else:
            return '.'.join(parts + ['txt'])

    def write_report(self, fmt, shared, attr='problems'):
        """Write a report. This base is just a stub."""
        pass

class OneshotReporter(ReporterBase):
    """Does one-off reports after one-off checks"""
    def __init__(self, chkr, out=sys.stdout):
        super().__init__(chkr)
        self.out = out

    def write_report(self, fmt, shared, attr='problems'):
        """Write the summary of what transpired."""
        # Find the template
        tmpname = self.get_template_filename(fmt)
        tmp_respath = os.path.join('resources', 'templates')

        if resource_exists(__package__, tmp_respath):
            filelist = self.chkr.db.get_files_by_attribute(self.chkr.path, attr, shared=shared)

            # Prune unwanted listings
            filelist = prune_empty_listings(filelist, attr)
            if not shared:
                filelist = prune_shared_probs(filelist, attr)

            if should_print_report(filelist):
                env = Environment(
                    loader=FileSystemLoader(resource_filename(__package__, tmp_respath)),
                    trim_blocks=True
                )

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

def prune_shared_probs(fl, attr):
    """Remove shared problem listings"""
    shared_probs = ('PROB_DIR_NOT_WRITABLE',
                    'PROB_FILE_NOT_GRPRD',
                    'PROB_FILE_NOT_GRPEXEC',
                    'PROB_DIR_NOT_WRITABLE',
                    'PROB_DIR_NOT_ACCESSIBLE')
    pruned = dict()
    if attr == 'problems':
        for key, val in fl.items():
            if key not in shared_probs:
                pruned[key] = val
    else:
        for key, val in fl.items():
            pruned[key] = []
            for fi in val:
                sps, fips = set(shared_probs), set(fi['problems'])

                spc = len(set.intersection(sps, fips))
                if spc != len(fips):
                    pruned[key].append(fi)
    return pruned

def prune_empty_listings(fl, attr):
    """Return a new dictionary with empty listings removed"""

    new = dict()
    if attr == 'problems':
        for key, value in fl.items():
            if len(value) > 0:
                new[key] = value
    else:
        for key, val in fl.items():
            for fi in val:
                if len(fi['problems']) > 0:
                    if key in new:
                        new[key].append(fi)
                    else:
                        new[key] = [fi]

    return new

def should_print_report(filelist):
    for values in filelist.values():
        if len(values) > 0:
            return True
    return False

class DaemonReporter(ReporterBase):
    """Reports issues in daemon mode"""
    def __init__(self, chkr):
        super().__init__(chkr)

    def write_report(self):
        queue = self.chkr.checked
        while queue:
            finfo = queue.pop()
            print("{} -- {}".format(finfo['path'], ', '.join(finfo['problems'])))
