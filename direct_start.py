#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接启动后端服务 - 虚拟数据模式
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量
os.environ['HEALTH_DATA_MODE'] = 'VIRTUAL'
os.environ['DISABLE_SCHEDULER'] = 'True'

print("=" * 60)
print("健康饮食系统 - 直接启动")
print("=" * 60)
print(f"数据模式: VIRTUAL (虚拟数据)")
print("=" * 60)

# 启动主程序
from run import *
