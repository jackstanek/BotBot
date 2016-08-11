""
import os
import sys

from botbot import __version__
from . import sqlcache
from . import ignore as ig
from . import daemon
from .config import CONFIG, config_sanity_check, InvalidConfigurationError

def initialize_parser():
    """Create a big 'ol argument parser"""

    from argparse import ArgumentParser
    parser = ArgumentParser(prog='botbot')
    parser.add_argument('-v', '--verbose', help='Print more output',
                        action='store_true')

    sp = parser.add_subparsers(dest='cmd')

    fs = sp.add_parser('file', help='Check a file or directory on the fly')
    daemon = sp.add_parser('daemon', help='Launch in daemon mode')
    env = sp.add_parser('env', help='Check environment variable')


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
    parser.add_argument('-o', '--out',
                        help='Write report to a file instead of stdout')

    return parser

def run_file_check(args, outpath):
    # Import relevant file-checking checker code
    from . import checks, schecks, checker

    if not hasattr(args, 'path'):
        path = CONFIG.get('important', 'defaultpath',
                          fallback='~')
    else:
        path = args.path

    # Initialize the checker
    chkr = checker.OneshotChecker(outpath, sqlcache.get_dbpath())

    # Add all file checks to the checker
    all_file_checks = checks.ALLCHECKS + schecks.ALLSCHECKS
    chkr.register(*all_file_checks)

    # Set up default options
    opt = {
        'shared': args.shared if hasattr(args, 'shared') else True,
        'link': args.follow_symlinks if hasattr(args, 'follow_symlinks') else False,
        'verbose': args.verbose if hasattr(args, 'verbose') else False,
        'force': args.force if hasattr(args, 'force') else False,
        'me': args.me if hasattr(args, 'me') else False,
        'cached': args.cached if hasattr(args, 'cached') else False
    }

    # Run the checker!
    chkr.check_all(path, **opt)

def run_env_check(args, outpath):
    # Import relevant environment checks
    from . import env, envchecks

    # Initialize environment checker
    chkr = env.EnvironmentChecker(outpath)

    # Add env checks to the checker
    chkr.register(*envchecks.ALLENVCHECKS)

    # Run the checks
    chkr.check_all()


def main():
    # Right off the bat, we want to do a quick sanity check on the
    # configuration file. Basically, make sure we have all the
    # required fields, and that the
    try:
        config_sanity_check(CONFIG)

    except InvalidConfigurationError:
        #TODO: Implement
        pass

    # Create the argument parser
    parser = initialize_parser()

    # Initialize the checker
    args = parser.parse_args()

    # Determine where to write the report
    outpath = args.out if args.out else sys.stdout

    # Decide the command we're using

    cmds = (run_file_check, run_env_check)

    if args.cmd:
        if args.cmd == 'file':
            cmds = (run_file_check,)

        # Environment variable checker
        elif args.cmd == 'env':
            cmds = (run_env_check,)

    for cmd in cmds:
        cmd(args, outpath)
