# todo: bug
#from .websocketthread import _WebsocketThread, WebsocketClient, CONST
from threading import Thread
from .utils.infowrap import withcaller
from .utils.packing import pack, unpack
from .utils.iptools import getLocalIP, isValidIPV4, checkPort
import logging

logger = logging.getLogger()

_servers = {}
_connections = {}

def logmsg(msg):
    print(msg)
    logger.info(msg)


class Connection(Thread):

    def __init__(self, wsconn, onrecv=logmsg, info={}):
        super().__init__()
        self.info = info
        self.wsconn = wsconn
        self.onrecv = onrecv
        from asyncio import new_event_loop
        self.__loop = new_event_loop()
        self.__future = self.__loop.create_future()
        self.stopped = True
    
    def packmsg(self, msg):
        return pack(msg, password=self.info.get('password', None))
    
    def unpackmsg(self, msg):
        return unpack(msg, password=self.info.get('password', None))

    def send(self, msg):
        from asyncio import run_coroutine_threadsafe
        run_coroutine_threadsafe(self.wsconn.send(self.packmsg(msg)),loop=self.__loop)

    async def listener(self):
        while not(self.stopped):
            msg = await self.wsconn.recv()
            msg = self.unpackmsg(msg)
            # todo: 子线程管理
            t = Thread(target = self.__onrecv, args = [msg])
            t.start()

    async def __aclient(self):
        from asyncio import gather
        gather(self.listener(), self.__future)
        await self.__future

    def run(self):
        from asyncio import set_event_loop
        set_event_loop(self.__loop)
        self.stopped = False
        self.__loop.run_until_complete(self.__aclient())



class Server(Thread):

    def __init__(self, host='0.0.0.0', port=5001, connection_onrecv=logmsg, info={}):
        super().__init__()
        self.info = info
        self.host = host
        if isValidIPV4(host) or host.lower()=='localhost':
            self.ip = host
        else:
            self.ip = getLocalIP()
        if checkPort(port):
            self.port = port
        else:
            logger.error(f'请求的端口 {port} 被占用或无访问权限')
            # todo: 尝试其他端口
            raise Exception(f'请求的端口 {port} 被占用或无访问权限')
        from asyncio import new_event_loop
        self.__loop = new_event_loop()
        self.__future = self.__loop.create_future()
        self.stopped = True
        
        self.connection_onrecv = connection_onrecv
        self.onConnect = self.__onConnect
        self.connections = {}

    async def __onConnect(self, wsconn):
        # todo
        global _connections
        wsid = id(wsconn)
        if wsid in _connections or wsid in self.connections:
            logger.warning(f'连接id {wsid} 已存在')
        info = {'password': self.info.get('password', None)}
        conn = Connection(wsconn, self.connection_onrecv, info = info)
        conn.start()
        self.connections[wsid] = conn
        _connections[wsid] = conn
    
    async def __aserver(self):
        from websockets.server import serve
        async with serve(self.onConnect, self.host, self.port):
            await self.__future
    
    def run(self):
        logger.warning(f'启动服务 ws://{self.ip}:{self.port}')
        from asyncio import set_event_loop
        set_event_loop(self.__loop)
        self.stopped = False
        self.__loop.run_until_complete(self.__aserver())

@withcaller
def connect(caller, uri, *, onrecv=logmsg, password=None):
    import websockets
    global _connections
    # todo: debug
    import websockets.sync.client
    wsconn = websockets.sync.client.connect(uri=uri)
    wsid = id(wsconn)
    if wsid in _connections:
        logger.warning(f'连接id {wsid} 已存在')
    info = {'password': password, 'uri': uri}
    conn = Connection(wsconn, onrecv=onrecv, info = info)
    conn.start()
    _connections[wsid] = conn
    return conn


@withcaller
def createServer(
    caller, 
    port, 
    *,
    connection_onrecv=logmsg, 
    host='0.0.0.0', 
    name=None, 
    password=None
    ):
    global _servers
    sid = name or caller
    if sid in _servers and _servers[sid].is_alive():
        logger.warning("Listener '%s' already exists" % sid)
        #raise Exception("Listener '%s' already exists" % lid)
        return _servers[sid]
    
    # todo: check port
    info = {caller:caller, name:name, password:password}
    server = Server(
        host = host, 
        port=port, 
        connection_onrecv=connection_onrecv,
        info=info )
    _servers[sid] = server
    server.start()
    return server


    
