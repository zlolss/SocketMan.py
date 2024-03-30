from itertools import pairwise
import struct

class 协同流程:
    def __init__(我, 角色, 接口):
        我.角色 = 角色
        我.接口 = 接口
        我.创建流程()
        我.完成 = False
        我.下一个过程= None
        我.异常 = None
        try:
            我.执行流程()
            我.完成 = True
        except Exception as e:
            我.异常 = e
            我.完成 = False

    def 执行流程(我):
        for 角色, 行动 in pairwise(我.流程):
            if 角色==我.角色:
                行动()

    def 创建流程(我):
        我.问候语 = '你好'.encode('utf-8')
        我.流程 = [
            '客户端', lambda :我.连接.send(我.问候语),
            '服务端', lambda :assert 我.连接.recv(1024) == 我.问候语,
            '服务端', lambda :我.连接.send(我.问候语),
            '客户端', lambda :assert 我.连接.recv(1024) == 我.问候语,
            ]


class 握手(协同流程):
    '''
    角色: 客户端, 服务端
    '''

    def 创建流程(我):
        我.问候语 = '你好'.encode('utf-8')
        我.流程 = [
            '客户端', lambda :我.接口.连接.send(我.问候语),
            '服务端', lambda :assert 我.接口.连接.recv(1024) == 我.问候语,
            '服务端', lambda :我.连接.send(我.问候语),
            '客户端', lambda :assert 我.接口.连接.recv(1024) == 我.问候语,
            ]


class 分配端口和角色(协同流程):
    '''
    角色: 客户端(端口名称), 服务端
    成功返回端口和角色'''
    def 创建流程(我):
        我.流程 = [
            '客户端', lambda : 我.接口.连接.send('分配端口和角色'.encode('utf-8')),
            '服务端', lambda : assert 我.接口.连接.recv(1024).decode('utf-8') == '分配端口和角色',
            '服务端', lambda : 我.接口.连接.send('分配端口和角色'.encode('utf-8')),
            '客户端', lambda : assert 我.接口.连接.recv(1024).decode('utf-8') == '分配端口和角色',
            '客户端', lambda : 我.接口.连接.send(我.接口.端口名称.encode('utf-8')),
            '服务端', lambda : 我.端口名称 = 我.接口.连接.recv(1024).decode('utf-8'),
            '服务端', lambda : 我.端口, 我.角色, 我.异常 = 我.接口.根据名称分配端口和角色(我.端口名称)
            '服务端', lambda : assert 我.异常 is not None
            '服务端', lambda : 我.接口.连接.send(struct.pack('<L',))
            ]


流程表 = {
    '分配端口和角色': 分配端口和角色
    }

class 流程分配(协同流程):
    '''
    角色: 客户端(分配流程:str), 服务端

    '''

    def 创建流程(我):
        global 流程表
        我.流程 = [
            '客户端', lambda : 我.接口.连接.send(我.接口.分配流程.encode('utf-8')),
            '服务端', lambda : 我.分配流程 = 我.接口.连接.recv(1024).decode('utf-8'),
            '服务端', lambda : assert 我.分配流程 in 流程表,
            '服务端', lambda : 我.下一个过程 = 我.分配流程,
            '服务端', lambda : 我.接口.连接.send(我.分配流程.encode('utf-8')),
            '客户端', lambda : assert 我.接口.分配流程 == 我.接口.连接.recv(1024).decode('utf-8'),
            '客户端', lambda : 我.下一个过程 = 我.接口.分配流程
            ]

