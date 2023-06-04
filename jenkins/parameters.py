# -*- coding: utf-8 -*-
"""
生成Jenkins控件
"""
import sys
import argparse
import uuid

def isfunction(obj):
    try:
        if hasattr(obj, '__call__'):
            return True
    except Exception as e:
        pass
    return False

class JenkinsParameter(object):
    """
    Jenkins上的控件
    """
    table_template = """
        <table width="100%" class="parameters" id="{fid}">
            <tbody>
            {rows}
            </tbody>
        </table>
    """
    def __init__(self, name, fields = []):
        self.name = name
        self.id = "py-jenkins_" + name + "_" + str(uuid.uuid1())
        self.registerFields(fields)
    def registerFields(self, fields):
        self.fields = fields
    def toFile(self, file="jenkins.html"):
        head = """
                <head>
                    <meta http-equiv=Content-Type content="text/html; charset=utf-8">
                    <title>Jenkins Parameters</title>
                </head>
                """
        with open(file, "w") as f:
            f.write(head + self.toJenkins())
    def toJenkins(self):
        rows = ""
        for field in self.fields:
            rows += field.toJenkins()
        return self.table_template.format(rows=rows, fid=self.id)
    def fromJenkins(self, params):
        result = {}
        pos = 0
        for field in self.fields:
            (name, value, skip) = field.fromJenkins(params, pos)
            result[name] = value
            pos += skip
        return result

class Field(object):
    """
    Jenkins上的一个参数
    """
    def __init__(self, name, description = "", **kwargs):
        """
        构造一个option
        :param name:变量名称
        :param description:变量描述
        """
        self.name = name
        self.description = description
        self.kwargs = kwargs
        self.id = self.get_selector_prefix() + name # + "_" + str(uuid.uuid1())
        self.description_id = self.id + "_desc"
        self.value = None
    def toJenkins(self):
        raise Exception("can not call interface Field.toJenkins")
    def fromJenkins(self, params, pos):
        raise Exception("can not call interface Field.fromJenkins")

    def get_id(self):
        """
        获取控件的id， 用于赛选器
        :return: str
        """
        return self.id

    def get_description_id(self):
        """
        获取控件的id， 用于赛选器
        :return: str
        """
        return self.description_id

    def get_selector_prefix(self):
        """
        获取html赛选器前缀
        """
        if 'selector_prefix' in self.kwargs:
            return "py-jenkins_" + self.kwargs['selector_prefix'] + "_"
        else:
            return "py-jenkins_"

    def get_init_value(self):
        """
        获取显示框的初始值
        :return: str
        """
        if 'value' in self.kwargs:
            value = self.kwargs['value']
            if isfunction(value):
                return value(self)
            else:
                return value
        else:
            return None

    def get_value(self):
        return self.value

    def get_description(self):
        """
        获取显示框的提示文本
        :return: str
        """
        if 'get_description' in self.kwargs:
            return self.kwargs['get_description'](self)
        else:
            return self.description or ""

    def get_scripts(self):
        """
        获取控件的事件脚本
        :return: (str, str)
        """
        if 'script' in self.kwargs:
            inscript = self.kwargs['script']
            script = inscript
            if isfunction(script):
                script = inscript(self)
            script_dec = []
            script_impl = []
            for (dec, impl) in script.items():
                script_dec.append(dec)
                script_impl.append(impl)

            return (" ".join(script_dec), "\n".join(script_impl))

        return (None, None)

    def make_scriptbody(self):
        (script_dec, script_impl) = self.get_scripts()
        if not script_dec or not script_impl: return ""
        return """<script type="text/javascript">
                {script_impl}
                </script>""".format(script_impl=script_impl)


class PartLineField(Field):
    """
    Jenksin上的一个横向分割线
    """
    def __init__(self, description = "", size=8):
        Field.__init__(self, "PARTLINE", description=description)
        self.size = size
    def toJenkins(self):
        return """<tr>
                    <td class="setting-leftspace">&nbsp;</td>
                    <td><div>
                        <hr style="filter: alpha(opacity=100,finishopacity=0,style=2)" align="left" width="100%;" color=#987cb9 size={size}>
                        <br/>
                        <hr style="filter: alpha(opacity=100,finishopacity=0,style=2)" align="left" width="100%;" color=#987cb9 size={size}>
                    </div></td>
                    <td><div>
                        <hr style="filter: alpha(opacity=100,finishopacity=0,style=2)" align="left" width="100%;" color=#987cb9 size={size}>
                        {desc}<br/>
                        <hr style="filter: alpha(opacity=100,finishopacity=0,style=2)" align="left" width="100%;" color=#987cb9 size={size}>
                    </div></td>
                    <td></td>
                </tr>
                """.format(desc=self.get_description(), size=self.size)

