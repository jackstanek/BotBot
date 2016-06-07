"""File information"""
import os
import time
import pwd
import stat

def FileInfo(fd, link=False, important=False):
    """Hold information about a file"""
    stats = os.stat(fd, follow_symlinks=link)
    return {
        'path': os.path.abspath(fd),
        'mode': stats.st_mode,
        'uid': stats.st_uid,
        'username': pwd.getpwuid(stats.st_uid).pw_name,
        'size': stats.st_size,
        'lastmod': stats.st_mtime,
        'lastcheck': 0,
        'isfile': os.path.isfile(fd),
        'isdir': not os.path.isfile(fd),
        'important': important,
        'lastmod': int(time.time()) - stats.st_mtime # seconds since last modification
    }
