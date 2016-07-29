import sys

from botbot import env, envchecks

def test_EnvironmentChecker_constructor():
    assert env.EnvironmentChecker(sys.stdout)

def test_env_check_constructor_register():
    ec = env.EnvironmentChecker(sys.stdout, envchecks.ALLENVCHECKS)
    assert ec.checks

def test_env_check_register_multiple_args():
    ec = env.EnvironmentChecker(sys.stdout)
    ec.register(*envchecks.ALLENVCHECKS)
    assert len(ec.checks) == 2

def test_env_check_single_iter_arg():
    ec = env.EnvironmentChecker(sys.stdout)
    ec.register(envchecks.ALLENVCHECKS)
    assert len(ec.checks) == 2
