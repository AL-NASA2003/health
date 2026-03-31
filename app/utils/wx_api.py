import requests
from app.config import WX_APPID, WX_SECRET, WX_LOGIN_URL
from loguru import logger

# 获取微信配置
# WX_APPID = config_map[env].WX_APPID
# WX_SECRET = config_map[env].WX_SECRET
# WX_LOGIN_URL = config_map[env].WX_LOGIN_URL

def wx_code2session(code):
    """微信小程序登录：code换取session_key和openid
    :param code: str 微信登录临时凭证
    :return: dict 微信返回结果
    """
    try:
        params = {
            "appid": WX_APPID,
            "secret": WX_SECRET,
            "js_code": code,
            "grant_type": "authorization_code"
        }
        response = requests.get(WX_LOGIN_URL, params=params, timeout=3)
        result = response.json()
        logger.info(f"微信code2session结果：{result}")
        return result
    except Exception as e:
        logger.error(f"微信登录接口调用失败：{str(e)}")
        return {"errcode": -1, "errmsg": str(e)}