#from . import manager, serialization, auto_socket, objsocket
#from .manager import 自动分配端口
#auto_socket.序列化工具 = serialization
#auto_socket.端口管理器 = manager

#autosocket = auto_socket.autosocket


from .objsocket import OBJSocketServer, OBJSocketClinet
from .manager.common import PType
from .manager import getPortAndCharacter

import logging
logger = logging.getLogger()

def autoConnect(pname, /, passwd=None, ptype=PType.p2p, host='localhost'):
    端口, 端口类型 = getPortAndCharacter(pname, ptype)
    地址 = (host, 端口)
    # 按端口类型连接
    try:
        if 端口类型 == PType.server:
            服务端 = OBJSocketServer(addr=地址, passwd=passwd)
            连接, 地址 = 服务端.accept()
            return 连接
        elif 端口类型 == PType.client:
            连接 = OBJSocketClinet(addr=地址, passwd=passwd)
            return 连接
        else:
            logger.error(f'无法识别的请求类型{ptype}')
    except Exception as e:
        logger.error(f'{地址}无法连接:{e}')
        if ptype==PType.p2p:
            logger.warning(f'为{PType.p2p} 尝试反向连接')
            try:
                if 端口类型 == PType.client:
                    服务端 = OBJSocketServer(addr=地址, passwd=passwd)
                    连接, 地址 = 服务端.accept()
                    return 连接
                else:
                    连接 = OBJSocketClinet(addr=地址, passwd=passwd)
                    return 连接
            except Exception as e:
                logger.error(f'{地址}无法反向连接:{e}')
    raise RuntimeError(f'无法建立连接,请检查变量:{locals()}')
    return None
