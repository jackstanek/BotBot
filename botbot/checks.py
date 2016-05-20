"""Functions for checking files"""
import os
import stat

from .checker import is_link

def file_exists(path):
    try:
        with open(path, mode='r') as test:
            pass
    except FileNotFoundError:
        if is_link(path):
            return 'PROB_BROKEN_LINK'
    except OSError:
        return 'PROB_UNKNOWN_ERROR'

def is_fastq(path):
    """Check whether a given file is a fastq file."""
    if os.path.splitext(path)[1] == ".fastq":
        if not is_link(path):
            return 'PROB_FILE_IS_FASTQ'

def sam_should_compress(path):
    """Check if a *.SAM file should be compressed or deleted"""
    name, ext = os.path.splitext(path)
    if ext == '.sam':
        if os.path.isfile('.'.join((name, 'bam'))):
            return 'PROB_SAM_AND_BAM_EXIST'
        else:
            return 'PROB_SAM_SHOULD_COMPRESS'
