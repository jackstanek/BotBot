"""Functions for checking files"""
import os
import stat
import mimetypes
import time

from .checker import is_link
from .config import CONFIG

def is_fastq(fi):
    """Check whether a given file is a fastq file."""
    path = fi['path']
    # Check the file extension.
    # ***ADVANCED TECHNOLOGY AHEAD***
    if os.path.splitext(path)[1] == ".fastq":
        if not is_link(path):
            return 'PROB_FILE_IS_FASTQ'
    # Hopefully you understood that. It _was_ pretty advanced.

def sam_should_compress(fi):
    """Check if a *.SAM file should be compressed or deleted"""
    path = fi['path']
    name, ext = os.path.splitext(path)
    # Check the extension.
    if ext == '.sam':
        # Check if there's an associated *.bam file
        if os.path.isfile('.'.join((name, 'bam'))):
            return 'PROB_SAM_AND_BAM_EXIST'
        else:
            return 'PROB_SAM_SHOULD_COMPRESS'
    elif ext == '.bam':
        # Basically, do the opposite
        if os.path.isfile('.'.join((name, 'sam'))):
            return 'PROB_SAM_AND_BAM_EXIST'

def is_large_plaintext(fi):
    """Detect if a file plaintext and >100MB"""
    # Try to figure out if we're dealing with a text file
    guess = mimetypes.guess_type(fi['path'])[0]
    if guess == 'text/plain' and is_old_and_large(fi):
        return 'PROB_OLD_LARGE_PLAINTEXT'

def is_old_and_large(fi):
    mod_days = int(time.time() - fi['lastmod'] / (24 * 60 * 60))
    # Days since last modification

    large = CONFIG.get('checks', 'largesize',
                       fallback=100000000) # Default to 100MB
    old = CONFIG.get('checks', 'oldage',
                     fallback=30) # Default to one month

    if fi['size'] > int(large) and mod_days >= int(old):
        return 'PROB_OLD_LARGE'
