import glob
import fnmatch
import re
import os
import sys

magic = re.compile(r'[*?[]')
magic_excludes = re.compile(r'\|')
magic_includes = re.compile(r'\&')

def getExcludes(s):
    v = magic_excludes.split(s)
    if v:
        v = v[1:]
        return filter(lambda x: not not x, v)

def getIncludes(s):
    v = magic_includes.split(s)
    if v:
        v = v[1:]
        return filter(lambda x: not not x, v)

def matchMagic(s, excludes):
    for x in excludes:
        if magic.search(x) is not None and fnmatch.fnmatch(s, x):
            return True
        elif s.find(x) != -1:
            return True
    return False

def emun_folder(src, recursive=False):
    for f in os.listdir(src):
        sourceF = os.path.join(src, f)
        if os.path.isdir(sourceF):
            yield (sourceF, "folder")
            if recursive:
                for x in emun_folder(sourceF, recursive):
                    yield x
        else:
            yield (sourceF, "file")
            

def SearchFiles(dirPath, partFileInfo, excludes=None, matchfilter = None, recursive=True):
    return list(iSearchFiles(dirPath, partFileInfo, excludes=excludes, matchfilter=matchfilter, recursive=recursive))

def iSearchFiles(dirPath, partFileInfo, excludes=None, matchfilter = None, recursive=True): 
    if dirPath.find('/**/') != -1 or dirPath.find('/*/') != -1:
        vps = dirPath.split('/**/')
        for x in emun_folder(vps[0], dirPath.find('/**/') != -1):
            if x[1] == "folder":
                for p in SearchFiles(x[0]+'/'+vps[1], partFileInfo, excludes=excludes, matchfilter=matchfilter, recursive=reversed):
                    yield p.replace('\\', '/')
    else:
        pathList = glob.glob(os.path.join(dirPath, '*'))
        for mPath in pathList: 
            matched = True 
            if excludes:
                matched = matched and not matchMagic(mPath, excludes)
            if matchfilter:
                matched = matched and matchMagic(mPath, matchfilter)
            if magic.search(partFileInfo) is not None and fnmatch.fnmatch(mPath, partFileInfo) and matched:
                yield mPath.replace('\\', '/')
            elif mPath.endswith(partFileInfo) and matched:
                yield mPath.replace('\\', '/')
            elif os.path.isdir(mPath) and recursive: 
                for x in SearchFiles(mPath, partFileInfo, excludes=excludes, matchfilter=matchfilter, recursive=reversed):
                    yield x.replace('\\', '/')
            else:  
                pass  

def match(patterns):
    excludes = getExcludes(patterns)
    pattern = patterns.split('|')[0]
    dirname, basename = os.path.split(pattern)
    if basename and magic.search(basename) is not None and basename[0:2] == "**":
        recursive = True
    else:
        recursive = False
    return SearchFiles(dirname, basename, recursive=recursive, excludes=excludes)

def main():
    print (match('F:/EightWorkspace/trunk/win/client/UnityProject/Assets/**/Editor/**.cs'))

if __name__ == '__main__':
    main()