import pytest

from botbot import checker, problems

# TODO: Implement real tests!
#
# Right now this is just here as a stub so that we at least have some
# test for Travis to go through. We want complete test coverage,
# eventually.

def test_fastq_checker():
    bad = checker.is_fastq("bad.fastq")
    good = checker.is_fastq("good.py")

    assert bad == problems.PROB_FILE_IS_FASTQ
    assert good == problems.PROB_NO_PROBLEM
