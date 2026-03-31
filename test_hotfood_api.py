import requests
import json

# 测试热点美食 API

# 先登录获取 token
login_url = 'http://localhost:5000/api/user/login'
login_data = {
    'username': 'test',
    'password': '123456'
}

response = requests.post(login_url, json=login_data)
print('登录响应:', response.json())

if response.status_code == 200 and response.json().get('code') == 200:
    token = response.json().get('data', {}).get('token')
    print('获取到 token:', token)
    
    # 测试热点美食列表 API
    hotfood_url = 'http://localhost:5000/api/hotfood/list'
    headers = {
        'Authorization': token
    }
    
    hotfood_response = requests.get(hotfood_url, headers=headers)
    print('\n热点美食 API 响应:', hotfood_response.json())
    
    # 检查返回的数据结构
    data = hotfood_response.json().get('data', {})
    hotfood_list = data.get('list', [])
    print(f'\n返回的热点美食数量: {len(hotfood_list)}')
    
    if hotfood_list:
        print('\n第一条热点美食数据:')
        print(json.dumps(hotfood_list[0], indent=2, ensure_ascii=False))
else:
    print('登录失败，无法测试热点美食 API')
