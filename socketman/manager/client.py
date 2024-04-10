import logging, sys
logger = logging.getLogger()

import time, socket

from .common import PType, 参数, 暗号, 端口字段类
from ..objsocket import OBJSocket


def 启动服务端():
    import subprocess, os
    logger.warning('启动新的端口管理器')
    当前文件路径 = os.path.abspath(__file__)
    管理器路径 = os.path.dirname(当前文件路径)
    try:
        sp = subprocess.Popen(['python', 管理器路径])
    except Exception as e:
        logger.error(e)


class Client:
    '''
Usage:
with Client() as c:
    port = c.getport(name=portname, ptype='p2p')'''

    def __init__(我):
        我.连接 = None

    def _启动并连接(我):
        连接失败计数 = 0
        我.连接 = 我._连接服务端()
        while(我.连接 is None):
            连接失败计数 += 1
            if 连接失败计数 < 3:
                logger.warning(f'连接失败{连接失败计数}次')
            else:
                raise RuntimeError(f'启动服务端失败')
            启动服务端()
            time.sleep(参数.服务端启动等待时间 + 连接失败计数)
            我._连接服务端()
        try:
            我._握手()
        except Exception as e:
            logger.error(f'{sys._getframe().f_code.co_name}:{e}')
            我.连接.close()
            return False
        return True

    def _连接服务端(我):
        try:
            _套子 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _套子.connect(参数.服务端地址)
            连接 = OBJSocket(_套子)
            我.连接 = 连接
            return 连接
        except Exception as e:
            logger.error(f'{sys._getframe().f_code.co_name}:{e}')
            return None

    def _握手(我):
        assert 我.连接 is not None, '未连接'
        我.连接.send(暗号.我是客户端)
        接收的暗号 = 我.连接.recv()
        assert 接收的暗号 == 暗号.我是服务端, '暗号错误'
        return True


    def getport(我, name, ptype):
        哈希码 = hash(name)
        请求段 = 端口字段类()
        请求段.哈希码 = 哈希码
        请求段.来源 = PType.client
        请求段.端口名称 = name
        请求段.类型 = ptype
        我.连接.send(请求段)
        接收段 = 我.连接.recv()
        assert isinstance(接收段, 端口字段类), '端口分配错误'
        return 接收段

    def __enter__(我):
        assert 我._启动并连接()
        return 我

    def __exit__(我, exc_type, exc_val, exc_tb):
        if 我.连接 is not None:
            我.连接.close()
        return False  # 不处理异常