class GroupField(Field):
    """
        控件组
    """
    def __init__(self, name, description = "", fields = [], **kwargs):
        Field.__init__(self, name, description=description, **kwargs)
        self.fields = fields
    @property
    def Fields(self):
        return self.fields
    def addField(self, field):
        self.fields.append(field)
    def __add__(self, field):
        self.addField(field)
        return self
    def toJenkins(self):
        rows = PartLineField(description = self.description).toJenkins()
        for field in self.fields:
            rows += field.toJenkins()
        return rows
    def fromJenkins(self, params, pos):
        result = {}
        old_pos = pos
        for field in self.fields:
            if isinstance(field, InputFiled):
                (name, value, skip) = field.fromJenkins(params, pos)
                result[name] = value
                pos += skip
                continue
            elif isinstance(field, CheckBoxField):
                (name, value, skip) = field.fromJenkins(params, pos)
                result[name] = value
                pos += skip
                continue
            elif isinstance(field, SelectField):
                (name, value, skip) = field.fromJenkins(params, pos)
                result[name] = value
                pos += skip
                continue
            elif isinstance(field, GroupField):
                (name, value, skip) = field.fromJenkins(params, pos)
                result[name] = value
                pos += skip
                continue
            else:
                continue
        self.value = {}
        self.value[self.name] = result
        return (self.name, result, pos-old_pos)

class InputFiled(Field):
    """
    Jenksin上的一个输入框
    """
    def __init__(self, name, description = "", readonly=False,  **kwargs):
        Field.__init__(self, name, description=description, **kwargs)
        self.input_type = "text"
        self.class_style = "setting-input"
        self.readonly = readonly
        self.value = self.get_init_value() or ""

    def toJenkins(self):
        (script_dec, script_impl) = self.get_scripts()
        self.value = self.get_init_value() or ""
        return """
                <tr>
                    <td class="setting-leftspace">&nbsp;</td>
                    <td class="setting-name">{param}</td>
                    <td class="setting-main">
                        <input name="value" type="{input_type}" class="{class_style}" value="{value}" id="{fid}" {readonly} {script_dec}>
                    </td>
                    <td class="setting-no-help"></td>
                </tr>
                <tr class="validation-error-area">
                    <td colspan="2"></td>
                    <td></td>
                    <td></td>
                </tr>
                <tr>
                    <td colspan="2"></td>
                    <td class="setting-description" id="{did}">{desc}</td>
                    <td></td>
                </tr>
                {script_body}
                """.format(param=self.name, 
                input_type=self.input_type, 
                class_style=self.class_style, 
                desc=self.get_description(), 
                value=self.value,
                fid=self.get_id(),
                did=self.get_description_id(),
                readonly='''readonly="readonly"''' if self.readonly else "",
                script_dec=script_dec or "",
                script_body=self.make_scriptbody())

    def fromJenkins(self, params, pos):
        self.value = params[pos]
        return (self.name, self.value, 1)

class CheckBoxField(Field):
    """
    Jenkins上的checkbox控件
    """
    def __init__(self, name, description = "", **kwargs):
        Field.__init__(self, name, description=description, **kwargs)
        self.input_type = "checkbox"
        self.class_style = "  "
        self.value = self.get_init_value() or "false"

    def toJenkins(self):
        (script_dec, script_impl) = self.get_scripts()
        self.value = self.get_init_value() or "false"
        value = '''checked="true"''' if self.get_value() == "true" else ""
        return """
                <tr>
                    <td class="setting-leftspace">&nbsp;</td>
                    <td class="setting-name">{param}</td>
                    <td class="setting-main">
                        <input name="value" type="{input_type}" class="{class_style}" id="{fid}" {value} {script_dec}>
                    </td>
                    <td class="setting-no-help"></td>
                </tr>
                <tr class="validation-error-area">
                    <td colspan="2"></td>
                    <td></td>
                    <td></td>
                </tr>
                <tr>
                    <td colspan="2"></td>
                    <td class="setting-description" id="{did}">{desc}</td>
                    <td></td>
                </tr>
                {script_body}
            """.format(param=self.name,
                       input_type=self.input_type,
                       class_style=self.class_style,
                       desc=self.get_description(),
                       fid=self.get_id(),
                       did=self.get_description_id(),
                       value=value,
                       script_dec=script_dec or "",
                       script_body=self.make_scriptbody())
    
    def fromJenkins(self, params, pos):
        self.value = params[pos]
        return (self.name, self.value, 1)

