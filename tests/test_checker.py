import os
import sys
import stat

import pytest

from botbot import checker, problems, checks, fileinfo

# Tests for Checker class methods
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

# Tests for checking functions

def test_symlink_checker_same_directory(tmpdir):
    prev = tmpdir.chdir()
    f = tmpdir.join('file.txt')
    f.write('')
    os.symlink(f.basename, 'link')
    fi = fileinfo.FileInfo('file.txt')
    lin = fileinfo.FileInfo('link')

    assert not checker.is_link(fi['path'])
    assert checker.is_link(lin['path'])
    prev.chdir()

def test_symlink_checker_link_in_lower_directory(tmpdir):
    prev = tmpdir.chdir()
    f = tmpdir.join('file.txt')
    f.write('')
    fi = fileinfo.FileInfo('file.txt')

    os.mkdir('newdir')
    os.symlink(os.path.join('..', 'file.txt'),
               os.path.join('newdir', 'link'))
    lin = fileinfo.FileInfo(os.path.join('newdir', 'link'))

    assert checker.is_link(lin['path'])
    assert not checker.is_link(fi['path'])

    prev.chdir()

def test_is_fastq(tmpdir):
    prev = tmpdir.chdir()
    bad = tmpdir.join('bad.fastq')
    bad.write('')
    b = fileinfo.FileInfo('bad.fastq')
    os.symlink(bad.basename, 'good.fastq')
    g = fileinfo.FileInfo('good.fastq')

    assert checks.is_fastq(b) == 'PROB_FILE_IS_FASTQ'
    assert checks.is_fastq(g) is None

def test_sam_raw_file_detection(tmpdir):
    prev = tmpdir.chdir()
    bad = tmpdir.join('bad.sam')
    bad.write('')
    f = fileinfo.FileInfo('bad.sam')

    # Check raw file
    assert checks.sam_should_compress(f) == 'PROB_SAM_SHOULD_COMPRESS'
    prev.chdir()

def test_sam_and_bam_detection(tmpdir):
    prev = tmpdir.chdir()

    sam = tmpdir.join('bad.sam')
    sam.write('')
    sami = fileinfo.FileInfo('bad.sam')

    assert checks.sam_should_compress(sami) == 'PROB_SAM_SHOULD_COMPRESS'

    bam = tmpdir.join('bad.bam')
    bam.write('')
    bami = fileinfo.FileInfo('bad.sam')

    assert checks.sam_should_compress(bami) is 'PROB_SAM_AND_BAM_EXIST'

    prev.chdir()

def test_is_large_plaintext_affirmative():
    fi = {
        'path': 'test.txt',
        'lastmod': 0,
        'size': 1000000000000000,
    }
    result = checks.is_large_plaintext(fi)
    assert result == 'PROB_OLD_LARGE_PLAINTEXT'

def test_is_large_plaintext_negatory():
    fi = {
        'path': 'bad.sam',
        'lastmod': 2 ** 32, # This test will work until 2038
        'size': 100
    }
    result = checks.is_large_plaintext(fi)
    assert not result
