from zlutils.const import 字段类
from socketman.manager.common import PType, 参数, 暗号, 端口字段类, 检查端口号格式
from socketman.objsocket import OBJSocket, OBJSocketServer
import socket
import logging
logger = logging.getLogger()

_端口定义 = {}

class 端口定义字段类(字段类):
    端口号 = None
    端口名称 = None
    请求次数 = 0
    分配类型 = None


def 从文件载入端口定义():
    import os, json
    global _端口定义
    if os.path.exists(参数.端口定义文件路径):
        try:
            with open(参数.端口定义文件路径, 'rt') as fp:
                _端口定义 =  json.load(fp)
        except:
            pass
    return _端口定义


def 保存端口定义到文件():
    import os, json
    global _端口定义
    try:
        with open(参数.端口定义文件路径, 'wt') as fp:
            json.dump(_端口定义 ,fp)
    except:
        pass



def 检查端口是否可以绑定(端口):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as 套子:
            套子.bind(('localhost', 端口))
    except Exception as e:
        logger.warning(f"{端口}:{e}")
        return False
    return True


def 从给定端口开始查找可用的端口(第一个端口, 最大尝试次数=10):
    for 增量 in range(最大尝试次数):
        if 检查端口是否可以绑定(第一个端口+增量):
            return 第一个端口+增量
    return None

'''
def 根据名称分配端口(端口名称):
    global _端口定义
    assert type(端口名称) is str and len(端口名称)>0
    if 端口名称 in _端口定义:
        return _端口定义[端口名称], '客户端', None
    可用端口 = 从给定端口开始查找可用的端口(max(_var.分配起始端口, max(_端口定义.values())+1 if len(_端口定义)>0 else -1))
    if 可用端口 is not None:
        _端口定义[端口名称] = 可用端口
        保存端口定义文件()
        return 可用端口, '服务端', None
    return None, None, None
'''

def 获取已分配的最大端口号():
    global _端口定义
    return max(参数.默认可分配端口, max([定义.端口号 for 定义 in _端口定义.values()])+1 if len(_端口定义)>0 else -1)


def 获取新端口():
    起始端口号 = 获取已分配的最大端口号()
    可用端口 = 从给定端口开始查找可用的端口(起始端口号)
    assert 可用端口 is not None
    return 可用端口


def 分配端口(端口名称, 分配类型):
    # 返回; 端口号, 类型
    global _端口定义
    if 分配类型 == PType.p2p:
        if 端口名称 in _端口定义:
            assert _端口定义[端口名称].分配类型 == PType.p2p, f'{端口名称},已被非配为{_端口定义[端口名称].分配类型}类型,非{PType.p2p}类型'
            #assert _端口定义[端口名称].请求次数 < 2, 'p2p端口不能重复分配'
            端口号 = _端口定义[端口名称].端口号
            端口类型 = PType.client if _端口定义[端口名称].请求次数 % 2 == 1 else PType.server
            _端口定义[端口名称].请求次数 += 1
            #del _端口定义[端口名称] # p2p端口两次分配后删除定义
        else:
            端口号 = 获取新端口()
            assert 端口号 >= 参数.默认可分配端口
            端口类型 = PType.server
            端口字段 = 端口定义字段类()
            端口字段.端口号 = 端口号
            端口字段.端口名称 = 端口名称
            端口字段.分配类型 = PType.p2p
            端口字段.请求次数 = 1
            _端口定义[端口名称] = 端口字段
    elif 分配类型 == PType.server:
        if 端口名称 in _端口定义:
            assert _端口定义[端口名称].分配类型 == PType.free
            端口号 = _端口定义[端口名称].端口号
            端口类型 = PType.server
        else:
            端口号 = 获取新端口()
            assert 端口号 >= 参数.默认可分配端口
            端口类型 = PType.server
            端口字段 = 端口定义字段类()
            端口字段.端口号 = 端口号
            端口字段.端口名称 = 端口名称
            端口字段.分配类型 = PType.free
            端口字段.请求次数 = 1
            _端口定义[端口名称] = 端口字段
    elif 分配类型 == PType.client:
        if 端口名称 in _端口定义:
            assert _端口定义[端口名称].分配类型 == PType.free
            端口号 = _端口定义[端口名称].端口号
            端口类型 = PType.client
        else:
            端口号 = 获取新端口()
            assert 端口号 >= 参数.默认可分配端口
            端口类型 = PType.client
            端口字段 = 端口定义字段类()
            端口字段.端口号 = 端口号
            端口字段.端口名称 = 端口名称
            端口字段.分配类型 = PType.free
            端口字段.请求次数 = 1
            _端口定义[端口名称] = 端口字段
    if 参数.保存端口定义到文件:
        保存端口定义到文件()
    return 端口号, 端口类型


def 握手(连接):
    assert 连接 is not None
    连接.send(暗号.我是服务端)
    assert 连接.recv() == 暗号.我是客户端
    return True

def 处理请求(连接):
    请求段 = 连接.recv()
    assert isinstance(请求段, 端口字段类)
    回复段 = 请求段
    回复段.端口号, 回复段.类型 = 分配端口(端口名称 = 请求段.端口名称, 分配类型=请求段.类型)
    assert 回复段.端口号 >= 参数.默认可分配端口
    连接.send(回复段)

# =============================================== 主程序
logger.warning(f'正在绑定服务端口:{参数.服务端地址}')
套子 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
套子.bind(参数.服务端地址)
logger.warning(f'{参数.服务端地址} 绑定成功,开始监听')
套子.listen(1)
while True:
    连接, 地址 = 套子.accept()
    对象连接 = OBJSocket(连接)
    try:
        握手(对象连接)
        处理请求(对象连接)
    except Exception as e:
        logger.error(f'主程序错误:{e}')
    finally:
        if 对象连接 is not None:
            对象连接.close()