class SelectField(Field):
    """
    Jenkins下拉选项控件
    """
    def __init__(self, name, description="", multi_select=False, **kwargs):
        Field.__init__(self, name, description=description, **kwargs)
        self.multi_select = multi_select

    def get_options(self):
        if 'options' in self.kwargs:
            options = self.kwargs['options']
            if isfunction(options):
                return options(self)
            else:
                return options
        else:
            return []

    def __isSelected(self, options, value):
        selects = self.get_value()
        # 单选列表的第一个默认被选中
        if not self.multi_select and not selects:
            if len(options) >0 and options[0] == value:
                return True

        if isinstance(selects, list):
            return value in selects
        else:
            return value == selects

    def __genSingleSelect(self):
        (script_dec, script_impl) = self.get_scripts()
        options = self.get_options()
        options_ = ""
        for option in options:
            options_ += """<option value="{param}${name}" {selected}>{name}</option>""".format(param=self.name,
                        name=option,
                        selected='''selected="selected"''' if self.__isSelected(options, option) else "")

        return """
                <tr>
                    <td class="setting-leftspace">&nbsp;</td>
                    <td class="setting-name">{param}</td>
                    <td class="setting-main">
                        <select name="value" id="{fid}" {script_dec}>
                            {options}
                        </select>
                    </td>
                    <td class="setting-no-help"></td>
                </tr>
                <tr class="validation-error-area">
                    <td colspan="2"></td>
                    <td></td>
                    <td></td>
                </tr>
                <tr>
                    <td colspan="2"></td>
                    <td class="setting-description" id="{did}">{desc}</td>
                    <td></td>
                </tr>
                {script_body}
            """.format(param=self.name, 
                options=options_, 
                desc=self.get_description(), 
                fid=self.get_id(),
                did=self.get_description_id(),
                script_dec=script_dec, 
                script_body=self.make_scriptbody())
    def __genMultiSelect(self):
        (script_dec, script_impl) = self.get_scripts()
        options = self.get_options()
        options_ = ""
        for option in options:
            options_ += """
            <tr style="white-space:nowrap">
            <td>
            <input {script_dec} id="{param}_{value}_{fid}_option" type="checkbox" name="value" alt="{param}${value}" json="{param}${value}" title="{param}${value}" value="{param}${value}" class=" " {checked}>
            <label title="{value}" class="attach-previous" id="{param}_{value}_{fid}_label">{value}</label>
            {extern_value}
            </td>
            </tr>
            """.format(param=self.name,
                       value=option,
                       checked='''checked="checked"''' if self.__isSelected(options, option) else "",
                       fid=self.get_id(),
                       script_dec=script_dec,
                       extern_value=self.kwargs['get_extern_value'](option) if 'get_extern_value' in self.kwargs else "")

        div = """<div style="float: left; overflow-y: auto; padding-right: 25px;" class="dynamic_checkbox">
            <table>
            <tbody>
            {tbody}
            </tbody>
            </table>
            </div>""".format(tbody=options_)
        return """
            <tr>
                <td class="setting-leftspace">&nbsp;</td>
                <td class="setting-name">{param}</td>
                <td class="setting-main">
                    {div}
                </td>
                <td class="setting-no-help"></td>
            </tr>
            <tr class="validation-error-area">
                <td colspan="2"></td>
                <td></td>
                <td></td>
            </tr>
            <tr>
                <td colspan="2"></td>
                <td class="setting-description" id="{did}">{desc}</td>
                <td></td>
            </tr>
            {script_body}
        """.format(param=self.name, 
            div=div, 
            desc=self.get_description(),
            did=self.get_description_id(),
            script_body=self.make_scriptbody())
    
    def toJenkins(self):
        self.value = self.get_init_value() or []
        if self.multi_select:
            return self.__genMultiSelect()
        else:
            return self.__genSingleSelect()

    def fromJenkins(self, params, pos):
        newpos = pos
        hasFind = False
        for x in xrange(newpos, len(params)):
            if params[x].startswith(self.name + "$"):
                newpos = x
                hasFind = True
                continue
            else:
                break
        if not hasFind:
            if self.isMuliSelect:
                self.value = []
            else:
                self.value = ""
            return (self.name, self.value, 0)
        results = params[pos:newpos+1]
        results = [ x.lstrip(self.name+"$") for x in results ]
        if self.isMuliSelect:
            self.value = results
            skippos = len(results)
        else:
            self.value = results[0] if len(results) >0 else ""
            skippos = 1
        return (self.name, self.value, skippos)

class FileField(Field):
    """
    文件上传空间
    """
    def __init__(self, name, description = "", accept="", **kwargs):
        """
        :param name:
        :param description:
        :param accept:支持的文件格式
        :param kwargs:
        """
        Field.__init__(self, name, description=description, **kwargs)
        self.input_type = "file"
        self.accept = accept

    def toJenkins(self):
        return """
               <tr>
                   <td class="setting-leftspace">&nbsp;</td>
                   <td class="setting-name">{param}</td>
                   <td class="setting-main">
                        <input id="{fid}" name="file" type="{input_type}" jsonaware="true" class="{class_style}" {accept} {value} />
                   </td>
                   <td class="setting-no-help"></td>
               </tr>
               <tr class="validation-error-area">
                    <td colspan="2"></td>
                    <td></td>
                    <td></td>
                </tr>
               <tr>
                   <td colspan="2"></td>
                   <td class="setting-description" id="{did}">{desc}</td>
                   <td></td>
               </tr>
                """.format(param=self.name, 
                        input_type=self.input_type, 
                        class_style="  ",
                        fid=self.get_id(),
                        did=self.get_description_id(),
                        desc=self.get_description(),
                        accept='''accept="{}"'''.format(self.accept) if self.accept else "",
                        value="")

