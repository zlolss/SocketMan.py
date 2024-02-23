# SocketMan

- 对 [websockets](https://pypi.org/project/websockets/) 包的易用封装。
- 使用起来非常简单
- 可以对发送内容简单加密和压缩
- 可以用它发送任何python对象包括自定义的类
- 注意！上述操作存在安全风险

# 简单示例

## 服务端
```python
# 建立一个回调函数处理接收的内容
def returnmsg(msg, conn):
    # 这个函数将接收的消息原路返回
    print(f'send back msg:{msg}')
    conn.send(msg)
# 启动一个服务端
serv = socketman.createServer(port=5010, onrecv=returnmsg)
# 关闭服务端
serv.close()
```

## 客户端
```python
# 建立一个回调函数处理接收的内容
def printmsg(msg, conn):
    # 这个函数将接收的消息显示出来
    print(f'recievemsg:{msg}')
# 连接到服务端uri
conn = socketman.connect(uri = "ws://127.0.0.1:5010", onrecv=printmsg)
# 发送一个自定义类(类是通过pickle封装的，所以接收端需要有该类的定义才能正确接收)
class UserClass:
    n = 1
c = UserClass()
conn.send(c)
# 关闭连接
conn.close()
```

# Tips
- 开启AES加密需要在服务端和客户端设置相同的password，例如：
```python
serv = socketman.createServer(port=5010, password='abc')
conn = socketman.connect(uri = "ws://127.0.0.1:5010",  password='abc')
```
- 不加密发送纯字符串不会进行封装，可以当作标准的websocket使用，但开启加密或发送python对象仅支持本库的服务端和客户端。