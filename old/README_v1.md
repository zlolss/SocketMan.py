# SocketMan

- 对 [websockets](https://pypi.org/project/websockets/) 包的易用封装。
- 在独立线程中封装了协程
- 可以非阻塞方式交互
- 符合面向过程习惯的send、recv方法 

 
# 应用场景示例

- 针对flask+werkzeug的单线程模式服务器无法使用服务websocket的问题，创建独立的websocket服务。


# 使用方法

## 启动线程（服务端）
```python
serv = WebsocketServer('0.0.0.0', 5001)
serv.start()
```
## 客户端访问地址，服务未运行时为None
```python
print(serv.url)
```
## 设置处理接收消息的回调函数
```python
# 有消息传入时会随消息附带wsid， wsid为传入消息的连接编号
@serv.ON_RECV
def func( txt, wsid):
    print(txt)
```    
## 用recv方法接收，默认阻塞（不推荐）
```python
serv.recv()

# 当设置wsid!=None时只接收对应wsid连接发送的数据
# block=False为非阻塞模式，无消息返回None
# 接收过程中连接关闭则raise一个RuntimeError
serv.recv(wsid=None, block=True)
```
## 发送消息到客户端
```python
# 单个连接可以不带wsid参数，即wsid默认为None时将对所有连接广播消息
serv.send(txt)
serv.send(txt, wsid=None)
```
## 关闭线程
```python
# 注意，线程启动关闭是一次性行为，如需再次使用需要重新实例化
serv.stop()
```

## 检查是否已在运行
```python
serv.is_alive()
```

## 启动线程（客户端）
客户端与服务端的调用逻辑基本一致
```python
client = WebsocketClient('ws://localhost:5001')
client.start()
```
## 设置处理接收消息的回调函数
```python
@client.ON_RECV
def func( txt ):
    print(txt)
```    
## 用recv方法接收，默认阻塞（不推荐）
```python
client.recv()
```

## 发送消息到服务端
```python
client.send(txt)
```
## 关闭线程
```python
# 注意，线程启动关闭是一次性行为，如需再次使用需要重新实例化
client.stop()
```
## 检查是否已在运行
```python
client.is_alive()
```

