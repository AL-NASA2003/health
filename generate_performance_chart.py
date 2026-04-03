#!/usr/bin/env python3
"""
根据已有测试结果生成性能测试图表
"""
import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False

# 加载测试结果
with open('performance_test_results.json', 'r', encoding='utf-8') as f:
    test_results = json.load(f)

# 测试的端点
endpoints = list(test_results.keys())

# 为每个端点生成图表
for endpoint in endpoints:
    results = test_results[endpoint]
    concurrency_levels = [r['concurrency'] for r in results]
    avg_times = [r['avg_time'] for r in results]
    max_times = [r['max_time'] for r in results]
    success_rates = [r['success_rate'] for r in results]
    
    # 创建图表
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # 响应时间曲线
    ax1.plot(concurrency_levels, avg_times, label='平均响应时间', marker='o', linewidth=2)
    ax1.plot(concurrency_levels, max_times, label='最大响应时间', marker='s', linewidth=2, linestyle='--')
    ax1.set_xlabel('并发数', fontsize=12)
    ax1.set_ylabel('响应时间 (ms)', fontsize=12)
    ax1.set_title(f'{endpoint} 并发-响应时间曲线', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='both', labelsize=10)
    
    # 成功率曲线
    ax2.plot(concurrency_levels, success_rates, label='成功率', marker='D', linewidth=2, color='green')
    ax2.set_xlabel('并发数', fontsize=12)
    ax2.set_ylabel('成功率 (%)', fontsize=12)
    ax2.set_title(f'{endpoint} 并发-成功率曲线', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([90, 105])
    ax2.tick_params(axis='both', labelsize=10)
    
    plt.tight_layout()
    
    # 保存图表
    chart_filename = f"performance_chart_{endpoint.replace('/', '_')}.png"
    plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
    print(f"图表已保存：{chart_filename}")
    plt.close()

# 生成综合对比图表
plt.figure(figsize=(14, 8))

endpoint_names = {
    '/api/user/login': '用户登录',
    '/api/diet/record': '饮食记录',
    '/api/recommend/recipe': '推荐系统',
    '/api/recipe/list': '食谱列表',
    '/api/hotfood/list': '热点美食'
}

colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

for i, endpoint in enumerate(endpoints):
    results = test_results[endpoint]
    concurrency_levels = [r['concurrency'] for r in results]
    avg_times = [r['avg_time'] for r in results]
    plt.plot(concurrency_levels, avg_times, 
             label=endpoint_names.get(endpoint, endpoint), 
             marker='o', linewidth=2, color=colors[i])

plt.xlabel('并发数', fontsize=13)
plt.ylabel('平均响应时间 (ms)', fontsize=13)
plt.title('各API端点性能对比 - 并发-响应时间曲线', fontsize=16, fontweight='bold')
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.tick_params(axis='both', labelsize=11)
plt.tight_layout()

plt.savefig('performance_chart_all_endpoints.png', dpi=300, bbox_inches='tight')
print("综合对比图表已保存：performance_chart_all_endpoints.png")
plt.close()

print("\n所有图表生成完成！")
