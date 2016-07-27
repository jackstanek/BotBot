import os

import pytest

from botbot import config

def test_config_is_read_automatically():
    assert config.CONFIG is not None
