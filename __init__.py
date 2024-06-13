# -*- coding: utf-8 -*-

def get_path_packaged(relative_path):
    import os, sys
    try:
        base_path = sys._MEIPASS # pyinstaller打包后的路径
    except AttributeError:
        base_path = os.path.abspath(".") # 当前工作目录的路径
    return os.path.normpath(os.path.join(base_path, relative_path)) # 返回实际路径