import requests
import json
import time

BASE_URL = "http://localhost:5000"

print("=" * 60)
print("详细测试所有路由")
print("=" * 60)

# 1. 根路径
print("\n1. 测试根路径...")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
except Exception as e:
    print(f"❌ 请求失败: {e}")

# 2. API doc路径
print("\n2. 测试API文档路径...")
try:
    response = requests.get(f"{BASE_URL}/api/docs")
    print(f"状态码: {response.status_code}")
    print(f"响应前100字符: {response.text[:100]}...")
except Exception as e:
    print(f"❌ 请求失败: {e}")

# 3. /api/test-demo
print("\n3. 测试 /api/test-demo...")
try:
    response = requests.get(f"{BASE_URL}/api/test-demo")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
except Exception as e:
    print(f"❌ 请求失败: {e}")

# 4. /api/image/test
print("\n4. 测试 /api/image/test...")
try:
    response = requests.get(f"{BASE_URL}/api/image/test")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
except Exception as e:
    print(f"❌ 请求失败: {e}")

# 5. /api/image/generate-handbook
print("\n5. 测试 /api/image/generate-handbook...")
try:
    image_data = {
        "prompt": "健康饮食手账页面",
        "style": "cute",
        "size": "1024x1024"
    }
    response = requests.post(f"{BASE_URL}/api/image/generate-handbook", json=image_data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
except Exception as e:
    print(f"❌ 请求失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
