from botbot import sqlcache

import os
from itertools import combinations
from string import ascii_letters

def get_dbpath():
    return os.path.join('.', 'test.db')

def test_FileDatabase_constructor(tmpdir):
    prev = tmpdir.chdir()

    f = sqlcache.FileDatabase(get_dbpath())
    assert f
    prev.chdir()

def test_db_finders(tmpdir):
    prev = tmpdir.chdir()

    tmp = sqlcache.get_dbpath
    sqlcache.get_dbpath = get_dbpath
    assert not sqlcache.db_exists()
    tmpdir.join(get_dbpath()).ensure(file=True)
    assert sqlcache.db_exists()
    sqlcache.get_dbpath = tmp

    prev.chdir()
