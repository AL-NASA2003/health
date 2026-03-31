#!/usr/bin/env python3
"""
最小化启动脚本 - 仅用于验证Flask环境
"""
import sys
import os
from datetime import datetime

# 修复Werkzeug与Flask的兼容性问题
import werkzeug.urls
if not hasattr(werkzeug.urls, 'url_quote'):
    werkzeug.urls.url_quote = werkzeug.urls.quote

try:
    from flask import Flask, jsonify
    
    # 创建应用
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'health_food_system_2026'
    
    # 简单的路由测试
    @app.route('/')
    def index():
        return jsonify({
            'code': 200,
            'message': '健康饮食系统API服务运行正常',
            'data': {
                'status': 'running',
                'version': '1.0.0',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'code': 200,
            'message': '服务健康',
            'data': {
                'status': 'ok',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    
    @app.route('/api/user/register', methods=['POST'])
    def register():
        return jsonify({
            'code': 200,
            'message': '注册接口（待实现）',
            'data': None
        })
    
    @app.route('/api/user/login', methods=['POST'])
    def login():
        return jsonify({
            'code': 200,
            'message': '登录接口（待实现）',
            'data': None
        })
    
    print("=" * 60)
    print("🎉 健康饮食系统API服务启动成功！")
    print("=" * 60)
    print(f"📍 服务地址: http://0.0.0.0:5000")
    print(f"📍 健康检查: http://0.0.0.0:5000/api/health")
    print(f"📍 用户注册: POST http://0.0.0.0:5000/api/user/register")
    print(f"📍 用户登录: POST http://0.0.0.0:5000/api/user/login")
    print("=" * 60)
    print("⚠️  注意：当前为最小化版本，数据库功能未启用")
    print("=" * 60)
    
    if __name__ == "__main__":
        app.run(
            host="0.0.0.0",
            port=5000,
            debug=True,
            threaded=True
        )
        
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("\n请确保已安装Flask:")
    print("  pip install Flask==2.3.3")
    sys.exit(1)
except Exception as e:
    print(f"❌ 启动失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
