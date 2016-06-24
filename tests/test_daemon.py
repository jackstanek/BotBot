import pytest

import os

from botbot import daemon

def test_func():
    pass


def get_dbpath():
    return os.path.join('.', 'test.db')

def test_daemon_constructor(tmpdir):
    daemon.get_dbpath = get_dbpath

    prev = tmpdir.chdir()
    d = daemon.DaemonizedChecker('.')
    assert d
    prev.chdir()

def test_daemon_init_no_handlers(tmpdir):
    daemon.get_dbpath = get_dbpath

    prev = tmpdir.chdir()

    d = daemon.DaemonizedChecker('.')
    d.init()
    assert len(d.handle_hook) == 0

    prev.chdir()

def test_daemon_init_with_handler(tmpdir):
    daemon.get_dbpath = get_dbpath

    prev = tmpdir.chdir()

    d = daemon.DaemonizedChecker('.')
    d.init((test_func, 0))
    assert len(d.handle_hook) == 1

    prev.chdir()


def test_daemon_init_with_multiple_handlers(tmpdir):
    daemon.get_dbpath = get_dbpath
    prev = tmpdir.chdir()

    d = daemon.DaemonizedChecker('.')
    d.init((test_func, 0), (test_func, 1))
    assert len(d.handle_hook) == 2

    prev.chdir()

def test_add_event_handler_default_mask(tmpdir):
    daemon.get_dbpath = get_dbpath
    prev = tmpdir.chdir()

    d = daemon.DaemonizedChecker('.')
    d.add_event_handler(test_func)

    assert d.handle_hook

    prev.chdir()

def test_add_event_handler_custom_mask(tmpdir):
    daemon.get_dbpath = get_dbpath
    prev = tmpdir.chdir()

    d = daemon.DaemonizedChecker('.')
    d.add_event_handler(test_func, 0)
    assert d.handle_hook

    prev.chdir()
