"""File information"""
import os
import pwd

from .config import CONFIG

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
        'problems': set()
    }
