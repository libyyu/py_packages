# -*- coding: utf-8 -*-
'''
命令行操作
'''
import socketserver
import sys
import os
import shutil
import locale
import argparse
import subprocess, shlex
from sys import version_info
import platform
import time

try:
	from flib import log as Log
	from flib.encode import toStr

	use_flib = True
except ImportError:
	use_flib = False

WINDOWS = platform.system() == "Windows"
PY3 = version_info >= (3, 0)
env_encoding = locale.getpreferredencoding()


def TOSTR(s):
	if use_flib:
		return toStr(s)
	else:
		return s


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


class CommandResult(object):
	"""
	"""

	def __init__(self, exitcode, outputs=None, errors=None):
		self.exitcode = exitcode
		self.outputs = outputs or []
		self.errors = errors or []

	if PY3:
		def __bool__(self):
			return self.exitcode == 0
	else:
		def __nonzero__(self):
			return self.exitcode == 0

	def __str__(self):
		return '''exitcode={exitcode}\noutput=\n\t{output}\nerror=\n\t{error}'''.format(exitcode=self.exitcode,
																						output="\n\t".join(
																							[str(x) for x in
																							 self.outputs]),
																						error="\n\t".join(
																							[str(x) for x in
																							 self.errors]))


class Command(object):
	"""
	"""
	# 变参调整
	args_tpl = {
		"bufsize": True,
		"executable": True,
		"stdin": True,
		"stdout": True,
		"stderr": True,
		"preexec_fn": True,
		"close_fds": True,
		"shell": True,
		"cwd": True,
		"env": True,
		"universal_newlines": True,
		"startupinfo": True,
		"creationflags": True,
		"restore_signals": PY3,
		"start_new_session": PY3,
		"pass_fds": PY3,
		"errors": PY3,
		"encoding": PY3
	}

	def _onReadProcWindows(self, collectlog=False, logout=False, try_exec=False):
		import contextlib
		def unbuffered(proc, stream='stdout'):
			newlines = ['\n', '\r\n', '\r']
			stream = getattr(proc, stream)
			with contextlib.closing(stream):
				while True:
					out = []
					last = stream.read(1)
					# Don't loop forever
					if not last or last == '' and proc.poll() is not None:
						break
					while last not in newlines:
						# Don't loop forever
						if last == '' and proc.poll() is not None:
							break
						out.append(last)
						last = stream.read(1)
					out = ''.join(out)
					yield out

		p_args = self.p_args
		if PY3:
			while p_args and p_args['stdout']:
				line = self.proc.stdout.readline()
				if not line or line == '': break
				line = line.rstrip().rstrip('\n')
				line = TOSTR(line)
				if collectlog: self.outputs.append(line)
				if logout: LOG(line)
				if self.OutputCallback is not None: self.OutputCallback(line, self.UserData)
			while p_args and p_args['stderr']:
				line = self.proc.stderr.readline()
				if not line or line == '': break
				line = line.rstrip().rstrip('\n')
				line = TOSTR(line)
				if collectlog: self.errors.append(line)
				if not try_exec and logout: LOGE(line)
				if self.ErrorCallback is not None: self.ErrorCallback(line, self.UserData)
		else:
			if p_args['stdout']:
				for line in unbuffered(self.proc):
					if line:
						line = line.rstrip().rstrip('\n')
						line = TOSTR(line)
						if collectlog: self.outputs.append(line)
						if logout: LOG(line)
						if self.OutputCallback is not None: self.OutputCallback(line, self.UserData)
			if p_args['stderr']:
				for line in unbuffered(self.proc, "stderr"):
					if not line: continue
					line = line.rstrip().rstrip('\n')
					line = TOSTR(line)
					if collectlog: self.errors.append(line)
					if not try_exec and logout: LOGE(line)
					if self.ErrorCallback is not None: self.ErrorCallback(line, self.UserData)

	def _onReadProcLinux(self, collectlog=False, logout=False, try_exec=False):
		import select
		rlist = [self.proc.stdout, self.proc.stderr]
		while rlist:
			readable, _, _ = select.select(rlist, [], [])
			for r in readable:
				if r is self.proc.stdout:
					line = r.readline()
					if not line:
						rlist.remove(r)
						continue
					line = line.rstrip().rstrip('\n')
					if not line: continue
					line = TOSTR(line)
					if collectlog: self.outputs.append(line)
					if logout: LOG(line)
					if self.OutputCallback is not None: self.OutputCallback(line, self.UserData)
				elif r is self.proc.stderr:
					line = r.readline()
					if not line:
						rlist.remove(r)
						continue
					line = line.rstrip().rstrip('\n')
					if not line: continue
					line = TOSTR(line)
					if collectlog: self.errors.append(line)
					if not try_exec and logout: LOGE(line)
					if self.ErrorCallback is not None: self.ErrorCallback(line, self.UserData)

	def __init__(self, cmds=None, simple=False, logout=False, collectlog=False, try_exec=False, communicate=None,
				 OutputCallback=None, ErrorCallback=None, NoWait=None, UserData=None, **kwargs):
		if cmds is not None:
			self.init(cmds, simple=simple, logout=logout, collectlog=collectlog, try_exec=try_exec,
					  communicate=communicate, OutputCallback=OutputCallback, ErrorCallback=ErrorCallback,
					  NoWait=NoWait, UserData=UserData, **kwargs)

	def init(self, cmds, simple=False, logout=False, collectlog=False, try_exec=False, communicate=None,
			 OutputCallback=None, ErrorCallback=None, NoWait=None, UserData=None, **kwargs):
		self.p_args = {}
		self.proc = None
		self.outputs = []
		self.errors = []
		self.UserData = UserData
		self.ErrorCallback = ErrorCallback
		self.OutputCallback = OutputCallback
		vlogout = logout or ErrorCallback is not None or OutputCallback is not None
		vcollectlog = collectlog or ErrorCallback is not None or OutputCallback is not None
		for v in kwargs:
			if v not in self.args_tpl or not self.args_tpl[v]: continue
			self.p_args[v] = kwargs[v]
		if self.args_tpl['encoding'] and 'encoding' not in self.p_args:
			self.p_args['encoding'] = env_encoding
		if simple and logout and not collectlog:
			self.p_args["stdout"] = subprocess.PIPE
			self.p_args["stderr"] = subprocess.PIPE
		else:
			if "stdout" not in self.p_args: self.p_args["stdout"] = subprocess.PIPE
			if "stderr" not in self.p_args: self.p_args["stderr"] = subprocess.PIPE
		if communicate and "stdin" not in self.p_args: self.p_args["stdin"] = subprocess.PIPE
		if "shell" not in self.p_args: self.p_args["shell"] = True
		try:
			if WINDOWS:
				self.proc = subprocess.Popen(shlex.split(cmds), **(self.p_args))
			else:
				self.proc = subprocess.Popen(cmds, **(self.p_args))
			# if communicate: communicate(self.proc)
			if (vcollectlog or vlogout):
				self._onReadProcWindows(collectlog=collectlog, logout=logout,
										try_exec=try_exec) if WINDOWS else self._onReadProcLinux(collectlog=collectlog,
																								 logout=logout,
																								 try_exec=try_exec)
			if not NoWait: self.Wait()
		except Exception as e:
			self.Kill()
			if self.ErrorCallback is not None: self.ErrorCallback(str(e), self.UserData)
			if collectlog: self.errors.insert(0, str(e))

	def __del__(self):
		self.Kill()
		self.p_args = None
		self.outputs = None
		self.errors = None

	@property
	def Result(self):
		exitcode = self.proc.returncode if self.proc is not None else -1
		return CommandResult(exitcode, self.outputs, self.errors)

	def __str__(self):
		return str(self.Result)

	if PY3:
		def __bool__(self):
			return not not self.Result
	else:
		def __nonzero__(self):
			return not not self.Result

	def Wait(self):
		self.proc.wait()

	def Kill(self):
		if self.proc is None: return
		if self.proc.stdin:
			self.proc.stdin.close()
		if self.proc.stdout:
			self.proc.stdout.close()
		if self.proc.stderr:
			self.proc.stderr.close()
		try:
			self.proc.kill()
			self.proc = None
		except OSError:
			pass

	def Input(self, cmd):
		from threading import Thread
		Thread(target=self.__InputProc, args=(self, cmd + "\n")).start()

	@classmethod
	def __InputProc(cls, self, cmd):
		# self.proc.communicate(cmd)
		self.proc.stdin.write(cmd)
	# self.proc.stdin.close()


