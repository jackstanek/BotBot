import hashlib

def _reader(fo, inc=128):
    """Generator which feeds bytes to the md5 hasher"""
    while True:
        b = fo.read(inc)
        if len(b) > 0:
            yield b
        else:
            raise StopIteration()

def _hash(fo, bytecount=4096):
    """Hash a file object"""
    inc = 128
    hasher, reader = hashlib.new('md5'), _reader(fo, inc=inc)

    while bytecount:
        b = next(reader)
        hasher.update(b)
        bytecount -= inc

    digest = hasher.hexdigest()
    return digest

def get_file_hash(path, bytecount=4096):
    """Get md5 hash of a file"""
    with open(path, mode='br') as infile:
        return _hash(infile, bytecount=bytecount)
