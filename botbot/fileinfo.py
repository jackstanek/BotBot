"""File information"""
import os
import pwd
import hashlib

from .config import CONFIG

def _reader(fo):
    """Generator which feeds bytes to the md5 hasher"""
    while True:
        b = fo.read(4096)
        if len(b) > 0:
            yield b
        else:
            raise StopIteration()

def _hash(fo):
    """Hash a file object"""
    hasher = hashlib.new('md5')
    for b in _reader(fo):
            hasher.update(b)

    digest = hasher.hexdigest()
    return digest


def get_file_hash(path):
    """Get md5 hash of a file"""
    if os.path.isdir(path):
        return
    else:
        ext = os.path.splitext(path)[0]
        if ext == '.sam' or ext == '.bam':
            try:
                with open(path, mode='br') as infile:
                    return _hash(infile)
            except PermissionError:
                return ''
        else:
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
        'important': os.path.splitext(fd)[1].strip('.') in CONFIG.get('fileinfo', 'important',
                                                                      fallback='.sam, .bam'),
        'md5sum': get_file_hash(fd),
        'problems': set()
    }
