"""Strict shared-folder permission checks"""

import stat

def file_groupreadable(fi):
    """Check whether a given path has bad permissons."""
    if not bool(stat.S_IRGRP & fi.mode):
        return 'PROB_FILE_NOT_GRPRD'

def file_group_executable(fi):
    """Check if a file should be group executable"""
    if stat.S_ISDIR(fi.mode):
        return
    if bool(stat.S_IXUSR & fi.mode) and not bool(stat.S_IXGRP & fi.mode):
        return 'PROB_FILE_NOT_GRPEXEC'

def dir_group_readable(fi):
    """Check if a directory is accessible and readable"""
    if not stat.S_ISDIR(fi.mode):
        return
    else:
        if not bool(stat.S_IXGRP & fi.mode):
            return 'PROB_DIR_NOT_ACCESSIBLE'
        elif not bool(stat.S_IWGRP & fi.mode):
            return 'PROB_DIR_NOT_WRITABLE'
