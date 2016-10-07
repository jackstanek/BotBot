"""Cache file information and problems in an SQLite database"""

import os
import sqlite3

from time import time

from .problems import every_problem
from .md5sum import get_file_hash
from . import checkinfo as ci

def get_dbpath():
    """Get the path to the SQLite database"""
    # Hardcoding paths is kinda bad practice, I guess... RIP
    home = os.path.expanduser('~')
    dbpath = os.path.join(home, '.botbot', 'filecache.sqlite')
    return dbpath

def db_exists():
    """Check if the database already exists"""
    return os.path.isfile(get_dbpath())

class FileDatabase:
    """Database of files and associate information"""
    def __init__(self, dbpath):
        self.conn = sqlite3.connect(dbpath)
        self.conn.row_factory = sqlite3.Row
        self.curs = self.conn.cursor()

        try:
            self._create_table()

        except sqlite3.OperationalError:
            # Table already exists, ya goof
            pass

        self.conn.commit()

    def _create_table(self):
        # Create the file table
        self.curs.execute(
            'create table files\
            (path text primary key,\
            lastcheck int,\
            md5sum text,\
            problems text)'  # Problems are stored in the
                             # database# as comma-separated
                             # problem identifier strings. yee
        )

    def store_file_problems(self, checked):
        """Store a list of check results with their problems in the database"""

        self.curs.executemany(
            'insert or replace into files values (\
            :path,\
            :lastcheck,\
            :md5sum,\
            :problems\
            )',
            [
                {'path': }
            ]
        )

        self.conn.commit()

    def get_cached_results(self, path, uid=None):
        """Get a list of FileInfo dictionaries from the database"""
        query = 'select * from files where path like ?'
        args = [path + '%']
        if uid:
            query += ' and uid = ?'
            args += [uid]

        cached = self.curs.execute(
            query,
            args
        )

        return [
            ci.CheckResult(
                **dict(res)
            )
            for res in cached
        ]

    def get_files_by_attribute(self, path, attr, shared=True):
        """
        Get a dictionary where keys are values of attr and values are lists
        of files with that attribute
        """
        # TODO: Reimplement!
        filelist = self.get_cached_filelist(path)
        if attr != 'problems':
            attrvals = list(set(f[attr] for f in filelist))
        else:
            attrvals = list(every_problem.keys())

        attrlists = []
        for val in attrvals:
            if attr == 'problems':
                attrlists.append([f for f in filelist if val in f[attr]])
            else:
                attrlists.append([f for f in filelist if f[attr] == val])

        return dict(zip(attrvals, attrlists))

    def prune(self, *old):
        """Remove db entries based on the FileInfos supplied in old"""
        for f in old:
            try:
                self.curs.execute(
                    'delete from files where path=?',
                    (f['path'],)
                )
            except TypeError:
                # Handle raw paths too
                self.curs.execute(
                    'delete from files where path=?',
                    (f,)
                )

    def clear(self):
        try:
            self.curs.execute('drop table files')
            self._create_table()

        except sqlite3.OperationalError:
            pass

    def __del__(self):
        """Close everything before ya die"""
        self.conn.commit()
        self.conn.close()
