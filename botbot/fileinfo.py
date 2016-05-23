"""File information"""
import os

class FileInfo():
    """Hold information about a file"""
    def __init__(self, path):
        self.path = os.path.abspath(path)

        stats = os.stat(path)
        self.mode = stats.st_mode
        self.uid = stats.st_uid

    def abspath(self):
        return os.path.abspath(self.path)
