# -*- coding: utf-8 -*-
import os
import sys
import json
import argparse
from jenkins.JenkinsParameters import *
from jenkins import channels

def gen_jenkins_version_option(_path):
    """
    获取所有版本信息
    :param _path:
    :return:
    """
    from py_script.FUtil import FUtil
    if _path[:7] == "http://":
        versions = FUtil.check_output("svn list {svn_url}".format(svn_url=_path), logout=False)
        versions = [x.rstrip("/") for x in versions]
    else:
        versions = FUtil.getFolderList(_path, recursion=False)
    return sorted(versions, lambda a, b: cmp(b, a))

def fixed_param(param):
    if not param:
        return param
    param = param.rstrip(',')
    if '$' in param:
        pos = param.find('$')
        return param[pos+1:]
    else:
        return param

class JenkinsChannel(object):
    def __init__(self, channel_name, channel_showname, fields = []):
        self.channel_name = channel_name
        self.channel_showname = channel_showname
        self.fields = fields
        self._keystoreFields = None
        self._iconField = None
        # 每个渠道都有的打包参数
        self.__genBuildConfig()
    def __genBuildConfig(self):
        versioninfo = GroupField("buildconfig", description="buildconfig", fields=[])
        versioninfo += SelectField("build_target", description="安卓编译版本",
                                   options=["17", "18", "19", "20", "21", "22", "23", "24"], init_value="19")
        from FApp import theApp
        svn_path = theApp.GetEnv().getChannelSvnPath(self.channel_name)
        selects = gen_jenkins_version_option(svn_path)
        default = selects[0] if len(selects) > 0 else None
        versioninfo += SelectField("version", description="SDK版本号",
                                   options=selects, init_value=default)
        self.fields.append(versioninfo)
        # 签名文件
        self._keystoreFields = GroupField("keystore", description="签名文件信息", fields=[])
        self._keystoreFields += InputFiled("storepass", description="签名文件密码")
        self._keystoreFields += InputFiled("alias", description="签名文件别名")
        self._keystoreFields += InputFiled("keypass", description="别名密码")
        # 角标
        self._iconField = GroupField("icon", description="角标展示", fields=[])
        self._iconField += ImageField("icon", description="角标")

    def __init_ChannelOptionField(self, project_name):
        project_data = self.getProjectConfig(project_name, self.channel_name)
        for groupfield in self.fields:
            for field in groupfield.Fields:
                def __getDefault(fd):
                    pk_type = fd.kwargs['pk_type']
                    if not project_data or pk_type not in project_data:
                        return fd.init_value
                    data = project_data[pk_type]
                    if fd.name not in data:
                        return fd.init_value
                    return data[fd.name]
                field.kwargs['pk_type'] = groupfield.name
                field.init_func = lambda fd: __getDefault(fd)
    def __init_keyStoreField(self, project_name):
        project_data = self.getKeyStoreConfig(project_name, self.channel_name)
        for field in self._keystoreFields.Fields:
            def __getDefault(fd):
                if not project_data:
                    return fd.init_value
                if fd.name not in project_data:
                    return fd.init_value
                return project_data[fd.name]
            field.init_func = lambda fd: __getDefault(fd)
    def __init_iconField(self, project_name):
        from FApp import theApp
        url = theApp.GetEnv().getChannelConfigSvnPath(project_name, self.channel_name) + "/icon/drawable-xxxhdpi/app_icon.png"
        for field in self._iconField.Fields:
            def __getDefault(fd):
                if not url:
                    return fd.init_value
                return url
            field.init_func = lambda fd: __getDefault(fd)
    def getProjectConfig(self, project_name, channel_name):
        from FApp import theApp
        theApp.GetEnv().setProjectName(project_name)
        project_path = theApp.GetEnv().getProjectRootPath()
        config_path = os.path.join(project_path, channel_name, "project_config.txt")
        if not os.path.exists(config_path): return
        with open(config_path, "r") as f:
            return json.load(f)
    def getKeyStoreConfig(self, project_name, channel_name):
        from FApp import theApp
        theApp.GetEnv().setProjectName(project_name)
        project_path = theApp.GetEnv().getProjectRootPath()
        config_path = os.path.join(project_path, channel_name, "keystore", "config.txt")
        if not os.path.exists(config_path): return
        with open(config_path, "r") as f:
            return json.load(f)
    def getGroupField(self, name):
        for groupfield in self.fields:
            if name == groupfield.name:
                return groupfield
    def __genChannelOptions(self, args):
        self.__init_ChannelOptionField(fixed_param(args.project))
        jenkins = JenkinsParameter(self.fields)
        return jenkins.toJenkins()
    def __genKeyStoreOption(self, args):
        self.__init_keyStoreField(fixed_param(args.project))
        jenkins = JenkinsParameter([self._keystoreFields])
        return jenkins.toJenkins()
    def __genIconOption(self, args):
        self.__init_iconField(fixed_param(args.project))
        jenkins = JenkinsParameter([self._iconField])
        return jenkins.toJenkins()
    def toJenkins(self, args):
        action = args.action
        from py_script.FUtil import FUtil
        if FUtil.toUTF8(action) == "生成渠道参数":
            return self.__genChannelOptions(args)
        elif FUtil.toUTF8(action) == "设置签名文件":
            return self.__genKeyStoreOption(args)
        elif FUtil.toUTF8(action) == "设置渠道图标":
            return self.__genIconOption(args)
        else:
            return "Not Finished."

    def __parseChannelParams(self, args):
        params = args.params.split(',')
        jenkins = JenkinsParameter(self.fields)
        return jenkins.fromJenkins(params)
    def __parseKeyStoreParams(self, args):
        params = args.params.split(',')
        jenkins = JenkinsParameter([self._keystoreFields])
        return jenkins.fromJenkins(params)
    def fromJenkins(self, args):
        action = args.action
        from py_script.FUtil import FUtil
        from py_script.FLog import FLog
        from FApp import theApp
        FLog.setLogLv(theApp.GetEnv().getLogLevel())
        out = args.out if args.out else theApp.GetEnv().getAppPath() + "/project"
        newargs = []
        newargs.extend(["-project", fixed_param(args.project)])
        newargs.extend(["-channel", fixed_param(args.channel)])
        newargs.extend(["-out", out])
        newargs.extend(["-executor", args.executor])
        newargs.extend(["-icon", args.icon])
        newargs.extend(["-keystore", args.keystore])
        if FUtil.toUTF8(action) == "生成渠道参数":
            result = self.__parseChannelParams(args)
        elif FUtil.toUTF8(action) == "设置签名文件":
            result = self.__parseKeyStoreParams(args)
        else:
            result = None
        newargs.extend(["-params", result])
        from py_config_script import ProjectConfigGenMain
        from py_config_script.UniClientConfig import UniClientConfig
        UniClientConfig.Instance().init({
            "template_path": theApp.GetEnv().getAppPath(),
            "project_path": theApp.GetEnv().getProjectRootPath(),
        })

        ProjectConfigGenMain.build(newargs)
        return newargs

