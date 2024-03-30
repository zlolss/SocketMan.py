# 旧版本
from .websocketthread import WebsocketServer, WebsocketClient

# 新版本
from .v3 import createServer, connect, disconnect, stopServer, send 
