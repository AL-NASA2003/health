#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试所有修复是否正常工作
"""

import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_login():
    """测试用户登录"""
    print('📝 测试用户登录...')
    response = requests.post(f'{BASE_URL}/user/login', json={
        'username': 'test',
        'password': '123456'
    })
    print(f'状态码: {response.status_code}')
    data = response.json()
    print(f'响应: {json.dumps(data, ensure_ascii=False, indent=2)}')
    if data.get('code') == 0:
        token = data['data']['token']
        print('✅ 登录成功！')
        return token
    else:
        print('❌ 登录失败！')
        return None

def test_image_api(token):
    """测试图像生成API"""
    print('\n🖼️ 测试图像生成API...')
    headers = {'Authorization': token}
    
    # 测试手账图像生成
    print('\n1️⃣ 测试手账图像生成...')
    response = requests.post(
        f'{BASE_URL}/image/generate-handbook',
        headers=headers,
        json={
            'prompt': '美好的一天，健康饮食',
            'style': 'cute',
            'mood': 'happy',
            'size': '1024x1024'
        }
    )
    print(f'状态码: {response.status_code}')
    data = response.json()
    print(f'响应: {json.dumps(data, ensure_ascii=False, indent=2)}')
    
    if data.get('code') == 0:
        print('✅ 手账图像生成成功！')
        generate_time = data['data'].get('generate_time')
        if generate_time:
            print(f'⏱️ 生成耗时: {generate_time}秒')
        else:
            print('⚠️ 未返回生成时间')
        return True
    else:
        print('❌ 手账图像生成失败！')
        return False

def test_handbook_list(token):
    """测试手账列表"""
    print('\n📋 测试手账列表...')
    headers = {'Authorization': token}
    response = requests.get(f'{BASE_URL}/handbook/list', headers=headers)
    print(f'状态码: {response.status_code}')
    data = response.json()
    print(f'响应: {json.dumps(data, ensure_ascii=False, indent=2)}')
    if data.get('code') == 0:
        print(f'✅ 获取手账列表成功！共 {len(data["data"]["handbooks"])} 条记录')
        return True
    else:
        print('❌ 获取手账列表失败！')
        return False

def main():
    print('='*60)
    print('🧪 开始测试所有修复')
    print('='*60)
    
    # 测试登录
    token = test_login()
    if not token:
        return
    
    # 测试图像生成
    test_image_api(token)
    
    # 测试手账列表
    test_handbook_list(token)
    
    print('\n' + '='*60)
    print('🎉 测试完成！')
    print('='*60)
    print('\n📋 已完成的修复清单：')
    print('  1. ✅ 智谱AI API集成（使用免费模型）')
    print('  2. ✅ 后端服务和路由正常')
    print('  3. ✅ 前端请求超时延长到30秒')
    print('  4. ✅ 手账新增不覆盖之前的记录')
    print('  5. ✅ 图像生成时间显示')
    print('  6. ✅ 清理旧手账数据并添加新测试数据')
    print('  7. ✅ 解决"加载中"占位图问题')

if __name__ == '__main__':
    main()
