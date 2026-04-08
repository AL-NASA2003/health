import json
import pytest
from datetime import datetime


def test_add_diet_record(client):
    """测试添加饮食记录接口"""
    # 首先登录获取token
    login_response = client.post('/api/user/login', json={"username": "test", "password": "123456"})
    login_data = json.loads(login_response.data)
    token = login_data['data']['token']
    
    # 准备饮食记录数据
    diet_data = {
        "food_name": "测试食物",
        "food_type": "主食",
        "meal_time": "午餐",
        "weight": 100
    }
    
    # 发送添加请求
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = client.post('/api/diet/record', json=diet_data, headers=headers)
    data = json.loads(response.data)
    
    # 检查响应状态码
    assert response.status_code == 200
    # 检查响应数据
    assert 'code' in data
    assert data['code'] == 200


def test_get_diet_record(client):
    """测试获取饮食记录接口"""
    # 首先登录获取token
    login_response = client.post('/api/user/login', json={"username": "test", "password": "123456"})
    login_data = json.loads(login_response.data)
    token = login_data['data']['token']
    
    # 添加一条饮食记录
    diet_data = {
        "food_name": "测试食物",
        "food_type": "主食",
        "meal_time": "午餐",
        "weight": 100
    }
    headers = {
        'Authorization': f'Bearer {token}'
    }
    # 发送添加请求并检查响应
    add_response = client.post('/api/diet/record', json=diet_data, headers=headers)
    add_data = json.loads(add_response.data)
    assert add_response.status_code == 200
    assert add_data['code'] == 200
    
    # 获取饮食记录（不指定日期范围，获取所有记录）
    response = client.get('/api/diet/record', headers=headers)
    data = json.loads(response.data)
    
    # 检查响应状态码
    assert response.status_code == 200
    # 检查响应数据结构
    assert 'code' in data
    assert 'data' in data
    assert 'list' in data['data']
    # 检查是否有记录
    assert len(data['data']['list']) > 0
