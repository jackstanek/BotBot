import os
import sys
import stat
from random import randint, choice
from string import ascii_letters

import pytest

from botbot import checker, problems, checks, fileinfo

def create_random_directory_tree(ic, directory):
    """Create a directory tree with ic files in it (files and directories)"""
    dp = directory
    while ic:
        name = ''.join(choice(ascii_letters) for _ in range(10))
        if not randint(0, 3): # Make a file
            dp.ensure(name)
            ic -= 1
        else:
            dp = dp.mkdir(name)

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

    c.process_checked_file({
        "problems": {}
    })
    assert len(c.checked) == 1

def test_oneshotchecker_finds_all_files(tmpdir):
    c = checker.OneshotChecker(sys.stdout, tmpdir.join('test.db').strpath)

    for i in range(10, 20):
        tdir = tmpdir.mkdir(str(i))
        create_random_directory_tree(i, tdir)
        c.build_new_checklist(tdir.strpath, verbose=False)
        assert len(c.checklist) == i

def test_oneshot_checker_populate_list_empty_db(tmpdir):
    _TMPDIR_CT = 20
    td = tmpdir.mkdir('doot')
    create_random_directory_tree(_TMPDIR_CT, td)

    c = checker.OneshotChecker(sys.stdout, tmpdir.join('test.db').strpath)
    c.populate_checklist(td.strpath)

    assert c.checklist

def test_oneshot_checker_update_list_with_entries(tmpdir):
    _TMPDIR_CT = 20
    td = tmpdir.mkdir('doot')
    tf = td.join('test.txt').ensure()

    c = checker.OneshotChecker(sys.stdout, tmpdir.join('test.db').strpath)
    files = [fileinfo.FileInfo(tf.strpath)]
    c.db.store_file_problems(*files)

    c.update_checklist(files)

    assert c.checklist

def test_oneshot_checker_populate_list_with_non_empty_db(tmpdir):
    pass

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
