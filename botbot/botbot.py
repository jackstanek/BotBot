"""Main method"""
import argparse
import sys

from botbot import __version__
from . import checks, schecks, checker, sqlcache
from . import ignore as ig
from .daemon import DaemonizedChecker

def main():
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
                        version='%(prog)s {}'.format(__version__))

    # Recheck options
    recheck = parser.add_mutually_exclusive_group()
    recheck.add_argument('-c', '--cached',
                        action='store_true',
                        help='Only return cached issues (no recheck)')
    recheck.add_argument('-k', '--force-recheck',
                        action='store_true',
                        help='Force a recheck of the tree')

    # Directory options
    parser.add_argument('path',
                        help='Path to check')
    parser.add_argument('-s', '--shared',
                        help='Use the shared folder ruleset',
                        action='store_true')

    parser.add_argument('-l', '--follow-symlinks',
                        help='Follow symlinks',
                        action='store_true')

    # Daemon options
    parser.add_argument('-d', '--daemon',
                        help='Run as a daemon',
                        action='store_true')

    # Initialize the checker
    args = parser.parse_args()

    # Determine if we should write to a file or to stdout. If a file
    # argument isn't given, default to stdout.
    out = None
    if args.out is not None:
        out = args.out
    else:
        out = sys.stdout

    # Give a list of checking functions to the Checker object so we
    # can go hog-wild with checks.
    c = checker.OneshotChecker(out, sqlcache.get_dbpath())
    clist = (checks.is_fastq,
             checks.sam_should_compress,
             checks.is_large_plaintext,
             schecks.file_groupreadable,
             schecks.file_group_executable,
             schecks.dir_group_readable)

    c.register(*clist)

    # Get ignore rules from ~/.botbotignore
    ignore = ig.parse_ignore_rules(ig.find_ignore_file())

    # Check the given directory
    c.check_all(args.path,
                cached=args.cached,
                force=args.force_recheck,
                shared=args.shared,
                link=args.follow_symlinks,
                verbose=args.verbose,
                fmt=args.format,
                ignore=ignore)
