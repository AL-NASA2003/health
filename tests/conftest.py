import pytest
import sys
import os

# 添加项目根目录到 Python 导入路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app import db

@pytest.fixture
def app():
    """创建测试应用"""
    # 设置环境变量，使用测试配置
    os.environ['DISABLE_SCHEDULER'] = 'True'
    
    # 创建应用实例
    app = create_app()
    
    # 配置测试环境
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # 使用内存数据库
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.app_context():
        # 创建数据库表
        db.create_all()
        yield app
        # 测试结束后清理数据库
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()
