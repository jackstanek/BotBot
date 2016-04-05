import stat

from problems import *

def permission_issues(mode):
    if stat.S_ISDIR(mode) and not stat.S_IXGRP(mode):
        return PermissionProblem.DIR_NOT_EXEC
    else:
        if not bool(stat.S_IRGRP & mode):
            return PROB_FILE_NOT_GRPRD
        else:
            return PROB_NO_PROBLEM
