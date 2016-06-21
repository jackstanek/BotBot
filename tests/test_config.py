import os

import pytest

from botbot import config

def test_config_is_read_automatically():
    assert config.CONFIG is not None

def test_init_config_dir_creates_directory(tmpdir):
    prev = tmpdir.chdir()
    config.CONFIG_DIR_PATH = tmpdir.join('config').basename
    config.CONFIG_FILE_PATH = os.path.join(config.CONFIG_DIR_PATH, 'botbot.conf')
    config.init_config_dir()

    assert os.path.isdir(config.CONFIG_DIR_PATH)
    assert os.path.isfile(config.CONFIG_FILE_PATH)
    prev.chdir()

def test_init_dir_adds_config_file_if_dir_exists(tmpdir):
    prev = tmpdir.chdir()
    config.CONFIG_DIR_PATH = tmpdir.mkdir('config').basename
    config.CONFIG_FILE_PATH = os.path.join(config.CONFIG_DIR_PATH, 'botbot.conf')
    config.init_config_dir()

    assert os.path.isfile(config.CONFIG_FILE_PATH)
    prev.chdir()
