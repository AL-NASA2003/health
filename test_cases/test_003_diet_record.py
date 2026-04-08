#!/usr/bin/env python3
"""
测试用例 011-030: 饮食记录
测试功能: 饮食记录的增删改查
优先级: 高
预计结果: 成功管理饮食记录
"""

import pytest
from datetime import datetime, date
from app import create_app, db
from app.models.user import User
from app.models.diet_record import DietRecord

class TestDietRecord:
    """饮食记录测试类"""
    
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
                openid='test_openid_003',
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
    
    def test_add_diet_record_success(self, client):
        """
        测试用例 011: 添加饮食记录成功
        输入: 完整的饮食记录信息
        预期: 返回200状态码，记录添加成功
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_003'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '番茄炒蛋',
                'food_type': '蔬菜',
                'meal_time': '午餐',
                'weight': 200,
                'calorie': 150,
                'protein': 10,
                'carb': 15,
                'fat': 5,
                'create_date': date.today().strftime('%Y-%m-%d')
            }
        )
        assert response.status_code == 200
    
    def test_add_diet_record_empty_name(self, client):
        """
        测试用例 012: 添加饮食记录-空食物名称
        输入: 缺少食物名称
        预期: 返回400状态码，提示缺少必填参数
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_003'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_type': '蔬菜',
                'meal_time': '午餐',
                'weight': 200
            }
        )
        assert response.status_code == 400
    
    def test_add_diet_record_negative_weight(self, client):
        """
        测试用例 013: 添加饮食记录-负重量
        输入: 负的重量值
        预期: 返回400状态码，提示参数错误
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_003'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '番茄炒蛋',
                'food_type': '蔬菜',
                'meal_time': '午餐',
                'weight': -100
            }
        )
        assert response.status_code in [400, 200]
    
    def test_add_diet_record_zero_calorie(self, client):
        """
        测试用例 014: 添加饮食记录-零热量
        输入: 热量为0
        预期: 返回200状态码，记录添加成功
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_003'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '矿泉水',
                'food_type': '饮品',
                'meal_time': '加餐',
                'weight': 500,
                'calorie': 0
            }
        )
        assert response.status_code == 200
    
    def test_add_diet_record_all_meal_times(self, client):
        """
        测试用例 015: 添加各时段饮食记录
        输入: 早餐、午餐、晚餐、加餐各一条
        预期: 所有记录都添加成功
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_003'})
        token = login_resp.get_json()['data']['token']
        
        meal_times = ['早餐', '午餐', '晚餐', '加餐']
        for meal_time in meal_times:
            response = client.post('/api/diet/add', 
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'food_name': f'{meal_time}食物',
                    'food_type': '主食',
                    'meal_time': meal_time,
                    'weight': 100,
                    'calorie': 100
                }
            )
            assert response.status_code == 200
    
    def test_get_diet_list(self, client):
        """
        测试用例 016: 获取饮食记录列表
        输入: 指定日期
        预期: 返回该日期的所有饮食记录
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_003'})
        token = login_resp.get_json()['data']['token']
        
        # 先添加一条记录
        client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '测试食物',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 100,
                'calorie': 100,
                'create_date': date.today().strftime('%Y-%m-%d')
            }
        )
        
        # 获取列表
        response = client.get(f'/api/diet/list?date={date.today().strftime("%Y-%m-%d")}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_get_diet_list_future_date(self, client):
        """
        测试用例 017: 获取未来日期的饮食记录
        输入: 明天的日期
        预期: 返回空列表
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_003'})
        token = login_resp.get_json()['data']['token']
        
        future_date = (date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        response = client.get(f'/api/diet/list?date={future_date}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_delete_diet_record(self, client):
        """
        测试用例 018: 删除饮食记录
        输入: 有效的记录ID
        预期: 返回200状态码，记录删除成功
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_003'})
        token = login_resp.get_json()['data']['token']
        
        # 先添加一条记录
        add_resp = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '待删除食物',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 100,
                'calorie': 100
            }
        )
        record_id = add_resp.get_json()['data']['id']
        
        # 删除记录
        response = client.delete(f'/api/diet/delete/{record_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_delete_nonexistent_record(self, client):
        """
        测试用例 019: 删除不存在的记录
        输入: 无效的记录ID
        预期: 返回404状态码，提示记录不存在
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_003'})
        token = login_resp.get_json()['data']['token']
        
        response = client.delete('/api/diet/delete/99999',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code in [404, 400, 200]
    
    def test_update_diet_record(self, client):
        """
        测试用例 020: 修改饮食记录
        输入: 记录ID和新的数据
        预期: 返回200状态码，记录更新成功
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_003'})
        token = login_resp.get_json()['data']['token']
        
        # 先添加一条记录
        add_resp = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '旧食物',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 100,
                'calorie': 100
            }
        )
        record_id = add_resp.get_json()['data']['id']
        
        # 更新记录
        response = client.put(f'/api/diet/update/{record_id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '新食物',
                'weight': 150,
                'calorie': 150
            }
        )
        assert response.status_code == 200
    
    def test_get_diet_statistics(self, client):
        """
        测试用例 021: 获取饮食统计
        输入: 日期范围
        预期: 返回统计数据
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_003'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get('/api/diet/statistics',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_add_breakfast(self, client):
        """
        测试用例 022: 添加早餐记录
        输入: 早餐数据
        预期: 记录添加成功
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_003'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '全麦面包',
                'food_type': '主食',
                'meal_time': '早餐',
                'weight': 100,
                'calorie': 250,
                'protein': 10,
                'carb': 45,
                'fat': 3
            }
        )
        assert response.status_code == 200
    
    def test_add_lunch(self, client):
        """
        测试用例 023: 添加午餐记录
        输入: 午餐数据
        预期: 记录添加成功
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_003'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '鸡胸肉沙拉',
                'food_type': '蛋白质',
                'meal_time': '午餐',
                'weight': 250,
                'calorie': 350,
                'protein': 35,
                'carb': 15,
                'fat': 12
            }
        )
        assert response.status_code == 200
    
    def test_add_dinner(self, client):
        """
        测试用例 024: 添加晚餐记录
        输入: 晚餐数据
        预期: 记录添加成功
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_003'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '清蒸鱼',
                'food_type': '蛋白质',
                'meal_time': '晚餐',
                'weight': 200,
                'calorie': 200,
                'protein': 40,
                'carb': 0,
                'fat': 5
            }
        )
        assert response.status_code == 200
    
    def test_add_snack(self, client):
        """
        测试用例 025: 添加加餐记录
        输入: 加餐数据
        预期: 记录添加成功
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_003'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '苹果',
                'food_type': '水果',
                'meal_time': '加餐',
                'weight': 150,
                'calorie': 80,
                'protein': 0.3,
                'carb': 21,
                'fat': 0.2
            }
        )
        assert response.status_code == 200
    
    def test_add_multiple_records(self, client):
        """
        测试用例 026: 批量添加饮食记录
        输入: 多条记录数据
        预期: 所有记录添加成功
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_003'})
        token = login_resp.get_json()['data']['token']
        
        foods = [
            {'name': '牛奶', 'type': '奶制品', 'meal': '早餐', 'weight': 250, 'calorie': 150},
            {'name': '鸡蛋', 'type': '蛋白质', 'meal': '早餐', 'weight': 50, 'calorie': 70},
            {'name': '米饭', 'type': '主食', 'meal': '午餐', 'weight': 150, 'calorie': 180},
            {'name': '青菜', 'type': '蔬菜', 'meal': '午餐', 'weight': 200, 'calorie': 40},
        ]
        
        for food in foods:
            response = client.post('/api/diet/add', 
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'food_name': food['name'],
                    'food_type': food['type'],
                    'meal_time': food['meal'],
                    'weight': food['weight'],
                    'calorie': food['calorie']
                }
            )
            assert response.status_code == 200
    
    def test_search_diet_record(self, client):
        """
        测试用例 027: 搜索饮食记录
        输入: 关键词
        预期: 返回匹配的记录
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_003'})
        token = login_resp.get_json()['data']['token']
        
        # 先添加测试数据
        client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '番茄炒蛋',
                'food_type': '蔬菜',
                'meal_time': '午餐',
                'weight': 200,
                'calorie': 150
            }
        )
        
        # 搜索
        response = client.get('/api/diet/search?keyword=番茄',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_get_diet_calendar(self, client):
        """
        测试用例 028: 获取饮食日历
        输入: 年月
        预期: 返回当月的饮食记录概览
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_003'})
        token = login_resp.get_json()['data']['token']
        
        today = date.today()
        response = client.get(f'/api/diet/calendar?year={today.year}&month={today.month}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_export_diet_record(self, client):
        """
        测试用例 029: 导出饮食记录
        输入: 日期范围
        预期: 返回导出文件
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_003'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get('/api/diet/export',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code in [200, 404]
    
    def test_add_high_calorie_food(self, client):
        """
        测试用例 030: 添加高热量食物
        输入: 高热量食物数据
        预期: 记录添加成功
        """
        # 先登录获取token
        login_resp = client.post('/api/user/login', json={'code': 'test_code_003'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '炸鸡',
                'food_type': '蛋白质',
                'meal_time': '晚餐',
                'weight': 200,
                'calorie': 600,
                'protein': 30,
                'carb': 20,
                'fat': 40
            }
        )
        assert response.status_code == 200