__jenkins_channels__ = {}
__jenkins_channels_showname__ = {}

def make_one_channel(channel_name, channel_showname, channel_config):
    """
    根据配置，构造一个渠道的Jenkins参数
    :param channel_name:
    :param channel_showname:
    :param channel_config:
    :return:
    """
    channel = GroupField("channelconfig", description=channel_config['description'] if 'description' in channel_config else "channelconfig", fields=[])
    options = channel_config['options']
    for option in options:
        fieldtype = "input"
        if 'type' in option: fieldtype = option['type']
        if fieldtype == "input":
            channel += InputFiled(option['name'], description=option['description'] if 'description' in option else option['name'], init_value=option['default'] if 'default' in option else "")
        elif fieldtype == "checkbox":
            channel += CheckBoxField(option['name'], description=option['description'] if 'description' in option else option['name'], init_value=option['default'] if 'default' in option else False)
        else:
            raise Exception("类型:{type}不支持".format(type=fieldtype))
    # 注册
    __jenkins_channels__[channel_name] = JenkinsChannel(channel_name, channel_showname, fields=[channel])
    __jenkins_channels_showname__[channel_showname] = channel_name

def registerChannels():
    """
    注册所有渠道
    :return:
    """
    __channels__ = channels.__channels__
    __options__ = channels.__options__
    for (k,v) in __options__.items():
        channel_name = k
        channel_showname = __channels__[k]
        channel_config = v["channelconfig"]
        make_one_channel(channel_name, channel_showname, channel_config)

