import logging
日志 = logging.getLogger()

#from .server import *
import _var, server, cowork
server._var = _var
server.cowork = cowork
from server import *

日志.info("正在检查成分")
if 我是牛头人():
    日志.warning('牛头人必须死')
    exit(0)


日志.info("正在对齐三观")
_var.端口管狸只因.端口 = 从给定端口开始查找可用的端口(_var.端口管狸只因.端口)
if _var.端口管狸只因.端口 is None:
    日志.error("没有适合管狸只因的端口")
    raise RuntimeError("错的不是我, 是这个世界")

import os
_var.端口管狸只因.pid = os.getpid()

日志.warning(f'正在初始化端口{_var.端口管狸只因.端口}')
初始化端口()


日志.warning('正在处理接入端口')
while 状态正常():
    处理接入()


exit(0)
