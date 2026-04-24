import os
from datetime import timedelta

# 项目根目录路径，用于定位项目文件和资源
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Flask基础配置
DEBUG = False  # 调试模式，生产环境应设置为False
SECRET_KEY = "health_food_system_2026"  # Flask应用密钥，用于会话管理和加密
PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # 会话有效期，7天

# 数据库配置
# 使用SQLite数据库（轻量级，适合开发和测试环境）
SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'health_food.db')}"  # 数据库连接URI
SQLALCHEMY_TRACK_MODIFICATIONS = False  # 禁用SQLAlchemy的修改跟踪，提高性能

# SQLAlchemy连接池配置（仅适用于支持连接池的数据库，如MySQL、PostgreSQL）
# SQLite不支持连接池参数，会自动使用NullPool
# 生产环境使用其他数据库时可以取消注释以下参数
# SQLALCHEMY_POOL_SIZE = 10  # 连接池大小
# SQLALCHEMY_POOL_TIMEOUT = 30  # 连接超时时间（秒）
# SQLALCHEMY_POOL_RECYCLE = 1800  # 连接回收时间（秒）
# SQLALCHEMY_MAX_OVERFLOW = 20  # 最大溢出连接数

# JWT Token配置
TOKEN_SECRET = "jwt_health_food_2026"  # JWT令牌密钥
TOKEN_EXPIRE = 86400 * 7  # 令牌过期时间，7天（单位：秒）

# 微信小程序配置
# 从环境变量读取，若环境变量不存在则使用默认值
WX_APPID = os.environ.get('WX_APPID', 'wx3b08203c772b2f67')  # 微信小程序AppID
WX_SECRET = os.environ.get('WX_SECRET', 'wx1d3b75be931bba28')  # 微信小程序AppSecret
WX_LOGIN_URL = "https://api.weixin.qq.com/sns/jscode2session"  # 微信登录API地址



# 智谱AI配置 - 使用智谱免费模型
ZHIPUAI_API_KEY = os.environ.get('ZHIPUAI_API_KEY', 'adbff1c3892644e1bef06d6dba1b1190.0HI68lIG4dNk0yO8')  # 智谱AI API Key
ZHIPUAI_BASE_URL = 'https://open.bigmodel.cn/api/paas/v4/'

# 智谱AI免费模型配置
ZHIPUAI_CHAT_MODEL = 'glm-4.7'                 # 免费对话模型
ZHIPUAI_VISION_MODEL = 'glm-4.6v-flash'        # 免费视觉模型
ZHIPUAI_THINKING_MODEL = 'glm-4.7'             # 免费思维模型
ZHIPUAI_IMAGE_MODEL = 'cogview-3-flash'        # 免费图像生成模型
ZHIPUAI_EMBEDDING_MODEL = 'embedding-2'         # 免费嵌入模型
ZHIPUAI_RERANK_MODEL = 'rerank'                 # 免费重排序模型

# Redis配置（用于缓存和会话存储）
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')  # Redis服务器地址
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))  # Redis端口
REDIS_DB = int(os.environ.get('REDIS_DB', 0))  # Redis数据库编号
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '')  # Redis密码

# 小红书爬虫配置
# 用于爬取热点美食数据
XHS_BASE_URL = "https://www.xiaohongshu.com"  # 小红书基础URL
XHS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}  # 爬虫请求头，模拟浏览器

# 小红书开放平台API配置
# 从环境变量读取，若环境变量不存在则使用默认值
XHS_CONFIG = {
    "app_key": os.environ.get('XHS_APP_KEY', '你的小红书开放平台app_key'),  # 小红书开放平台App Key
    "app_secret": os.environ.get('XHS_APP_SECRET', '你的小红书开放平台app_secret'),  # 小红书开放平台App Secret
    "cookies": os.environ.get('XHS_COOKIES', '')  # 小红书登录Cookies
}
