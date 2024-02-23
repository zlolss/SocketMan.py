#from .websocketthread import _WebsocketThread, CONST

import logging

logger = logging.getLogger()

def logmsg(msg, wsconn=None):
    print(msg)
    logger.info(msg)


from .utils.packing import pack, unpack
from asyncio import run_coroutine_threadsafe
class Connection:

    def __init__(
            self, 
            wsconn, 
            event_loop = None,
            onrecv = logmsg,
            onconnect = logmsg,
            ondisconnect = logmsg,
            info = {}
            ) -> None:
        import asyncio
        from typing import Callable
        self.wsconn = wsconn
        if isinstance(event_loop, asyncio.events.AbstractEventLoop):
            self.__loop = event_loop
        else:
            logger.warning('event_loop is not a valid asyncio event loop')
            self.__loop = asyncio.get_event_loop()
        if isinstance(onrecv, Callable):
            self.onrecv = onrecv
        else:
            logger.warning('onrecv is not a valid function')
            self.onrecv = logmsg
        if isinstance(onconnect, Callable):
            self.onconnect = onconnect
        else:
            logger.warning('onconnect is not a valid function')
            self.onconnect = logmsg
        if isinstance(ondisconnect, Callable):
            self.ondisconnect = ondisconnect
        else:
            logger.warning('ondisconnect is not a valid function')
            self.ondisconnect = logmsg
        self.info = info
        from concurrent.futures import ThreadPoolExecutor
        self.callback_executor = ThreadPoolExecutor(max_workers=10)
        self.awaiter = self.__alisten()

    def send(self, msg):
        msg = self.packmsg(msg)
        #self.__loop.create_task(self.wsconn.send(msg)) # addtask 会被recv阻塞
        run_coroutine_threadsafe(self.wsconn.send(msg), self.__loop)
        
    async def __alisten(self):
        #self.onconnect(self.info, self)
        self.callback_executor.submit(self.onconnect, self.info, self)
        try:
            while True:
                msg = await self.wsconn.recv()
                msg = self.unpackmsg(msg)
                self.callback_executor.submit(self.onrecv, msg, self)
                #self.onrecv(msg, self)
        except Exception as e:
            logger.error(e)
        finally:
            #self.ondisconnect(self.info, self)
            self.callback_executor.submit(self.ondisconnect, self.info, self)

    def recv(self):
        logger.warning('recv不会接收任何东西，使用onrecv(msg, connection)处理接收的内容')
        pass

    def packmsg(self, msg):
        return pack(msg, password=self.info.get('password', None))
    
    def unpackmsg(self, msg):
        return unpack(msg, password=self.info.get('password', None))
    
    def close(self):
        run_coroutine_threadsafe(self.wsconn.close(), self.__loop)
        self.awaiter.close()
        #todo
        pass


from threading import Thread
class Server(Thread):

    def __init__(
            self, 
            host='127.0.0.1', 
            port=5001, 
            onrecv=logmsg, 
            info={}
            ):
        from .utils.iptools import getLocalIP, isValidIPV4, checkPort
        super().__init__()        
        self.info = info
        self.host = host
        self.ip = host if isValidIPV4(host) or host.lower()=='localhost' else getLocalIP()
        self.port = port
        self.conn_onrecv = onrecv
        from asyncio import new_event_loop
        self.__loop = new_event_loop()
        self.__future = self.__loop.create_future()
        self.connections = []
        self.atask = None

    async def handleConn(self, wsconn):
        conn = Connection(wsconn=wsconn, event_loop=self.__loop, onrecv=self.conn_onrecv, info=self.info)
        #self.__loop.create_task(conn.alisten())
        self.connections.append(conn)
        await conn.awaiter
        self.connections.remove(conn)
        #conn.alisten()

    def send(self, msg, conn=None):
        if conn is None:
            for conn in self.connections:
                conn.send(msg)
        else:
            conn.send(msg)

    async def __aserver(self):
        from websockets.server import serve
        async with serve(self.handleConn, self.host, self.port):
            await self.__future

    async def aserver(self):
        self.atask = self.__loop.create_task(self.__aserver())
        await self.atask
    
    def run(self):
        from asyncio import set_event_loop
        set_event_loop(self.__loop)
        self.__loop.run_until_complete(self.aserver())

    def close(self):
        for conn in self.connections:
            conn.close()
        self.__future.cancel()
        #self.__future.set_result("")
        if self.atask is not None:
            self.atask.cancel()
        else:
            logger.error('not a task')
        #self.aserver.close()
        try:
            self.__loop.stop()
        except Exception as e:
            #logger.error(e)
            pass
        # todo

