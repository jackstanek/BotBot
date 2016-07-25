"""Data deduplication"""

import sqlite3

from .checker import CheckerBase
from .report import ReporterBase
from . import sqlcache
from . import md5sum

def _group_by_size(fl):
    """Group FileInfos by their size"""

    # Start by sorting
    fl.sort(key=lambda f: f['size'])

    begin, end, length = 0, 1, len(fl)
    groups = []

    while end < length:
        # Get bounds of same-size files
        while fl[begin]['size'] == fl[end]['size']:
            end += 1

        # Take the slice of same-size files
        group = tuple(fl[begin:end])
        groups.append(group)

        # Advance the slicer
        begin = end
        end += 1

    return groups

class DedupeChecker():
    """Try to deduplicate data"""
    def __init__(self, dbpath):
        self.db = sqlcache.FileDatabase(dbpath)
        self.db.row_factory = sqlite3.Row
        self.reporter = DedupeReporter(self)

        self.dupes = []
        self.status = {
            'checked': 0,
            'files': 0
        }

    def heur_find_dupes(self, path, verbose=True):
        """Get a list of tuples of duplicates by heuristic"""
        dupes = []

        filelist = self.db.get_cached_filelist(path)
        self.status['files'] = len(filelist)

        filelist = _group_by_size(filelist)

        for group in filelist:
            if len(group) > 1:
                # Calculate hash of first 4KB of each file
                for item in group:
                    item['hash'] = md5sum.get_file_hash(item['path'])

                # Compare each hash
                i, j, l = 0, 0, len(group)

                while i < l:
                    while j < l:
                        if i != j and group[i]['hash'] == group[j]['hash']:
                            dupes.append((group[i], group[j]))

                        j += 1

                    i += 1

                    self.status['checked'] += 1
                    if verbose:
                        self.reporter.write_status(barlen=30)

        self.dupes = dupes

class DedupeReporter(ReporterBase):
    """Reporting of duplicates"""

    #TODO: I may expand this in the future
    pass
