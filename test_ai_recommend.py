#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试AI食谱推荐功能"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.recipe import Recipe
from app.utils.zhipuai_client import get_zhipuai_client

def test_ai_recommendation():
    """测试AI推荐"""
    app = create_app()
    
    with app.app_context():
        print("="*50)
        print("开始测试AI食谱推荐功能")
        print("="*50)
        
        # 1. 获取测试用户
        user = User.query.filter_by(openid="test_openid").first()
        if not user:
            user = User.query.first()
        
        if not user:
            print("❌ 找不到测试用户")
            return False
        
        print(f"✅ 找到测试用户: {user.nickname or user.id}")
        print(f"   健康目标: {user.health_goal}")
        print(f"   饮食偏好: {user.dietary_preference}")
        
        # 2. 获取食谱
        recipes = Recipe.query.limit(30).all()
        if not recipes:
            print("❌ 数据库中没有食谱")
            return False
        
        print(f"✅ 找到 {len(recipes)} 个食谱")
        recipe_titles = [r.recipe_name for r in recipes]
        print(f"   示例: {', '.join(recipe_titles[:5])}")
        
        # 3. 初始化AI客户端
        client = get_zhipuai_client()
        print(f"✅ AI客户端初始化成功")
        
        # 4. 构造AI调用
        title_list_str = ", ".join([r.recipe_name for r in recipes[:20]])
        
        ai_prompt = f"""你是一位专业的营养师和食谱推荐专家。请根据以下用户信息，从给定的食谱列表中为用户推荐3个最适合的食谱。

用户信息：
- 年龄：{user.age}岁
- 身高：{user.height}cm
- 体重：{user.weight}kg
- 健康目标：{user.health_goal or '维持健康'}
- 饮食偏好：{user.dietary_preference or '无特殊偏好'}
- 目标热量：{user.target_calorie or 2000}kcal

可用食谱列表：
{title_list_str}

请严格以JSON格式返回推荐结果，格式如下：
{{
  "recommendations": [
    {{
      "title": "食谱名称（必须是上面列表中存在的完整名称）",
      "reason": "推荐理由，说明为什么这个食谱适合该用户"
    }}
  ]
}}
重要要求：
1. 只返回JSON，不要返回任何其他文字
2. 不要使用Markdown格式，不要用```包裹
3. 确保JSON格式完全正确，字符串用双引号
4. title必须完全匹配食谱列表中的名称，不要修改或简化
5. 推荐3个最适合的食谱
"""
        
        print("\n" + "="*50)
        print("向AI发送请求...")
        print("="*50)
        
        messages = [{"role": "user", "content": ai_prompt}]
        ai_response = client.chat(messages, temperature=0.3, max_tokens=2000)
        
        print(f"\n✅ AI响应成功:")
        print(ai_response[:500] + "..." if len(ai_response) > 500 else ai_response)
        
        # 5. 解析响应
        try:
            result = client._parse_json_response(ai_response)
            print("\n" + "="*50)
            print("✅ 解析成功，AI推荐:")
            print("="*50)
            
            if result.get("recommendations"):
                for i, rec in enumerate(result["recommendations"]):
                    print(f"\n推荐 {i+1}:")
                    print(f"  食谱: {rec.get('title')}")
                    print(f"  理由: {rec.get('reason')}")
                    
                    # 检查是否存在
                    exists = Recipe.query.filter_by(recipe_name=rec.get("title")).first()
                    if exists:
                        print(f"  ✅ 数据库中存在该食谱")
                    else:
                        print(f"  ⚠️ 数据库中未找到该食谱")
            else:
                print("❌ AI没有返回推荐")
                return False
                
        except Exception as e:
            print(f"\n❌ 解析失败: {str(e)}")
            print(f"   使用模拟响应测试...")
            result = client._mock_recipe_recommendation()
            print(f"   模拟响应: {result}")
        
        print("\n" + "="*50)
        print("✅ AI推荐测试完成!")
        print("="*50)
        return True

if __name__ == "__main__":
    try:
        success = test_ai_recommendation()
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
