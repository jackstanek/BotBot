from itertools import combinations
from string import ascii_lowercase

from botbot import checkinfo as ci

def test_bidirectional_problem_serialization(tmpdir):
    info = ci.CheckResult(tmpdir.strpath)
    for probs in combinations(ascii_lowercase, 3):
        info.add_problem(''.join(probs))

    old_probs = info.problems

    ps = info.serialize_problems()
    info.decode_probstr(ps)
    assert info.problems == old_probs
