import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 60)
print("简单测试")
print("=" * 60)

# 1. 测试根路径
print("\n1. 测试根路径...")
response = requests.get(f"{BASE_URL}/")
print(f"根路径状态码: {response.status_code}")
print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

# 2. 测试图像测试路由
print("\n2. 测试图像测试路由...")
response = requests.get(f"{BASE_URL}/api/image/test")
print(f"状态码: {response.status_code}")
print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
