"""Main method"""
import argparse
import sys

import botbot
from . import checks, schecks, checker, config, sqlcache

def main():
    conf = config.read_config()
    parser = argparse.ArgumentParser(description="Manage lab computational resources.")

    # Verbosity and output options
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument('-v', '--verbose',
                           help='Print issues and fixes for all files',
                           action='store_true')
    parser.add_argument('-o', '--out',
                        help='Print the report to a file',
                        action='store')
    parser.add_argument('-f', '--format',
                        help='Specify the output format',
                        action='store',
                        default='generic')
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s {}'.format(botbot.__version__))

    # Directory options
    parser.add_argument('path',
                        help='Path to check')
    parser.add_argument('-s', '--shared',
                        help='Use the shared folder ruleset',
                        action='store_true')

    parser.add_argument('-l', '--follow-symlinks',
                        help='Follow symlinks',
                        action='store_true')
    # Initialize the checker
    args = parser.parse_args()

    out = None
    if args.out is not None:
        out = args.out
    else:
        out = sys.stdout

    c = checker.Checker(out, sqlcache.get_dbpath())
    clist = [checks.is_fastq,
             checks.sam_should_compress,
             checks.is_large_plaintext,
             schecks.file_groupreadable,
             schecks.file_group_executable,
             schecks.dir_group_readable]

    c.register(*clist)

    # Check the given directory
    c.check_all(args.path,
                shared=args.shared,
                link=args.follow_symlinks,
                verbose=args.verbose,
                fmt=args.format)
