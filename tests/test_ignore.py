import pytest

from botbot import ignore

def test_ignore_file_finder(tmpdir):
    prev = tmpdir.chdir()
    f = ignore.find_ignore_file('.')

    assert f is None

    igf = tmpdir.join('.botbotignore').write('')

    f = ignore.find_ignore_file('.')

    assert f is not None

    prev.chdir()

def test_comment_stripper_when_comment_at_start_of_line():
    for i in range(1, 3):
        string = '#' + 'a' * i
        assert len(ignore.strip_comments(string)) == 0

def test_comment_stripper_removes_comment_at_end_of_line():
    string = 'random text # <- thats really random xD'
    assert ignore.strip_comments(string) == 'random text'

def test_ignore_rules_parser_one_rule(tmpdir):
    prev = tmpdir.chdir()

    igf = tmpdir.join('ignore.txt')
    igf.write('*.txt # ignore text files') # Sample ignore rule

    igr = ignore.parse_ignore_rules(igf.basename)

    assert igr[0] == '*.txt'

    prev.chdir()

def test_ignore_rules_parser_one_rule(tmpdir):
    prev = tmpdir.chdir()

    igf = tmpdir.join('ignore.txt')
    igf.write('*.txt # ignore text files\n*.sam') # Sample ignore rule

    igr = ignore.parse_ignore_rules(igf.basename)

    assert '*.txt' in igr
    assert '*.sam' in igr

    prev.chdir()