class FileExtendField(Field):
    """
    文件上传控件
    """
    def __init__(self, name, description = "", init_value = "", accept="", onclick = None, **kwargs):
        """
        :param name:
        :param description:
        :param init_value:
        :param accept:支持的文件格式
        :param kwargs:
        """
        Field.__init__(self, name, description=description, **kwargs)
        self.input_type = "file"
        self.init_value = init_value
        self.accept = accept
        self.onclick = onclick
    def toJenkins(self):
        return """
               <tr>
                   <td class="setting-leftspace">&nbsp;</td>
                   <td class="setting-name">{param}</td>
                   <td class="setting-main">
                       <input type="text" id="{param}_f_file" readonly="readonly" />
                       <input name="{param}" id="{param}" type="button" value="文件上传" jsonaware="true" class="{class_style}" {accept} {value} onclick="btn_{param}()" />
                       <input name="{param}" type="file" id="{param}_t_file" onchange="{param}_f_file.value=this.value" style="display:none" />
                   </td>
               </tr>
               <tr>
                   <td colspan="2"></td>
                   <td class="setting-description">{desc}</td>
               </tr>
               <script type="text/javascript">
               function btn_{param}() {{
                    {param}_t_file.click();
               }}
               </script>
                """.format(param=self.name, class_style="  ",
                            desc=self.description,
                            accept='''accept="{}"'''.format(self.accept) if self.accept else "",
                            value="",
                            onclick=self.onclick(self) if self.onclick else "")

class TableField(Field):
    """
    二维表控件
    """
    def __init__(self, name, description = "", title = [], datas = [], **kwargs):
        Field.__init__(self, name, description=description, **kwargs)
        self.input_type = "table"
        self.title = title
        self.datas = datas
    def __genHead(self):
        if not self.title: return ""
        options = ""
        for title in self.title:
            options += """
                        <th>{title}</th>
                        """.format(title=title)
        return """<tr>
                    {options}
                 </tr>
                """.format(options=options)
    def __genRow(self, rows):
        options = ""
        for row in rows:
            options += """
                        <td>{row}</td>
                        """.format(row=row)
        return """
                <tr>
                    {options}
                </tr>
                """.format(options=options)
    def __genContent(self):
        if not self.datas: return ""
        rows = ""
        for row in self.datas:
            rows += self.__genRow(row)
        return """
                {rows}
                """.format(rows=rows)
    def __genTable(self):
        return """
                <table border="1" cellspacing="0">
                    <tbody>
                        {head}
                        {content}
                    </tbody>
                </table>
                """.format(head=self.__genHead(), content=self.__genContent())
    def toJenkins(self):
        return """
               <tr>
                   <td class="setting-leftspace">&nbsp;</td>
                   <td class="setting-name">{param}</td>
                   <td class="setting-main">
                       {table}
                   </td>
                   <td class="setting-no-help"></td>
               </tr>
               <tr class="validation-error-area">
                    <td colspan="2"></td>
                    <td></td>
                    <td></td>
                </tr>
               <tr>
                   <td colspan="2"></td>
                   <td class="setting-description">{desc}</td>
                   <td></td>
               </tr>
                """.format(param=self.name, class_style="  ",
                            desc=self.get_description(),
                            table=self.__genTable())

class ImageField(Field):
    def __init__(self, name, description = "", width = 64, height = 64, **kwargs):
        Field.__init__(self, name, description=description, **kwargs)
        self.width = width
        self.height = height
        self.value = self.get_init_value() or ""
    def toJenkins(self):
        self.value = self.get_init_value() or ""
        return """
            <tr>
                <td class="setting-leftspace">&nbsp;</td>
                <td class="setting-name">{param}</td>
                <td>
                    <img src="{url}" width="{width}" height="{height}"/>
                </td>
            </tr>
            <tr class="validation-error-area">
                <td colspan="2"></td>
                <td></td>
                <td></td>
            </tr>
            <tr>
                <td colspan="2"></td>
                <td class="setting-description">{desc}</td>
                <td></td>
            </tr>
            """.format(param=self.name,
                       desc=self.get_description(),
                       width=self.width,
                       height=self.height,
                       url=self.value)


