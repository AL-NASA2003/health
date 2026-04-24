#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康饮食管理系统 - 综合测试脚本
符合毕业设计终稿中的系统实现与测试
"""

import sys
import os
import time
import json
import unittest
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.models.diet_record import DietRecord
from app.models.exercise_record import ExerciseRecord
from app.models.forum_post import ForumPost
from app.models.hand_account import HandAccount
from app.models.health_index_record import HealthIndexRecord
from app.models.comment import Comment
from app.models.water_record import WaterRecord


class TestColors:
    """终端输出颜色"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """打印测试标题"""
    print(f"\n{TestColors.HEADER}{TestColors.BOLD}{'='*70}{TestColors.ENDC}")
    print(f"{TestColors.HEADER}{TestColors.BOLD}  {text}{TestColors.ENDC}")
    print(f"{TestColors.HEADER}{'='*70}{TestColors.ENDC}\n")


def print_success(text):
    """打印成功信息"""
    print(f"{TestColors.OKGREEN}✓ {text}{TestColors.ENDC}")


def print_failure(text):
    """打印失败信息"""
    print(f"{TestColors.FAIL}✗ {text}{TestColors.ENDC}")


def print_warning(text):
    """打印警告信息"""
    print(f"{TestColors.WARNING}⚠ {text}{TestColors.ENDC}")


def print_info(text):
    """打印信息"""
    print(f"{TestColors.OKCYAN}  {text}{TestColors.ENDC}")


class HealthSystemTester:
    """健康饮食系统综合测试"""

    def __init__(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.token = None
        self.user_id = None

    def run_test(self, test_name, test_func):
        """运行单个测试"""
        self.total_tests += 1
        print_info(f"测试: {test_name}")
        try:
            start_time = time.time()
            result = test_func()
            elapsed = time.time() - start_time
            if result:
                self.passed_tests += 1
                print_success(f"{test_name} 通过 ({elapsed:.2f}s)")
                self.test_results.append({
                    'name': test_name,
                    'status': 'PASS',
                    'time': elapsed
                })
                return True
            else:
                self.failed_tests += 1
                print_failure(f"{test_name} 失败")
                self.test_results.append({
                    'name': test_name,
                    'status': 'FAIL',
                    'time': elapsed
                })
                return False
        except Exception as e:
            self.failed_tests += 1
            print_failure(f"{test_name} 异常: {str(e)}")
            self.test_results.append({
                'name': test_name,
                'status': 'ERROR',
                'time': 0,
                'error': str(e)
            })
            return False

    # ==================== 测试模块 ====================

    def test_1_system_init(self):
        """测试1: 系统初始化"""
        print_header("测试模块1: 系统初始化")

        def test_root():
            """测试根路径访问"""
            response = self.client.get('/')
            return response.status_code == 200

        def test_db_connection():
            """测试数据库连接"""
            with self.app.app_context():
                test_query = db.session.execute(db.text('SELECT 1'))
                return test_query.scalar() == 1

        self.run_test("根路径访问", test_root)
        self.run_test("数据库连接", test_db_connection)

        return self.failed_tests == 0

    def test_2_user_management(self):
        """测试2: 用户管理模块"""
        print_header("测试模块2: 用户管理")

        def test_login():
            """测试用户登录"""
            response = self.client.post('/api/user/login', json={
                'username': 'test',
                'password': '123456'
            })
            data = response.get_json()
            if response.status_code == 200:
                self.token = data.get('data', {}).get('token')
                self.user_id = data.get('data', {}).get('user_info', {}).get('id')
                return self.token is not None
            return False

        def test_get_user_info():
            """测试获取用户信息"""
            if not self.token:
                return False
            response = self.client.get('/api/user/info', headers={
                'Authorization': f'Bearer {self.token}'
            })
            return response.status_code == 200

        self.run_test("用户登录", test_login)
        self.run_test("获取用户信息", test_get_user_info)

        return self.failed_tests <= 1

    def test_3_recipe_module(self):
        """测试3: 食谱模块"""
        print_header("测试模块3: 食谱功能")

        def test_get_recipe_list():
            """测试获取食谱列表"""
            if not self.token:
                return False
            response = self.client.get('/api/recipe/list', headers={
                'Authorization': f'Bearer {self.token}'
            })
            return response.status_code == 200

        def test_recipe_search():
            """测试食谱搜索"""
            if not self.token:
                return False
            response = self.client.get('/api/recipe/search?keyword=鸡蛋', headers={
                'Authorization': f'Bearer {self.token}'
            })
            return response.status_code == 200

        self.run_test("获取食谱列表", test_get_recipe_list)
        self.run_test("食谱搜索", test_recipe_search)

        return self.failed_tests <= 1

    def test_4_ingredient_module(self):
        """测试4: 食材管理模块"""
        print_header("测试模块4: 食材管理")

        def test_get_ingredient_list():
            """测试获取食材列表"""
            if not self.token:
                return False
            response = self.client.get('/api/ingredient/list', headers={
                'Authorization': f'Bearer {self.token}'
            })
            return response.status_code == 200

        self.run_test("获取食材列表", test_get_ingredient_list)

        return self.failed_tests <= 1

    def test_5_diet_record_module(self):
        """测试5: 饮食记录模块"""
        print_header("测试模块5: 饮食记录")

        def test_get_diet_records():
            """测试获取饮食记录"""
            if not self.token:
                return False
            response = self.client.get('/api/diet/list', headers={
                'Authorization': f'Bearer {self.token}'
            })
            return response.status_code == 200

        self.run_test("获取饮食记录", test_get_diet_records)

        return self.failed_tests <= 1

    def test_6_exercise_module(self):
        """测试6: 运动记录模块"""
        print_header("测试模块6: 运动记录")

        def test_get_exercise_records():
            """测试获取运动记录"""
            if not self.token:
                return False
            response = self.client.get('/api/exercise/list', headers={
                'Authorization': f'Bearer {self.token}'
            })
            return response.status_code == 200

        self.run_test("获取运动记录", test_get_exercise_records)

        return self.failed_tests <= 1

    def test_7_water_module(self):
        """测试7: 饮水记录模块"""
        print_header("测试模块7: 饮水记录")

        def test_get_water_records():
            """测试获取饮水记录"""
            if not self.token:
                return False
            response = self.client.get('/api/water/list', headers={
                'Authorization': f'Bearer {self.token}'
            })
            return response.status_code == 200

        self.run_test("获取饮水记录", test_get_water_records)

        return self.failed_tests <= 1

    def test_8_forum_module(self):
        """测试8: 论坛模块"""
        print_header("测试模块8: 论坛功能")

        def test_get_post_list():
            """测试获取帖子列表"""
            if not self.token:
                return False
            response = self.client.get('/api/forum/list', headers={
                'Authorization': f'Bearer {self.token}'
            })
            return response.status_code == 200

        def test_add_post():
            """测试发布帖子"""
            if not self.token:
                return False
            response = self.client.post('/api/forum/add', headers={
                'Authorization': f'Bearer {self.token}'
            }, json={
                'title': '测试帖子 - 健康饮食分享',
                'content': '今天尝试了一份健康的沙拉，非常美味！'
            })
            return response.status_code in [200, 201]

        self.run_test("获取帖子列表", test_get_post_list)
        self.run_test("发布帖子", test_add_post)

        return self.failed_tests <= 1

    def test_9_handbook_module(self):
        """测试9: 手账模块"""
        print_header("测试模块9: 手账功能")

        def test_get_handbook_list():
            """测试获取手账列表"""
            if not self.token:
                return False
            response = self.client.get('/api/handbook/list', headers={
                'Authorization': f'Bearer {self.token}'
            })
            return response.status_code == 200

        def test_add_handbook():
            """测试添加手账"""
            if not self.token:
                return False
            response = self.client.post('/api/handbook/add', headers={
                'Authorization': f'Bearer {self.token}'
            }, json={
                'title': '测试手账',
                'content': '今天的饮食记录'
            })
            return response.status_code in [200, 201]

        self.run_test("获取手账列表", test_get_handbook_list)
        self.run_test("添加手账", test_add_handbook)

        return self.failed_tests <= 1

    def test_10_recommend_module(self):
        """测试10: 个性化推荐模块"""
        print_header("测试模块10: 个性化推荐")

        def test_get_personalized_recipes():
            """测试个性化食谱推荐"""
            if not self.token:
                return False
            response = self.client.post('/api/recipe/recommend', headers={
                'Authorization': f'Bearer {self.token}'
            })
            return response.status_code == 200

        self.run_test("个性化食谱推荐", test_get_personalized_recipes)

        return self.failed_tests <= 1

    def test_11_hotfood_module(self):
        """测试11: 热点美食模块"""
        print_header("测试模块11: 热点美食")

        def test_get_hotfood_list():
            """测试获取热点美食列表"""
            response = self.client.get('/api/hotfood/list')
            return response.status_code == 200

        self.run_test("获取热点美食列表", test_get_hotfood_list)

        return self.failed_tests <= 1

    def test_12_health_module(self):
        """测试12: 健康指标模块"""
        print_header("测试模块12: 健康指标")

        def test_get_health_records():
            """测试获取健康记录"""
            if not self.token:
                return False
            response = self.client.get('/api/health/list', headers={
                'Authorization': f'Bearer {self.token}'
            })
            return response.status_code == 200

        self.run_test("获取健康记录", test_get_health_records)

        return self.failed_tests <= 1

    def test_13_api_documentation(self):
        """测试13: API文档"""
        print_header("测试模块13: API文档")

        def test_api_docs():
            """测试API文档访问"""
            response = self.client.get('/api/docs')
            return response.status_code in [200, 301, 302]

        self.run_test("API文档访问", test_api_docs)

        return self.failed_tests == 0

    # ==================== 主测试流程 ====================

    def run_all_tests(self):
        """运行所有测试"""
        print_header("健康饮食管理系统 - 综合测试开始")
        print_info(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print_info(f"环境: {self.app.config.get('ENV', 'development')}")

        start_time = time.time()

        # 运行各个测试模块
        with self.app.app_context():
            self.test_1_system_init()
            self.test_2_user_management()
            self.test_3_recipe_module()
            self.test_4_ingredient_module()
            self.test_5_diet_record_module()
            self.test_6_exercise_module()
            self.test_7_water_module()
            self.test_8_forum_module()
            self.test_9_handbook_module()
            self.test_10_recommend_module()
            self.test_11_hotfood_module()
            self.test_12_health_module()
            self.test_13_api_documentation()

        total_time = time.time() - start_time

        # 打印测试报告
        self.print_report(total_time)

        return self.failed_tests == 0

    def print_report(self, total_time):
        """打印测试报告"""
        print_header("测试报告")

        print_info(f"总测试数: {self.total_tests}")
        print_success(f"通过: {self.passed_tests}")
        if self.failed_tests > 0:
            print_failure(f"失败: {self.failed_tests}")

        pass_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print_info(f"通过率: {pass_rate:.1f}%")
        print_info(f"总耗时: {total_time:.2f}秒")

        # 打印详细结果
        print_header("详细测试结果")
        for result in self.test_results:
            status_symbol = "✓" if result['status'] == 'PASS' else "✗"
            status_color = TestColors.OKGREEN if result['status'] == 'PASS' else TestColors.FAIL
            print(f"{status_color}{status_symbol} {result['name']} ({result.get('time', 0):.2f}s){TestColors.ENDC}")
            if result.get('error'):
                print(f"  错误: {result['error']}")

        # 总体评价
        print_header("总体评价")
        if pass_rate >= 90:
            print_success("系统运行良好，所有核心功能正常！")
        elif pass_rate >= 70:
            print_warning("系统基本可用，部分功能需要修复")
        else:
            print_failure("系统存在较多问题，需要全面检查")

        print()


def main():
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                   健康饮食管理系统测试脚本                       ║
║           Health Diet Management System Test Suite              ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    tester = HealthSystemTester()
    success = tester.run_all_tests()

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
