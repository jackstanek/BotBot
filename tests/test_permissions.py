import os
import stat

import pytest

from botbot import schecks
from botbot import fileinfo as fi

def test_group_readable_checker(tmpdir):
    # Create a test file
    p = tmpdir.join("bad_permissions.txt")
    p.write('')
    prev = tmpdir.chdir()

    # Change its permissions a bunch... maybe this is too expensive?
    for m in range(0o000, 0o700, 0o001):
        p.chmod(m)
        f = fi.FileInfo(p.basename)
        prob = schecks.file_groupreadable(f)
        if not bool(0o040 & m): # octal Unix permission for 'group readable'
            assert prob == 'PROB_FILE_NOT_GRPRD'
        else:
            assert prob is None

    prev.chdir()

def test_dir_exececutable_checker(tmpdir):
    prev = tmpdir.chdir()
    p = tmpdir.mkdir('bad_dir')


    for m in range(0o000, 0o700, 0o001):
        p.chmod(m)
        f = fi.FileInfo(p.basename)
        prob = schecks.dir_group_readable(f)
        if not bool(0o010 & m): # octal Unix permission for 'group executable'
            assert prob == 'PROB_DIR_NOT_ACCESSIBLE'
        elif not bool(0o020 & m):
            assert prob == 'PROB_DIR_NOT_WRITABLE'
        else:
            assert prob is None

def test_file_grp_exec_checker(tmpdir):
    p = tmpdir.join('bad_exec')
    p.write('')
    prev = tmpdir.chdir()

    for m in range(0o000, 0o700, 0o001):
        p.chmod(m)
        f = fi.FileInfo(p.basename)
        prob = schecks.file_group_executable(f)
        if bool(0o100 & m) and not bool(0o010 & m):
            assert prob == 'PROB_FILE_NOT_GRPEXEC'
        else:
            assert prob is None
