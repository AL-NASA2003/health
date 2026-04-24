import requests
import json

BASE_URL = "http://localhost:5000/api"

print("=" * 60)
print("测试修复后的图像生成")
print("=" * 60)

# 1. 登录
print("\n1. 登录获取token...")
login_data = {"username": "test", "password": "123456"}
response = requests.post(f"{BASE_URL}/user/login", json=login_data)
print(f"登录状态码: {response.status_code}")

if response.status_code == 200 and response.json().get("code") == 0:
    token = response.json()["data"]["token"]
    print(f"✅ 登录成功，获取到token")
    
    # 2. 测试生成手账图像
    import datetime
    test_prompt = f"测试手账页面 {datetime.datetime.now().strftime('%H%M%S')}"
    print(f"\n2. 测试手账图像生成，prompt: {test_prompt}...")
    headers = {"Authorization": token}
    image_data = {
        "prompt": test_prompt,
        "style": "cute",
        "size": "1024x1024"
    }
    
    print("正在请求图像生成API（可能需要几秒钟）...")
    response = requests.post(f"{BASE_URL}/image/generate-handbook", json=image_data, headers=headers, timeout=60)
    print(f"图像生成状态码: {response.status_code}")
    print(f"图像生成响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("code") == 0:
            print("✅ 手账图像生成API正常!")
            print(f"返回的图片URL: {result['data'].get('image_url')}")
            print(f"图片来源: {result['data'].get('source')}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
