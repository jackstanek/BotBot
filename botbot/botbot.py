#!/usr/bin/python

import os, stat, sys
import checker

from enum import Enum

import problems

def main():
    checker_list = [checker.permission_issues]
    c = checker.Checker()
    c.register(checker_list)
    c.check_tree('.')
    c.pretty_print_issues()

if __name__ == '__main__':
    main()
