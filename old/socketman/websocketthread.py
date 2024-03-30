
'''
todo: client.reconnect
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
    return txt.lower() not in  ["0.0.0.0"]

    
class CONST:
    SERVER = 0
    CLIENT = 1


from .utils.packing import pack, unpack
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
            self.ip = host_or_uri if isValidIPV4(host_or_uri) or host_or_uri.lower()=='localhost' else getLocalIP()
            self.serve_on = host_or_uri #if host_or_uri.lower()!='localhost' else '127.0.0.1'
            self.onrecv = lambda msg, wsid:print(f'server_receive from {wsid}: {msg}')
        elif mtype==CONST.CLIENT:
            self.uri = host_or_uri
            self.onrecv = lambda msg:print(f'client_receive from {self.uri}: {msg}')
        self.port = port
        self.wsconns = {}
        self.__recv_cache = {None:None}
        self.__recv_condition = Condition()
        self.__loop = new_event_loop()
        self.__future = self.__loop.create_future()
        self.stopped = False
        self.onconnect = lambda wsconn:print(f'{wsconn} connected')
        self.ondisconnect = lambda wsconn:print(f'{wsconn} disconnected')
        
        
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
            self.onrecv = func
        return func
        
    def setCallback(self, func):
        from typing import Callable
        if isinstance(func, Callable):
            self.onrecv = func
        
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
        msg = self.packmsg(msg)
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
            
    def packmsg(self, msg):
        return msg
    
    def unpackmsg(self, msg):
        return msg
    
    async def handleConn(self, wsconn):
        #from asyncio import to_thread
        from threading import Thread
        wsid = id(wsconn)
        self.wsconns[wsid] = wsconn
        self.onconnect(wsconn)
        if wsid not in self.__recv_cache:
            self.__recv_cache[wsid] = None
        try:
            while not(self.stopped):
                msg = await wsconn.recv()
                msg = self.unpackmsg(msg)
                if self.mtype==CONST.SERVER:
                    t = Thread(target = self.onrecv, args = [msg, wsid])
                    t.start()
                    #await to_thread(self.__onrecv, args=[msg, wsid])
                    #self.__onrecv( msg, wsid )
                elif self.mtype==CONST.CLIENT:
                    t = Thread(target = self.onrecv, args = [msg])
                    t.start()
                    #await to_thread(self.__onrecv, args=[msg])
                    #self.__onrecv( msg )
                
                self.__pushCache(msg, wsid)
                if wsid is not None:
                    self.__pushCache(msg)
                with self.__recv_condition:
                    self.__recv_condition.notify_all()
                    
        except Exception as e:
            print(e)
            pass
        finally:
            self.ondisconnect(wsconn)
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
        with self.__recv_condition:
            self.__recv_condition.notify_all()
        run_coroutine_threadsafe(self.astop(),loop=self.__loop)
        try:
            self.join()
        except:
            pass
        self.wsconns = {}
        self.__recv_cache = {}
    
    
    def __del__(self):
        if not self.stopped:
            self.stop()

    
    def run(self):
        from asyncio import set_event_loop
        set_event_loop(self.__loop)
        if self.mtype==CONST.SERVER:
            self.__loop.run_until_complete(self.__aserver())
        elif self.mtype==CONST.CLIENT:
            self.__loop.run_until_complete(self.__aclient())
    
    
    
    
class WebsocketServer(_WebsocketThread):

    def __init__(self, host='127.0.0.1', port=5001, info={}):
        super().__init__(host_or_uri=host, port=port, mtype=CONST.SERVER)
        self.info = info
    
    
class WebsocketClient(_WebsocketThread):

    def __init__(self, uri='ws://127.0.0.1:5001', info={}):
        super().__init__(host_or_uri=uri, mtype=CONST.CLIENT)
        self.info = info