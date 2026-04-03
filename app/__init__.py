# 导入必要的库和模块
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from app.config import *  # 导入配置信息
import pymysql  # MySQL数据库驱动
from apscheduler.schedulers.background import BackgroundScheduler  # 定时任务调度器
import os  # 操作系统相关功能
from flask_restx import Api  # API文档生成
from flask_talisman import Talisman  # HTTPS安全增强
from flask_cors import CORS  # 跨域资源共享
from loguru import logger  # 导入日志库

# 解决MySQL兼容问题
pymysql.install_as_MySQLdb()

# 初始化数据库
# db是全局数据库实例，用于数据库操作
db = SQLAlchemy()

# 初始化定时任务
# scheduler用于管理定时任务，如数据备份、爬虫定时更新等
scheduler = BackgroundScheduler()

# 初始化 API 文档
# restx_api用于生成RESTful API文档，方便前端开发人员了解API接口
restx_api = Api(
    version='1.0',  # API版本
    title='健康饮食系统 API',  # API文档标题
    description='健康饮食系统的 RESTful API 文档',  # API文档描述
    doc='/api/docs'  # API文档访问路径
)


def create_app():
    """
    创建Flask应用实例
    此函数是Flask应用的工厂函数，负责初始化和配置应用
    """
    # 导入日志库
    from loguru import logger
    
    # 创建Flask应用实例
    app = Flask(__name__)
    
    # 加载配置
    # 从当前模块导入配置信息
    app.config.from_object(__name__)
    
    # 配置静态文件目录
    # 静态文件包括小程序前端资源，如图片、CSS、JavaScript等
    import os
    static_dir = os.path.join(BASE_DIR, 'miniprogram')  # 静态文件目录路径
    app.static_folder = static_dir  # 设置静态文件目录
    app.static_url_path = '/'  # 设置静态文件URL路径
    print(f'静态文件目录: {static_dir}')  # 打印静态文件目录
    print(f'静态文件URL路径: {app.static_url_path}')  # 打印静态文件URL路径
    
    # 确保上传目录存在
    upload_dir = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
        logger.info(f"创建上传目录: {upload_dir}")
    
    # 添加上传文件的路由
    @app.route('/static/uploads/<filename>')
    def serve_uploaded_file(filename):
        """提供上传文件的访问"""
        import os
        from flask import send_from_directory
        from loguru import logger
        try:
            upload_dir = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
            file_path = os.path.join(upload_dir, filename)
            logger.info(f"尝试访问文件: {file_path}")
            logger.info(f"文件是否存在: {os.path.exists(file_path)}")
            if os.path.exists(file_path):
                logger.info(f"文件存在，返回文件: {filename}")
                return send_from_directory(upload_dir, filename)
            else:
                logger.error(f"文件不存在: {file_path}")
                return "文件不存在", 404
        except Exception as e:
            logger.error(f"提供上传文件时发生错误: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return "服务器错误", 500
    
    # 初始化数据库
    # 将数据库实例与Flask应用关联
    db.init_app(app)
    
    # 初始化 API 文档
    # 将API文档实例与Flask应用关联
    restx_api.init_app(app)
    
    # 启用CORS（跨域资源共享）
    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Length"],
            "allow_credentials": True,
            "max_age": 86400
        }
    })
    
    # 创建数据库表（首次运行）
    # 在应用上下文中创建数据库表结构
    with app.app_context():
        # 导入所有模型，确保数据库表被创建
        # 导入用户模型
        from app.models.user import User
        # 导入饮食记录模型
        from app.models.diet_record import DietRecord
        # 导入食材模型
        from app.models.ingredient import Ingredient
        # 导入食谱和食谱食材关联模型
        from app.models.recipe import Recipe, RecipeIngredient
        # 导入热点美食模型
        from app.models.hot_food import HotFood
        # 导入论坛帖子模型
        from app.models.forum_post import ForumPost
        # 导入手账模型
        from app.models.hand_account import HandAccount
        # 导入评论模型
        from app.models.comment import Comment
        # 导入用户收藏模型
        from app.models.user_collection import UserCollection
        # 导入用户食材模型
        from app.models.user_ingredient import UserIngredient
        # 导入用户点赞模型
        from app.models.user_like import UserLike
        # 导入饮水记录模型
        from app.models.water_record import WaterRecord
        # 导入运动记录模型
        from app.models.exercise_record import ExerciseRecord
        # 导入健康指数记录模型
        from app.models.health_index_record import HealthIndexRecord
        # 导入饮食统计记录模型
        from app.models.diet_stat_record import DietStatRecord
        # 导入用户目标模型
        from app.models.user_goal import UserGoal
        
        # 创建所有数据库表
        db.create_all()
    
    # 注册使用Blueprint的API
    # Blueprint是Flask中组织路由的方式，用于将相关路由分组
    from app.api.like_api import like_bp  # 点赞相关API
    from app.api.forum_api import forum_bp  # 论坛相关API
    from app.api.handbook_api import handbook_bp  # 手账相关API
    from app.api.hot_food_api import hot_food_bp  # 热点美食相关API
    from app.api.ingredient_api import ingredient_bp  # 食材相关API
    from app.api.recipe_api import recipe_bp  # 食谱相关API
    from app.api.recommend_api import recommend_bp  # 推荐相关API
    from app.api.image_api import image_bp  # 图像生成相关API
    from app.api.remove_bg_api import remove_bg_bp  # 图像抠图相关API
    from app.api.nutrition_api import nutrition_bp  # 营养计算相关API
    from app.api.ai_assistant_api import ai_assistant_bp  # AI助手相关API
    
    # 注册Blueprint到应用，并设置URL前缀
    app.register_blueprint(like_bp, url_prefix="/api/like")  # 点赞API路径: /api/like
    app.register_blueprint(forum_bp, url_prefix="/api/forum")  # 论坛API路径: /api/forum
    app.register_blueprint(handbook_bp, url_prefix="/api/handbook")  # 手账API路径: /api/handbook
    app.register_blueprint(hot_food_bp, url_prefix="/api/hotfood")  # 热点美食API路径: /api/hotfood
    app.register_blueprint(ingredient_bp, url_prefix="/api/ingredient")  # 食材API路径: /api/ingredient
    app.register_blueprint(recipe_bp, url_prefix="/api/recipe")  # 食谱API路径: /api/recipe
    app.register_blueprint(recommend_bp, url_prefix="/api/recommend")  # 推荐API路径: /api/recommend
    app.register_blueprint(image_bp, url_prefix="/api/image")  # 图像生成API路径: /api/image
    app.register_blueprint(remove_bg_bp, url_prefix="/api/removebg")  # 图像抠图API路径: /api/removebg
    app.register_blueprint(nutrition_bp, url_prefix="/api/nutrition")  # 营养计算API路径: /api/nutrition
    app.register_blueprint(ai_assistant_bp, url_prefix="/api/ai")  # AI助手API路径: /api/ai
    
    # 导入并注册使用restx命名空间的API
    # 动态导入模块，避免循环导入问题
    import importlib
    
    # 导入模块
    user_api_module = importlib.import_module('app.api.user_api')  # 用户API模块
    diet_api_module = importlib.import_module('app.api.diet_api')  # 饮食记录API模块
    collection_api_module = importlib.import_module('app.api.collection_api')  # 收藏API模块
    comment_api_module = importlib.import_module('app.api.comment_api')  # 评论API模块
    upload_api_module = importlib.import_module('app.api.upload_api')  # 上传API模块
    wechat_api_module = importlib.import_module('app.api.wechat_api')  # 微信API模块
    water_api_module = importlib.import_module('app.api.water_api')  # 饮水记录API模块
    exercise_api_module = importlib.import_module('app.api.exercise_api')  # 运动记录API模块
    health_api_module = importlib.import_module('app.api.health_api')  # 健康相关API模块
    
    # 直接从模块中获取命名空间并注册
    restx_api.add_namespace(user_api_module.user_ns, path='/api/user')  # 用户API路径: /api/user
    restx_api.add_namespace(diet_api_module.diet_ns, path='/api/diet')  # 饮食记录API路径: /api/diet
    restx_api.add_namespace(collection_api_module.collection_ns, path='/api/collection')  # 收藏API路径: /api/collection
    restx_api.add_namespace(comment_api_module.comment_ns, path='/api/comment')  # 评论API路径: /api/comment
    restx_api.add_namespace(upload_api_module.upload_ns, path='/api/upload')  # 上传API路径: /api/upload
    restx_api.add_namespace(wechat_api_module.wechat_ns, path='/api/wechat')  # 微信API路径: /api/wechat
    restx_api.add_namespace(water_api_module.water_ns, path='/api/water')  # 饮水记录API路径: /api/water
    restx_api.add_namespace(exercise_api_module.exercise_ns, path='/api/exercise')  # 运动记录API路径: /api/exercise
    restx_api.add_namespace(health_api_module.health_ns, path='/api/health')  # 健康相关API路径: /api/health
    
    # 统一错误处理
    from app.utils.common import format_response  # 导入统一响应格式化函数
    
    @app.errorhandler(404)
    def not_found(error):
        """
        处理404错误（资源不存在）
        否则返回统一的404错误响应
        """
        return format_response(404, "资源不存在")
    
    @app.errorhandler(500)
    def internal_error(error):
        """
        处理500错误（服务器内部错误）
        返回统一的500错误响应
        """
        return format_response(500, "服务器内部错误")
    
    @app.errorhandler(400)
    def bad_request(error):
        """
        处理400错误（请求参数错误）
        返回统一的400错误响应
        """
        return format_response(400, "请求参数错误")
    
    # 启动定时任务（每半小时爬取一次小红书热点美食）
    # 暂时禁用爬虫任务，以便服务能够正常运行
    if False and not os.environ.get('DISABLE_SCHEDULER'):
        from app.crawler.xhs_drission_crawler import crawl_xhs_hot_food  # 导入爬虫函数
        import threading
        from loguru import logger
        
        # 启动时立即爬取一次（在后台线程中执行，避免阻塞启动）
        def start_crawl_on_startup():
            try:
                logger.info("后端启动，立即执行一次爬取任务")
                crawl_xhs_hot_food(force_login=False, manual=False)
            except Exception as e:
                logger.error(f"启动时爬取失败：{str(e)}")
        
        # 在后台线程中执行爬取，避免阻塞启动
        startup_thread = threading.Thread(target=start_crawl_on_startup)
        startup_thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
        startup_thread.start()
        
        # 添加定时任务，每2小时执行一次
        scheduler.add_job(crawl_xhs_hot_food, "interval", minutes=120, args=[False, False], id='auto_crawl', replace_existing=True)
        # 启动定时任务调度器
        scheduler.start()
        logger.info("定时任务已启动，每2小时执行一次爬取任务")
    else:
        logger.info("爬虫任务已禁用，服务将正常运行")
    
    # 启用 HTTPS 强制和安全头
    # 本地开发环境禁用 HTTPS 强制，生产环境启用
    # Talisman 默认强制 HTTPS，但在开发环境会导致问题
    if not app.debug and os.environ.get('ENABLE_TALISMAN', 'False').lower() == 'true':
        Talisman(app, content_security_policy=None, force_https=True)
    elif app.debug:
        # 开发环境，禁用 HTTPS 强制但保留安全头
        Talisman(app, content_security_policy=None, force_https=False)
    
    # 返回配置好的Flask应用实例
    return app