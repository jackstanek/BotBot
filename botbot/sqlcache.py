"""Cache file information and problems in an SQLite database"""

import os
import sqlite3

from . import fileinfo

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
        self.conn = sqlite3.connect(dbpath)
        self.curs = self.conn.cursor()
        if not db_exists():
            # Create the table
            self.conn.cursor().execute(
                'create table files\
                (path text,\
                mode integer,\
                uid integer,\
                username text,\
                size integer,\
                lastmod float,\
                lastcheck float,\
                isfile integer,\
                important integer,\
                problems text)'  # Problems are stored in the
                                 # database# as comma-separated
                                 # problem identifier strings. yee
                )
            self.conn.commit()

    def prune(self):
        """Prune old entries from the database"""
        pass

    def get_stored_problems(self, path):
        """Get a set of problems associated with a path at the last last check"""
        self.curs.execute(
            'select problems from files where path=?',
            path
        )
        probs = self.curs.fetchone()[0].split(',')
        return set(probs)

    def get_fileinfo(self, path):
        """Get a FileInfo object from the database for a given path"""
        db_keys = ['path', 'mode', 'uid', 'username', 'size',
                   'lastmod', 'lastcheck', 'isfile', 'important']
        self.curs.execute(
            'select {} from files where path=?'.format(','.join(db_keys)),
            path
        )
        return dict(zip(db_keys, self.curs.fetchone()))

    def get_filelist(self):
        """Get a list of FileInfo dictionaries from the database"""
        db_keys = ['path', 'mode', 'uid', 'username', 'size',
                   'lastmod', 'lastcheck', 'isfile', 'important'] # NOT ALL OF THE KEYS!
        self.curs.execute(
            'select {} from files'.join(db_keys)
        )
        return [dict(zip(db_keys), d) for d in self.curs.fetchall()]

    def get_files_by_attribute(self, key):
        self.curs.execute(
            'select ? from'
        )

    def __del__(self):
        """Close everything before ya die"""
        self.conn.commit()
        self.conn.close()
