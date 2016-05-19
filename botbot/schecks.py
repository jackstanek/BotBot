"""Strict shared-folder permission checks"""

import os
import stat

def file_groupreadable(path):
    """Check whether a given path has bad permissons."""
    mode = os.stat(path).st_mode
    if not bool(stat.S_IRGRP & mode):
        return 'PROB_FILE_NOT_GRPRD'

def file_group_executable(path):
    """Check if a file should be group executable"""
    mode = os.stat(path).st_mode
    if stat.S_ISDIR(mode):
        return
    if bool(stat.S_IXUSR & mode) and not bool(stat.S_IXGRP & mode):
        return 'PROB_FILE_NOT_GRPEXEC'

def dir_group_readable(path):
    """Check if a directory is accessible and readable"""
    mode = os.stat(path).st_mode
    if not stat.S_ISDIR(mode):
        return
    else:
        if not bool(stat.S_IXGRP & mode):
            return 'PROB_DIR_NOT_ACCESSIBLE'
        elif not bool(stat.S_IWGRP & mode):
            return 'PROB_DIR_NOT_WRITABLE'
