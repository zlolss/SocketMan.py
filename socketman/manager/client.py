import logging
日志 = logging.getLogger()

import time, socket
from . import _var, cowork
import zlutils.shared as zls

_服务启动计数 = 0
_套子 = None

def 服务可用():
    return _var.管狸只因的心跳.有心跳


def 启动服务():
    global _服务启动计数
    import subprocess
    日志.warning('启动新的端口管理器')
    _服务启动计数 +=1
    import os
    当前文件路径 = os.path.abspath(__file__)
    管理器路径 = os.path.dirname(当前文件路径)
    try:
        sp = subprocess.Popen(['python', 管理器路径])
    except Exception as e:
        日志.error(e)


def 连接服务():
    global _套子
    _套子 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _套子.connect(_var.获取服务绑定用地址())
    return _套子


def 自动分配端口(端口名称):
    '''
    随便取个名字, 分配一个可用的端口号, 同名会分配到相同的端口
'''
    global _服务启动计数
    while not(服务可用()):
        启动服务()
        time.sleep(5)
        if _服务启动计数 > 3:
            日志.error('服务启动失败超过3次')
            raise RuntimeError('服务启动失败超过3次')
    _服务启动计数 = 0

    连接 = 连接服务()
    if cowork.握手(locals()).角色('甲方'):
        分配 = cowork.分配端口(locals())
        完成 = 分配.角色('甲方')
        连接.close()
        if 完成:
            return 分配.端口, 分配.角色
        else:
            日志.error('端口分配错误')
            raise RuntimeError('端口分配错误')
    连接.close()
    raise RuntimeError('握手失败')



