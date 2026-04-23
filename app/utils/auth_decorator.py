from functools import wraps
from flask import request, g
from app.utils.jwt_token import verify_token
from app.utils.common import format_response
import os


def login_required(f):
    """Token 验证装饰器
    用于验证请求中的 Token 是否有效
    开发模式下临时禁用验证，方便调试
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 开发模式临时禁用token验证
        if os.environ.get('DISABLE_TOKEN_VERIFY') == 'True':
            print("⚠️ [开发模式] 跳过Token验证，使用固定user_id=1")
            g.user_id = 1
            g.valid = True
            return f(*args, **kwargs)
        
        token = request.headers.get("Authorization")
        if not token:
            return format_response(401, "缺少Token")
        
        payload = verify_token(token)
        if not payload:
            return format_response(401, "Token无效或已过期")
        
        g.user_id = payload.get("user_id")
        g.valid = True
        return f(*args, **kwargs)
    
    return decorated_function