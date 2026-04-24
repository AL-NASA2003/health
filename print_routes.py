#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

print("=" * 60)
print("Flask 应用所有已注册路由")
print("=" * 60)

print(f"路由总数: {len(app.url_map._rules)}\n")

for rule in app.url_map._rules:
    methods = ', '.join(rule.methods - {'HEAD', 'OPTIONS'})
    print(f"  - {rule.rule}  [{methods}]  ({rule.endpoint})")

print("\n" + "=" * 60)
print("特别关注以下路由:")
for path in ['/', '/api/test-demo', '/api/image/test', '/api/image/generate-handbook']:
    found = any(rule.rule == path for rule in app.url_map._rules)
    print(f"  {path}: {'✅ 已注册' if found else '❌ 未找到'}")

print("=" * 60)
