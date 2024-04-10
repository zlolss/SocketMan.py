from .client import Client
from .common import PType

def getPortAndCharacter(pname, ptype=PType.p2p):
    with Client() as c:
        端口字段 = c.getport(name=pname, ptype=ptype)
        return 端口字段.端口号, 端口字段.类型
