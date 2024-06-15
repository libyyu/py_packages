# -*- coding: utf-8 -*-

__author__ = "lidengfeng"

import sys
import re
import os
import select
import env
import subprocess
from xml.etree import ElementTree
try:
    import paramiko
except ImportError:
    pass

#reload(sys)
#sys.setdefaultencoding("utf-8")
try:
    from flib import log as Log
    use_flib = True
except ImportError:
    use_flib = False

def LOG(*args):
    if use_flib:
        Log.log(*args)
    else:
        param = " ".join([str(x) for x in args])
        sys.stdout.write(param+"\n")
        sys.stdout.flush()

def LOGI(*args):
    if use_flib:
        Log.i(*args)
    else:
        param = " ".join([str(x) for x in args])
        sys.stdout.write("[info]" + param + "\n")
        sys.stdout.flush()

def LOGW(*args):
    if use_flib:
        Log.w(*args)
    else:
        param = " ".join([str(x) for x in args])
        sys.stdout.write("[warn]" + param + "\n")
        sys.stdout.flush()

def LOGE(*args):
    if use_flib:
        Log.e(*args)
    else:
        param = " ".join([str(x) for x in args])
        sys.stderr.write("[error]" + param + "\n")
        sys.stderr.flush()

def check_output(command, out=1, debug=0, tab=0, safe=1, **kw):
    """本地执行, 目标平台Linux
    """
    if debug:
        LOG("\t" if tab else "" + "Executing: %s" % command)
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, **kw)
    rlist = [p.stdout, p.stderr]
    output = ""
    while rlist:
        readable, _, _ = select.select(rlist, [], [])
        for r in readable:
            try:
                line = r.readline()
            except UnicodeDecodeError as e:
                LOGW("SSH.check_output 有一行无法解析")
                continue
            if not line:
                rlist.remove(r)
                continue
            if out or r == p.stderr:
                if r == p.stderr:
                    LOGE("\t" if tab else "" + line.strip("\n"))
                else:
                    LOG("\t" if tab else "" + line.strip("\n"))
            if r == p.stdout:
                output += line
    p.wait()
    if safe:
        if p.returncode != 0: raise Exception(p.returncode)
        return output
    else:
        return None


class SSH(object):
    def __init__(self, client):
        self.client = client

    def check_output(self, command, tab=0, debug=0, out=1, err=1, line_filter=None, **kw):
        """远程执行
        """
        if debug:
            LOG("\t" if tab else "" + "远程执行: %s" % command)
        _, std_out, std_err = self.client.exec_command(command, **kw)
        output = ""
        while True:
            try:
                line = std_out.readline()
            except UnicodeDecodeError as e:
                LOGW("SSH.check_output 有一行无法解析")
                continue
            if not line:
                break
            if line_filter and not line_filter(line):
                continue
            if out:
                LOG("\t" if tab else "" + line.strip("\n"))
            output += line
        err_put = std_err.read()
        if err_put and err:
            LOGE("\t" if tab else "" + err_put.strip("\n"))
        return output

    @classmethod
    def create(cls, address, username):
        """链接服务器
        """
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(address, username=username)
        ssh = cls(client)
        return ssh

    def open_sftp(self):
        """开启sftp隧道来传输文件
        """
        return self.client.open_sftp()

    def get_file(self, src, dst):
        self.open_sftp().get('/export/samba/'+src, dst)


def test():
    ssh = SSH.create("10.236.100.35", "game")
    ssh.check_output("cat  ")

if __name__ == "__main__":
    test()