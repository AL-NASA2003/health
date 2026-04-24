#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试营养数据显示"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.user import User

def test_nutrition():
    """测试营养数据"""
    app = create_app()
    
    with app.app_context():
        print("="*50)
        print("测试营养数据")
        print("="*50)
        
        # 获取用户
        user = User.query.filter_by(openid="test_openid").first()
        if not user:
            user = User.query.first()
        
        if not user:
            print("❌ 找不到用户")
            return False
        
        print(f"✅ 用户: {user.nickname or user.id}")
        
        # 计算营养需求
        from app.utils.nutrition_needs_calculator import NutritionNeedsCalculator
        nutrition_needs = NutritionNeedsCalculator.calculate_all(user)
        
        print(f"\n✅ 后端计算:")
        for key, value in nutrition_needs.items():
            print(f"  - {key}: {value}")
        
        # 转换为前端格式
        nutrition_frontend = {
            "calorie": nutrition_needs.get("target_calorie"),
            "protein": nutrition_needs.get("target_protein"),
            "carb": nutrition_needs.get("target_carb"),
            "fat": nutrition_needs.get("target_fat")
        }
        
        print(f"\n✅ 前端格式:")
        for key, value in nutrition_frontend.items():
            print(f"  - {key}: {value}")
        
        print("\n" + "="*50)
        print("✅ 测试完成!")
        print("="*50)
        
        return True

if __name__ == "__main__":
    try:
        success = test_nutrition()
        if success:
            print("\n🎉 测试通过!")
            exit(0)
        else:
            print("\n❌ 测试失败")
            exit(1)
    except Exception as e:
        print(f"\n❌ 发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
