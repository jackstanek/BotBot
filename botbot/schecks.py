"""Strict shared-folder permission checks"""

import stat

def file_groupreadable(fi):
    """Check whether a given path has bad permissons."""
    if not bool(stat.S_IRGRP & fi['mode']):
        return 'PROB_FILE_NOT_GRPRD'

def file_group_executable(fi):
    """Check if a file should be group executable"""
    mode = fi['mode']
    if stat.S_ISDIR(mode):
        return
    if bool(stat.S_IXUSR & mode) and not bool(stat.S_IXGRP & mode):
        return 'PROB_FILE_NOT_GRPEXEC'

def dir_group_readable(fi):
    """Check if a directory is accessible and readable"""
    mode = fi['mode']
    if not stat.S_ISDIR(fi['mode']):
        return
    else:
        if not bool(stat.S_IXGRP & mode):
            return 'PROB_DIR_NOT_ACCESSIBLE'
        elif not bool(stat.S_IWGRP & mode):
            return 'PROB_DIR_NOT_WRITABLE'
