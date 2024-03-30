# SocketMan

- 通过socket进行进程或python脚本间通信
- 可传输python对象
- 自动管理和分配端口
- 轻量化

# 安装
```bash
pip install socketman
```

# 使用
```python
# script_A

import socketman

def handle_recieve( robj, rconn ):
    print(robj)
    rconn.send({'reciverd':robj})

conn = conn = socketman.autosocket(name='mysocket', onrecvobj=handle_recieve)
conn.send({'test':'obj'})
```

```python
# script_B

import socketman

def handle_recieve( robj, rconn ):
    print(robj)

conn = conn = socketman.autosocket(name='mysocket', onrecvobj=handle_recieve)

```
