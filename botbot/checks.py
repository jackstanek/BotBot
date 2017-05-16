"""Functions for checking files"""
import os
import stat
import mimetypes
import time

from .checker import is_link
from .config import CONFIG

def is_fastq(path):
    """Check whether a given file is a fastq file."""
    # Check the file extension, and make sure it's not a link.
    # ***ADVANCED TECHNOLOGY AHEAD***
    if path.ext == '.fastq':
        if not path.islink():
            return 'PROB_FILE_IS_FASTQ'
    # Hopefully you understood that. It _was_ pretty advanced.

def sam_should_compress(path):
    """Check if a *.SAM file should be compressed or deleted"""
    name, ext = path.purebasename, path.ext
    # Check the extension.
    if ext == '.sam':
        # Check if there's an associated *.bam file
        if path.new(ext='.bam').check():
            return 'PROB_SAM_AND_BAM_EXIST'
        else:
            return 'PROB_SAM_SHOULD_COMPRESS'
    elif ext == '.bam':
        # Basically, do the opposite
        if path.new(ext='.sam').check():
            return 'PROB_SAM_AND_BAM_EXIST'

def is_large_plaintext(path):
    """Detect if a file plaintext and >100MB"""
    # Try to figure out if we're dealing with a text file
    guess = mimetypes.guess_type(path.strpath)[0]
    if guess == 'text/plain' and is_old_and_large(path):
        return 'PROB_OLD_LARGE_PLAINTEXT'

def is_old_and_large(path):
    mod_days = int(time.time() - path.mtime() / (24 * 60 * 60))
    # Days since last modification

    large = CONFIG.get('checks', 'largesize',
                       fallback=100000000) # Default to 100MB
    old = CONFIG.get('checks', 'oldage',
                     fallback=30) # Default to one month

    if path.size() > int(large) and mod_days >= int(old):
        return 'PROB_OLD_LARGE'

ALLCHECKS = (is_fastq, sam_should_compress, is_large_plaintext,
             is_old_and_large)
