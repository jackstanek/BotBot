"""Tools for checking environment variables"""

import os
from configparser import NoOptionError

from .config import CONFIG

def _var_check_builder(var, confitem, probid):
    def _var_check_base(important=None):
        paths = important if important else CONFIG.get('important', confitem).split(':')

        for path in paths:
            try:
                if path not in os.environ[var]:
                    return (probid, path)

            except KeyError as err:
                return ('PROB_VAR_NOT_SET', err)

    return _var_check_base

"""
Checks whether all of the given paths are in the PATH environment
variable. If the variable is not set, a tuple is returned with the
error string ID and the actual exception object.
"""
path_sufficient = _var_check_builder('PATH',
                                     'pathitems',
                                     'PROB_PATH_NOT_COMPLETE')

"""
Checks whether all of the given paths are in the LD_LIBRARY_PATH
environment variable. If the variable is not set, a tuple is
returned with the error string ID and the actual exception object.
"""
ld_lib_path_sufficient = _var_check_builder('LD_LIBRARY_PATH',
                                            'ldlibitems',
                                            'PROB_LD_LIBRARY_PATH_NOT_COMPLETE')

ALLENVCHECKS = [path_sufficient, ld_lib_path_sufficient]
