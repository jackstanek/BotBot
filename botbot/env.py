"""Checker object for verifying environment variables"""

from .checker import CheckerBase
from .report import EnvReporter

class EnvironmentChecker():
    def __init__(self, outpath, *checks):
        self.checks = []
        if checks:
            self.checks = list(checks)
        self.problems = []
        self.reporter = EnvReporter(self, out=outpath)

    def register(self, *checks):
        """Add checks to this checker"""
        for chk in checks:
            if hasattr(chk, '__iter__'):
                self.checks.extend(chk)
            else:
                self.checks.append(chk)

    def check_all(self):
        for check in self.checks:
            rv = check()
            if rv:
                self.problems.append(rv)

        self.reporter.write_report()
