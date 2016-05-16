"""Problems a file can have"""

class Problem:
    """Defines a problem that a file could have."""
    def __init__(self, code, message, fix):
        self.code = code
        self.message = message
        self.fix = fix

PROB_NO_PROBLEM          = Problem(0, 'Good.', 'Nothing to be done.')
PROB_DIR_NOT_WRITABLE    = Problem(1, 'Directory not writable.', 'Run \'chmod 0655\' on this directory.')
PROB_FILE_NOT_GRPRD      = Problem(2, 'File not group readable.', 'Run \'chmod 0644\' on this file.')
PROB_FILE_IS_FASTQ       = Problem(3, 'File is a fastq file.', 'Don\'t copy fastq files, instead use \'ln -s\'')
PROB_BROKEN_LINK         = Problem(4, 'Symbolic link points to nonexistant file.', 'Delete this link.')
PROB_SAM_SHOULD_COMPRESS = Problem(5, '*.sam files are large.', 'Consider compressing.')
PROB_SAM_AND_BAM_EXIST   = Problem(6, 'The *.sam file has been compressed, but it still exists.', 'Delete the uncompressed copy.')
