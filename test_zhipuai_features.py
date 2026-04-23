#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试智谱AI所有功能
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app.utils.zhipuai_client import get_zhipuai_client
from loguru import logger

def test_text_generation():
    """测试文本生成"""
    print("\n" + "="*60)
    print("测试1: 文本生成")
    print("="*60)
    
    try:
        client = get_zhipuai_client()
        
        messages = [
            {"role": "user", "content": "简单介绍一下健康饮食的重要性"}
        ]
        
        print(f"\n提示词: {messages[0]['content']}")
        print("\n正在生成...")
        
        response = client.chat(messages, max_tokens=300)
        print(f"\n生成结果:")
        print(f"{response}")
        
        if "饮食" in response or "健康" in response:
            print("\n✅ 文本生成测试通过")
            return True
        else:
            print("\n⚠️  文本生成可能有问题")
            return False
            
    except Exception as e:
        print(f"\n❌ 文本生成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_image_generation():
    """测试图像生成"""
    print("\n" + "="*60)
    print("测试2: 图像生成 (CogView-3-Flash)")
    print("="*60)
    
    try:
        client = get_zhipuai_client()
        
        test_prompt = "美味的水果沙拉，色彩鲜艳，健康食品"
        test_size = "1024x1024"
        
        print(f"\n提示词: {test_prompt}")
        print(f"尺寸: {test_size}")
        print("\n正在生成...")
        
        result = client.generate_image(test_prompt, test_size)
        
        print(f"\n结果:")
        print(f"成功: {result.get('success')}")
        print(f"图片URL: {result.get('image_url')}")
        print(f"模型: {result.get('model')}")
        
        if result.get('success') and result.get('image_url'):
            print("\n✅ 图像生成测试通过")
            return True
        else:
            print("\n⚠️  图像生成可能有问题")
            return False
            
    except Exception as e:
        print(f"\n❌ 图像生成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_food_analysis():
    """测试美食分析"""
    print("\n" + "="*60)
    print("测试3: 美食图片分析 (GLM-4.1V-Thinking-Flash)")
    print("="*60)
    
    try:
        client = get_zhipuai_client()
        
        test_image_url = "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=delicious%20salad%20healthy%20food&image_size=square_hd"
        
        print(f"\n图片URL: {test_image_url[:60]}...")
        print("\n正在分析...")
        
        result = client.analyze_food_image(image_url=test_image_url, use_thinking=True)
        
        print(f"\n分析结果:")
        print(f"食物名称: {result.get('food_name')}")
        print(f"分类: {result.get('food_type')}")
        print(f"菜系: {result.get('cuisine')}")
        print(f"食材: {result.get('ingredients')}")
        print(f"口味: {result.get('taste')}")
        print(f"是否健康: {result.get('is_healthy')}")
        print(f"健康评分: {result.get('health_rating')}")
        
        nutrition = result.get('nutrition_estimate')
        if nutrition:
            print(f"\n营养估算:")
            if isinstance(nutrition, dict):
                for key, value in nutrition.items():
                    print(f"  {key}: {value}")
            else:
                print(f"  {nutrition}")
        
        if result.get('food_name') and result.get('food_type'):
            print("\n✅ 美食分析测试通过")
            return True
        else:
            print("\n⚠️  美食分析可能有问题")
            return False
            
    except Exception as e:
        print(f"\n❌ 美食分析测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*60)
    print("智谱AI全部功能测试")
    print("="*60)
    
    print("\n包含功能:")
    print("- GLM-4.7-Flash 文本生成")
    print("- GLM-4.6V-Flash 视觉分析")
    print("- GLM-4.1V-Thinking-Flash 深度视觉分析")
    print("- CogView-3-Flash 图像生成")
    
    # 运行所有测试
    results = []
    
    # 1. 测试文本生成
    results.append(("文本生成", test_text_generation()))
    
    # 2. 测试图像生成
    results.append(("图像生成", test_image_generation()))
    
    # 3. 测试美食分析
    results.append(("美食分析", test_food_analysis()))
    
    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name:20s}: {status}")
    
    pass_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    print(f"\n总结: {pass_count}/{total_count} 测试通过")
    
    if pass_count == total_count:
        print("\n🎉 恭喜！所有功能正常工作！")
    else:
        print(f"\n⚠️  请检查失败的功能")

if __name__ == "__main__":
    main()
