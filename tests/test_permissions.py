import os
import stat

import pytest

from botbot import schecks

def test_group_readable_checker(tmpdir):
    # Create a test file
    p = tmpdir.join("bad_permissions.txt")
    p.write('')
    prev = tmpdir.chdir()

    # Change its permissions a bunch... maybe this is too expensive?
    for m in range(0o300, 0o700, 0o010):
        p.chmod(m)
        prob = schecks.file_groupreadable(p.basename)
        if not bool(0o040 & m): # octal Unix permission for 'group readable'
            assert prob == 'PROB_FILE_NOT_GRPRD'
        else:
            assert prob is None

    prev.chdir()

def test_dir_exececutable_checker(tmpdir):
    pass

def test_file_grp_exec_checker(tmpdir):
    pass
