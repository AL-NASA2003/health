#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 60)
print("测试 /debug/ 前缀路由")
print("=" * 60)

print("\n1. GET /debug/test")
try:
    r1 = requests.get(f"{BASE_URL}/debug/test")
    print(f"状态码: {r1.status_code}")
    print(f"响应: {json.dumps(r1.json(), ensure_ascii=False, indent=2)}")
except Exception as e:
    print(f"错误: {e}")

print("\n2. GET /debug/image/test")
try:
    r2 = requests.get(f"{BASE_URL}/debug/image/test")
    print(f"状态码: {r2.status_code}")
    print(f"响应: {json.dumps(r2.json(), ensure_ascii=False, indent=2)}")
except Exception as e:
    print(f"错误: {e}")

print("\n3. POST /debug/image/generate-handbook")
try:
    data = {
        "prompt": "测试手账",
        "style": "cute"
    }
    r3 = requests.post(f"{BASE_URL}/debug/image/generate-handbook", json=data)
    print(f"状态码: {r3.status_code}")
    print(f"响应: {json.dumps(r3.json(), ensure_ascii=False, indent=2)}")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

print("\n4. GET /api/test-demo")
try:
    r4 = requests.get(f"{BASE_URL}/api/test-demo")
    print(f"状态码: {r4.status_code}")
    print(f"响应: {json.dumps(r4.json(), ensure_ascii=False, indent=2)}")
except Exception as e:
    print(f"错误: {e}")

print("\n" + "=" * 60)
