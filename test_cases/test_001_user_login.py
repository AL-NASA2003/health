#!/usr/bin/env python3
"""
测试用例 001: 用户登录
测试功能: 用户微信登录
优先级: 高
预计结果: 成功获取用户信息并返回Token
"""

import pytest
from app import create_app, db
from app.models.user import User

class TestUserLogin:
    """用户登录测试类"""
    
    @pytest.fixture
    def app(self):
        """创建测试应用"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """创建测试客户端"""
        return app.test_client()
    
    def test_login_success(self, client):
        """
        测试用例 001-01: 正常登录
        输入: 有效的微信code
        预期: 返回200状态码，包含用户信息和token
        """
        response = client.post('/api/user/login', json={
            'code': 'test_valid_code_001'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 0
        assert 'token' in data['data']
        assert 'user' in data['data']
    
    def test_login_empty_code(self, client):
        """
        测试用例 001-02: 空code登录
        输入: 空的code
        预期: 返回400状态码，提示缺少参数
        """
        response = client.post('/api/user/login', json={
            'code': ''
        })
        assert response.status_code == 400
    
    def test_login_invalid_code(self, client):
        """
        测试用例 001-03: 无效code登录
        输入: 无效的微信code
        预期: 返回401状态码，提示登录失败
        """
        response = client.post('/api/user/login', json={
            'code': 'invalid_code_001'
        })
        assert response.status_code in [400, 401]
    
    def test_login_no_code(self, client):
        """
        测试用例 001-04: 不传code登录
        输入: 不包含code字段
        预期: 返回400状态码，提示缺少参数
        """
        response = client.post('/api/user/login', json={})
        assert response.status_code == 400
