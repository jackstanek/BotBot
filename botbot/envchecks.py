"""Tools for checking environment variables"""

import os
from configparser import NoOptionError

from .config import CONFIG

def path_sufficient():
    """
    Checks whether all of the given paths are in the PATH environment
    variable
    """
    paths = CONFIG.get('important', 'pathitems').split(':')
    for path in paths:
        if path not in os.environ['PATH']:
            return ('PROB_PATH_NOT_COMPLETE', path)
