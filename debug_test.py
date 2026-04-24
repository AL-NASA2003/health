#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 60)
print("调试：测试 GET /api/image/test")
print("=" * 60)

try:
    # 详细调试请求
    session = requests.Session()
    
    # 调试 GET
    print("\n--- 1. GET /api/image/test ---")
    r_get = session.get(f"{BASE_URL}/api/image/test")
    print(f"状态码: {r_get.status_code}")
    print(f"响应内容: {json.dumps(r_get.json(), ensure_ascii=False, indent=2)}")
    print(f"响应头: {dict(r_get.headers)}")
    
    print("\n--- 2. POST /api/image/generate-handbook ---")
    test_data = {
        "prompt": "测试手账",
        "style": "cute"
    }
    r_post = session.post(f"{BASE_URL}/api/image/generate-handbook", json=test_data)
    print(f"状态码: {r_post.status_code}")
    print(f"响应内容: {json.dumps(r_post.json(), ensure_ascii=False, indent=2)}")
    
    print("\n--- 3. POST /api/image/test ---")
    # 试试 POST 方法到测试路由（虽然我们只设置了 GET）
    r_post_test = session.post(f"{BASE_URL}/api/image/test")
    print(f"状态码: {r_post_test.status_code}")

except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
