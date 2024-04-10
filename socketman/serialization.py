import pickle, json, base64, zlib
from Crypto.Cipher import AES

_文本编码 = 'utf-8'


class AES_二进制:
    _aes密码长度 = 32

    def __init__(我, 密码):
        我.aes密码 = 我.密码规范化(密码)

    def 密码规范化(我, 密码):
        return base64.b64encode(密码.encode(_文本编码))[:AES_二进制._aes密码长度].ljust(AES_二进制._aes密码长度)

    def 加密(我, 序列):
        编解码器 = AES.new(我.aes密码, AES.MODE_OCB)
        密文, 标签 = 编解码器.encrypt_and_digest(序列)
        assert len(编解码器.nonce) == 15
        随机码 = cipher.nonce
        return 标签 + 随机码 + 密文

    def 解密(我, 序列):
        标签, 随机码, 密文 = 序列[:16], 序列[16:31], 序列[31:]
        编解码器 = AES.new(我.aes密码, AES.MODE_OCB, nonce=随机码)
        return 编解码器.decrypt_and_verify(密文, 标签)


class 二进制序列:

    class _打包头:
        头长度 = 4
        AES = 'AES+'.encode(_文本编码)
        PICKLE = 'PKL+'.encode(_文本编码)
        #JSON = 'JSN+'.encode(_文本编码)
        #BASE64 = 'B64+'.encode(_文本编码)
        ZIP = 'ZIP+'.encode(_文本编码)


    def __init__(我, 密码=None, 压缩阈值=12800):
        我.密码 = 密码
        我.压缩阈值 = 压缩阈值

    def 序列化(我, python对象):
        序列 = 二进制序列._打包头.PICKLE + pickle.dumps(python对象)
        if len(序列) > 我.压缩阈值:
            序列 = 二进制序列._打包头.ZIP + zlib.compress(序列)
        if 我.密码:
            序列 = 二进制序列._打包头.AES + AES_二进制(我.密码).加密(序列)
        我.结果 = 序列
        return 序列

    def 反序列化(我, 序列):
        头长度 = 二进制序列._打包头.头长度
        if 序列[:头长度] == 二进制序列._打包头.AES:
            序列 = AES_二进制(我.密码).解密(序列[头长度:])
        if 序列[:头长度] == 二进制序列._打包头.ZIP:
            序列 = zlib.decompress(序列[头长度:])
        if 序列[:头长度] == 二进制序列._打包头.PICKLE:
            python对象 = pickle.loads(序列[头长度:])
        我.结果 = python对象
        return python对象

