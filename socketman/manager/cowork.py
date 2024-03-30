import struct


class 协作流程:
    def __init__(我, 接口):
        我.成功 = False
        我.接口 = 接口

    def 接收(我, 超时=None):
        我.接口['连接'].settimeout(超时)
        文本 =  我.接口['连接'].recv(1024).decode('utf-8')
        if 超时:
            我.接口['连接'].settimeout(None)
        return 文本

    def 接收二进制序列(我, 超时=None):
        我.接口['连接'].settimeout(超时)
        文本 =  我.接口['连接'].recv(1024)
        if 超时:
            我.接口['连接'].settimeout(None)
        return 文本

    def 发送二进制序列(我, 文本):
        return 我.接口['连接'].send(文本)

    def 发送(我, 文本):
        return 我.接口['连接'].send(文本.encode('utf-8'))

    def 角色(我, 角色):
        try:
            if 角色 == '甲方':
                return 我.甲方流程()
            elif 角色 == '乙方':
                return 我.乙方流程()
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def 甲方流程(我):
        return True

    def 乙方流程(我):
        return True


class 握手(协作流程):

    def 甲方流程(我):
        我.接收的内容 = 我.接收(超时 = 5)
        #print(我.接收的内容)
        if 我.接收的内容 != '握手':
            return False
        我.发送('握手2')
        return True

    def 乙方流程(我):
        我.发送('握手')
        我.接收的内容 = 我.接收(超时 = 5)
        #print(我.接收的内容)
        if 我.接收的内容!= '握手2':
            return False
        return True


class 分配端口(协作流程):
    分配信息打包 = '<L9s'

    def 甲方流程(我):
        我.发送(我.接口['端口名称'])
        序列 = 我.接收二进制序列(超时 = 15)
        我.端口, 我.角色 =  struct.unpack(我.分配信息打包, 序列)
        我.角色 = 我.角色.decode('utf-8')
        if 我.角色 not in ['服务端', '客户端']:
            return False
        return True

    def 乙方流程(我):
        我.端口名称 = 我.接收(超时 = 5)
        端口, 角色, 异常 =  我.接口['根据名称分配端口'](我.端口名称)
        if 异常:
            return False
        我.发送二进制序列(struct.pack(我.分配信息打包, 端口, 角色.encode('utf-8')))
        return True





