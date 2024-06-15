# -*- coding: utf-8 -*-
'''
svn 操作
'''
from .command import *
SVNSEP="------------------------------------------------------------------------"

class SvnLogInfo(object):
    def __init__(self):
        self.changes = []
        self.Revision = -1
        self.Author = None
        self.Message = None
        self.Time = None
        
class ChangeStatus(object):
    def __init__(self):
        self.Action = None
        self.Path = None
        self.NodeKind = None

class SvnTarget(object):
    def __init__(self):
        self.Path = None
        self.Name = None
        self.URL = None
        self.RelativeURL = None
        self.RepositoryRoot = None
        self.RepositoryUUID = None
        self.Revision = None
        self.NodeKind = None
        self.LastChangedAuthor = None
        self.LastChangedRev = None
        self.LastChangedDate = None

class SvnClient(object):
    """
    Svn客户端操作
    """
    def __init__(self, username = None, password = None):
        self.username = username
        self.password = password

    @property
    def Authorization(self):
        if self.username and self.password:
            return " --username " + self.username + " --password " + self.password
        else:
            return ""

    def CheckOut(self, url, p, **kw):
        arg = '''svn checkout {url} "{path}"'''.format(url=url, path=p.replace('\\', '/')) + self.Authorization
        cmd = Command(arg, **kw)
        if not cmd: raise Exception("Can't checkout " + url + " at " + p)

    def Diff(self, url, vFrom, vTo, **kw):
        arg = '''svn diff {url} -r {vFrom}:{vTo} --summarize'''.format(url=url, vFrom=vFrom, vTo=vTo) + self.Authorization
        if 'collectlog' in kw: raise Exception('collectlog is internal here, do not use')
        cmd = Command(arg, collectlog=True, **kw)
        if not cmd: raise Exception("Failed to Diff " + args)
        # 长度小于3（A、M、D、AM即增加且修改）即是更新标识
        results = []
        for x in cmd.Result.outputs:
            change = ChangeStatus()
            change.Action = x[0:1]
            change.Path = x[1:].lstrip(' ')
            obj = self.GetInfo(change.Path)
            change.NodeKind = obj.NodeKind
            results.append(change)
        return results
        
    def GetLog(self, url, vFrom=None, vTo=None,limit=None, quiet=True, detail=False, **kw):
        arg = '''svn log {url}'''.format(url=url) + self.Authorization
        if limit: arg += " -l {limit}".format(limit=limit)
        if quiet: arg += " -q"
        if vFrom and vTo: arg += " -r {vFrom}:{vTo}".format(vFrom=vFrom,vTo=vTo)
        elif vFrom: arg += " -r {vFrom}".format(vFrom=vFrom)
        elif vTo: arg += " -r {vTo}".format(vTo=vTo)
        if 'collectlog' in kw: raise Exception('collectlog is internal here, do not use')
        cmd = Command(arg, collectlog=True, **kw)
        if not cmd: raise Exception("Failed to get log " + args)
        param = " | ".join([str(x) for x in cmd.Result.outputs[1:-1]])
        params = param.split(" | "+self.SVNSEP+" | ")
        outlogs = []
        for x in params:
            info = x.split(' | ')
            svnLog = SvnLogInfo()
            svnLog.Revision = int(info[0][1:])
            svnLog.Author = info[1]
            svnLog.Time = info[2]
            svnLog.Message = info[4] if len(info) > 4 else None
            if detail:
                changes = self.Diff(url, svnLog.Revision-1, svnLog.Revision, **kw)
                svnLog.changes = changes
            outlogs.append(svnLog)
        return outlogs

    def GetInfo(self, uri, revision=None, **kw):
        arg = '''svn info {uri}'''.format(uri=uri) + self.Authorization
        if revision: arg += " -r {revision}".format(revision)
        if 'collectlog' in kw: raise Exception('collectlog is internal here, do not use')
        cmd = Command(arg, collectlog=True, **kw)
        if not cmd: raise Exception("Failed to get info " + uri)
        obj = SvnTarget()
        for line in cmd.Result.outputs:
            lineTrimed = line.strip()
            if not lineTrimed: continue
            line = lineTrimed.split(': ')
            value = line[1].strip()
            if line[0] == "Path": obj.Path = value
            elif line[0] == "URL": obj.URL = value
            elif line[0] == "Name": obj.Name = value
            elif line[0] == "Relative URL": obj.RelativeURL = value[2:]
            elif line[0] == "Repository Root": obj.RepositoryRoot = value
            elif line[0] == "Repository UUID": obj.RepositoryUUID = value
            elif line[0] == "Revision": obj.Revision = int(value)
            elif line[0] == "Node Kind": obj.NodeKind = value
            elif line[0] == "Last Changed Author": obj.LastChangedAuthor = value
            elif line[0] == "Last Changed Rev": obj.LastChangedRev = int(value)
            elif line[0] == "Last Changed Date": obj.LastChangedDate = value
        return obj

    def DoAction(self, args, **kw):
        arg = '''svn {args}'''.format(args=args) + self.Authorization
        cmd = Command(arg, **kw)
        return cmd


def main():
    cmd = SvnClient()
    print (cmd.GetInfo('.').Path)

if __name__ == '__main__':
    main()