# -*- coding: utf8 -*-
import os
import sys
import shutil


def getUserNames():
    if len(sys.argv) < 2:
        sys.exit("Please provide at least one user name!\n")
    return sys.argv[1:]


def debugPrint(*args, **kwargs):
    if __debug__:
        print(*args, **kwargs)


def convert2Int(string):
    return int(string.replace(',', ''))


def resetDir(path):
    debugPrint("Resetting %s ..." % path)
    shutil.rmtree(path, ignore_errors=True)
    os.makedirs(path)
