#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细调试路由
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app import create_app
from loguru import logger

def debug_routes():
    """详细调试路由"""
    app = create_app()
    
    print("\n" + "="*80)
    print("调试路由注册")
    print("="*80)
    
    # 打印所有路由
    print("\n所有注册的路由:")
    print("-"*80)
    all_rules = list(app.url_map.iter_rules())
    for i, rule in enumerate(all_rules):
        methods = [m for m in rule.methods if m not in ('HEAD', 'OPTIONS')]
        print(f"{i+1:3d}. {rule.rule:40s} {methods}")
    
    # 检查是否有我们的路由
    print("\n" + "="*80)
    print("检查特定的路由:")
    print("="*80)
    
    check_routes = [
        '/api/image/test',
        '/api/image/handbook-templates',
        '/api/image/generate-handbook',
        '/api/zhipu/status',
        '/api/test-demo'
    ]
    
    for route in check_routes:
        exists = any(r.rule == route for r in all_rules)
        status = "✅ 存在" if exists else "❌ 不存在"
        print(f"  {route:45s} {status}")
    
    # 检查Flask-RESTX Api
    print("\n" + "="*80)
    print("检查RESTX Api:")
    print("="*80)
    
    try:
        restx_api = None
        for key in app.extensions:
            if 'restx' in key:
                restx_api = app.extensions[key].get('api')
                break
        
        if restx_api:
            print(f"找到RESTX Api: {restx_api}")
            print(f"Api URL前缀: {restx_api.prefix}")
            print("\nRESTX Namespaces:")
            for ns_name, ns in restx_api.namespaces.items():
                print(f"  - {ns_name:20s} (路径: {ns.path})")
    except Exception as e:
        print(f"检查RESTX Api时出错: {str(e)}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    debug_routes()
