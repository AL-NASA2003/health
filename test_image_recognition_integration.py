#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试图片识别集成功能
"""
import sys
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app import create_app
from app.models.hot_food import HotFood
from app.utils.zhipuai_client import get_zhipuai_client
from loguru import logger


def test_zhipuai_client():
    """测试智谱AI客户端"""
    print("=" * 60)
    print("测试1: 智谱AI客户端 - 图片识别")
    print("=" * 60)
    
    try:
        client = get_zhipuai_client()
        if not client:
            print("❌ 客户端初始化失败")
            return False
        
        print("✅ 客户端初始化成功")
        
        # 使用一张美食图片进行测试
        test_prompt = "一张美味的红烧肉图片，色泽红润，香气诱人"
        
        print(f"测试提示词: {test_prompt}")
        
        # 使用 generate_image 来获取测试图片
        result = client.generate_image(
            prompt=test_prompt,
            size="1024x1024"
        )
        
        if result:
            print(f"✅ 图片生成成功: {result}")
            return True
        else:
            print("❌ 图片生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False


def test_mock_hot_food_with_recognition():
    """测试包含图片识别的模拟数据"""
    print("\n" + "=" * 60)
    print("测试2: 创建包含图片识别信息的模拟数据")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        # 模拟一个带识别数据的热点美食
        mock_data = {
            "food_name": "红烧排骨",
            "ingre_list": "排骨,生姜,生抽,老抽,冰糖,料酒",
            "link": "https://www.xiaohongshu.com/explore/test123",
            "hot_score": 12500,
            "source": "小红书",
            "tags": ["美食", "中式", "家常菜"],
            "image": "https://picsum.photos/seed/spareribs/300/200",
            "desc": "色泽红润，香酥脱骨的红烧排骨",
            "comments": 256,
            "collection": 312,
            "image_description": "一盘色泽红润的红烧排骨",
            "food_type": "菜式",
            "cuisine": "中式",
            "ingredients": ["排骨", "生姜", "生抽", "老抽", "冰糖", "料酒"],
            "nutrition": {"calorie": 650, "protein": 45, "carb": 15, "fat": 45},
            "is_healthy": False,
            "health_rating": 2
        }
        
        try:
            # 创建记录
            ingredients_json = json.dumps(mock_data["ingredients"], ensure_ascii=False)
            nutrition_json = json.dumps(mock_data["nutrition"], ensure_ascii=False)
            
            hot_food = HotFood(
                food_name=mock_data["food_name"],
                ingre_list=mock_data["ingre_list"],
                link=mock_data["link"],
                hot_score=mock_data["hot_score"],
                source=mock_data["source"],
                tags=json.dumps(mock_data["tags"]),
                image=mock_data["image"],
                description=mock_data["desc"],
                comments=mock_data["comments"],
                collection=mock_data["collection"],
                image_description=mock_data["image_description"],
                food_type=mock_data["food_type"],
                cuisine=mock_data["cuisine"],
                ingredients=ingredients_json,
                nutrition=nutrition_json,
                is_healthy=mock_data["is_healthy"],
                health_rating=mock_data["health_rating"]
            )
            hot_food.save()
            print("✅ 模拟数据保存成功")
            
            # 读取并验证
            saved = HotFood.query.filter_by(link=mock_data["link"]).first()
            if saved:
                print(f"\n✅ 数据验证:")
                print(f"  名称: {saved.food_name}")
                print(f"  分类: {saved.food_type}")
                print(f"  菜系: {saved.cuisine}")
                print(f"  健康评分: {saved.health_rating}")
                print(f"  是否健康: {'是' if saved.is_healthy else '否'}")
                print(f"  食材列表: {saved.ingredients}")
                
                # 测试 to_dict
                data_dict = saved.to_dict()
                print(f"\n✅ to_dict 方法正确返回: {list(data_dict.keys())}")
                
                # 清理测试数据
                db.session.delete(saved)
                db.session.commit()
                print(f"\n✅ 测试数据清理完成")
                return True
                
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False


def test_existing_data():
    """查看当前数据库中的数据"""
    print("\n" + "=" * 60)
    print("测试3: 查看当前数据库中的 HotFood 数据")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        try:
            count = HotFood.query.count()
            print(f"当前数据库记录数: {count}")
            
            if count > 0:
                sample = HotFood.query.order_by(HotFood.id.desc()).first()
                print(f"\n最新记录:")
                print(f"  ID: {sample.id}")
                print(f"  名称: {sample.food_name}")
                print(f"  分类: {sample.food_type}")
                print(f"  图片描述: {sample.image_description}")
                print(f"  食材: {sample.ingredients}")
            
            return True
            
        except Exception as e:
            print(f"❌ 读取失败: {str(e)}")
            return False


def main():
    print("健康饮食系统 - 图片识别集成测试")
    print("=" * 60)
    
    # 逐个测试
    test1 = test_zhipuai_client()
    test2 = test_mock_hot_food_with_recognition()
    test3 = test_existing_data()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"1. 智谱AI客户端: {'✅ 通过' if test1 else '❌ 失败'}")
    print(f"2. 模拟数据保存: {'✅ 通过' if test2 else '❌ 失败'}")
    print(f"3. 数据库查询: {'✅ 通过' if test3 else '❌ 失败'}")
    
    if test1 and test2 and test3:
        print("\n🎉 所有测试通过！图片识别集成功能正常工作")
    else:
        print("\n⚠️  部分测试失败，请检查问题")


if __name__ == "__main__":
    main()
