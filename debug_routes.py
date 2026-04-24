#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试路由注册问题
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app import create_app
from loguru import logger

def check_routes():
    """检查所有路由"""
    app = create_app()
    
    print("=" * 60)
    print("所有注册的路由")
    print("=" * 60)
    
    all_routes = []
    for rule in app.url_map.iter_rules():
        methods = [m for m in rule.methods if m not in ('HEAD', 'OPTIONS')]
        route_info = {
            "path": rule.rule,
            "methods": methods,
            "endpoint": rule.endpoint
        }
        all_routes.append(route_info)
        print(f"{rule.rule:50s} {methods}")
    
    print("\n" + "=" * 60)
    print("图像相关路由")
    print("=" * 60)
    
    image_routes = [r for r in all_routes if '/image' in r['path']]
    for route in image_routes:
        print(f"{route['path']:50s} {route['methods']}")
    
    print("\n" + "=" * 60)
    
    # 测试image test路由是否在列表中
    test_route_exists = any(r['path'] == '/api/image/test' for r in all_routes)
    print(f"test路由是否存在: {'✅ 是' if test_route_exists else '❌ 否'}")
    
    return app, all_routes

if __name__ == "__main__":
    app, routes = check_routes()
    
    # 简单测试
    print("\n开始简单测试...")
    
    from flask import current_app
    with app.test_request_context():
        # 测试蓝图注册
        from app.api.image_api import image_bp
        print(f"image_bp name: {image_bp.name}")
        print(f"image_bp routes:")
        for rule in image_bp.url_map.iter_rules():
            print(f"  {rule}")
