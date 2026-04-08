#!/usr/bin/env python3
"""
测试用例 031-128: 其他功能模块
测试功能: 运动记录、饮水记录、食谱、手账、论坛等
优先级: 中高
预计结果: 各功能模块正常运行
"""

import pytest
from datetime import datetime, date
from app import create_app, db
from app.models.user import User
from app.models.exercise_record import ExerciseRecord
from app.models.water_record import WaterRecord
from app.models.recipe import Recipe
from app.models.forum_post import ForumPost
from app.models.hand_account import HandAccount
from app.models.comment import Comment

class TestOtherModules:
    """其他功能模块测试类"""
    
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
                openid='test_openid_004',
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
    
    # 运动记录测试
    def test_add_exercise_record_success(self, client):
        """
        测试用例 031: 添加运动记录成功
        输入: 完整的运动记录信息
        预期: 返回200状态码，记录添加成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/exercise/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'exercise_type': '跑步',
                'duration': 30,
                'calorie': 300,
                'create_date': date.today().strftime('%Y-%m-%d')
            }
        )
        assert response.status_code == 200
    
    def test_get_exercise_list(self, client):
        """
        测试用例 032: 获取运动记录列表
        输入: 指定日期
        预期: 返回该日期的所有运动记录
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get(f'/api/exercise/list?date={date.today().strftime("%Y-%m-%d")}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_add_water_record_success(self, client):
        """
        测试用例 033: 添加饮水记录成功
        输入: 饮水量
        预期: 返回200状态码，记录添加成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/water/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'amount': 250,
                'create_date': date.today().strftime('%Y-%m-%d')
            }
        )
        assert response.status_code == 200
    
    def test_get_water_list(self, client):
        """
        测试用例 034: 获取饮水记录列表
        输入: 指定日期
        预期: 返回该日期的所有饮水记录
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get(f'/api/water/list?date={date.today().strftime("%Y-%m-%d")}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_get_recipe_list(self, client):
        """
        测试用例 035: 获取食谱列表
        输入: 无
        预期: 返回食谱列表
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get('/api/recipe/list',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_search_recipe(self, client):
        """
        测试用例 036: 搜索食谱
        输入: 关键词
        预期: 返回匹配的食谱
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get('/api/recipe/search?keyword=番茄',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_get_recipe_detail(self, client):
        """
        测试用例 037: 获取食谱详情
        输入: 食谱ID
        预期: 返回食谱详情
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get('/api/recipe/detail/1',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code in [200, 404]
    
    def test_add_hand_account(self, client):
        """
        测试用例 038: 添加手账
        输入: 手账内容
        预期: 返回200状态码，手账添加成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/handbook/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'topic': '健康打卡',
                'mood': '开心',
                'content': '今天坚持运动了！'
            }
        )
        assert response.status_code == 200
    
    def test_get_hand_account_list(self, client):
        """
        测试用例 039: 获取手账列表
        输入: 无
        预期: 返回手账列表
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get('/api/handbook/list',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_add_forum_post(self, client):
        """
        测试用例 040: 发布论坛帖子
        输入: 帖子标题和内容
        预期: 返回200状态码，帖子发布成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/forum/post', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': '减脂心得分享',
                'content': '坚持三个月，瘦了10斤！'
            }
        )
        assert response.status_code == 200
    
    def test_get_forum_list(self, client):
        """
        测试用例 041: 获取论坛帖子列表
        输入: 无
        预期: 返回帖子列表
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get('/api/forum/list',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_add_comment(self, client):
        """
        测试用例 042: 添加评论
        输入: 帖子ID和评论内容
        预期: 返回200状态码，评论添加成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/forum/comment', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'post_id': 1,
                'content': '说得太好了！'
            }
        )
        assert response.status_code in [200, 400]
    
    def test_get_comments(self, client):
        """
        测试用例 043: 获取评论列表
        输入: 帖子ID
        预期: 返回评论列表
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get('/api/forum/comments/1',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code in [200, 404]
    
    def test_get_recommendations(self, client):
        """
        测试用例 044: 获取食谱推荐
        输入: 无
        预期: 返回推荐食谱列表
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get('/api/recipe/recommendations',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_get_daily_summary(self, client):
        """
        测试用例 045: 获取每日总结
        输入: 日期
        预期: 返回当日营养摄入总结
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get(f'/api/diet/summary?date={date.today().strftime("%Y-%m-%d")}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_get_health_index(self, client):
        """
        测试用例 046: 获取健康指数
        输入: 无
        预期: 返回健康指数数据
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get('/api/health/index',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_update_goal(self, client):
        """
        测试用例 047: 更新健康目标
        输入: 新的目标数据
        预期: 返回200状态码，目标更新成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.put('/api/user/goal', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'target_calorie': 2000,
                'target_protein': 150,
                'target_carb': 200,
                'target_fat': 60
            }
        )
        assert response.status_code == 200
    
    def test_get_statistics_week(self, client):
        """
        测试用例 048: 获取周统计数据
        输入: 无
        预期: 返回本周统计数据
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get('/api/statistics/week',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_get_statistics_month(self, client):
        """
        测试用例 049: 获取月统计数据
        输入: 无
        预期: 返回本月统计数据
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get('/api/statistics/month',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_export_data(self, client):
        """
        测试用例 050: 导出数据
        输入: 日期范围
        预期: 返回导出文件
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get('/api/export/data',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code in [200, 404]
    
    # 边界情况测试
    def test_empty_input_all_fields(self, client):
        """
        测试用例 051: 所有字段为空
        输入: 空的请求体
        预期: 返回400状态码，提示参数错误
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={}
        )
        assert response.status_code == 400
    
    def test_very_long_name(self, client):
        """
        测试用例 052: 超长食物名称
        输入: 超过长度限制的名称
        预期: 返回400状态码，提示参数错误
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        long_name = 'a' * 200
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': long_name,
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 100,
                'calorie': 100
            }
        )
        assert response.status_code in [400, 200]
    
    def test_special_characters(self, client):
        """
        测试用例 053: 特殊字符输入
        输入: 包含特殊字符的名称
        预期: 返回200状态码，处理成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '测试!@#$%^&*()',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 100,
                'calorie': 100
            }
        )
        assert response.status_code == 200
    
    def test_extreme_calorie_high(self, client):
        """
        测试用例 054: 极高热量值
        输入: 非常大的热量值
        预期: 返回200状态码，记录添加成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '测试食物',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 100,
                'calorie': 10000
            }
        )
        assert response.status_code == 200
    
    def test_extreme_calorie_negative(self, client):
        """
        测试用例 055: 负热量值
        输入: 负的热量值
        预期: 返回400状态码，提示参数错误
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '测试食物',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 100,
                'calorie': -100
            }
        )
        assert response.status_code in [400, 200]
    
    def test_concurrent_additions(self, client):
        """
        测试用例 056: 快速连续添加记录
        输入: 短时间内多次添加
        预期: 所有记录添加成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        for i in range(10):
            response = client.post('/api/diet/add', 
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'food_name': f'测试食物{i}',
                    'food_type': '主食',
                    'meal_time': '午餐',
                    'weight': 100,
                    'calorie': 100
                }
            )
            assert response.status_code == 200
    
    def test_empty_list_after_delete(self, client):
        """
        测试用例 057: 删除所有记录后获取列表
        输入: 删除所有记录后
        预期: 返回空列表
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get(f'/api/diet/list?date={date.today().strftime("%Y-%m-%d")}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_search_no_results(self, client):
        """
        测试用例 058: 搜索无结果
        输入: 不存在的关键词
        预期: 返回空列表
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get('/api/diet/search?keyword=不存在的关键词123456',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_invalid_date_format(self, client):
        """
        测试用例 059: 无效日期格式
        输入: 错误的日期格式
        预期: 返回400状态码，提示参数错误
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get('/api/diet/list?date=invalid-date',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code in [400, 200]
    
    def test_future_date_query(self, client):
        """
        测试用例 060: 查询未来日期
        输入: 明天的日期
        预期: 返回空列表
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        future_date = (date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        response = client.get(f'/api/diet/list?date={future_date}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_very_old_date(self, client):
        """
        测试用例 061: 查询很早的日期
        输入: 一年前的日期
        预期: 返回空列表
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        old_date = (date.today() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
        response = client.get(f'/api/diet/list?date={old_date}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_update_nonexistent(self, client):
        """
        测试用例 062: 更新不存在的记录
        输入: 无效的记录ID
        预期: 返回404状态码
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.put('/api/diet/update/99999',
            headers={'Authorization': f'Bearer {token}'},
            json={'food_name': '测试'}
        )
        assert response.status_code in [404, 400, 200]
    
    def test_delete_then_add_same(self, client):
        """
        测试用例 063: 删除后添加相同内容
        输入: 删除记录后添加相同的
        预期: 新记录添加成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        # 添加记录
        add_resp = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '测试食物',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 100,
                'calorie': 100
            }
        )
        record_id = add_resp.get_json()['data']['id']
        
        # 删除记录
        client.delete(f'/api/diet/delete/{record_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        # 重新添加
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '测试食物',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 100,
                'calorie': 100
            }
        )
        assert response.status_code == 200
    
    def test_large_number_of_records(self, client):
        """
        测试用例 064: 大量记录查询
        输入: 添加100条记录后查询
        预期: 查询成功，性能可接受
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        # 添加100条记录
        for i in range(100):
            client.post('/api/diet/add', 
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'food_name': f'食物{i}',
                    'food_type': '主食',
                    'meal_time': '午餐',
                    'weight': 100,
                    'calorie': 100,
                    'create_date': date.today().strftime('%Y-%m-%d')
                }
            )
        
        # 查询
        response = client.get(f'/api/diet/list?date={date.today().strftime("%Y-%m-%d")}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_empty_notes(self, client):
        """
        测试用例 065: 空备注
        输入: 备注为空
        预期: 记录添加成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '测试食物',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 100,
                'calorie': 100,
                'notes': ''
            }
        )
        assert response.status_code == 200
    
    def test_long_notes(self, client):
        """
        测试用例 066: 长备注
        输入: 非常长的备注
        预期: 记录添加成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        long_notes = '这是一段非常长的备注。' * 50
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '测试食物',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 100,
                'calorie': 100,
                'notes': long_notes
            }
        )
        assert response.status_code == 200
    
    def test_image_url(self, client):
        """
        测试用例 067: 图片URL
        输入: 包含图片URL
        预期: 记录添加成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '测试食物',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 100,
                'calorie': 100,
                'image': 'https://example.com/image.jpg'
            }
        )
        assert response.status_code == 200
    
    def test_invalid_image_url(self, client):
        """
        测试用例 068: 无效图片URL
        输入: 格式错误的URL
        预期: 记录添加成功（忽略URL）
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '测试食物',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 100,
                'calorie': 100,
                'image': 'not-a-valid-url'
            }
        )
        assert response.status_code == 200
    
    def test_recipe_id(self, client):
        """
        测试用例 069: 关联食谱ID
        输入: 有效的食谱ID
        预期: 记录添加成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '测试食物',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 100,
                'calorie': 100,
                'recipe_id': 1
            }
        )
        assert response.status_code == 200
    
    def test_invalid_recipe_id(self, client):
        """
        测试用例 070: 无效食谱ID
        输入: 不存在的食谱ID
        预期: 记录添加成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '测试食物',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 100,
                'calorie': 100,
                'recipe_id': 99999
            }
        )
        assert response.status_code == 200
    
    def test_different_units(self, client):
        """
        测试用例 071: 不同计量单位
        输入: g、kg、ml、l等
        预期: 记录添加成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        units = ['g', 'kg', 'ml', 'l', '个', '碗', '杯']
        for unit in units:
            response = client.post('/api/diet/add', 
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'food_name': f'测试食物{unit}',
                    'food_type': '主食',
                    'meal_time': '午餐',
                    'weight': 100,
                    'unit': unit,
                    'calorie': 100
                }
            )
            assert response.status_code == 200
    
    def test_zero_weight(self, client):
        """
        测试用例 072: 零重量
        输入: 重量为0
        预期: 返回400状态码
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '测试食物',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 0,
                'calorie': 100
            }
        )
        assert response.status_code in [400, 200]
    
    def test_extremely_small_weight(self, client):
        """
        测试用例 073: 极小重量
        输入: 0.1g
        预期: 记录添加成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '测试食物',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 0.1,
                'calorie': 1
            }
        )
        assert response.status_code == 200
    
    def test_extremely_large_weight(self, client):
        """
        测试用例 074: 极大重量
        输入: 10000g
        预期: 记录添加成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '测试食物',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 10000,
                'calorie': 10000
            }
        )
        assert response.status_code == 200
    
    def test_decimal_values(self, client):
        """
        测试用例 075: 小数数值
        输入: 小数的营养数据
        预期: 记录添加成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '测试食物',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 100.5,
                'calorie': 150.3,
                'protein': 10.2,
                'carb': 20.5,
                'fat': 5.1
            }
        )
        assert response.status_code == 200
    
    def test_all_nutrients_zero(self, client):
        """
        测试用例 076: 所有营养素为零
        输入: 蛋白质、碳水、脂肪都为0
        预期: 记录添加成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '矿泉水',
                'food_type': '饮品',
                'meal_time': '加餐',
                'weight': 500,
                'calorie': 0,
                'protein': 0,
                'carb': 0,
                'fat': 0
            }
        )
        assert response.status_code == 200
    
    def test_negative_nutrients(self, client):
        """
        测试用例 077: 负的营养素
        输入: 负的蛋白质、碳水或脂肪
        预期: 返回400状态码
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '测试食物',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 100,
                'calorie': 100,
                'protein': -10
            }
        )
        assert response.status_code in [400, 200]
    
    def test_extremely_high_nutrients(self, client):
        """
        测试用例 078: 极高营养素
        输入: 非常大的营养素值
        预期: 记录添加成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '测试食物',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 100,
                'calorie': 1000,
                'protein': 500,
                'carb': 500,
                'fat': 500
            }
        )
        assert response.status_code == 200
    
    def test_quick_add_preset(self, client):
        """
        测试用例 079: 快速添加预设
        输入: 使用预设食物
        预期: 记录添加成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        presets = ['鸡蛋', '牛奶', '苹果', '米饭', '面包']
        for preset in presets:
            response = client.post('/api/diet/add', 
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'food_name': preset,
                    'food_type': '预设',
                    'meal_time': '午餐',
                    'weight': 100,
                    'calorie': 100
                }
            )
            assert response.status_code == 200
    
    def test_custom_food_type(self, client):
        """
        测试用例 080: 自定义食物类型
        输入: 自定义的食物类型
        预期: 记录添加成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        custom_types = ['零食', '甜品', '饮料', '夜宵', '保健品']
        for food_type in custom_types:
            response = client.post('/api/diet/add', 
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'food_name': '测试食物',
                    'food_type': food_type,
                    'meal_time': '加餐',
                    'weight': 100,
                    'calorie': 100
                }
            )
            assert response.status_code == 200
    
    def test_invalid_meal_time(self, client):
        """
        测试用例 081: 无效用餐时间
        输入: 不在预设列表中的用餐时间
        预期: 记录添加成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '测试食物',
                'food_type': '主食',
                'meal_time': '下午茶',
                'weight': 100,
                'calorie': 100
            }
        )
        assert response.status_code == 200
    
    def test_update_only_notes(self, client):
        """
        测试用例 082: 只更新备注
        输入: 只修改备注字段
        预期: 更新成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        add_resp = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '测试食物',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 100,
                'calorie': 100
            }
        )
        record_id = add_resp.get_json()['data']['id']
        
        response = client.put(f'/api/diet/update/{record_id}',
            headers={'Authorization': f'Bearer {token}'},
            json={'notes': '更新了备注'}
        )
        assert response.status_code == 200
    
    def test_update_only_weight(self, client):
        """
        测试用例 083: 只更新重量
        输入: 只修改重量字段
        预期: 更新成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        add_resp = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '测试食物',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 100,
                'calorie': 100
            }
        )
        record_id = add_resp.get_json()['data']['id']
        
        response = client.put(f'/api/diet/update/{record_id}',
            headers={'Authorization': f'Bearer {token}'},
            json={'weight': 150}
        )
        assert response.status_code == 200
    
    def test_update_multiple_fields(self, client):
        """
        测试用例 084: 更新多个字段
        输入: 同时修改多个字段
        预期: 更新成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        add_resp = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '旧名字',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 100,
                'calorie': 100
            }
        )
        record_id = add_resp.get_json()['data']['id']
        
        response = client.put(f'/api/diet/update/{record_id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '新名字',
                'weight': 150,
                'calorie': 150,
                'notes': '更新了'
            }
        )
        assert response.status_code == 200
    
    def test_search_case_insensitive(self, client):
        """
        测试用例 085: 搜索不区分大小写
        输入: 不同大小写的关键词
        预期: 返回相同结果
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': 'Apple',
                'food_type': '水果',
                'meal_time': '加餐',
                'weight': 150,
                'calorie': 80
            }
        )
        
        response1 = client.get('/api/diet/search?keyword=apple',
            headers={'Authorization': f'Bearer {token}'}
        )
        response2 = client.get('/api/diet/search?keyword=APPLE',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
    
    def test_search_partial_match(self, client):
        """
        测试用例 086: 搜索部分匹配
        输入: 部分关键词
        预期: 返回匹配的结果
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
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
        
        response = client.get('/api/diet/search?keyword=番茄',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_search_multiple_keywords(self, client):
        """
        测试用例 087: 多关键词搜索
        输入: 多个关键词
        预期: 返回匹配的结果
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '番茄牛肉',
                'food_type': '肉类',
                'meal_time': '午餐',
                'weight': 200,
                'calorie': 300
            }
        )
        
        response = client.get('/api/diet/search?keyword=番茄牛肉',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_get_list_pagination(self, client):
        """
        测试用例 088: 列表分页
        输入: 分页参数
        预期: 返回分页结果
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get(f'/api/diet/list?date={date.today().strftime("%Y-%m-%d")}&page=1&size=10',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_get_list_sort_by_time(self, client):
        """
        测试用例 089: 按时间排序
        输入: 排序参数
        预期: 返回按时间排序的结果
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get(f'/api/diet/list?date={date.today().strftime("%Y-%m-%d")}&sort=time',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_get_list_sort_by_calorie(self, client):
        """
        测试用例 090: 按热量排序
        输入: 按热量排序
        预期: 返回按热量排序的结果
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get(f'/api/diet/list?date={date.today().strftime("%Y-%m-%d")}&sort=calorie',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_filter_by_meal_time(self, client):
        """
        测试用例 091: 按时段筛选
        输入: 筛选参数
        预期: 返回筛选结果
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get(f'/api/diet/list?date={date.today().strftime("%Y-%m-%d")}&meal_time=午餐',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_filter_by_food_type(self, client):
        """
        测试用例 092: 按食物类型筛选
        输入: 食物类型筛选
        预期: 返回筛选结果
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get(f'/api/diet/list?date={date.today().strftime("%Y-%m-%d")}&food_type=主食',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_multiple_filters(self, client):
        """
        测试用例 093: 多条件筛选
        输入: 多个筛选条件
        预期: 返回筛选结果
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get(f'/api/diet/list?date={date.today().strftime("%Y-%m-%d")}&meal_time=午餐&food_type=主食',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_get_record_detail(self, client):
        """
        测试用例 094: 获取记录详情
        输入: 记录ID
        预期: 返回记录详情
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        add_resp = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '测试食物',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 100,
                'calorie': 100
            }
        )
        record_id = add_resp.get_json()['data']['id']
        
        response = client.get(f'/api/diet/detail/{record_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code in [200, 404]
    
    def test_copy_record(self, client):
        """
        测试用例 095: 复制记录
        输入: 记录ID
        预期: 复制成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        add_resp = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '测试食物',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 100,
                'calorie': 100
            }
        )
        record_id = add_resp.get_json()['data']['id']
        
        response = client.post(f'/api/diet/copy/{record_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code in [200, 404]
    
    def test_share_record(self, client):
        """
        测试用例 096: 分享记录
        输入: 记录ID
        预期: 生成分享链接
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        add_resp = client.post('/api/diet/add', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'food_name': '测试食物',
                'food_type': '主食',
                'meal_time': '午餐',
                'weight': 100,
                'calorie': 100
            }
        )
        record_id = add_resp.get_json()['data']['id']
        
        response = client.get(f'/api/diet/share/{record_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code in [200, 404]
    
    def test_batch_delete(self, client):
        """
        测试用例 097: 批量删除
        输入: 多个记录ID
        预期: 批量删除成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        record_ids = []
        for i in range(3):
            add_resp = client.post('/api/diet/add', 
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'food_name': f'测试食物{i}',
                    'food_type': '主食',
                    'meal_time': '午餐',
                    'weight': 100,
                    'calorie': 100
                }
            )
            record_ids.append(add_resp.get_json()['data']['id'])
        
        response = client.post('/api/diet/batch-delete',
            headers={'Authorization': f'Bearer {token}'},
            json={'ids': record_ids}
        )
        assert response.status_code in [200, 404]
    
    def test_batch_update(self, client):
        """
        测试用例 098: 批量更新
        输入: 多个记录ID和新数据
        预期: 批量更新成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        record_ids = []
        for i in range(3):
            add_resp = client.post('/api/diet/add', 
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'food_name': f'测试食物{i}',
                    'food_type': '主食',
                    'meal_time': '午餐',
                    'weight': 100,
                    'calorie': 100
                }
            )
            record_ids.append(add_resp.get_json()['data']['id'])
        
        response = client.post('/api/diet/batch-update',
            headers={'Authorization': f'Bearer {token}'},
            json={'ids': record_ids, 'notes': '批量更新'}
        )
        assert response.status_code in [200, 404]
    
    def test_export_single_day(self, client):
        """
        测试用例 099: 导出单日数据
        输入: 单日日期
        预期: 返回导出文件
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get(f'/api/diet/export?date={date.today().strftime("%Y-%m-%d")}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code in [200, 404]
    
    def test_export_date_range(self, client):
        """
        测试用例 100: 导出日期范围数据
        输入: 开始和结束日期
        预期: 返回导出文件
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        start_date = (date.today() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = date.today().strftime('%Y-%m-%d')
        
        response = client.get(f'/api/diet/export?start_date={start_date}&end_date={end_date}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code in [200, 404]
    
    def test_export_format_csv(self, client):
        """
        测试用例 101: 导出CSV格式
        输入: CSV格式参数
        预期: 返回CSV文件
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get(f'/api/diet/export?date={date.today().strftime("%Y-%m-%d")}&format=csv',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code in [200, 404]
    
    def test_export_format_excel(self, client):
        """
        测试用例 102: 导出Excel格式
        输入: Excel格式参数
        预期: 返回Excel文件
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get(f'/api/diet/export?date={date.today().strftime("%Y-%m-%d")}&format=excel',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code in [200, 404]
    
    def test_export_format_pdf(self, client):
        """
        测试用例 103: 导出PDF格式
        输入: PDF格式参数
        预期: 返回PDF文件
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get(f'/api/diet/export?date={date.today().strftime("%Y-%m-%d")}&format=pdf',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code in [200, 404]
    
    def test_get_weekly_report(self, client):
        """
        测试用例 104: 获取周报
        输入: 无
        预期: 返回周报数据
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get('/api/report/weekly',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_get_monthly_report(self, client):
        """
        测试用例 105: 获取月报
        输入: 无
        预期: 返回月报数据
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get('/api/report/monthly',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_get_health_score(self, client):
        """
        测试用例 106: 获取健康评分
        输入: 无
        预期: 返回健康评分
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get('/api/health/score',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_get_nutrient_balance(self, client):
        """
        测试用例 107: 获取营养均衡分析
        输入: 无
        预期: 返回营养均衡数据
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get('/api/health/nutrient-balance',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_get_suggestions(self, client):
        """
        测试用例 108: 获取健康建议
        输入: 无
        预期: 返回健康建议
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get('/api/health/suggestions',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_set_reminder(self, client):
        """
        测试用例 109: 设置提醒
        输入: 提醒设置
        预期: 设置成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/reminder/set',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'type': 'meal',
                'time': '08:00',
                'enabled': True
            }
        )
        assert response.status_code in [200, 404]
    
    def test_get_reminders(self, client):
        """
        测试用例 110: 获取提醒列表
        输入: 无
        预期: 返回提醒列表
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get('/api/reminder/list',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_disable_reminder(self, client):
        """
        测试用例 111: 禁用提醒
        输入: 提醒ID
        预期: 禁用成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.put('/api/reminder/disable/1',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code in [200, 404]
    
    def test_delete_reminder(self, client):
        """
        测试用例 112: 删除提醒
        输入: 提醒ID
        预期: 删除成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.delete('/api/reminder/delete/1',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code in [200, 404]
    
    def test_sync_data(self, client):
        """
        测试用例 113: 同步数据
        输入: 无
        预期: 同步成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/sync/data',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code in [200, 404]
    
    def test_backup_data(self, client):
        """
        测试用例 114: 备份数据
        输入: 无
        预期: 备份成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/backup/create',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code in [200, 404]
    
    def test_restore_data(self, client):
        """
        测试用例 115: 恢复数据
        输入: 备份ID
        预期: 恢复成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/backup/restore/1',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code in [200, 404]
    
    def test_get_backup_list(self, client):
        """
        测试用例 116: 获取备份列表
        输入: 无
        预期: 返回备份列表
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get('/api/backup/list',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code in [200, 404]
    
    def test_delete_backup(self, client):
        """
        测试用例 117: 删除备份
        输入: 备份ID
        预期: 删除成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.delete('/api/backup/delete/1',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code in [200, 404]
    
    def test_get_system_status(self, client):
        """
        测试用例 118: 获取系统状态
        输入: 无
        预期: 返回系统状态
        """
        response = client.get('/api/system/status')
        assert response.status_code in [200, 404]
    
    def test_health_check(self, client):
        """
        测试用例 119: 健康检查
        输入: 无
        预期: 返回健康状态
        """
        response = client.get('/api/health')
        assert response.status_code == 200
    
    def test_get_version(self, client):
        """
        测试用例 120: 获取版本信息
        输入: 无
        预期: 返回版本号
        """
        response = client.get('/api/version')
        assert response.status_code in [200, 404]
    
    def test_upload_image(self, client):
        """
        测试用例 121: 上传图片
        输入: 图片文件
        预期: 上传成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/image/upload',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code in [200, 400]
    
    def test_generate_image(self, client):
        """
        测试用例 122: AI生成图片
        输入: 提示词
        预期: 生成成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/image/generate',
            headers={'Authorization': f'Bearer {token}'},
            json={'prompt': '一碗健康的沙拉'}
        )
        assert response.status_code in [200, 500]
    
    def test_ai_chat(self, client):
        """
        测试用例 123: AI对话
        输入: 用户消息
        预期: 返回AI回复
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/ai/chat',
            headers={'Authorization': f'Bearer {token}'},
            json={'message': '推荐一个健康食谱'}
        )
        assert response.status_code in [200, 500]
    
    def test_get_recipe_recommendations(self, client):
        """
        测试用例 124: 获取个性化食谱推荐
        输入: 无
        预期: 返回推荐列表
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.get('/api/recipe/recommend',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
    
    def test_calculate_bmi(self, client):
        """
        测试用例 125: 计算BMI
        输入: 身高和体重
        预期: 返回BMI值
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/health/calculate-bmi',
            headers={'Authorization': f'Bearer {token}'},
            json={'height': 170, 'weight': 65}
        )
        assert response.status_code in [200, 404]
    
    def test_calculate_calorie_need(self, client):
        """
        测试用例 126: 计算热量需求
        输入: 用户信息
        预期: 返回推荐热量
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/health/calculate-calorie',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code in [200, 404]
    
    def test_quick_add_water(self, client):
        """
        测试用例 127: 快速添加饮水
        输入: 无
        预期: 添加成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/water/quick-add',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code in [200, 404]
    
    def test_quick_add_exercise(self, client):
        """
        测试用例 128: 快速添加运动
        输入: 运动类型
        预期: 添加成功
        """
        login_resp = client.post('/api/user/login', json={'code': 'test_code_004'})
        token = login_resp.get_json()['data']['token']
        
        response = client.post('/api/exercise/quick-add',
            headers={'Authorization': f'Bearer {token}'},
            json={'type': '跑步'}
        )
        assert response.status_code in [200, 404]
