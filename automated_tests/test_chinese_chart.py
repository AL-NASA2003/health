#!/usr/bin/env python3
"""简单的中文图表测试脚本"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入并运行测试
from automated_test_suite import TestDataGenerator, VisualizationGenerator, OUTPUT_DIR

# 创建测试数据
test_data = TestDataGenerator.generate_test_data()

print(f"✅ 测试数据已生成")
print(f"📊 正在生成图表...")

# 只生成第一个图表
VisualizationGenerator._generate_data_stats_chart(test_data)

print(f"✅ 图表已保存到: {os.path.join(OUTPUT_DIR, '01_data_statistics.png')}")
print(f"🎯 请查看图表，验证中文是否正常显示")
