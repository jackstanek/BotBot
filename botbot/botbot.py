"""Main method"""
import sys

from botbot import __version__
from . import checks, schecks, checker, sqlcache
from . import ignore as ig
from . import daemon
from . import config

def config_sanity_check():
    pass # TODO: implement

def initialize_parser():
    """Create a big 'ol argument parser"""

    from argparse import ArgumentParser
    parser = ArgumentParser()

    sp = parser.add_subparsers(dest='cmd')
    sp.required = True

    fs = sp.add_parser('file', help='Check a file or directory on the fly')
    daemon = sp.add_parser('daemon', help='Launch in daemon mode')
    env = sp.add_parser('env', help='Check environment variables')


    # Oneshot file checker options
    ## Recheck options
    recheck = fs.add_mutually_exclusive_group()
    recheck.add_argument('-c', '--cached',
                        action='store_true',
                        help='Only return cached issues (no recheck)')
    recheck.add_argument('-k', '--force-recheck',
                        action='store_true',
                        help='Force a recheck of the tree')

    ## Directory options
    fs.add_argument('path',
                    help='Path to check')
    fs.add_argument('-s', '--shared',
                    help='Use the shared folder ruleset',
                    action='store_true')

    fs.add_argument('-l', '--follow-symlinks',
                    help='Follow symlinks',
                    action='store_true')
    fs.add_argument('-m', '--me',
                    help='Only check files that belong to you',
                    action='store_true')

    ## Output options
    fs.add_argument('-o', '--out',
                    help='Write report to a file instead of stdout')

    return parser


def main():
    # Right off the bat, we want to do a quick sanity check on the
    # configuration file. Basically, make sure we have all the
    # required fields, and that the
    try:
        config.config_sanity_check()
    except:
        #TODO: Implement
        pass

    # Create the argument parser
    parser = initialize_parser()

    # Initialize the checker
    args = parser.parse_args()
