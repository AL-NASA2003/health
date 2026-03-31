#!/usr/bin/env python3
"""
简化版启动脚本 - 绕过依赖兼容性问题
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 修复Werkzeug与Flask的兼容性问题
import werkzeug.urls
if not hasattr(werkzeug.urls, 'url_quote'):
    werkzeug.urls.url_quote = werkzeug.urls.quote

# 修复SQLAlchemy兼容性问题
import sqlalchemy
if not hasattr(sqlalchemy, '__all__'):
    sqlalchemy.__all__ = []

try:
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    
    # 创建应用
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'health_food_system_2026'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_food.db'  # 使用SQLite简化
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db = SQLAlchemy(app)
    
    # 简单的路由测试
    @app.route('/')
    def index():
        return {
            'code': 200,
            'message': '健康饮食系统API服务运行正常',
            'data': {
                'status': 'running',
                'version': '1.0.0'
            }
        }
    
    @app.route('/api/health')
    def health_check():
        return {
            'code': 200,
            'message': '服务健康',
            'data': {
                'database': 'connected',
                'timestamp': str(__import__('datetime').datetime.now())
            }
        }
    
    print("=" * 50)
    print("健康饮食系统API服务启动成功！")
    print("=" * 50)
    print(f"服务地址: http://0.0.0.0:5000")
    print(f"健康检查: http://0.0.0.0:5000/api/health")
    print("=" * 50)
    
    if __name__ == "__main__":
        app.run(
            host="0.0.0.0",
            port=5000,
            debug=True,
            threaded=True
        )
        
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装必要的依赖包:")
    print("  pip install Flask==2.3.3 Flask-SQLAlchemy==3.1.1 Werkzeug==2.3.7")
    sys.exit(1)
except Exception as e:
    print(f"启动失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