_servers = {}
from .utils.infowrap import withcaller
@withcaller
def createServer(
    caller, 
    port, 
    *,
    onrecv=logmsg, 
    host='0.0.0.0', 
    name=None, 
    password=None
    ):
    global _servers
    sid = name or caller
    if sid in _servers and _servers[sid].is_alive():
        logger.warning("Server '%s' already running" % sid)
        #raise Exception("Listener '%s' already exists" % lid)
        return _servers[sid]
    # todo: check port
    info = {'caller':caller, 'name':name, 'password':password}
    server = Server(
        host = host, 
        port=port, 
        onrecv=onrecv,
        info=info )
    _servers[sid] = server
    server.start()
    logger.warning(f'websocket服务于ws://{server.ip}:{server.port}')
    return server

@withcaller
def closeServer(caller, name=None):
    global _servers
    sid = name or caller
    if sid in _servers:
        _servers[sid].close()
        del _servers[sid]
    else:
        logger.warning("Server '%s' not found" % sid)


from threading import Thread
class Client(Thread):
    def __init__(
            self, 
            uri, 
            onrecv=logmsg, 
            info={}
            ):
        super().__init__()
        self.uri = uri
        self.onrecv = onrecv
        self.info = info
        from asyncio import new_event_loop
        self.__loop = new_event_loop()
        self.conn = None
        self.atask = None
        #self.__future = self.__loop.create_future()

    async def __aclient(self):
        import websockets.client
        async with websockets.client.connect(self.uri) as wsconn:
            conn = Connection(wsconn=wsconn, event_loop=self.__loop, onrecv=self.onrecv, info=self.info)
            self.conn = conn
            await conn.awaiter

    async def aclient(self):
        self.atask = self.__loop.create_task(self.__aclient())
        await self.atask

    def send(self, msg):
        return self.conn.send(msg)

    def run(self) -> None:
        from asyncio import set_event_loop
        set_event_loop(self.__loop)
        self.__loop.run_until_complete(self.aclient())
    
    def close(self):
        self.conn.close()
        self.atask.cancel()
        try:
            self.__loop.close()
        except Exception as e:
            logger.error(f"{e}")

_clients = {}
from .utils.infowrap import withcaller
@withcaller
def connect(caller, uri, onrecv=logmsg, *, name=None, password=None):
    global _clients
    cid = name or caller
    if cid in _clients and _clients[cid].is_alive():
        logger.warning(f"{cid} already connected")
        return _clients[cid]
    info = {"name": name, "password": password}
    client = Client(uri, onrecv=onrecv, info=info)
    client.start()
    _clients[cid] = client
    import time
    t0 = time.time()
    while not client.conn and (time.time()-t0)<10: # timeout 10s
        time.sleep(0.1)
    if not client.conn:
        raise RuntimeError(f"{cid} failed to connect")
    return client.conn

from .utils.infowrap import withcaller
@withcaller
def disconnect(caller, name=None):
    global _clients
    cid = name or caller
    if cid not in _clients:
        logger.warning(f"{cid} not connected")
        return
    client = _clients[cid]
    client.close()
    del _clients[cid]

@withcaller
def send(caller, name=None, msg=None):
    global _clients
    cid = name or caller
    if cid not in _clients:
        logger.warning(f"{cid} not connected")
        return
    client = _clients[cid]
    client.send(msg)

@withcaller
def stopServer(caller, name=None):
    global _servers
    sid = name or caller
    if sid not in _servers:
        logger.warning(f"{sid} not started")
        return
    server = _servers[sid]
    server.close()
    del _servers[sid]
