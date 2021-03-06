import io
import string
import random
import subprocess
import pytest

from botbot import md5sum as md5
from botbot import checkinfo as ci

def test_hasher():
    test, result = io.BytesIO(b'hello, world!\n'), '910c8bc73110b0cd1bc5d2bcae782511'
    assert md5._hash(test) == result

def test_file_hasher(tmpdir):
    prev = tmpdir.chdir()
    testfile = tmpdir.join('test.txt')
    testfile.write('hello, world!\n')

    assert md5.get_file_hash(testfile) == '910c8bc73110b0cd1bc5d2bcae782511' # Expected
    prev.chdir()

def test_arbitrary_hash():
    """Let's try the hasher with a lot of hashes, say 75 maybe?"""
    all_ascii = string.ascii_letters + string.digits
    for i in range(100):
        inbytes = ''.join(random.choice(all_ascii) for _ in range(500)).encode()
        testhash = md5._hash(io.BytesIO(inbytes))
        echo = subprocess.Popen(('/bin/echo', '-e', '-n', inbytes), stdout=subprocess.PIPE)
        syshash = subprocess.check_output('md5sum', stdin=echo.stdout).decode().split(' ')[0] # eww
        assert syshash == testhash

def test_reader_reads_correct_number_of_bytes():
    # Test both below and above 128 bytes
    for i in range(1, 2 ** 10):
        b = io.BytesIO(('a' * i).encode())
        tb = 0
        for r in md5._reader(b):
            tb += len(r)
        assert tb == i
