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

    if bytecount:
        while bytecount:
            try:
                b = next(reader)
                hasher.update(b)
                bytecount -= inc

            except StopIteration:
                break

        digest = hasher.hexdigest()
        return digest

    else:
        for b in reader:
            hasher.update(b)
            return hasher.hexdigest()

def get_file_hash(path, bytecount=4096):
    """Get md5 hash of a file"""
    try:
        with path.open(mode='br') as infile:
            return _hash(infile, bytecount=bytecount)
    except PermissionError:
        return ''
