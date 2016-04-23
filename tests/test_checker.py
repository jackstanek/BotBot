import pytest
import os, stat

from botbot import checker, problems

def test_fastq_checker_path_names():
    assert checker.is_fastq("bad.fastq") == problems.PROB_FILE_IS_FASTQ
    assert checker.is_fastq("good.py") == problems.PROB_NO_PROBLEM
    assert checker.is_fastq("fastq.actually_ok_too") == problems.PROB_NO_PROBLEM

def test_fastq_checker_symlinks(tmpdir):
    prev = tmpdir.chdir()

    # Make a test file
    p = tmpdir.join("bad.fastq")
    p.write('')
    os.symlink(p.basename, "good.fastq")

    assert checker.is_fastq("bad.fastq") == problems.PROB_FILE_IS_FASTQ
    assert checker.is_fastq("good.fastq") == problems.PROB_NO_PROBLEM
    prev.chdir()

def test_permission_checker(tmpdir):
    # Create a test file
    p = tmpdir.join("bad_permissions.txt")
    p.write('')
    prev = tmpdir.chdir()

    # Change its permissions a bunch... maybe this is too expensive?
    for m in range(0o300, 0o700, 0o010):
        p.chmod(m)
        prob = checker.has_permission_issues(os.path.abspath(p.basename))
        if not bool(0o040 & m): # octal Unix permission for 'group readable'
            assert prob == problems.PROB_FILE_NOT_GRPRD
        else:
            assert prob == problems.PROB_NO_PROBLEM

    prev.chdir()
