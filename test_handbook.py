import requests
import json

BASE_URL = "http://localhost:5000/api"

print("=" * 60)
print("测试手账相关API")
print("=" * 60)

# 1. 登录
print("\n1. 登录获取token...")
login_data = {"username": "test", "password": "123456"}
response = requests.post(f"{BASE_URL}/user/login", json=login_data)

if response.status_code == 200:
    result = response.json()
    if result.get("code") == 0:
        token = result["data"]["token"]
        print(f"✅ 登录成功")
        
        # 2. 获取手账列表
        print("\n2. 获取手账列表...")
        headers = {"Authorization": token}
        response = requests.get(f"{BASE_URL}/handbook/list", headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        # 3. 添加新手账
        print("\n3. 测试添加新手账...")
        new_handbook = {
            "title": "测试手账 " + __import__('datetime').datetime.now().strftime('%H:%M:%S'),
            "content": "这是一个测试手账内容，用于验证添加功能是否正常工作！",
            "image": ""
        }
        response = requests.post(f"{BASE_URL}/handbook/add", json=new_handbook, headers=headers)
        print(f"添加手账状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200 and response.json().get("code") == 0:
            print("✅ 添加手账成功！")
            # 4. 再次获取列表，验证新增成功
            print("\n4. 再次获取手账列表，验证新增...")
            response = requests.get(f"{BASE_URL}/handbook/list", headers=headers)
            result = response.json()
            if result.get("code") == 0:
                list_data = result.get("data", {}).get("list", [])
                print(f"✅ 当前手账数量: {len(list_data)}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