def get_channel_info(name):
    """
    返回渠道英文名，中文名称
    :param name:
    :return:
    """
    from py_script.FUtil import FUtil
    if __jenkins_channels__.has_key(name):
        channel = __jenkins_channels__[name]
        return (channel.channel_name, channel.channel_showname)
    else:
        name = FUtil.toUTF8(name)
        if __jenkins_channels_showname__.has_key(name) and __jenkins_channels__.has_key(__jenkins_channels_showname__[name]):
            channel =__jenkins_channels__[__jenkins_channels_showname__[name]]
            return (channel.channel_name, channel.channel_showname)
        raise Exception("{} 渠道未定义，请检查是否已经注册过该渠道。".format(name))

def getChannel(name):
    from py_script.FUtil import FUtil
    if __jenkins_channels__.has_key(name):
        return __jenkins_channels__[name]
    else:
        name = FUtil.toUTF8(name)
        if __jenkins_channels_showname__.has_key(name) and __jenkins_channels__.has_key(__jenkins_channels_showname__[name]):
            return __jenkins_channels__[__jenkins_channels_showname__[name]]
        raise Exception("{} 渠道未定义，请检查是否已经注册过该渠道。".format(name))

def gen_channel_param(name):
    """
    生成渠道对应的命令行参数信息
    :param name:渠道名称，英文或者中文名称
    :return:
    """
    from py_script.FUtil import FUtil
    channel_ = getChannel(name)
    if not channel_:
        raise Exception("{} 渠道未定义，请检查是否已经注册过该渠道。".format(FUtil.toUTF8(name)))
    groupField = channel_.getGroupField("channelconfig")
    if not groupField:
        raise Exception("{} 渠道没有channelconfig参数，请检查是否已经在Jenkins中注册过。".format(FUtil.toUTF8(name)))
    ret = []
    for field in groupField.Fields:
        ret.append("-" + field.name)
    return tuple(ret)

def gen_common_param(name):
    """
    生成通用配置对应的命令行参数信息
    :return:
    """
    return ("-build_target","-version")

def gen_keystore_param(channel):
    """
    签名配置参数列表
    :param channel:
    :return:
    """
    return ("-storepass","-alias", "-keypass")

def gen_jenkins_option(args):
    try:
        channel = getChannel(fixed_param(args.channel))
        print channel.toJenkins(args)
    except Exception as e:
        print """<font color="red">{err}</font>""".format(err=str(e))

def parser_jenkins_option(args):
    name = fixed_param(args.channel)
    from py_script.FUtil import FUtil
    channel = getChannel(name)
    if not channel:
        raise Exception("{} 渠道未定义，请检查是否已经注册过该渠道。".format(FUtil.toUTF8(name)))
    channel.fromJenkins(args)

registerChannels()

def main():
    parser = argparse.ArgumentParser(prefix_chars='-+/')
    parser.add_argument("-p", "--project", help="project name", type=str)
    parser.add_argument("-c", "--channel", help="channel name", type=str)
    parser.add_argument("-a", "--action", help="channel action", type=str)
    subparsers = parser.add_subparsers(title='Jenkins Channel Operation',
                                    description='Jenkins Channel Operation',
                                    help='Jenkins Channel Operation',
                                    dest='Jenkins Channel Operation')
    gen_option = subparsers.add_parser('options')
    gen_option.set_defaults(func=gen_jenkins_option)

    from FApp import theApp
    parser_option = subparsers.add_parser('parser')
    parser_option.add_argument("-ps", "--params", help="input params", type=str, required=True)
    parser_option.add_argument("-o", "--out", help="配置输出地址", type=str)
    parser_option.add_argument("-e", "--executor", help="执行者",  type=str, default="jenkins")
    parser_option.add_argument("-i", "--icon", help="icon路径，512*512大小", type=str, default="")
    parser_option.add_argument("-k", "--keystore", help="签名文件路径", type=str, default="")
    parser_option.set_defaults(func=parser_jenkins_option)

    args = parser.parse_args()
    #args = parser.parse_args('''-p=seven, -c=CHANNEL$tt, -a=生成渠道参数 options'''.split())
    #args = parser.parse_args('''-p=seven -c=tt -a=生成渠道参数 parser -ps="com.zulong.seven.uc,733195,55300,build_target$19,version$1.0," -o="./" -e=lidengfeng'''.split())
    #args = parser.parse_args('''-p=seven -c=tt -a=设置签名文件 parser -ps=enVsb25nLnNldmVu,com.zulong.seven,cGVyZmVjdGdhbWU=, -e=lidengfeng'''.split())
    args.func(args)

if __name__ == "__main__":
    main()