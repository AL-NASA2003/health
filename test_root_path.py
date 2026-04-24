import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 60)
print("测试后端根路径")
print("=" * 60)

# 1. 测试根路径
print("\n1. 测试根路径...")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
except Exception as e:
    print(f"❌ 请求失败: {e}")

# 2. 测试测试demo路由
print("\n2. 测试demo路由...")
try:
    response = requests.get(f"{BASE_URL}/api/test-demo")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
except Exception as e:
    print(f"❌ 请求失败: {e}")

# 3. 测试用户登录
print("\n3. 测试用户登录...")
try:
    response = requests.get(f"{BASE_URL}/api/user/init-test-data")
    print(f"初始化测试数据状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 尝试登录
    login_data = {"username": "test", "password": "test123"}
    response = requests.post(f"{BASE_URL}/api/user/login", json=login_data)
    print(f"\n登录状态码: {response.status_code}")
    print(f"登录响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200 and response.json().get("code") == 0:
        token = response.json()["data"]["token"]
        print(f"✅ 登录成功，获取到token")
        
        # 4. 测试图像生成
        print("\n4. 测试图像生成...")
        headers = {"Authorization": token}
        image_data = {
            "prompt": "健康饮食手账页面",
            "style": "cute",
            "size": "1024x1024"
        }
        response = requests.post(f"{BASE_URL}/api/image/generate-handbook", json=image_data, headers=headers)
        print(f"图像生成状态码: {response.status_code}")
        print(f"图像生成响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                print("✅ 手账图像生成API正常!")
                print(f"返回的图片URL: {result['data'].get('image_url')}")

except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
