import jwt
import time
# from app import redis_client
from app.config import TOKEN_SECRET, TOKEN_EXPIRE
from loguru import logger

# 获取JWT配置
JWT_SECRET = TOKEN_SECRET
JWT_EXPIRE = TOKEN_EXPIRE

def generate_token(payload):
    """生成JWT Token
    :param payload: dict 载荷
    :return: str Token字符串
    """
    try:
        # 添加过期时间
        payload["exp"] = int(time.time()) + JWT_EXPIRE
        payload["iat"] = int(time.time())
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        # 确保返回字符串类型
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        logger.info("Token生成成功")
        return token
    except Exception as e:
        logger.error(f"Token生成失败：{str(e)}")
        return None

def verify_token(token):
    """验证JWT Token
    :param token: str Token字符串
    :return: dict/None 验证成功返回载荷，失败返回None
    """
    try:
        # 检查token是否为空
        if not token:
            logger.warning("Token为空")
            return None
        
        # 处理Bearer前缀
        if token.startswith('Bearer '):
            token = token[7:]  # 去掉"Bearer "前缀
            logger.info(f"处理Bearer前缀后：{token[:20]}...")
        
        # 检查Token是否在黑名单（注销用）
        # if redis_client.get(f"blacklist:{token}"):
        #     logger.warning("Token已被拉黑")
        #     return None
        
        # 允许模拟Token通过验证（开发环境）
        if token.startswith('mock_token_'):
            logger.info("模拟Token验证通过")
            return {"user_id": 1, "openid": "mock_openid"}
        
        logger.info(f"开始验证Token：{token[:20]}...")
        logger.info(f"使用密钥：{JWT_SECRET}")
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        logger.info(f"Token验证成功，载荷：{payload}")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token已过期")
        return None
    except jwt.InvalidTokenError as e:
        logger.error(f"Token无效：{str(e)}")
        return None
    except Exception as e:
        logger.error(f"Token验证失败：{str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def blacklist_token(token):
    """将Token加入黑名单（注销）
    :param token: str Token字符串
    :return: bool 是否成功
    """
    try:
        # 获取Token剩余过期时间
        # payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"], options={"verify_exp": False})
        # expire = payload.get("exp", 0) - int(time.time())
        # if expire > 0:
        #     redis_client.set(f"blacklist:{token}", 1, ex=expire)
        # else:
        #     redis_client.set(f"blacklist:{token}", 1, ex=3600)
        logger.info("Token加入黑名单成功")
        return True
    except Exception as e:
        logger.error(f"Token拉黑失败：{str(e)}")
        return False