class RemoteCommand(object):
	def __init__(self, ServerName, UserName, ServerPort=22, PriviteKeyFile=None, Password=None):
		self.ServerName = ServerName
		self.UserName = UserName
		self.ServerPort = ServerPort
		self.PriviteKeyFile = PriviteKeyFile
		self.Password = Password
		self.cmd = Command()
		self.__connect()

	def __connect(self):
		print('begin connect remote', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
		# from threading import Thread
		# p = Thread(target=self.__proc, args=(self,))
		# p.start()
		# p.join()
		self.__proc(self)

	def __proc(self, *args):
		print('enter proc', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
		cmds = '''sh -c "ssh -tt -o BatchMode=yes -i ./RemoteToolChainPrivate.key -p 22 zulong@10.236.179.85"'''
		if WINDOWS:cmds = "cmd /c " + cmds
		self.cmd.init(cmds,
			logout=True, collectlog=True, simple=True, communicate=True)
		print('proc', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

	def Pwd(self):
		print("pwd", self.cmd, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
		self.cmd.Input('pwd')

	def Input(self, cmd):
		self.cmd.Input(cmd)


def exec_command(*args, **kwargs):
	param = " ".join([str(x) for x in args])
	arg = param.format(**kwargs)
	cmd = Command(arg, logout=True, collectlog=True, simple=True)
	if not cmd: raise Exception("failed '" + arg + "'")


def exec_output(*args, **kwargs):
	param = " ".join([str(x) for x in args])
	arg = param.format(**kwargs)
	cmd = Command(arg, logout=False, collectlog=True, simple=True)
	if not cmd: raise Exception("failed '" + arg + "'")
	return cmd.Result.outputs, cmd.Result.errors


def exec_sh(*args, **kwargs):
	import uuid
	name = os.path.join(os.getcwd(), str(uuid.uuid1()) + ".sh").replace("\\", "/")
	param = " ".join([str(x) for x in args])
	arg = param.format(**kwargs)
	with open(name, "w+") as f:
		f.write(arg)
		f.close()
	try:
		return exec_command("sh " + name)
	finally:
		os.remove(name)


def exec_simple(*args, **kwargs):
	try:
		param = " ".join([str(x) for x in args])
		p = subprocess.Popen(shlex.split(param.format(**kwargs)), shell=True)
		p.wait()
		if p.returncode != 0:
			LOGE("Failed to execute command '" + param.format(**kwargs) + "'")
			return False
		else:
			return True
	except Exception as e:
		LOGE(e)
		return False


def main():
	cmd = Command("echo 'a'", logout=True, collectlog=True, simple=True)
	print(cmd)

	# rcmd = RemoteCommand("10.236.179.85", "zulong")
	# rcmd.Pwd()
	# rcmd.Input("ls")

	exec_command("ls -l")
	print(exec_output("ls -l"))



if __name__ == '__main__':
	main()
