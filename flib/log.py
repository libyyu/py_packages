# -*- coding: utf-8 -*-
import sys, os
import threading
import multiprocessing

_lock = threading.Lock()
_lock2 = multiprocessing.Lock()
no_prefix = False


def __tostr__(s):
    try:
        from flib.encode import toStr
        return toStr(s)
    except:
        return str(s)

# 日志输出
def __print__(s, newLine = True, color = None):
    try:
        from flib.tools.console_util import print_with_color
        print_with_color(s, newLine=newLine, color=color)
    except:
        sys.stdout.write(s)
        if newLine: sys.stdout.write('\n')
        sys.stdout.flush()
    
    
def __log__(tag, color, *args):
    if tag and tag != "": __print__(__tostr__(tag), newLine=False, color=color)
    __index__ = 0
    for s in args:
        __index__ = __index__ + 1
        tmp = __tostr__(s)
        __print__(tmp if tmp else str(s), newLine=False, color=color)
        __print__(" " if __index__ != len(args) else "", newLine=False, color=color)
    __print__("", newLine=True, color=color)
    sys.stdout.flush()


def logWithColor(color, *args):
    _lock2.acquire()
    _lock.acquire()
    __log__("", color, *args)
    _lock.release()
    _lock2.release()
    
def log(*args):
    _lock2.acquire()
    _lock.acquire()
    __log__("", None, *args)
    _lock.release()
    _lock2.release()
    
def i(*args):
    _lock2.acquire()
    _lock.acquire()
    if no_prefix:
        __log__("", None, *args)
    else:
        __log__("[info]", None, *args)
    _lock.release()
    _lock2.release()
    
def d(*args):
    _lock2.acquire()
    _lock.acquire()
    if no_prefix:
        __log__("", "blue", *args)
    else:
        __log__("[debug]", "blue", *args)
    _lock.release()
    _lock2.release()

def w(*args):
    _lock2.acquire()
    _lock.acquire()
    if no_prefix:
        __log__("", "yellow", *args)
    else:
        __log__("[warning]", "yellow", *args)
    _lock.release()
    _lock2.release()

def e(*args):
    _lock2.acquire()
    _lock.acquire()
    if no_prefix:
        __log__("", "red", *args)
    else:
        __log__("[error]", "red", *args)
    _lock.release()
    _lock2.release()

def s(*args):
    _lock2.acquire()
    _lock.acquire()
    if no_prefix:
        __log__("", "green", *args)
    else:
        __log__("[session]", "green", *args)
    _lock.release()
    _lock2.release()

def expt(*args):
    _lock2.acquire()
    _lock.acquire()
    if no_prefix:
        __log__("", "red", *args)
    else:
        __log__("[error]", "red", *args)
    err_msg = " ".join([__tostr__(x) for x in args])
    _lock.release()
    _lock2.release()
    raise Exception(err_msg)


if __name__ == '__main__':
    i("这是一条普通日志")
    w("这是一条warning日志")
    e("这是一条error日志")
    expt("这是一条异常日志")

