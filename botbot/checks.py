"""Functions for checking files"""
import os
import stat

from .checker import is_link

def is_fastq(fi):
    """Check whether a given file is a fastq file."""
    path = fi.path
    if os.path.splitext(path)[1] == ".fastq":
        if not is_link(path):
            return 'PROB_FILE_IS_FASTQ'

def sam_should_compress(fi):
    """Check if a *.SAM file should be compressed or deleted"""
    path = fi.path
    name, ext = os.path.splitext(path)
    if ext == '.sam':
        if os.path.isfile('.'.join((name, 'bam'))):
            return 'PROB_SAM_AND_BAM_EXIST'
        else:
            return 'PROB_SAM_SHOULD_COMPRESS'
