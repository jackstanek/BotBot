"""Cache file information and problems in an SQLite database"""

import os
import sqlite3

from . import fileinfo
from .problems import every_problem

def get_dbpath():
    """Get the path to the SQLite database"""
    # Hardcoding paths is kinda bad practice, I guess... RIP
    home = os.path.expanduser('~')
    dbpath = os.path.join(home , '.botbot', 'filecache.sqlite')
    return dbpath

def db_exists():
    """Check if the database already exists"""
    return os.path.isfile(get_dbpath())

class FileDatabase:
    """Database of files and associate information"""
    def __init__(self, dbpath):
        self.fi_keys = ['path', 'mode', 'uid', 'username',
                        'size', 'lastmod', 'lastcheck', 'isfile',
                        'isdir', 'important', 'problemse']

        self.conn = sqlite3.connect(dbpath)
        self.curs = self.conn.cursor()
        try:
            self.curs.execute(
                'create table files\
                (path text primary key,\
                mode integer,\
                uid integer,\
                username text,\
                size integer,\
                lastmod float,\
                lastcheck float,\
                isfile integer,\
                isdir integer,\
                important integer,\
                problems text)'  # Problems are stored in the
                                 # database# as comma-separated
                                 # problem identifier strings. yee
            )
        except sqlite3.OperationalError:
            pass

        self.conn.commit()

    def store_file_problems(self, checked):
        """Store a list of FileInfos with their problems in the database"""
        mod = list(checked)
        for fi in mod:
            try:
                problemstr = ','.join(fi['problems'])
                fi['problems'] = problemstr
            except KeyError:
                pass

        self.curs.executemany(
            'insert or replace into files values (\
            :path,\
            :mode,\
            :uid,\
            :username,\
            :size,\
            :lastmod,\
            :lastcheck,\
            :isfile,\
            :isdir,\
            :important,\
            \':problems\'\
            )',
            mod
        )

    def get_stored_problems(self, path):
        """Get a set of problems associated with a path at the last last check"""
        self.curs.execute(
            'select problems from files where path=?',
            path
        )
        probs = self.curs.fetchone()['problems'].split(',')
        return set(probs)

    def get_fileinfo(self, path):
        """Get a FileInfo object from the database for a given path"""
        self.curs.execute(
            'select {} from files where path=?'.format(','.join(self.db_keys)),
            path
        )
        return dict(zip(db_keys, self.curs.fetchone()))

    def get_cached_filelist(self, path):
        """Get a list of FileInfo dictionaries from the database"""
        self.curs.execute(
            'select * from files where path like ?',
            (path + '%',)
        )
        files = self.curs.fetchall()
        return [dict(zip(self.fi_keys, d)) for d in files]

    def get_files_by_attribute(self, attr):
        """
        Get a dictionary where keys are values of attr and values are lists
        of files with that attribute
        """
        filelist = self.get_cached_filelist('/')
        if attr != 'problems':
            attrvals = list(set([f[attr] for f in filelist]))
        else:
            attrvals = list(every_problem.keys())

        return dict(zip(attrvals, [f for f in filelist if f[attr] == attr]))


    def __del__(self):
        """Close everything before ya die"""
        self.conn.commit()
        self.conn.close()
