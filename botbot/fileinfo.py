"""File information"""
import os

class FileInfo():
    """Hold information about a file"""
    def __init__(self, path):
        self.path = path
        if (os.path.isfile(path)):
            stats = os.stat(path)
            self.mode = stats.st_mode
            self.uid = stats.st_uid
