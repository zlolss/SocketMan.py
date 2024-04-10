# SocketMan

- 通过socket进行进程或python脚本间通信
- 可传输python对象
- 通过命名而非端口号管理和分配端口
- 自动查找可用端口
- 简单数据加密
- 试验用途, 请勿在生产环境中使用

# 安装
```bash
pip install socketman
```

# 使用
- 一个程序间通信的样例
```python
# script_A

from socketman import autoConnect

def handle_recieve( eventparams ):
    print(eventparams)
    rconn.send({'reciverd':eventparams['obj']})

conn = autoConnect('端口a')
conn.autorecv(handle_recieve) # 自动接收消息
```

```python
# script_B

from socketman import autoConnect

conn = autoConnect('端口a')
conn.send({'test':'obj'})
print(conn.recv())
conn.close()

```

## 进阶使用

```python
import socketman
conn = autoConnect(pname='端口a', passwd='abcde', ptype=socketman.PType.p2p, host='localhost')

```
