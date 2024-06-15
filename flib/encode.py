# -*- coding: utf-8 -*-
import sys
import chardet

def getEncoding(s):
    try:
        enc = chardet.detect(s)
        return enc
    except:
        pass

def toUnicode(s):
    if not s:
        return
    if sys.version_info < (3, 0) and isinstance(s, unicode):
        return s
    if sys.version_info >= (3, 0) and isinstance(s, str):
        return s
    try:
        enc = chardet.detect(s)['encoding']
        #print enc
        gbkmap = ['ISO-8859-2', 'iso-8859-1', 'TIS-620', 'IBM855', 'IBM866', 'windows-1252']
        if enc in gbkmap:
            enc = 'gbk'
            us = unicode(s, enc)
        # 继续往后转码
        if enc == None:
            enc = sys.getdefaultencoding()
        if sys.version_info < (3, 0):
            return unicode(s, enc, 'ignore')
        else:
            return s.decode('utf-8', 'ignore')
    except Exception as e:
        # TODO:
        print (e)
        pass

    ###
    charsets = ('gbk', 'gb18030', 'gb2312', 'iso-8859-1', 'utf-16', 'utf-8', 'utf-32', 'ascii', 'KOI8-R', 'iso-8859-2', 'iso-8859-5', 'iso-8859-7', 'iso-8859-8', 'IBM855', 'IBM866', 'windows-1252')
    for charset in charsets:
        try:
            #print charset
            if sys.version_info < (3, 0):
                return unicode(s, charset)
            else:
                return s.decode(charset)
        except:
            continue

def toUTF8(s):
    try:
        if sys.version_info < (3, 0):
            if not isinstance(s, unicode) and not isinstance(s, str) and not isinstance(s, bytes):
                return
        else:
            if not isinstance(s, str) and not isinstance(s, bytes):
                return
        if sys.version_info < (3, 0) and isinstance(s, unicode):
            return s.encode('utf-8')
        elif sys.version_info >= (3, 0) and isinstance(s, str):
            return s.encode('utf-8')
        elif sys.version_info >= (3, 0) and isinstance(s, bytes):
            return s
        enc = chardet.detect(s)['encoding']
        if enc == 'utf-8':
            return s
        else:
            s = toUnicode(s)
            if s:
                return s.encode('utf-8')
    except Exception as e:
        # TODO:
        print (e)
        return

def toGB2312(s):
    try:
        enc = getEncoding(s)
        if enc and enc['encoding'] == "utf-8":
            s = s.decode('utf-8')
    except Exception as e:
        pass
    s = toUnicode(s)
    if s:
        return s.encode('gb2312')

def toGBK(s):
    try:
        enc = getEncoding(s)
        if enc and enc['encoding'] == "utf-8":
            s = s.decode('utf-8')
    except Exception as e:
        pass
    s = toUnicode(s)
    if s:
        return s.encode('gbk')

def toANSI(s):
    try:
        enc = getEncoding(s)
        if enc and enc['encoding'] == "utf-8":
            s = s.decode('utf-8')
    except Exception as e:
        pass
    s = toUnicode(s)
    if s:
        return s.encode('ascii')

def toStr(s):
    if not s: return ""
    try:
        if sys.version_info < (3, 0):
            if not isinstance(s, unicode) and not isinstance(s, str) and not isinstance(s, bytes):
                return str(s)
        else:
            if not isinstance(s, str) and not isinstance(s, bytes):
                return str(s)
            if isinstance(s, str):
                return s
            elif isinstance(s, bytes):
                return s.decode('utf-8')
        if sys.stdout.encoding == "cp936":
            return toGBK(s)
        return toUTF8(s)
    except Exception as e:
        # TODO:
        print (e)
        return s
