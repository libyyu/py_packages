# -*- coding: utf-8 -*-
import os, sys
from sys import version_info

def get_path_packaged(relative_path):
    try:
        base_path = sys._MEIPASS # pyinstaller打包后的路径
    except AttributeError:
        base_path = os.path.abspath(".") # 当前工作目录的路径
    return os.path.normpath(os.path.join(base_path, relative_path)) # 返回实际路径

def open(name, mode='r', encoding='utf-8'):
    if version_info < (3, 0):
        import __builtin__
        return __builtin__.open(name, mode=mode)
    else:
        import builtins
        return builtins.open(name, mode=mode, encoding=encoding)

def import_driver(drivers, preferred=None):
    """Import the first available driver or preferred driver.
    """
    if preferred:
        drivers = [preferred]

    for d in drivers:
        try:
            return __import__(d, None, None, ['x'])
        except ImportError:
            pass
    raise ImportError("Unable to import " + " or ".join(drivers))

def import_path(paths):
    """import absolute path
    """
    for dirpath in paths:
        if os.path.isfile(dirpath):
            (dirpath, filename) = os.path.split(dirpath)
        if dirpath not in sys.path: sys.path.append(dirpath)

def import_file(file):
    """Import file with absolute path
    """
    (dirpath, filename) = os.path.split(file)
    (fname, fext) = os.path.splitext(filename)
    if dirpath not in sys.path: sys.path.append(dirpath)
    return import_driver([fname])