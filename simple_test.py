#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

print("测试1: 直接测试图像模板路由")
print("=" * 60)

url = f"{BASE_URL}/image/handbook-templates"
print(f"\n测试URL: {url}")

try:
    response = requests.get(url, timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"\n响应头: {dict(response.headers)}")
    print(f"\n响应内容: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n解析成功! 数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print(f"\n错误!")
        
except Exception as e:
    print(f"\n异常: {str(e)}")
