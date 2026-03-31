#!/usr/bin/env python3
"""
性能测试脚本
使用locust进行性能测试，生成并发-响应时间曲线
"""
import time
import json
import requests
import matplotlib.pyplot as plt
import numpy as np
from concurrent.futures import ThreadPoolExecutor

# 测试配置
BASE_URL = "http://localhost:5000"
TEST_ENDPOINTS = [
    "/api/user/login",
    "/api/diet/record",
    "/api/recommend/recipe",
    "/api/recipe/list",
    "/api/hotfood/list"
]

# 模拟用户数据
TEST_USER = {
    "code": "test_code"
}

TEST_DIET = {
    "food_name": "测试食物",
    "food_type": "主食",
    "meal_time": "早餐",
    "weight": 100
}

# 性能测试函数
def test_endpoint(endpoint, headers=None):
    """测试单个端点的响应时间"""
    url = BASE_URL + endpoint
    start_time = time.time()
    
    try:
        if endpoint == "/api/user/login":
            response = requests.post(url, json=TEST_USER, timeout=30)
        elif endpoint == "/api/diet/record":
            response = requests.post(url, json=TEST_DIET, headers=headers, timeout=30)
        elif endpoint == "/api/recommend/recipe":
            response = requests.post(url, headers=headers, timeout=30)
        else:
            response = requests.get(url, headers=headers, timeout=30)
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # 转换为毫秒
        return response_time, response.status_code
    except Exception as e:
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        return response_time, 500

# 并发测试函数
def run_concurrent_test(endpoint, concurrency, headers=None):
    """运行并发测试"""
    response_times = []
    status_codes = []
    
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(test_endpoint, endpoint, headers) for _ in range(concurrency)]
        for future in futures:
            response_time, status_code = future.result()
            response_times.append(response_time)
            status_codes.append(status_code)
    
    # 计算统计数据
    if response_times:
        avg_time = np.mean(response_times)
        max_time = np.max(response_times)
        min_time = np.min(response_times)
        success_rate = sum(1 for code in status_codes if code < 400) / len(status_codes) * 100
    else:
        avg_time = 0
        max_time = 0
        min_time = 0
        success_rate = 0
    
    return {
        "concurrency": concurrency,
        "avg_time": avg_time,
        "max_time": max_time,
        "min_time": min_time,
        "success_rate": success_rate,
        "response_times": response_times
    }

# 主测试函数
def run_performance_test():
    """运行性能测试"""
    print("=== 性能测试开始 ===")
    
    # 首先获取登录Token
    print("获取登录Token...")
    login_url = BASE_URL + "/api/user/login"
    try:
        response = requests.post(login_url, json=TEST_USER, timeout=30)
        if response.status_code == 200:
            token = response.json().get("data", {}).get("token")
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ 登录成功，获取到Token")
        else:
            print("⚠️  登录失败，使用空Token进行测试")
            headers = None
    except Exception as e:
        print(f"⚠️  登录失败：{e}，使用空Token进行测试")
        headers = None
    
    # 测试不同并发数
    concurrency_levels = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    test_results = {}
    
    for endpoint in TEST_ENDPOINTS:
        print(f"\n测试端点：{endpoint}")
        test_results[endpoint] = []
        
        for concurrency in concurrency_levels:
            print(f"  并发数：{concurrency}")
            result = run_concurrent_test(endpoint, concurrency, headers)
            test_results[endpoint].append(result)
            print(f"    平均响应时间：{result['avg_time']:.2f}ms")
            print(f"    最大响应时间：{result['max_time']:.2f}ms")
            print(f"    最小响应时间：{result['min_time']:.2f}ms")
            print(f"    成功率：{result['success_rate']:.2f}%")
    
    # 保存测试结果
    with open("performance_test_results.json", "w", encoding="utf-8") as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    
    print("\n=== 性能测试完成 ===")
    print("测试结果已保存到 performance_test_results.json")
    
    return test_results

# 生成性能测试图表
def generate_performance_charts(test_results):
    """生成性能测试图表"""
    print("\n=== 生成性能测试图表 ===")
    
    # 为每个端点生成图表
    for endpoint in TEST_ENDPOINTS:
        results = test_results[endpoint]
        concurrency_levels = [r['concurrency'] for r in results]
        avg_times = [r['avg_time'] for r in results]
        max_times = [r['max_time'] for r in results]
        
        # 创建图表
        plt.figure(figsize=(10, 6))
        plt.plot(concurrency_levels, avg_times, label='平均响应时间', marker='o')
        plt.plot(concurrency_levels, max_times, label='最大响应时间', marker='s')
        plt.xlabel('并发数')
        plt.ylabel('响应时间 (ms)')
        plt.title(f'{endpoint} 并发-响应时间曲线')
        plt.legend()
        plt.grid(True)
        
        # 保存图表
        chart_filename = f"performance_chart_{endpoint.replace('/', '_')}.png"
        plt.savefig(chart_filename)
        plt.close()
        print(f"✅ 图表已保存：{chart_filename}")

# 运行核心功能测试用例
def run_core_functionality_tests():
    """运行核心功能测试用例"""
    print("\n=== 核心功能测试用例 ===")
    
    test_cases = [
        {
            "name": "用户登录测试",
            "endpoint": "/api/user/login",
            "method": "POST",
            "data": TEST_USER,
            "expected_status": 200
        },
        {
            "name": "饮食记录添加测试",
            "endpoint": "/api/diet/record",
            "method": "POST",
            "data": TEST_DIET,
            "expected_status": 200
        },
        {
            "name": "食谱推荐测试",
            "endpoint": "/api/recommend/recipe",
            "method": "POST",
            "data": {},
            "expected_status": 200
        },
        {
            "name": "食谱列表测试",
            "endpoint": "/api/recipe/list",
            "method": "GET",
            "data": {},
            "expected_status": 200
        },
        {
            "name": "热点美食列表测试",
            "endpoint": "/api/hotfood/list",
            "method": "GET",
            "data": {},
            "expected_status": 200
        }
    ]
    
    # 获取登录Token
    login_url = BASE_URL + "/api/user/login"
    try:
        response = requests.post(login_url, json=TEST_USER, timeout=30)
        if response.status_code == 200:
            token = response.json().get("data", {}).get("token")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            headers = None
    except Exception as e:
        print(f"登录失败：{e}")
        headers = None
    
    # 运行测试用例
    for test_case in test_cases:
        print(f"\n测试：{test_case['name']}")
        url = BASE_URL + test_case['endpoint']
        
        try:
            if test_case['method'] == "POST":
                response = requests.post(url, json=test_case['data'], headers=headers, timeout=30)
            else:
                response = requests.get(url, headers=headers, timeout=30)
            
            status_code = response.status_code
            print(f"  状态码：{status_code}")
            print(f"  预期状态码：{test_case['expected_status']}")
            
            if status_code == test_case['expected_status']:
                print("  ✅ 测试通过")
            else:
                print("  ❌ 测试失败")
                print(f"  响应内容：{response.text[:200]}...")
        except Exception as e:
            print(f"  ❌ 测试失败：{e}")

if __name__ == "__main__":
    # 首先启动服务器
    print("请先启动服务器，然后按回车键继续...")
    input()
    
    # 运行性能测试
    test_results = run_performance_test()
    
    # 生成性能测试图表
    generate_performance_charts(test_results)
    
    # 运行核心功能测试用例
    run_core_functionality_tests()
