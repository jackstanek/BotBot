"""Strict shared-folder permission checks"""

import stat

def file_groupreadable(path):
    """Check whether a given path has bad permissons."""
    if not bool(stat.S_IRGRP & path.stat().mode):
        return 'PROB_FILE_NOT_GRPRD'

def file_group_executable(path):
    """Check if a file should be group executable"""
    mode = path.stat().mode
    if stat.S_ISDIR(mode):
        return
    if bool(stat.S_IXUSR & mode) and not bool(stat.S_IXGRP & mode):
        return 'PROB_FILE_NOT_GRPEXEC'

def dir_group_readable(path):
    """Check if a directory is accessible and readable"""
    mode = path.stat().mode
    if not stat.S_ISDIR(mode):
        return
    else:
        if not bool(stat.S_IXGRP & mode):
            return 'PROB_DIR_NOT_ACCESSIBLE'
        elif not bool(stat.S_IWGRP & mode):
            return 'PROB_DIR_NOT_WRITABLE'

ALLSCHECKS = (file_groupreadable, file_group_executable, dir_group_readable)
