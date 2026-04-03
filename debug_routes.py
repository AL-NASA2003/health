#!/usr/bin/env python3
"""
调试：列出所有注册的路由
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

print("=" * 60)
print("所有注册的路由:")
print("=" * 60)

for rule in app.url_map.iter_rules():
    methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
    print(f"{rule.endpoint:40s} {methods:10s} {rule.rule}")

print("=" * 60)
print(f"总共 {len(list(app.url_map.iter_rules()))} 个路由")
print("=" * 60)
