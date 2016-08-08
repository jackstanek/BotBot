"""Problems a file can have"""

from collections import namedtuple

Problem = namedtuple('Problem', ('code', 'message', 'fix'))

every_problem = {
    'PROB_DIR_NOT_WRITABLE': Problem(1,
                                     'Directory not writable',
                                     'Run \'chmod 0655\' on this directory'),

    'PROB_FILE_NOT_GRPRD': Problem(2,
                                   'File not group readable',
                                   'Run \'chmod 0644\' on this file'),

    'PROB_FILE_IS_FASTQ': Problem(3,
                                  'File is a fastq file',
                                  'Don\'t copy fastq files, instead use \'ln -s\''),

    'PROB_BROKEN_LINK': Problem(4,
                                'Symbolic link points to nonexistant file',
                                'Delete this link'),

    'PROB_SAM_SHOULD_COMPRESS': Problem(5,
                                        '*.sam files are large',
                                        'Consider compressing'),

    'PROB_SAM_AND_BAM_EXIST': Problem(6,
                                      'The *.sam file has been compressed, but it still exists',
                                      'Delete the uncompressed copy'),

    'PROB_FILE_NOT_GRPEXEC': Problem(7,
                                     'File is not group executable',
                                     'Run chmod 0755 on this file'),

    'PROB_DIR_NOT_ACCESSIBLE': Problem(8,
                                       'Directory is not accessible to the group',
                                       'Run chmod 0755 on this directory'),

    'PROB_UNKNOWN_ERROR': Problem(9,
                                  'Unknown error occurred',
                                  'Not sure what to do'),

    'PROB_OLD_LARGE_PLAINTEXT': Problem(10,
                                        'File is an old large plaintext file',
                                        'Consider compressing'),

    'PROB_PATH_NOT_COMPLETE': Problem(11,
                                      'The PATH environment variable does not contain all necessary paths',
                                      'Add the path to the PATH environment variable'),

    'PROB_LD_LIBRARY_PATH_NOT_COMPLETE': Problem(12,
                                                 'The LD_LIBRARY_PATH environment variable does not contain all necessary paths',
                                                 'Add the path the LD_LIBRARY_PATH variable'),

    'PROB_VAR_NOT_SET': Problem(13,
                                'This environment variable is not set',
                                'Try exporting an appropriate definition in your ~/.bash_profile'),
    'PROB_OLD_LARGE': Problem(14,
                              'This file is old and large',
                              'Try compressing it or moving it to secondary storage')
}
