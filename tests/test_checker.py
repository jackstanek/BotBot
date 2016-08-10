import os
import sys
import stat
from random import randint, choice
from string import ascii_letters

import pytest

from botbot import checker, problems, checks
from botbot import checkinfo as ci

def create_random_directory_tree(ic, directory):
    """Create a directory tree with ic files in it (files and directories)"""
    dp = directory
    files = 0
    while ic:
        name = ''.join(choice(ascii_letters) for _ in range(10))
        if not randint(0, 3): # Make a file
            dp.ensure(name)
            ic -= 1
            files += 1
        else:
            dp = dp.mkdir(name)

    return files

# Tests for Checkern class methods
def test_checker_register_accept_single_function(tmpdir):
    c = checker.OneshotChecker(sys.stdout, tmpdir.join('test.db').strpath)
    c.register(lambda: print("Hello world!"))
    assert len(c.checks) == 1

def test_checker_register_accept_function_list(tmpdir):
    c = checker.OneshotChecker(sys.stdout, tmpdir.join('test.db').strpath)

    # Function list
    f = list()
    f.append(lambda : print("Hello world!"))
    f.append(lambda i : i + i)
    c.register(*f)
    assert len(c.checks) == 2

def test_oneshotchecker_checked_file_processing(tmpdir):
    c = checker.OneshotChecker(sys.stdout, tmpdir.join('test.db').strpath)
    assert len(c.checked) == 0

    c.check_file(tmpdir.strpath)

    assert len(c.checked) == 1

def test_oneshotchecker_finds_all_files(tmpdir):
    for i in range(10, 20):
        c = checker.OneshotChecker(sys.stdout, tmpdir.join('test.db').strpath)
        tdir = tmpdir.mkdir(str(i))
        d = create_random_directory_tree(i, tdir)
        c.build_new_checklist(tdir.strpath, verbose=False)
        assert len(c.checklist) == d

# Tests for checking functions

def test_is_fastq(tmpdir):
    prev = tmpdir.chdir()
    bad = tmpdir.join('bad.fastq')
    bad.ensure()

    good = tmpdir.join('good.txt')
    good.ensure()

    crb, crg = ci.CheckResult(bad), ci.CheckResult(good)
    crb.add_problem(checks.is_fastq(bad))
    crg.add_problem(checks.is_fastq(good))

    assert crb.problems
    assert crb.problems.pop() == 'PROB_FILE_IS_FASTQ'
    assert not crg.problems

def test_sam_raw_file_detection(tmpdir):
    prev = tmpdir.chdir()
    bad = tmpdir.join('bad.sam')
    bad.ensure()

    cr = ci.CheckResult(bad)
    cr.add_problem(checks.sam_should_compress(bad))

    # Check raw file
    assert cr.problems.pop()
    prev.chdir()

def test_sam_and_bam_detection(tmpdir):
    prev = tmpdir.chdir()

    sam = tmpdir.join('bad.sam')
    sam.ensure()

    crs = ci.CheckResult(sam)

    assert checks.sam_should_compress(sam) == 'PROB_SAM_SHOULD_COMPRESS'
    crs.add_problem(checks.sam_should_compress(sam))

    bam = tmpdir.join('bad.bam')
    bam.ensure()

    assert checks.sam_should_compress(bam) == 'PROB_SAM_AND_BAM_EXIST'

    prev.chdir()
