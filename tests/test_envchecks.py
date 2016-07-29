import os

from botbot import envchecks

def test_generic_env_checker():
    generic = envchecks._var_check_builder('DOOT',
                                           None,
                                           'PROB_DOOT')

    os.environ['DOOT'] = 'thank mr skeltal'

    assert generic(important=['thank', 'mr', 'skeltal']) is None
    assert 'PROB_DOOT' in generic(important=['forgot', 'to', 'thank'])

    del os.environ['DOOT']

def test_path_checker():
    assert envchecks.path_sufficient(important=['/usr/bin']) is None
    assert envchecks.path_sufficient(important=['/not/a/real/path']) is not None

def test_ld_checker():
    try:
        llp = os.environ['LD_LIBRARY_PATH']
        assert envchecks.ld_lib_path_sufficient(important=['lib']) is None
    except KeyError:
        assert 'PROB_VAR_NOT_SET' in envchecks.ld_lib_path_sufficient()
