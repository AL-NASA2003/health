from functools import wraps
from flask import request, g
from app.utils.jwt_token import verify_token
from app.utils.common import format_response


def login_required(f):
    """Token 验证装饰器
    用于验证请求中的 Token 是否有效
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
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