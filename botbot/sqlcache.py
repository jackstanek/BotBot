"""Cache file information and problems in an SQLite database"""

import os
import sqlite3

from .problems import every_problem

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
        # Dict keys that are the column names
        self.fi_keys = ['path', 'mode', 'uid', 'username',
                        'size', 'lastmod', 'lastcheck', 'isfile',
                        'isdir', 'important', 'problems']
        self.conn = sqlite3.connect(dbpath)
        self.conn.row_factory = sqlite3.Row
        self.curs = self.conn.cursor()
        try:
            # Create the file table
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
                md5sum text,\
                problems text)'  # Problems are stored in the
                                 # database# as comma-separated
                                 # problem identifier strings. yee
            )
        except sqlite3.OperationalError:
            # Table already exists, ya goof
            pass

        self.conn.commit()

    def store_file_problems(self, *checked):
        """Store a list of FileInfos with their problems in the database"""

        def serialize_problems(fi):
            """Turn a set of problems in a FileInfo dict into a string"""
            probset = fi['problems']
            if probset is not None:
                fi['problems'] = ','.join(probset)
            else:
                fi['problems'] = ''

        # Copy the list
        mod = list(checked)
        for fi in mod:
            try:
                serialize_problems(fi)
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
            :md5sum,\
            :problems\
            )',
            mod
        )
        self.conn.commit()

    def get_stored_problems(self, path):
        """Get a set of problems associated with a path at the last last check"""
        self.curs.execute(
            'select problems from files where path=?',
            path
        )
        probs = self.curs.fetchone()['problems'].split(',')
        return set(probs)

    def get_cached_filelist(self, path):
        """Get a list of FileInfo dictionaries from the database"""

        def decode_problems(fi):
            """Turn a string of problems in a fresh SQL fileinfo to a set"""
            probstr = fi['problems']
            if len(probstr) > 0:
                fi['problems'] = set(probstr.split(','))
            else:
                fi['problems'] = set()

        self.curs.execute(
            'select * from files where path like ?',
            (path + '%',)
        )
        files = [dict(r) for r in self.curs.fetchall()]
        for fi in files:
            decode_problems(fi)

        return files

    def get_files_by_attribute(self, path, attr, shared=True):
        """
        Get a dictionary where keys are values of attr and values are lists
        of files with that attribute
        """
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

    def __del__(self):
        """Close everything before ya die"""
        self.conn.commit()
        self.conn.close()
