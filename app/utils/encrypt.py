import hashlib
import base64
import os
from loguru import logger

# 尝试导入 AES 相关模块
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    AES_AVAILABLE = True
    # AES配置（从环境变量读取，16/24/32位）
    AES_KEY = os.environ.get('AES_KEY', 'health_food_2026_key').encode('utf-8')
    AES_IV = os.environ.get('AES_IV', 'health_food_iv_123').encode('utf-8')
except ImportError:
    logger.warning("pycryptodome 库未安装，AES 加密功能不可用")
    AES_AVAILABLE = False

def md5_encrypt(text):
    """MD5加密
    :param text: str 待加密字符串
    :return: str 加密结果
    """
    try:
        md5 = hashlib.md5()
        md5.update(text.encode("utf-8"))
        return md5.hexdigest()
    except Exception as e:
        logger.error(f"MD5加密失败：{str(e)}")
        return None

def aes_encrypt(text):
    """AES-CBC加密
    :param text: str 待加密字符串
    :return: str 加密结果（base64编码）
    """
    if not AES_AVAILABLE:
        logger.warning("AES 加密功能不可用")
        return text
    
    try:
        cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
        encrypted = cipher.encrypt(pad(text.encode("utf-8"), AES.block_size))
        return base64.b64encode(encrypted).decode("utf-8")
    except Exception as e:
        logger.error(f"AES加密失败：{str(e)}")
        return text

def aes_decrypt(encrypted_text):
    """AES-CBC解密
    :param encrypted_text: str 加密字符串（base64编码）
    :return: str 解密结果
    """
    if not AES_AVAILABLE:
        logger.warning("AES 解密功能不可用")
        return encrypted_text
    
    try:
        cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
        decrypted = unpad(cipher.decrypt(base64.b64decode(encrypted_text)), AES.block_size)
        return decrypted.decode("utf-8")
    except Exception as e:
        logger.error(f"AES解密失败：{str(e)}")
        return encrypted_text

# 别名函数，保持与user.py的导入一致
encrypt_data = aes_encrypt
decrypt_data = aes_decrypt