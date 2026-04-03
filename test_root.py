#!/usr/bin/env python3
"""
简单测试根路径
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from app.utils.common import format_response

app = Flask(__name__)

@app.route('/')
def index():
    return format_response(data={
        "service": "健康饮食管理系统API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/docs"
    })

@app.route('/test')
def test():
    return format_response(data={"message": "test success"})

if __name__ == "__main__":
    print("=" * 50)
    print("测试服务器启动")
    print("=" * 50)
    app.run(host="127.0.0.1", port=5001, debug=True)
