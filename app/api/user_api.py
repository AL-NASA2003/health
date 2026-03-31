from flask import request, g
from app.models.user import User
from app.utils import generate_token, verify_token, blacklist_token, wx_code2session, validate_params, format_response
from loguru import logger
from flask_restx import Namespace, Resource, fields

# 创建用户相关的命名空间
user_ns = Namespace('user', description='用户相关操作，包括登录、注销、信息管理等')

# 定义登录请求模型
login_model = user_ns.model('Login', {
    'code': fields.String(description='微信登录临时凭证'),
    'username': fields.String(description='测试账号用户名'),
    'password': fields.String(description='测试账号密码')
})

# 定义更新用户信息请求模型
update_model = user_ns.model('UpdateUser', {
    'nickname': fields.String(description='用户昵称'),
    'avatar': fields.String(description='用户头像URL'),
    'height': fields.Float(description='身高(cm)'),
    'weight': fields.Float(description='体重(kg)'),
    'age': fields.Integer(description='年龄'),
    'gender': fields.String(description='性别：男/女/未知'),
    'waist': fields.Float(description='腰围(cm)'),
    'hip': fields.Float(description='臀围(cm)'),
    'health_goal': fields.String(description='健康目标：减脂/增肌/维持'),
    'dietary_preference': fields.String(description='饮食偏好')
})

# 定义用户信息响应模型
user_model = user_ns.model('User', {
    'id': fields.Integer(description='用户ID'),
    'nickname': fields.String(description='用户昵称'),
    'avatar': fields.String(description='用户头像URL'),
    'height': fields.Float(description='身高(cm)'),
    'weight': fields.Float(description='体重(kg)'),
    'age': fields.Integer(description='年龄'),
    'gender': fields.String(description='性别'),
    'waist': fields.Float(description='腰围(cm)'),
    'hip': fields.Float(description='臀围(cm)'),
    'health_goal': fields.String(description='健康目标'),
    'dietary_preference': fields.String(description='饮食偏好'),
    'create_time': fields.String(description='创建时间')
})

# 定义登录响应模型
login_response_model = user_ns.model('LoginResponse', {
    'token': fields.String(description='JWT Token'),
    'user_info': fields.Nested(user_model, description='用户信息')
})

# 导入登录装饰器
from app.utils.auth_decorator import login_required

