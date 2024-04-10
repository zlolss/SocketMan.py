from zlutils.const import  模式类, 常量类, 字段类
import logging
logger = logging.getLogger()


class PType(模式类):
    # 端口类型
    p2p = 0
    free = 0
    server = 0
    client = 0


def 检查端口号格式(端口号):
    if 端口号 is None:
        return None
    端口号 = int(端口号)
    if 端口号>=1024:
        return 端口号
    logger.error(f'端口号{端口号}不合法')
    return None


import os, tempfile
class 参数(常量类):

    默认服务端口 = 23333
    定义服务端口的环境变量名 = 'SOCKETMAN_PORT'
    环境变量中的服务端口 = 检查端口号格式(os.environ.get(定义服务端口的环境变量名)) or 默认服务端口
    服务端地址 = ('localhost', 环境变量中的服务端口)
    服务端启动等待时间 = 3

    默认可分配端口 = 23344
    保存端口定义到文件 = True
    端口定义文件名 = 'socketman.info'
    端口定义文件路径 = os.path.join( tempfile.gettempdir(), 端口定义文件名 )




class 暗号(常量类):

    我是客户端 = 'R1aeiiwMjvJaXA=='
    我是服务端 = '9MSGO8Op7y30SQ=='


class 端口字段类(字段类):

    哈希码:int = None
    来源:PType = None
    类型:PType = None
    端口名称:str = None
    端口号:int = None

