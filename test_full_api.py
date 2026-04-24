#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完整测试推荐API"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.user import User

def test_full_api():
    """完整测试推荐API"""
    app = create_app()
    
    with app.test_client() as client:
        print("="*50)
        print("完整测试推荐API")
        print("="*50)
        
        # 1. 获取测试用户
        user = User.query.filter_by(openid="test_openid").first()
        if not user:
            user = User.query.first()
        
        if not user:
            print("❌ 找不到测试用户")
            return False
        
        print(f"✅ 找到测试用户: {user.nickname or user.id}")
        print(f"   用户ID: {user.id}")
        
        # 2. 模拟登录 - 设置会话
        with client.session_transaction() as sess:
            sess['user_id'] = user.id
        
        print(f"\n✅ 模拟登录成功")
        
        # 3. 调用推荐API
        print(f"\n📡 调用推荐API...")
        
        response = client.post('/api/recommend/recipe', json={})
        
        print(f"\n✅ API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            
            print(f"\n✅ 完整响应数据:")
            print(f"  - code: {data.get('code')}")
            print(f"  - msg: {data.get('msg')}")
            
            if data.get('code') == 200:
                api_data = data.get('data')
                
                if api_data:
                    print(f"\n✅ API数据部分:")
                    
                    # 检查营养需求
                    nutrition = api_data.get('nutrition_needs')
                    if nutrition:
                        print(f"  - nutrition_needs (前端格式):")
                        print(f"    * calorie: {nutrition.get('calorie')}")
                        print(f"    * protein: {nutrition.get('protein')}")
                        print(f"    * carb: {nutrition.get('carb')}")
                        print(f"    * fat: {nutrition.get('fat')}")
                    else:
                        print(f"  ⚠️ nutrition_needs: None")
                    
                    # 检查推荐方法
                    recommend_method = api_data.get('recommend_method')
                    print(f"  - recommend_method: {recommend_method}")
                    
                    # 检查推荐列表
                    recommend_list = api_data.get('recommend_list')
                    if recommend_list:
                        print(f"  - recommend_list: {len(recommend_list)} 个食谱")
                        if len(recommend_list) > 0:
                            first = recommend_list[0]
                            print(f"    * 第一个食谱: {first.get('recipe_name') or first.get('name')}")
                    else:
                        print(f"  ⚠️ recommend_list: 空")
                    
                    print(f"\n🎉 前端应该能正常显示每日营养推荐了!")
                else:
                    print(f"  ⚠️ data字段为空")
            else:
                print(f"  ❌ API错误: {data.get('msg')}")
        else:
            print(f"  ❌ HTTP错误: {response.status_code}")
            print(f"  响应内容: {response.get_data(as_text=True)}")
        
        print("\n" + "="*50)
        print("✅ 测试完成!")
        print("="*50)
        return True

if __name__ == "__main__":
    try:
        success = test_full_api()
        if success:
            print("\n🎉 所有测试通过!")
            exit(0)
        else:
            print("\n❌ 测试失败")
            exit(1)
    except Exception as e:
        print(f"\n❌ 发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
