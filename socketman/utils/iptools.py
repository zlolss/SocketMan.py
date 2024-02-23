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

import socket
def checkPort(port):
    try:
        # 创建一个socket对象
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 尝试连接到指定的端口
        result = sock.connect_ex(('localhost', port))
        # 如果结果是0，则端口没有被监听
        if result == 0:
            return False
        else:
            return True
    except socket.error as msg:
        return False