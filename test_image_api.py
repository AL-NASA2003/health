import requests
import json

BASE_URL = "http://localhost:5000/api"

print("=" * 60)
print("测试图像API")
print("=" * 60)

# 1. 测试图像测试路由
print("\n1. 测试图像测试路由...")
try:
    response = requests.get(f"{BASE_URL}/image/test")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    if response.status_code == 200 and response.json().get("code") == 0:
        print("✅ 图像测试路由正常！")
except Exception as e:
    print(f"❌ 请求失败: {e}")

# 2. 测试手账图像生成
print("\n2. 测试手账图像生成...")
try:
    image_data = {
        "prompt": "健康饮食手账页面",
        "style": "cute",
        "size": "1024x1024"
    }
    response = requests.post(f"{BASE_URL}/image/generate-handbook", json=image_data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
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
