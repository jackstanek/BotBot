"""File information"""
import os
import time
import pwd
import stat
import hashlib

from .config import CONFIG

def get_file_hash(path):
    """Get md5 hash of a file"""
    def reader(fo):
        """Generator which feeds bytes to the md5 hasher"""
        while True:
            b = fo.read(128)
            if len(b) > 0:
                yield b
            else:
                raise StopIteration()

    hasher = hashlib.new('md5')
    if os.path.isdir(path):
        return
    else:
        try:
            with open(path, mode='br') as infile:
                for b in reader(infile):
                    hasher.update(b)

            digest = hasher.hexdigest()
            return digest
        except PermissionError:
            return ''

def FileInfo(fd, link=False, important=False):
    """Hold information about a file"""
    stats = os.stat(fd, follow_symlinks=link)
    return {
        'path': os.path.abspath(fd),
        'mode': stats.st_mode,
        'uid': stats.st_uid,
        'username': pwd.getpwuid(stats.st_uid).pw_name,
        'size': stats.st_size,
        'lastmod': int(stats.st_ctime),
        'lastcheck': 0,
        'isfile': os.path.isfile(fd),
        'isdir': not os.path.isfile(fd),
        'important': os.path.splitext(fd)[1] in CONFIG.get('fileinfo', 'important'),
        'md5sum': get_file_hash(fd),
        'problems': set()
    }
