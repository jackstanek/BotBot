import os, stat

from . import problems, checker

def is_fastq(path):
    """Check whether a given file is a fastq file."""
    if os.path.splitext(path)[1] == ".fastq":
        if not checker.is_link(path):
            return problems.PROB_FILE_IS_FASTQ

    return problems.PROB_NO_PROBLEM

def has_permission_issues(path):
    """Check whether a given path has bad permissons."""
    mode = os.stat(path).st_mode
    if stat.S_ISDIR(mode) and not stat.S_IXGRP(mode):
        return problems.PROB_DIR_NOT_EXEC
    else:
        if not bool(stat.S_IRGRP & mode):
            return problems.PROB_FILE_NOT_GRPRD
        else:
            return problems.PROB_NO_PROBLEM
