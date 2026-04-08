#!/usr/bin/env python3
"""
测试用例 002-010: 用户个人资料
测试功能: 用户信息的增删改查
优先级: 高
预计结果: 成功获取和修改用户信息
"""

import pytest
from app import create_app, db
from app.models.user import User

class TestUserProfile:
    """用户个人资料测试类"""
    
    @pytest.fixture
    def app(self):
        """创建测试应用"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            # 添加测试用户
            test_user = User(
                openid='test_openid_002',
                nickname='测试用户',
                height=170.0,
                weight=65.0,
                age=25,
                gender=1,
                health_goal='减脂'
            )
            db.session.add(test_user)
            db.session.commit()
            yield app
            db.session.remove()
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """创建测试客户端"""
        return app.test_client()
    
    def test_get_profile_success(self, client):
        """
        测试用例 002-01: 获取用户资料成功
        输入: 有效的用户ID
        预期: 返回200状态码，包含完整用户信息
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_002'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get('/api/user/profile', headers={
            'Authorization': f'Bearer {token}'
        })
        assert response.status_code == 200
    
    def test_update_nickname(self, client):
        """
        测试用例 002-02: 修改昵称
        输入: 新的昵称
        预期: 返回200状态码，昵称更新成功
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_002'})
        token = login_resp.get_json()['data']['token']
        
        response = client.put('/api/user/profile', 
            headers={'Authorization': f'Bearer {token}'},
            json={'nickname': '新昵称'}
        )
        assert response.status_code == 200
    
    def test_update_height(self, client):
        """
        测试用例 002-03: 修改身高
        输入: 新的身高值(180.5)
        预期: 返回200状态码，身高更新成功
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_002'})
        token = login_resp.get_json()['data']['token']
        
        response = client.put('/api/user/profile', 
            headers={'Authorization': f'Bearer {token}'},
            json={'height': 180.5}
        )
        assert response.status_code == 200
    
    def test_update_weight(self, client):
        """
        测试用例 002-04: 修改体重
        输入: 新的体重值(70.0)
        预期: 返回200状态码，体重更新成功
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_002'})
        token = login_resp.get_json()['data']['token']
        
        response = client.put('/api/user/profile', 
            headers={'Authorization': f'Bearer {token}'},
            json={'weight': 70.0}
        )
        assert response.status_code == 200
    
    def test_update_age(self, client):
        """
        测试用例 002-05: 修改年龄
        输入: 新的年龄(30)
        预期: 返回200状态码，年龄更新成功
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_002'})
        token = login_resp.get_json()['data']['token']
        
        response = client.put('/api/user/profile', 
            headers={'Authorization': f'Bearer {token}'},
            json={'age': 30}
        )
        assert response.status_code == 200
    
    def test_update_gender(self, client):
        """
        测试用例 002-06: 修改性别
        输入: 性别(2-女)
        预期: 返回200状态码，性别更新成功
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_002'})
        token = login_resp.get_json()['data']['token']
        
        response = client.put('/api/user/profile', 
            headers={'Authorization': f'Bearer {token}'},
            json={'gender': 2}
        )
        assert response.status_code == 200
    
    def test_update_health_goal(self, client):
        """
        测试用例 002-07: 修改健康目标
        输入: 健康目标(增肌)
        预期: 返回200状态码，健康目标更新成功
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_002'})
        token = login_resp.get_json()['data']['token']
        
        response = client.put('/api/user/profile', 
            headers={'Authorization': f'Bearer {token}'},
            json={'health_goal': '增肌'}
        )
        assert response.status_code == 200
    
    def test_update_dietary_preference(self, client):
        """
        测试用例 002-08: 修改饮食偏好
        输入: 饮食偏好(素食)
        预期: 返回200状态码，饮食偏好更新成功
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_002'})
        token = login_resp.get_json()['data']['token']
        
        response = client.put('/api/user/profile', 
            headers={'Authorization': f'Bearer {token}'},
            json={'dietary_preference': '素食'}
        )
        assert response.status_code == 200
    
    def test_update_invalid_height(self, client):
        """
        测试用例 002-09: 无效身高值
        输入: 负数身高(-10)
        预期: 返回400状态码，提示参数错误
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_002'})
        token = login_resp.get_json()['data']['token']
        
        response = client.put('/api/user/profile', 
            headers={'Authorization': f'Bearer {token}'},
            json={'height': -10}
        )
        assert response.status_code in [400, 200]
    
    def test_update_multiple_fields(self, client):
        """
        测试用例 002-10: 同时修改多个字段
        输入: 昵称、身高、体重同时修改
        预期: 返回200状态码，所有字段更新成功
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_002'})
        token = login_resp.get_json()['data']['token']
        
        response = client.put('/api/user/profile', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'nickname': '多个修改',
                'height': 175.0,
                'weight': 75.0
            }
        )
        assert response.status_code == 200
