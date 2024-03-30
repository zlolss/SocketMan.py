#from . import manager as 端口管理器
#from . import serialization as 序列化工具
import struct, threading, time, socket
from typing import Callable
import logging
日志 = logging.getLogger()

端口管理器 = None
序列化工具 = None


class 状态:
    初始化 = 0
    已连接 = 1
    等待连接 = 2
    已断开 = 3
    出错 = 4


class 自动分配的端口(threading.Thread):
    _数据帧头 = '<L'

    def __init__(我, 名称, 密码=None, 接收对象处理方法=lambda x,_:print(x), 自动重连=True):
        assert type(名称) is str
        super().__init__()
        我.名称 = 名称
        我.自动重连 = 自动重连
        我.接收对象处理方法 = 接收对象处理方法
        我.__已连接 = False
        我.序列处理 = 序列化工具.二进制序列(密码=密码)
        我._关闭 = False
        我.角色 = None
        我.缓存 = b''
        我.状态 = 状态.初始化
        我.start()


    def __开始接收(我, 连接):
        _数据帧头 = 我._数据帧头
        我.缓存 = b''

        def 取出指定长度(长度):
            异常计数 = 0
            延迟 = 异常计数/100
            while len(我.缓存)<长度:
                接收 = 连接.recv(1024)
                if len(接收) <= 0:
                    我.关闭()
                    return b''
                我.缓存 += 接收
                异常计数+=1
                if 异常计数 % 10 == 0:
                    延迟 = 异常计数/100
                    日志.warning(f'发生异常{异常计数}次,当前获取延迟{延迟}s')
                time.sleep(延迟)
            取出 = 我.缓存[:长度]
            我.缓存 = 我.缓存[长度:]
            return 取出

        我.状态 = 状态.已连接
        try:
            while not(我._关闭):
                数据帧 = {'序列长度':None, '序列':None}
                数据帧['序列长度'] = struct.unpack(_数据帧头 , 取出指定长度(struct.calcsize(_数据帧头)))[0]
                数据帧['序列'] = 取出指定长度(数据帧['序列长度'])
                if 我._关闭:
                    break
                接收的对象 = 我.序列处理.反序列化(数据帧['序列'])
                if isinstance(我.接收对象处理方法, Callable):
                    我.接收对象处理方法(接收的对象, 我)
                else:
                    日志.error(f'未定义"接收对象处理方法", 无法处理接收的对象:{接收的对象}')
        except Exception as e:
            日志.error(e)
        我.状态 = 状态.已断开

    def _作为服务端连接(我):
        套子 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        套子.bind(('localhost', 我.端口))
        套子.listen(1)
        我.服务端套子 = 套子
        我.状态 = 状态.等待连接
        连接, 我.客户端地址 = 套子.accept()
        我.角色 = '服务端'
        return 连接


    def _作为客户端连接(我):
        连接 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        连接.connect(('127.0.0.1', 我.端口))
        我.角色 = '客户端'
        return 连接

    def 连接端口(我, 优先尝试角色):
        if 我.__已连接:
            日志.warning('重复连接!')
            return 我.连接
        if 优先尝试角色=='客户端':
            try:
                连接 = 我._作为客户端连接()
            except:
                连接 = 我._作为服务端连接()
        else:
            try:
                连接 = 我._作为服务端连接()
            except:
                连接 = 我._作为客户端连接()
        我.__已连接 = True
        return 连接


    def 发送(我, python对象):
        if 我.状态!=状态.已连接:
            日志.error('未连接无法发送')
            return False
        序列 = 我.序列处理.序列化(python对象)
        数据头 = struct.pack(我._数据帧头, len(序列))
        我.连接.send(数据头+序列)
        return True


    def run(我):
        我.端口, 优先尝试角色 = 端口管理器.自动分配端口(我.名称)
        我.连接 = 我.连接端口(优先尝试角色)
        我.__开始接收(我.连接)
        我.关闭()
        while 我.自动重连:
            我._关闭 = False
            我.连接 = 我.连接端口('服务端')
            我.__开始接收(我.连接)
            我.关闭()

    def 关闭(我):
        我._关闭 = True
        我.状态 = 状态.已断开
        我.连接.shutdown(socket.SHUT_RDWR)



class autosocket(自动分配的端口):

    def __init__(self, name, password=None, onrecvobj=lambda x,_:print(x)):
        super().__init__(名称=name, 密码=password, 接收对象处理方法=onrecvobj)

    def setonrecvobj(self, func):
        assert isinstance(func, callable)
        self.接收对象处理方法 = func

    def send(self, obj):
        return self.发送(obj)

    def close(self):
        return self.关闭()
