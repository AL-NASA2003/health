#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== 测试config.py ===")

# 直接读取config.py文件
with open('app/config.py', 'r', encoding='utf-8') as f:
    content = f.read()
    print("\nconfig.py 内容片段:")
    print(content[300:500])

print("\n=== 导入config ===")
from app.config import (
    ERNIE_API_KEY,
    ERNIE_SECRET_KEY,
    ERNIE_ACCESS_TOKEN_URL
)

print(f"ERNIE_API_KEY: '{ERNIE_API_KEY}'")
print(f"ERNIE_SECRET_KEY: '{ERNIE_SECRET_KEY}'")
print(f"长度 API_KEY: {len(ERNIE_API_KEY)}")
print(f"长度 SECRET_KEY: {len(ERNIE_SECRET_KEY)}")
print(f"是否为空 API_KEY: {ERNIE_API_KEY == ''}")
print(f"是否为None API_KEY: {ERNIE_API_KEY is None}")

print("\n=== 测试环境变量 ===")
print(f"os.environ.get('ERNIE_API_KEY'): {os.environ.get('ERNIE_API_KEY')}")
print(f"os.environ.get('ERNIE_SECRET_KEY'): {os.environ.get('ERNIE_SECRET_KEY')}")
