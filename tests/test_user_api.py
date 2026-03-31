import json
import pytest


def test_user_login(client):
    """测试用户登录接口"""
    # 使用测试账号登录
    login_data = {
        "username": "test",
        "password": "123456"
    }
    
    response = client.post('/api/user/login', json=login_data)
    data = json.loads(response.data)
    
    # 检查响应状态码
    assert response.status_code == 200
    # 检查响应数据结构
    assert 'code' in data
    assert 'data' in data
    assert 'token' in data['data']
    assert 'user_info' in data['data']


def test_user_info(client):
    """测试获取用户信息接口"""
    # 首先登录获取token
    login_response = client.post('/api/user/login', json={"username": "test", "password": "123456"})
    login_data = json.loads(login_response.data)
    token = login_data['data']['token']
    
    # 使用token获取用户信息
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = client.get('/api/user/info', headers=headers)
    data = json.loads(response.data)
    
    # 检查响应状态码
    assert response.status_code == 200
    # 检查响应数据结构
    assert 'code' in data
    assert 'data' in data
    assert 'id' in data['data']
    assert 'nickname' in data['data']


def test_user_update(client):
    """测试更新用户信息接口"""
    # 首先登录获取token
    login_response = client.post('/api/user/login', json={"username": "test", "password": "123456"})
    login_data = json.loads(login_response.data)
    token = login_data['data']['token']
    
    # 准备更新数据
    update_data = {
        "nickname": "测试用户",
        "avatar": "https://picsum.photos/seed/avatar/100/100"
    }
    
    # 发送更新请求
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = client.put('/api/user/info', json=update_data, headers=headers)
    data = json.loads(response.data)
    
    # 检查响应状态码
    assert response.status_code == 200
    # 检查响应数据
    assert 'code' in data
    assert data['code'] == 200
