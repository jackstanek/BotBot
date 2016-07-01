"""Configuration file loading"""

import os

from shutil import copy2
from pkg_resources import resource_filename

# Where we should find the configuration directory
CONFIG_DIR_PATH = os.path.expanduser('~/.botbot')
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR_PATH, 'botbot.conf')

def init_config_dir():
    """Find or create the configuration directory"""
    if not os.path.isdir(CONFIG_DIR_PATH):
        os.mkdir(CONFIG_DIR_PATH)
    if not os.path.isfile(CONFIG_FILE_PATH):
        copy2(resource_filename(__package__, 'resources/botbot.conf'), CONFIG_FILE_PATH)

def read_config():
    """Get a dictionary"""
    init_config_dir()

    from configparser import ConfigParser
    cfg = ConfigParser()
    if os.path.exists(CONFIG_FILE_PATH):
        cfg.read(CONFIG_FILE_PATH)
    return cfg

CONFIG = read_config()
