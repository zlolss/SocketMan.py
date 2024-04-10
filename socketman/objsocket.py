from .serialization import 二进制序列
import time, threading, struct, socket
from zlutils.wrapper import 篡改类
from zlutils.event import 事件类

import logging
日志 = logging.getLogger()

_数据帧头 = '<L'

class PEvent(事件类):

    CONNECT = 'conn'
    DISCONNECT = 1
    RECV = 'obj, conn'
    SEND = 'obj, conn'


class PSEvent(事件类):

    ACCEPT = 'conn, addr'


class 状态类:
    初始化 = 0
    已连接 = 1
    等待连接 = 2
    已断开 = 3
    出错 = 4


# =============================================== base

class OBJSocket(threading.Thread, 篡改类):

    块大小 = 1024

    def __init__(我, conn, passwd=None):
        threading.Thread.__init__(我)
        篡改类.__init__(我, conn)
        我.连接 = conn
        我.序列化工具 = 二进制序列(密码=passwd)
        我.缓存 = b''
        我.event = PEvent()
        我.event.sendevent(PEvent.CONNECT, conn=我)
        我.可用 = True


    def recv(我, *_):

        def 取出指定长度(长度):
            异常计数 = 0
            延迟 = 异常计数/100
            while len(我.缓存)<长度:
                接收 = 我.连接.recv(OBJSocket.块大小)
                if len(接收) <= 0:
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

        try:
            数据帧 = {'序列长度':None, '序列':None}
            数据帧['序列长度'] = struct.unpack(_数据帧头 , 取出指定长度(struct.calcsize(_数据帧头)))[0]
            数据帧['序列'] = 取出指定长度(数据帧['序列长度'])
            assert len(数据帧['序列']) == 数据帧['序列长度']
            接收的对象 = 我.序列化工具.反序列化(数据帧['序列'])
            我.event.触发事件(PEvent.RECV,  obj=接收的对象, conn=我)
            return 接收的对象
        except Exception as e:
            日志.error(f'端口异常关闭{e}')
            我.shutdown()
        return None


    def send(我, python对象):
        序列 = 我.序列化工具.序列化(python对象)
        数据头 = struct.pack(_数据帧头, len(序列))
        我.连接.send(数据头+序列)
        我.event.触发事件(PEvent.SEND, obj=python对象, conn=我)
        return

    def close(我):
        return 我.shutdown()

    def shutdown(我):
        我.可用 = False
        我.连接.shutdown(socket.SHUT_RDWR)
        我.event.触发事件(PEvent.DISCONNECT, conn=我)

    #def autorecv(我, callback):
    #    return run()

    def autorecv(我, callback):
        from typing import Callable
        assert 我.可用 and not(我.is_alive()), '线程异常'
        assert isinstance(callback, Callable), '回调函数不可访问'
        我.event.设置唯一监听器(PEvent.RECV, callback)
        我.start()

    def run(我):
        while(我.可用):
            我.recv()


# =============================================== server & client

class OBJSocketServer:
    def __init__(我, addr, passwd=None):
        我.密码 = passwd
        我.event = PSEvent()
        我.套子 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        我.套子.bind(addr)
        我.listen()


    def listen(我, flag=1):
        我.套子.listen(flag)

    def accept(我):
        连接, 地址 = 我.套子.accept()
        return OBJSocket(conn=连接, passwd=我.密码) ,地址

    def close(我):
        if 我.套子 is not None:
            我.套子.close()



class OBJSocketClinet(OBJSocket):

    def __init__(我, addr, passwd=None):
        我.密码 = passwd
        连接 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        连接.connect(addr)
        super().__init__(conn=连接, passwd=我.密码)
