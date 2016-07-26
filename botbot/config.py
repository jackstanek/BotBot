"""Configuration file loading"""

import os

from shutil import copy2
from pkg_resources import resource_filename

# Where we should find the configuration directory
CONFIG_DIR_PATH = os.path.expanduser('~/.botbot')
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR_PATH, 'botbot.conf')

def config_sanity_check(config):
    pass

def read_config():
    """Get the config dictionary"""
    from configparser import ConfigParser
    cfg = ConfigParser()

    if os.path.exists(CONFIG_FILE_PATH):
        cfg.read(CONFIG_FILE_PATH)

    return cfg

CONFIG = read_config()
