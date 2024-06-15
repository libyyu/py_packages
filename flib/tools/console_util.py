# -*- coding: utf-8 -*-
'''
#----------------------------------------------------------------------------------------
# 功能：提供修改控制台终端颜色的接口
#----------------------------------------------------------------------------------------
'''
import sys, os
import platform
isJenkinsMode = "WINSW_EXECUTABLE" in os.environ or 'JENKINS_HOME' in os.environ
#print "isJenkinsMode: ", isJenkinsMode

def has_key(d, k):
    if sys.version_info < (3,0):
        return d.has_key(k)
    else:
        return k in d

if platform.system() == "Windows" and not isJenkinsMode:
    import ctypes
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE = -12

    # 字体颜色定义 ,关键在于颜色编码，由2位十六进制组成，分别取0~f，前一位指的是背景色，后一位指的是字体色
    # 由于该函数的限制，应该是只有这16种，可以前景色与背景色组合。也可以几种颜色通过或运算组合，组合后还是在这16种颜色中

    # Windows CMD命令行 字体颜色定义 text colors
    FOREGROUND = {}
    FOREGROUND['BLACK'] = 0x00  # black.
    FOREGROUND['DARKBLUE'] = 0x01  # dark blue.
    FOREGROUND['DARKGREEN'] = 0x02  # dark green.
    FOREGROUND['DARKSKYBLUE'] = 0x03  # dark skyblue.
    FOREGROUND['DARKRED'] = 0x04  # dark red.
    FOREGROUND['DARKPINK'] = 0x05  # dark pink.
    FOREGROUND['DARKYELLOW'] = 0x06  # dark yellow.
    FOREGROUND['DARKWHITE'] = 0x07  # dark white.
    FOREGROUND['DARKGRAY'] = 0x08  # dark gray.
    FOREGROUND['BLUE'] = 0x09  # blue.
    FOREGROUND['GREEN'] = 0x0a  # green.
    FOREGROUND['SKYBLUE'] = 0x0b  # skyblue.
    FOREGROUND['RED'] = 0x0c  # red.
    FOREGROUND['PINK'] = 0x0d  # pink.
    FOREGROUND['YELLOW'] = 0x0e  # yellow.
    FOREGROUND['WHITE'] = 0x0f  # white.

    # Windows CMD命令行 背景颜色定义 background colors
    BACKGROUND = {}
    BACKGROUND['BLACK'] = 0x00
    BACKGROUND['DARKBLUE'] = 0x10  # dark blue.
    BACKGROUND['DARKGREEN'] = 0x20  # dark green.
    BACKGROUND['DARKSKYBLUE'] = 0x30  # dark skyblue.
    BACKGROUND['DARKRED'] = 0x40  # dark red.
    BACKGROUND['DARKPINK'] = 0x50  # dark pink.
    BACKGROUND['DARKYELLOW'] = 0x60  # dark yellow.
    BACKGROUND['DARKWHITE'] = 0x70  # dark white.
    BACKGROUND['DARKGRAY'] = 0x80  # dark gray.
    BACKGROUND['BLUE'] = 0x90  # blue.
    BACKGROUND['GREEN'] = 0xa0  # green.
    BACKGROUND['SKYBLUE'] = 0xb0  # skyblue.
    BACKGROUND['RED'] = 0xc0  # red.
    BACKGROUND['PINK'] = 0xd0  # pink.
    BACKGROUND['YELLOW'] = 0xe0  # yellow.
    BACKGROUND['WHITE'] = 0xf0  # white.

    STYLE = {
        'fore':
            {  # 前景色
                'black': FOREGROUND['BLACK'],  # 黑色
                'red': FOREGROUND['RED'],  # 红色
                'green': FOREGROUND['GREEN'],  # 绿色
                'yellow': FOREGROUND['YELLOW'],  # 黄色
                'blue': FOREGROUND['BLUE'],  # 蓝色
                'purple': FOREGROUND['PINK'],  # 紫红色
                'cyan': FOREGROUND['DARKSKYBLUE'],  # 青蓝色
                'white': FOREGROUND['WHITE'],  # 白色
            },

        'back':
            {  # 背景
                'black': BACKGROUND['BLACK'],  # 黑色
                'red': BACKGROUND['RED'],  # 红色
                'green': BACKGROUND['GREEN'],  # 绿色
                'yellow': BACKGROUND['YELLOW'],  # 黄色
                'blue': BACKGROUND['BLUE'],  # 蓝色
                'purple': BACKGROUND['PINK'],  # 紫红色
                'cyan': BACKGROUND['DARKSKYBLUE'],  # 青蓝色
                'white': BACKGROUND['WHITE'],  # 白色
            },

        'mode':
            {  # 显示模式
                'mormal': 0,  # 终端默认设置
                'bold': 1,  # 高亮显示
                'underline': 4,  # 使用下划线
                'blink': 5,  # 闪烁
                'invert': 7,  # 反白显示
                'hide': 8,  # 不可见
            },

        'default':
            {
                'end': 0,
            },
    }

    # get handle
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    std_err_handle = ctypes.windll.kernel32.GetStdHandle(STD_ERROR_HANDLE)


    def get_ori_attri(handle=std_out_handle):
        import struct
        csbi = ctypes.create_string_buffer(22)
        if ctypes.windll.kernel32.GetConsoleScreenBufferInfo(std_out_handle, csbi):
            #print csbi
            (bufx, bufy, curx, cury, wattr, left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            #print wattr
            return wattr
        else:
            return 0x00

    std_out_ori = get_ori_attri()
    std_err_ori = get_ori_attri(std_err_handle)
    #print std_out_ori, std_err_ori

    std_out_bg_ori = 0x00
    std_err_bg_ori = 0x00

    for (_, f) in FOREGROUND.items():
        for(_, b) in BACKGROUND.items():
            if f | b == std_out_ori:
                std_out_bg_ori = b
                break
    for (_, f) in FOREGROUND.items():
        for(_, b) in BACKGROUND.items():
            if f | b == std_err_ori:
                std_err_bg_ori = b
                break
    #print std_out_bg_ori, std_err_bg_ori


    def set_cmd_text_color(color, handle=std_out_handle):
        bg = std_out_bg_ori if handle == std_out_handle else std_err_bg_ori
        Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color | bg)
        return Bool

    # reset white
    def reset_cmd_color(handle=std_out_handle):
        #set_cmd_text_color(FOREGROUND.RED | FOREGROUND.GREEN | FOREGROUND.BLUE, handle=handle)
        if handle == std_out_handle:
            set_cmd_text_color(std_out_ori, handle=handle)
        else:
            set_cmd_text_color(std_err_ori, handle=handle)


    def error(text):
        set_cmd_text_color(STYLE['fore']['red'], handle=std_err_handle)
        sys.stderr.write(text + "\n")
        sys.stderr.flush()
        reset_cmd_color(handle=std_err_handle)

    def warn(text):
        set_cmd_text_color(STYLE['fore']['yellow'])
        sys.stdout.write(text + "\n")
        sys.stdout.flush()
        reset_cmd_color()

    def info(text):
        sys.stdout.write(text + "\n")
        sys.stdout.flush()

    def debug(text):
        set_cmd_text_color(STYLE['fore']['blue'])
        sys.stdout.write(text + "\n")
        sys.stdout.flush()
        reset_cmd_color()

    def verbose(text):
        set_cmd_text_color(STYLE['fore']['cyan'])
        sys.stdout.write(text + "\n")
        sys.stdout.flush()
        reset_cmd_color()

    def print_with_color(text, newLine=True, color=None):
        if not color or color not in STYLE['fore'].keys():
            sys.stdout.write(text)
            if newLine: sys.stdout.write('\n')
            sys.stdout.flush()
        else:
            set_cmd_text_color(STYLE['fore'][color])
            sys.stdout.write(text)
            if newLine: sys.stdout.write('\n')
            sys.stdout.flush()
            reset_cmd_color()
