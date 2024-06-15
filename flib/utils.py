# -*- coding: utf-8 -*-
'''
#----------------------------------------------------------------------------------------
# 功能：python工具库
#----------------------------------------------------------------------------------------
'''
import contextlib
import os
import platform
import select
import shlex
import socket
import subprocess
import multiprocessing
import sys
import threading
import time
from functools import wraps

try:
	from flib import log as Log
	from flib.encode import toStr
	use_flib = True
except ImportError:
	use_flib = False

def LOG(*args):
	if use_flib:
		Log.log(*args)
	else:
		param = " ".join([str(x) for x in args])
		sys.stdout.write(param + "\n")
		sys.stdout.flush()

def LOG(*args):
	if use_flib:
		Log.log(*args)
	else:
		param = " ".join([str(x) for x in args])
		sys.stdout.write(param + "\n")
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
  
def LOGFATAL(*args):
	if use_flib:
		Log.expt(*args)
	else:
		param = " ".join([str(x) for x in args])
		sys.stderr.write("[exception]" + param + "\n")
		sys.stderr.flush()
		raise Exception(param)


def singleton(cls):
    """
    单例
    使用装饰器(decorator),
    这是一种更pythonic,更elegant的方法,
    单例类本身根本不知道自己是单例的,因为他本身(自己的代码)并不是单例的
    """
    instances = {}
    @wraps(cls)
    def _singleton(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton

def SetReadOnly(filename, readonly = False):
    """
    设置是否只读属性
    """
    if not os.path.isfile(filename):
        os.system('attrib -r ' + filename + '//*.* /s')
        return
    import stat
    os.chmod(filename, stat.S_IWRITE) if not readonly else os.chmod(filename, ~stat.S_IWRITE)

class dict_to_object(dict):
    """docstring for dict_to_object"""
    def __getattr__(self, key):
        try:
            return self[key]
        except :
            return ''
        pass

    def __setattr__(self, key, value):
        self[key] = value
        pass

# 环境变量
def getenv(key, default=None):
    return os.environ[key] if key in os.environ else default
def setenv(key, v):
    os.environ[key] = v

# 全局唯一uuid
def newuuid():
    import uuid
    return uuid.uuid1()

#quit
def quit(func):
    def quit_call(*arg, **kw):
        result = func(*arg, **kw)
        if not result:
            exit(-1)
        return result
    return quit_call

# netcat 服务器
class nc_server(threading.Thread):
    """netcat for nc_server"""
    class nc_client(threading.Thread):
        def __init__(self, client_socket, server):
            super(nc_server.nc_client, self).__init__()
            self.socket = client_socket
            self.server = server
            self.lock = threading.Lock()
            self.stopped = False
        def __del__(self):
            self.stop()
        def stop(self):
            try:
                self.lock.acquire()
                self.stopped = True
                self.lock.release()
                self.socket.close()
            except:
                pass
        def run(self):
            while True:
                try:
                    self.lock.acquire()
                    if self.stopped:
                        break
                    data = self.socket.recv(1024)
                    recv_len = len(data)
                    if recv_len == 0:
                        __print__("")
                        break
                    tmp = toStr(data) or data
                    color = None
                    if tmp and tmp.startswith("[error]"):
                        color = "red"
                    # elif tmp and tmp.startswith("[warning]"):
                    #     color = "yellow"
                    __print__(tmp.strip('\r\n').strip('\n'), newLine=True if recv_len < 1024 else False, color=color)
                except:
                    time.sleep(0.01)
                    pass
                finally:
                    self.lock.release()
            Log.i("client_handler finished")

    def __init__(self, host="0.0.0.0", port=0):
        super(nc_server, self).__init__()
        self.stopped = False
        self.clients = []
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(0)
        self.server.setblocking(0)
        self.lock = threading.Lock()
        Log.i("start nc server [{0}:{1}]!".format(host, self.get_port()))

    def get_port(self):
        a = self.server.getsockname()
        self.port = a[1]
        return self.port

    def get_ip(self):
        a = self.server.getsockname()
        self.host = a[0]
        return self.host

    def stop(self):
        self.lock.acquire()
        self.stopped = True
        self.lock.release()
        Log.i("stop netcat.")

    def isStoped(self):
        self.lock.acquire()
        try:
            return self.stopped
        finally:
            self.lock.release()

    def run(self):
        while True:
            try:
                self.lock.acquire()
                if self.stopped:
                    break
                client_socket, addr = self.server.accept()
                client_socket.setblocking(0)
                Log.i("accept client:{0}".format(addr))
                client_thread = nc_server.nc_client(client_socket, self) #threading.Thread(target=nc_server.client_handler, args=(client_socket, self))
                client_thread.start()
                self.clients.append(client_thread)
            except Exception as e:
                time.sleep(0.01)
                pass
            finally:
                self.lock.release()

        self.server.close()
        for subthread in self.clients:
            subthread.stop()

@singleton
class dir_op:
    """
    目录操作,更改目录操作，
    离开当前作用域后，自动还原到以前路径
    """
    old_dir = os.getcwd()
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.old_dir is not None:
            Log.log("Leave Directory:", os.getcwd())
            os.chdir(self.old_dir)
            self.old_dir = os.getcwd()
    @classmethod
    def Enter(cls, _dir):
        old_dir = os.getcwd()
        os.chdir(_dir)
        Log.log("Enter Directory:", _dir)
        return cls()
    @property
    def curdir(self):
        return os.getcwd()

class guard_op:
    """
    安全锁操作
    """
    def __init__(self, lock):
        self._lock = lock
    def __enter__(self):
        self.Lock()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.UnLock()
    def Lock(self):
        if not self._lock:
            return
        if hasattr(self._lock, "acquire"):
            self._lock.acquire()
        elif hasattr(self._lock, "lock"):
            self._lock.lock()
        elif hasattr(self._lock, "tryLock"):
            self._lock.tryLock()
    def UnLock(self):
        if not self._lock:
            return
        if hasattr(self._lock, "release"):
            self._lock.release()
        elif hasattr(self._lock, "unlock"):
            self._lock.unlock()
        elif hasattr(self._lock, "tryUnLock"):
            self._lock.tryUnLock()

def getJavaProperty(key):
    from plugins import __plugin_path__
    if key.startswith('-D'): key = key[2:]
    jar = os.path.join(__plugin_path__, "getProperty.jar")
    outputs = check_output('''java -jar "{bin}" {key}''', bin=jar, key=key)
    if outputs:
        value = outputs[0]
        return value.rstrip('\r\n')

__jenkins_encoding = None

def toJenkinsEncoding(s):
    if not s: return ""
    try:
        if flib.PY2:
            if not isinstance(s, unicode) and not isinstance(s, str) and not isinstance(s, bytes):
                return str(s)
        elif flib.PY3:
            if not isinstance(s, str) and not isinstance(s, bytes):
                return str(s)
            if isinstance(s, bytes):
                s = s.decode('utf-8', 'ignore')
        global __jenkins_encoding
        if not __jenkins_encoding:
            __jenkins_encoding = getJavaProperty("file.encoding")
        if __jenkins_encoding.lower() == 'gbk':
            return toGBK(s)
        elif __jenkins_encoding.lower() == 'gb2312':
            return toGB2312(s)
        else:
            return toUTF8(s)
    except Exception as e:
        flib.printf( str(e) )
        return s

#测试
def main():
    from locale import getpreferredencoding
    flib.printf( sys.stdout.encoding, getpreferredencoding() )
    LOG("b", "a")
    #Log.expt("Tesxt你好")
    flib.printf(toUTF8('Hello你好'))
    # p = subprocess.Popen(shlex.split("svn log -l 10"), shell=True, stdout=subprocess.PIPE)
    # print(p.stdout.read())
    # p.wait()
    exec_sh("svn info $1", args=["F:/Seven/ElementUnityWin"], logout=True)
    exec_command('''svn info "{path}"''', path="F:/Seven/ElementUnityWin")
    safe_execute('''svn info "F:/Seven/ElementUnity"''', logout=True)
    # print platform.system()
    # Log.log("b", "a")
    # __log__('',"为什么")
    # print toStr("为什么")
    #nc_server().start()
    print (getJavaProperty("-Dfile.encoding"))
    #print toStr("你好"), toJenkinsEncoding('你好')

if __name__ == '__main__':
    main()
