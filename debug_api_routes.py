#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试API路由
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app import create_app
from app.api.image_api import image_bp

def debug_routes():
    """调试API路由"""
    app = create_app()
    
    print("=" * 60)
    print("所有注册的路由:")
    print("=" * 60)
    
    for rule in app.url_map.iter_rules():
        methods = [m for m in rule.methods if m not in ('HEAD', 'OPTIONS')]
        print(f"{rule.rule:40s} {methods}")
    
    print("\n" + "=" * 60)
    print("图像相关的路由:")
    print("=" * 60)
    
    for rule in app.url_map.iter_rules():
        if '/image' in rule.rule:
            methods = [m for m in rule.methods if m not in ('HEAD', 'OPTIONS')]
            print(f"{rule.rule:40s} {methods}")
    
    return app


def test_route_structure(app):
    """测试路由结构"""
    print("\n" + "=" * 60)
    print("Blueprint结构:")
    print("=" * 60)
    
    print(f"Image Blueprint name: {image_bp.name}")
    print(f"Image Blueprint url_prefix: /api/image")
    print(f"Number of routes: {len(list(image_bp.url_map.iter_rules()))}")
    
    print("\nImage Blueprint routes:")
    for rule in image_bp.url_map.iter_rules():
        print(f"  {rule.rule}")


if __name__ == "__main__":
    app = debug_routes()
    test_route_structure(app)
    
    print("\n" + "=" * 60)
    print("✅ 路由调试完成")
    print("=" * 60)