else:
    # 格式：\033[显示方式;前景色;背景色m
    #   说明:
    #
    #   前景色            背景色            颜色
    #   ---------------------------------------
    #     30                40              黑色
    #     31                41              红色
    #     32                42              绿色
    #     33                43              黃色
    #     34                44              蓝色
    #     35                45              紫红色
    #     36                46              青蓝色
    #     37                47              白色
    #
    #   显示方式           意义
    #   -------------------------
    #      0           终端默认设置
    #      1             高亮显示
    #      4            使用下划线
    #      5              闪烁
    #      7             反白显示
    #      8              不可见
    #
    #   例子：
    #   \033[1;31;40m    <!--1-高亮显示 31-前景色红色  40-背景色黑色-->
    #   \033[0m          <!--采用终端默认设置，即取消颜色设置-->]]]

    STYLE = {
        'fore':
            {  # 前景色
                'black': 30,  # 黑色
                'red': 31,  # 红色
                'green': 32,  # 绿色
                'yellow': 33,  # 黄色
                'blue': 34,  # 蓝色
                'purple': 35,  # 紫红色
                'cyan': 36,  # 青蓝色
                'white': 37,  # 白色
            },

        'back':
            {  # 背景
                'black': 40,  # 黑色
                'red': 41,  # 红色
                'green': 42,  # 绿色
                'yellow': 43,  # 黄色
                'blue': 44,  # 蓝色
                'purple': 45,  # 紫红色
                'cyan': 46,  # 青蓝色
                'white': 47,  # 白色
            },

        'mode':
            {  # 显示模式
                'mormal': 0,  # 终端默认设置
                'bold': 1,  # 高亮显示
                'underline': 4,  # 使用下划线
                'blink': 5,  # 闪烁
                'invert': 7,  # 反白显示
                'hide': 8,  # 不可见
            },

        'default':
            {
                'end': 0,
            },
    }

    def UseStyle(string, mode = '', fore = '', back = ''):

        mode  = '%s' % STYLE['mode'][mode] if has_key(STYLE['mode'], mode) else ''

        fore  = '%s' % STYLE['fore'][fore] if has_key(STYLE['fore'], fore) else ''

        back  = '%s' % STYLE['back'][back] if has_key(STYLE['back'], back) else ''

        style = ';'.join([s for s in [mode, fore, back] if s])

        style = '\033[%sm' % style if style else ''

        end   = '\033[%sm' % STYLE['default']['end'] if style else ''

        return '%s%s%s' % (style, string, end)

    def error(text):
        text = UseStyle(text, fore='red')
        sys.stderr.write(text)
        sys.stderr.write('\n')
        sys.stderr.flush()

    def warn(text):
        text = UseStyle(text, fore='yellow')
        sys.stdout.write(text)
        sys.stdout.write('\n')
        sys.stdout.flush()

    def info(text):
        sys.stdout.write(text)
        sys.stdout.write('\n')
        sys.stdout.flush()

    def debug(text):
        text = UseStyle(text, fore='blue')
        sys.stdout.write(text)
        sys.stdout.write('\n')
        sys.stdout.flush()

    def verbose(text):
        text = UseStyle(text, fore='cyan')
        sys.stdout.write(text)
        sys.stdout.write('\n')
        sys.stdout.flush()

    def print_with_color(text, newLine=True, color=None):
        if not color or color not in STYLE['fore'].keys():
            sys.stdout.write(text)
            if newLine: sys.stdout.write('\n')
            sys.stdout.flush()
        else:
            text = UseStyle(text, fore=color)
            sys.stdout.write(text)
            if newLine: sys.stdout.write('\n')
            sys.stdout.flush()

##############################################################


def main():
    verbose("[verbose]hello python")
    debug("[debug]hello python")
    info("[info]hello python")
    warn("[warn]hello python")
    error("[error]hello python")

if __name__ == '__main__':
    main()