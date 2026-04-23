#!/usr/bin/env python3
"""
快速启动脚本 - 禁用爬虫和定时任务，禁用Token验证，提升开发速度
"""
import sys
import os

# 设置环境变量禁用爬虫和定时任务
os.environ['DISABLE_SCHEDULER'] = 'True'
os.environ['HEALTH_DATA_MODE'] = 'VIRTUAL'
os.environ['DISABLE_TOKEN_VERIFY'] = 'True'  # 开发模式禁用token验证

print("🚀 快速启动模式已开启：")
print("   - ✅ 爬虫已禁用")
print("   - ✅ Token验证已禁用")
print("   - ✅ 使用固定 user_id=1")
print("")

# 导入并运行
from run import *