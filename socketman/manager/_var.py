import os, tempfile
import zlutils.shared as zls


允许远程 = False # False:端口只在本地使用
分配起始端口 = 23344
端口定义文件名 = 'socketman.info'

# 下面的内容不要修改
端口定义文件路径 = os.path.join( tempfile.gettempdir(), 端口定义文件名 )
服务地址 = '0.0.0.0' if 允许远程 else 'localhost'

class 端口管狸只因(zls.公鸡):
    端口 = 23333
    pid = -1

管狸只因的心跳 = zls.鸡心管理器(端口管狸只因)
获取服务绑定用地址 = lambda :(服务地址, 端口管狸只因.端口)

