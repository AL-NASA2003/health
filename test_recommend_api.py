#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试推荐API返回的数据格式"""

import sys
import os
import requests

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.user import User

def test_recommend_api():
    """测试推荐API"""
    app = create_app()
    
    with app.app_context():
        print("="*50)
        print("开始测试推荐API")
        print("="*50)
        
        # 1. 获取测试用户
        user = User.query.filter_by(openid="test_openid").first()
        if not user:
            user = User.query.first()
        
        if not user:
            print("❌ 找不到测试用户")
            return False
        
        print(f"✅ 找到测试用户: {user.nickname or user.id}")
        print(f"   身高: {user.height}cm, 体重: {user.weight}kg")
        print(f"   腰围: {user.waist}cm, 臀围: {user.hip}cm")
        print(f"   目标热量: {user.target_calorie}kcal")
        
        # 2. 直接调用推荐函数进行测试
        from app.api.recommend_api import get_personal_recommend
        from app.extensions import db
        
        # 构造一个测试请求上下文
        with app.test_request_context():
            # 模拟登录用户
            from flask import g
            g.current_user = user
            
            try:
                result = get_personal_recommend()
                
                print(f"\n✅ API调用成功!")
                print(f"\n返回数据:")
                print(f"  - code: {result.json.get('code')}")
                print(f"  - msg: {result.json.get('msg')}")
                
                data = result.json.get('data')
                if data:
                    print(f"\n✅ 数据部分:")
                    
                    # 检查营养需求
                    nutrition = data.get('nutrition_needs')
                    if nutrition:
                        print(f"  - nutrition_needs: {nutrition}")
                        print(f"    * calorie: {nutrition.get('calorie')}")
                        print(f"    * protein: {nutrition.get('protein')}")
                        print(f"    * carb: {nutrition.get('carb')}")
                        print(f"    * fat: {nutrition.get('fat')}")
                    else:
                        print(f"  ⚠️ nutrition_needs: None 或 未找到")
                    
                    # 检查推荐方法
                    recommend_method = data.get('recommend_method')
                    print(f"  - recommend_method: {recommend_method}")
                    
                    # 检查推荐列表
                    recommend_list = data.get('recommend_list')
                    if recommend_list:
                        print(f"  - recommend_list: {len(recommend_list)} 个食谱")
                    else:
                        print(f"  ⚠️ recommend_list: None 或 空")
                
            except Exception as e:
                print(f"\n❌ 调用API出错: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
        
        print("\n" + "="*50)
        print("✅ 测试完成!")
        print("="*50)
        return True

if __name__ == "__main__":
    try:
        success = test_recommend_api()
        if success:
            print("\n🎉 所有测试通过!")
            sys.exit(0)
        else:
            print("\n❌ 测试失败")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
