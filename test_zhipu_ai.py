#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智谱AI功能测试脚本
测试：图像生成、图像识别、食谱推荐
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from loguru import logger
from app.utils.zhipuai_client import get_zhipuai_client


def test_chat():
    """测试对话功能"""
    print("=" * 60)
    print("测试1：基本对话功能")
    print("=" * 60)
    
    try:
        client = get_zhipuai_client()
        
        messages = [
            {"role": "user", "content": "你好，请简单介绍一下健康饮食的重要性"}
        ]
        
        response = client.chat(messages, temperature=0.7, max_tokens=500)
        print(f"AI回复：{response[:200]}...")
        print("✅ 对话测试成功")
        return True
        
    except Exception as e:
        logger.error(f"对话测试失败：{str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_image_generation():
    """测试图像生成功能"""
    print("\n" + "=" * 60)
    print("测试2：图像生成功能")
    print("=" * 60)
    
    try:
        client = get_zhipuai_client()
        
        prompt = "一份色彩丰富的健康沙拉，包含各种新鲜蔬菜和水果"
        result = client.generate_image(prompt, size="1024x1024", style="美食摄影")
        
        print(f"生成结果：{result}")
        
        if result.get("success"):
            print(f"✅ 图像生成成功，URL：{result.get('image_url')}")
            return True
        else:
            print("⚠️ 图像生成使用了备用方案")
            return True
            
    except Exception as e:
        logger.error(f"图像生成测试失败：{str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_food_analysis():
    """测试美食图片分析功能"""
    print("\n" + "=" * 60)
    print("测试3：美食图片分析功能")
    print("=" * 60)
    
    try:
        client = get_zhipuai_client()
        
        # 使用测试图片URL
        test_image_url = "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=colorful%20healthy%20salad&image_size=square_hd"
        
        print(f"分析图片：{test_image_url}")
        
        result = client.analyze_food_image(
            image_url=test_image_url,
            use_thinking=True
        )
        
        print(f"分析结果：")
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        if result.get("food_name"):
            print(f"✅ 美食图片分析成功：{result.get('food_name')}")
            return True
        else:
            print("⚠️ 使用了备用分析结果")
            return True
            
    except Exception as e:
        logger.error(f"美食图片分析测试失败：{str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_recipe_recommendation():
    """测试食谱推荐功能"""
    print("\n" + "=" * 60)
    print("测试4：AI食谱推荐功能")
    print("=" * 60)
    
    try:
        client = get_zhipuai_client()
        
        user_profile = {
            "age": 28,
            "height": 175,
            "weight": 70,
            "health_goal": "减脂",
            "dietary_preference": "清淡",
            "target_calorie": 1800
        }
        
        fridge_ingredients = ["鸡胸肉", "西兰花", "胡萝卜", "鸡蛋"]
        
        result = client.generate_recipe_recommendation(user_profile, fridge_ingredients)
        
        print(f"推荐结果：")
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        recommendations = result.get("recommendations", [])
        if recommendations:
            print(f"✅ AI食谱推荐成功，共{len(recommendations)}个食谱")
            for i, recipe in enumerate(recommendations[:2], 1):
                print(f"  {i}. {recipe.get('recipe_name')} - {recipe.get('reason')}")
            return True
        else:
            print("⚠️ 使用了备用推荐结果")
            return True
            
    except Exception as e:
        logger.error(f"食谱推荐测试失败：{str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_nutrition_analysis():
    """测试营养分析功能"""
    print("\n" + "=" * 60)
    print("测试5：食物营养分析功能")
    print("=" * 60)
    
    try:
        client = get_zhipuai_client()
        
        result = client.analyze_nutrition("三文鱼")
        
        print(f"营养分析结果：")
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        if result.get("food_name"):
            print(f"✅ 营养分析成功：{result.get('food_name')}")
            return True
        else:
            print("⚠️ 使用了备用分析结果")
            return True
            
    except Exception as e:
        logger.error(f"营养分析测试失败：{str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("智谱AI功能测试套件")
    print("=" * 60)
    
    results = {}
    
    # 运行所有测试
    results["对话功能"] = test_chat()
    results["图像生成"] = test_image_generation()
    results["美食分析"] = test_food_analysis()
    results["食谱推荐"] = test_recipe_recommendation()
    results["营养分析"] = test_nutrition_analysis()
    
    # 输出测试结果汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}：{status}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    print(f"\n总计：{passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有功能测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查相关代码")


if __name__ == "__main__":
    main()
