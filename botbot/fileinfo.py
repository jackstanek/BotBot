import py

<<<<<<< HEAD
from .config import CONFIG
from .md5sum import get_file_hash

def is_important(path):
    return os.path.splitext(path)[1].strip('.') in CONFIG.get('important', 'fileinfo',
                                                              fallback='.sam, .bam')

def FileInfo(fd, link=False, important=False):
    """Hold information about a file"""
    fi = {
        'path': os.path.abspath(fd),
    }

    try:
        fi['problems'] = set()

        stats = os.stat(fd, follow_symlinks=link)
        fi['mode'] = stats.st_mode
        fi['uid'] = stats.st_uid
        fi['username'] = pwd.getpwuid(stats.st_uid).pw_name
        fi['size'] = stats.st_size
        fi['lastmod'] = int(stats.st_ctime)
        fi['lastcheck'] = 0
        fi['isfile'] = os.path.isfile(fd)
        fi['isdir'] = not os.path.isfile(fd)
        fi['md5sum'] = get_file_hash(fd) if is_important(fd) else ''
        fi['important'] = is_important(fd)


    except FileNotFoundError:
        fi['problems'].add('PROB_BROKEN_LINK')

    except PermissionError:
        fi['problems'].add('PROB_FILE_NOT_GRPRD')

    finally:
        # Do a few more cursory initial checks
        if not can_access(fi):
            fi['problems'].add('PROB_FILE_NOT_GRPRD')

        return fi

def can_access(fi):
    if fi['uid'] == os.getuid():
        return bool(fi['mode'] | 0o700)
    else:
        return bool(fi['mode'] | 0o055)
    # With those masks, we don't really to worry about the difference
    # in meaning between directory and file permission bits. Thanks,
    # based bitwise OR operator.
