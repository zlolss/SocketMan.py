
'''
# 对websockets端单线程封装，方便在任意线程中启动，无需额外的线程调度。
# 开发的初衷是由于flask app在子线程中运行时无法同时兼容websocket服务
# 用法
## 启动服务（服务端）
serv = WebsocketServer('0.0.0.0', 5001)
serv.start()
## 客户端访问地址，服务未运行时为None
print(serv.url)

## 设置处理接收消息的回调函数，wsid为传入消息的连接编号
@serv.ON_RECV
def func( txt, wsid):
    print(txt)
    
## 用recv方法接收，默认阻塞（不推荐）
serv.recv()
# 当设置wsid!=None时只接收对应wsid连接发送的数据
# block=False为非阻塞模式，无消息返回None
# 接收过程中连接关闭则raise一个RuntimeError
serv.recv(wsid=None, block=True)

## 发送消息到客户端，wsid默认为None时将对所有连接广播消息
serv.send(txt)
serv.send(txt, wsid=None)

## 关闭服务（注意线程启动关闭是一次性行为，如需再次使用需要重新实例化）
serv.stop()

## 检查是否已在运行
serv.is_alive()

## 客户端与服务端的调用逻辑基本一致
## 启动客户端
client = WebsocketClient('ws://localhost:5001')
client.start()

## 以下方法与服务端基本一致
## 设置处理接收消息的回调函数
@client.ON_RECV
def func( txt ):
    print(txt)
    
## 用recv方法接收，默认阻塞（不推荐）
client.recv()


## 发送消息到客户端，wsid默认为None时将对所有连接广播消息
client.send(txt)

## 关闭服务（注意线程启动关闭是一次性行为，如需再次使用需要重新实例化）
client.stop()

## 检查是否已在运行
client.is_alive()


'''

def getLocalIP():
    from socket import socket, AF_INET, SOCK_DGRAM

    ip = '127.0.0.1'
    try:
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(('114.114.114.114',80)) # 连接一个dns获取网址
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip
    
    
def isValidIPV4(txt):
    # todo: 判断是否是一个合法的ipv4
    nums = txt.split('.')
    if len(nums)!=4:
        return False
    for num in nums:
        try:
            n = int(num)
            if n>255 or n<0:
                return False
        except:
            return False
    return txt.lower() not in  ["0.0.0.0", 'localhost']

    
class CONST:
    SERVER = 0
    CLIENT = 1


    
from threading import Thread as __Thread
class _WebsocketThread(__Thread):
    '''
    可以在线程中启动的简单websocket
    recv接收所有端口连接并send广播到所有连接
    '''
    def __init__(self, host_or_uri='127.0.0.1', port=5001, mtype=CONST.SERVER):
        from threading import Condition
        from asyncio import new_event_loop
        super().__init__()
        self.mtype = mtype
        if mtype==CONST.SERVER:
            self.ip = host_or_uri if isValidIPV4(host_or_uri) else getLocalIP()
            self.serve_on = host_or_uri
            self.__onrecv = lambda msg, wsid:print(f'server_receive from {wsid}: {msg}')
        elif mtype==CONST.CLIENT:
            self.uri = host_or_uri
            self.__onrecv = lambda msg:print(f'client_receive from {self.uri}: {msg}')
        self.port = port
        self.wsconns = {}
        self.__recv_cache = {None:None}
        self.__recv_condition = Condition()
        self.__loop = new_event_loop()
        self.__future = self.__loop.create_future()
        self.stopped = False
        
        
    @property
    def url(self):
        if self.is_alive() and self.mtype==CONST.SERVER:
            return f'ws://{self.ip}:{self.port}' 
        elif self.mtype==CONST.CLIENT:
            return self.uri
        return None
        
        
    def ON_RECV(self, func):
        from typing import Callable
        if isinstance(func, Callable):
            self.__onrecv = func
        return func
        
        
    def recv(self, wsid=None, block=True):
        # 为了兼容面向过程的习惯而设置，不推荐使用
        # 获取任意端口输入的消息，应该优先使用回调函数模式处理
        while wsid in self.__recv_cache and self.__recv_cache[wsid] is None and block:
            with self.__recv_condition:
                self.__recv_condition.wait()
                
        if wsid not in self.__recv_cache:
            raise RuntimeError(f'recv：连接{wsid}已关闭')
            
        msg = self.__recv_cache.get(wsid, None)
        self.__recv_cache[wsid] = None
        return msg

    
    def _send(self, msg , wsid):
        from asyncio import run_coroutine_threadsafe
        wsconn = self.wsconns.get(wsid, None)
        if wsconn is None:
            raise RuntimeError(f'send：错误的id{wsid}')
            return False
        run_coroutine_threadsafe(wsconn.send(msg),loop=self.__loop)
        return True
    
    
    def send(self, msg, wsid=None):
        if wsid is None:
            result = False
            for wsid in self.wsconns:
                result = self._send(msg, wsid)
            return result
        
        return self._send(msg, wsid)
            
    
    def __pushCache(self, msg, wsid=None):
        if self.__recv_cache[wsid] is None:
            self.__recv_cache[wsid] = msg
        else:
            self.__recv_cache[wsid] += msg
            
    
    
    async def handleConn(self, wsconn):
        wsid = id(wsconn)
        self.wsconns[wsid] = wsconn
        if wsid not in self.__recv_cache:
            self.__recv_cache[wsid] = None
        try:
            while not(self.stopped):
                msg = await wsconn.recv()
                
                if self.mtype==CONST.SERVER:
                    self.__onrecv( msg, wsid )
                elif self.mtype==CONST.CLIENT:
                    self.__onrecv( msg )
                
                self.__pushCache(msg, wsid)
                if wsid is not None:
                    self.__pushCache(msg)
                with self.__recv_condition:
                    self.__recv_condition.notify_all()
                    
        except Exception as e:
            print(e)
            pass
        finally:
        
            self.wsconns.pop(wsid, None)
            
            if wsid is not None:
                self.__recv_cache.pop(wsid, None)
                
    
    async def __aserver(self):
        from websockets.server import serve
        async with serve(self.handleConn, self.serve_on, self.port):
            await self.__future
            
    
    async def __aclient(self):
        from websockets.client import connect
        from asyncio import gather
        async with connect(self.uri) as wsconn:
            gather(self.handleConn(wsconn), self.__future)
            await self.__future

    
    async def astop(self):
        self.__future.set_result('')
    
    
    def stop(self):
        from asyncio import run_coroutine_threadsafe
        self.stopped = True
        run_coroutine_threadsafe(self.astop(),loop=self.__loop)
        with self.__recv_condition:
            self.__recv_condition.notify_all()
        self.join()
        self.wsconns = {}
        self.__recv_cache = {}
    
    
    def __del__(self):
        self.stop()
    
    
    def run(self):
        from asyncio import set_event_loop
        set_event_loop(self.__loop)
        if self.mtype==CONST.SERVER:
            self.__loop.run_until_complete(self.__aserver())
        elif self.mtype==CONST.CLIENT:
            self.__loop.run_until_complete(self.__aclient())
    
    
    
    
class WebsocketServer(_WebsocketThread):

    def __init__(self, host='127.0.0.1', port=5001):
        super().__init__(host_or_uri=host, port=port, mtype=CONST.SERVER)
    
    
class WebsocketClient(_WebsocketThread):

    def __init__(self, uri='ws://127.0.0.1:5001'):
        super().__init__(host_or_uri=uri, mtype=CONST.CLIENT)