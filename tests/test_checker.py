import os
import stat

import pytest

from botbot import checker, problems, checks

# Tests for Checker class methods
def test_checker_register_accept_single_function():
    c = checker.Checker()
    c.register(lambda: print("Hello world!"))
    assert len(c.checks) == 1

def test_checker_register_accept_function_list():
    c = checker.Checker()

    # Function list
    f = list()
    f.append(lambda : print("Hello world!"))
    f.append(lambda i : i + i)
    c.register(f)

# Tests for checking functions

def test_symlink_checker_same_directory(tmpdir):
    prev = tmpdir.chdir()
    f = tmpdir.join('file.txt')
    f.write('')
    os.symlink(f.basename, 'link')

    assert not checker.is_link(f.basename)
    assert checker.is_link('link')
    prev.chdir()

def test_symlink_checker_link_in_lower_directory(tmpdir):
    prev = tmpdir.chdir()
    f = tmpdir.join('file.txt')
    f.write('')

    os.mkdir('newdir')
    os.symlink(f.basename, os.path.join('newdir', 'link'))

    assert checker.is_link(os.path.join('newdir', 'link'))
    assert not checker.is_link(f.basename)

    prev.chdir()

def test_is_fastq(tmpdir):
    prev = tmpdir.chdir()
    bad = tmpdir.join('bad.fastq')
    bad.write('')
    os.symlink(bad.basename, 'good.fastq')

    assert checks.is_fastq('bad.fastq') == 'PROB_FILE_IS_FASTQ'
    assert checks.is_fastq('good.fastq') is None

def test_sam_raw_file_detection(tmpdir):
    prev = tmpdir.chdir()
    bad = tmpdir.join('bad.sam')
    bad.write('')

    # Check raw file
    assert checks.sam_should_compress('bad.sam') == 'PROB_SAM_SHOULD_COMPRESS'
    prev.chdir()

def test_sam_and_bam_detection(tmpdir):
    prev = tmpdir.chdir()
    bam = tmpdir.join('bad.bam')
    bam.write('')
    assert checks.sam_should_compress('bad.sam') == 'PROB_SAM_AND_BAM_EXIST'

    prev.chdir()
