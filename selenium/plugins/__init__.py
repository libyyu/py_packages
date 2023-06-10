import platform
import os, sys
__plugin_path__ = os.path.split(os.path.realpath(__file__))[0]
if platform.system() == "Windows":
    os.environ['PATH'] += ";" + os.path.join(__plugin_path__, "windows\\bin")
elif platform.system() == "Linux":
    os.environ['PATH'] += ":" + os.path.join(__plugin_path__, "linux/bin")
elif platform.system() == "Darwin":
    os.environ['PATH'] += ":" + os.path.join(__plugin_path__, "mac/bin")
