import py

class FileInfo(py._path.local.LocalPath):
    def __init__(self, path=None, expanduser=False):
        super().__init__(**locals())
