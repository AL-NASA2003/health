#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试最简单的路由
"""
import requests
import json

# 测试根路径
print("测试根路径...")
response = requests.get("http://localhost:5000")
print(f"状态码: {response.status_code}")
print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

# 测试API文档路径
print("\n测试API文档路径...")
response = requests.get("http://localhost:5000/api/docs")
print(f"状态码: {response.status_code}")

# 测试一个已知的好路由 - 比如用户登录
print("\n测试用户登录API...")
response = requests.get("http://localhost:5000/api/user/login")
print(f"状态码: {response.status_code}")
if response.status_code != 404:
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

print("\n所有测试完成！")
