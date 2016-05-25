"""Functions for checking files"""
import os
import stat
import mimetypes

from .checker import is_link

def is_fastq(fi):
    """Check whether a given file is a fastq file."""
    path = fi['path']
    if os.path.splitext(path)[1] == ".fastq":
        if not is_link(path):
            return 'PROB_FILE_IS_FASTQ'

def sam_should_compress(fi):
    """Check if a *.SAM file should be compressed or deleted"""
    path = fi['path']
    name, ext = os.path.splitext(path)
    if ext == '.sam':
        if os.path.isfile('.'.join((name, 'bam'))):
            return 'PROB_SAM_AND_BAM_EXIST'
        else:
            return 'PROB_SAM_SHOULD_COMPRESS'

def is_large_plaintext(fi):
    """Detect if a file plaintext and >100MB"""
    guess = mimetypes.guess_type(fi['path'])
    mod_days = fi['lastmod'] / (24 * 60 * 60) # Days since last modification

    if guess == 'text/plain' and fi['size'] > 100000 and mod_days >= 30:
        return 'PROB_OLD_LARGE_PLAINTEXT'
