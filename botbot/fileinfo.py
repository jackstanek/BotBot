"""File information"""
import os
import time
import pwd

class FileInfo():
    """Hold information about a file"""
    def __init__(self, path, link=False):
        self.path = os.path.abspath(path)

        stats = os.stat(path, follow_symlinks=link)
        self.mode = stats.st_mode
        self.uid = stats.st_uid
        self.username = pwd.getpwuid(self.uid).pw_name
        self.size = stats.st_size
        self.lastmod = int(time.time()) - stats.st_mtime # seconds since last modification

    def abspath(self):
        return os.path.abspath(self.path)