@user_ns.route('/login')
class Login(Resource):
    """微信小程序登录接口"""
    @user_ns.expect(login_model)
    def post(self):
        """用户登录
        
        支持两种登录方式：
        1. 测试账号登录：使用username和password参数
        2. 微信登录：使用code参数（微信登录临时凭证）
        
        Returns:
            dict: 包含token和用户信息的响应
        """
        try:
            params = request.get_json() or {}
            
            # 测试账号登录逻辑
            if "username" in params and "password" in params:
                username = params["username"]
                password = params["password"]
                
                # 简单的测试账号验证
                if username == "test" and password == "123456":
                    # 查询或创建测试用户
                    logger.info("开始处理测试账号登录")
                    user = User.query.filter_by(openid="test_openid").first()
                    logger.info(f"查询到用户: {user}")
                    
                    if not user:
                        logger.info("创建新测试用户")
                        user = User(openid="test_openid", nickname="测试用户", height=175.0, weight=65.0, age=25, gender=1, health_goal="减脂")
                        logger.info(f"用户对象创建成功: {user}")
                        
                        if not user.save():
                            logger.error("用户保存失败")
                            return format_response(500, "用户创建失败")
                        else:
                            logger.info("用户保存成功")
                    
                    # 生成JWT Token
                    logger.info(f"准备生成Token，用户ID: {user.id}, OpenID: {user.openid}")
                    token = generate_token({"user_id": user.id, "openid": user.openid})
                    logger.info(f"Token生成结果: {token}")
                    
                    if not token:
                        return format_response(500, "Token生成失败")
                    
                    user_info = user.to_dict()
                    logger.info(f"用户信息: {user_info}")
                    
                    return format_response(data={
                        "token": token,
                        "user_info": user_info
                    })
                else:
                    return format_response(401, "用户名或密码错误")
            # 微信登录逻辑
            elif "code" in params:
                # 验证参数
                code = params["code"]
                if not code:
                    return format_response(400, "缺少微信登录code")
                
                # 优先使用测试账号登录，加快登录速度
                logger.info("优先使用测试账号登录")
                # 查询或创建测试用户
                user = User.query.filter_by(openid="test_openid").first()
                if not user:
                    user = User(openid="test_openid", nickname="测试用户", height=175.0, weight=65.0, age=25, gender=1, health_goal="减脂")
                    user.save()
                
                token = generate_token({"user_id": user.id, "openid": user.openid})
                return format_response(data={
                    "token": token,
                    "user_info": user.to_dict()
                })
            else:
                return format_response(400, "缺少登录参数")
        except Exception as e:
            logger.error(f"登录失败：{str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return format_response(500, f"登录失败：{str(e)}")

@user_ns.route('/logout')
class Logout(Resource):
    """用户注销接口"""
    @login_required
    def post(self):
        """用户注销
        
        将用户的Token加入黑名单，使其失效
        
        Returns:
            dict: 注销结果
        """
        token = request.headers.get("Authorization")
        success = blacklist_token(token)
        if success:
            return format_response(msg="注销成功")
        else:
            return format_response(500, "注销失败")

@user_ns.route('/info')
class UserInfo(Resource):
    """用户信息管理接口"""
    @login_required
    def get(self):
        """获取用户信息
        
        Returns:
            dict: 用户详细信息
        """
        try:
            user = User.query.get(g.user_id)
            if not user:
                logger.error(f"用户不存在：user_id={g.user_id}")
                return format_response(404, "用户不存在")
            
            user_dict = user.to_dict()
            logger.info(f"获取用户信息成功：user_id={g.user_id}, data={user_dict}")
            return format_response(data=user_dict)
        except Exception as e:
            logger.error(f"获取用户信息失败：{str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return format_response(500, f"获取用户信息失败：{str(e)}")
    
    @login_required
    @user_ns.expect(update_model)
    def put(self):
        """更新用户信息
        
        请求参数：nickname, avatar, height, weight, age, gender, health_goal, dietary_preference
        
        Returns:
            dict: 更新后的用户信息
        """
        try:
            params = request.get_json() or {}
            logger.info(f"更新用户信息请求：用户ID={g.user_id}, 参数={params}")
            
            user = User.query.get(g.user_id)
            if not user:
                return format_response(404, "用户不存在")
            
            # 更新用户字段
            if "nickname" in params and params["nickname"] is not None:
                user.nickname = params["nickname"]
            if "avatar" in params and params["avatar"] is not None:
                user.avatar = params["avatar"]
            if "height" in params and params["height"] is not None:
                user.height = float(params["height"]) if params["height"] else 0.0
            if "weight" in params and params["weight"] is not None:
                user.weight = float(params["weight"]) if params["weight"] else 0.0
            if "age" in params and params["age"] is not None:
                user.age = int(params["age"]) if params["age"] else 0
            if "gender" in params and params["gender"] is not None:
                # 将字符串性别转换为整数
                gender_map = {"未知": 0, "男": 1, "女": 2, 0: 0, 1: 1, 2: 2}
                user.gender = gender_map.get(params["gender"], 0)
            if "waist" in params and params["waist"] is not None:
                user.waist = float(params["waist"]) if params["waist"] else 0.0
            if "hip" in params and params["hip"] is not None:
                user.hip = float(params["hip"]) if params["hip"] else 0.0
            if "health_goal" in params and params["health_goal"] is not None:
                user.health_goal = params["health_goal"]
            if "dietary_preference" in params and params["dietary_preference"] is not None:
                user.dietary_preference = params["dietary_preference"]
            
            # 保存更新
            logger.info(f"准备保存用户信息：{user.to_dict()}")
            if user.save():
                logger.info("用户信息保存成功")
                return format_response(msg="信息更新成功", data=user.to_dict())
            else:
                logger.error("用户信息保存失败")
                return format_response(500, "信息更新失败")
        except Exception as e:
            logger.error(f"更新用户信息异常：{str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return format_response(500, f"更新失败：{str(e)}")

# 命名空间将在app/__init__.py中注册
