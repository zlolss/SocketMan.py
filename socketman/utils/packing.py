from typing import Any
import logging
import pickle, json, base64, zlib
from Crypto.Cipher import AES

logger = logging.getLogger()
_header_lenth = 4
_codectype = 'utf-8'
_aes_key_length = 32
class Headers:
    '''
    封装的头部标识（4个字符）
    '''
    def __getattr__(self, __name: str) -> Any:
        if __name in self.__dict__ and isinstance(self.__dict__[__name], str):
            return self.__dict__[__name][:_header_lenth].ljust(_header_lenth)
        
    def __setattr__(self, key, value):
        if key in self.__dict__:
            raise TypeError("常量不能被修改")
        self.__dict__[key] = value

    AES = 'AES+'
    PICKLE = 'PKL+'
    JSON = 'JSN+'
    BASE64 = 'B64+'
    ZIP = 'ZIP+'

def password2aeskey(password:str) -> bytes:
    return base64.b64encode(password.encode(_codectype))[:_aes_key_length].ljust(_aes_key_length)

def aes_encrypt(package:bytes, password:str) -> bytes:
    aeskey = password2aeskey(password)
    cipher = AES.new(aeskey, AES.MODE_OCB)
    ciphertext, tag = cipher.encrypt_and_digest(package)
    assert len(cipher.nonce) == 15
    nonce = cipher.nonce
    return tag + nonce + ciphertext
    pass

def aes_decrypt(package:bytes, password:str) -> bytes:
    aeskey = password2aeskey(password)
    tag, nonce, ciphertext = package[:16], package[16:31], package[31:]
    cipher = AES.new(aeskey, AES.MODE_OCB, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)
    pass

def pack(item:Any, password:str=None, compresssize=128000) -> str:
    '''
    将任意对象封装为websocket可以发送的字符串
    :param item: 待打包的对象
    :param password: 密码为空时不加密
    :param compresssize: 压缩阈值，当对象序列化后大于该值则进行简单压缩
    :return: 打包后的字符串
    '''
    package = item
    if isinstance(item, str):
        if password is None:
            return package
        package = item.encode(_codectype)
    else:
        try:
            # json可能造成浮点型数据的精度损失
            package = (Headers.JSON + json.dumps(item, ensure_ascii=False)).encode(_codectype)
        except Exception as e:
            #logger.warning(f'pack json error: {e}')
            try:
                package = Headers.PICKLE.encode(_codectype) + pickle.dumps(item)
            except Exception as e:
                #logger.warning(f'pack pickle error: {e}')
                logger.error(f'pack error: {e}')
        '''
        try:
            package = Headers.PICKLE.encode(_codectype) + pickle.dumps(item)
        except Exception as e:
            logger.warning(f'pack pickle error: {e}')
            logger.error(f'pack error: {e}')
        '''
    if len(package) > compresssize:
        try:
            package = Headers.ZIP.encode(_codectype) + zlib.compress(package)
        except Exception as e:
            logger.warning(f'pack zip error: {e}')
    if password is not None:
        try:
            package = Headers.AES.encode(_codectype) + aes_encrypt(package, password)
        except Exception as e:
            logger.warning(f'pack aes error: {e}')
    package = Headers.BASE64 + base64.encodebytes(package).decode(_codectype)
    return package

# 将任意对象封装为websocket可以发送的字符串
def unpack(package:str, password:str=None, raw=None) -> Any:
    '''
    websocket接收到的包解码为相应对象
    :param package: 待解包的对象
    :param password: 密码
    :param raw: 递归调用的中间量，用于保存原始字符串
    :return: 解包得到的对象
    '''
    if raw is None:
        raw = package
    head = package[:_header_lenth]
    if isinstance(head, bytes):
        try:
            head = head.decode(_codectype)
        except:
            logger.warning("bytes非法")
            return raw
    if head == Headers.AES:
        try:
            result =  aes_decrypt(package[_header_lenth:], password)
            return unpack(result, password, raw)
        except Exception as e:
            logger.warning(f"AES解密失败, 密码错误")
            return raw
    elif head == Headers.PICKLE:
        if password is None:
            logger.warning("""通过websocket传输python对象存在安全风险，
建议添加password参数启用AES加密""")
        try:
            return pickle.loads(package[_header_lenth:])
        except:
            logger.warning("Pickle解码失败")
            return raw
    elif head == Headers.JSON:
        try:
            return json.loads(package[_header_lenth:])
        except:
            logger.warning("JSON解码失败")
            return raw
    elif head == Headers.BASE64:
        try:
            b64str = package[_header_lenth:]
            if isinstance(b64str, bytes):
                b64byte = b64str
            else:
                b64byte = b64str.encode(_codectype)
            result = base64.decodebytes(b64byte)
            return unpack(result, password, raw)
        except Exception as e:
            logger.warning(f"Base64解码失败:{e}")
            return raw
    elif head == Headers.ZIP:
        try:
            result = zlib.decompress(package[_header_lenth:])
            return unpack(result, password, raw)
        except:
            logger.warning("ZIP解压失败")
            return raw
    if isinstance(package, bytes):
        try:
            return package.decode(_codectype)
        except:
            logger.warning("数据包可能损坏")
            return raw
    return package

