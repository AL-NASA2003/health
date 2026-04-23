
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新食谱数据脚本：为现有食谱添加菜系、难度、烹饪时间
"""
import sys
import os

# 添加项目根目录到路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# 初始化Flask应用上下文
from app import create_app
app = create_app()

from app import db
from app.models.recipe import Recipe


def get_cuisine_by_name(name):
    """根据食谱名称判断菜系"""
    if any(keyword in name for keyword in ["宫保", "鱼香", "麻婆", "红烧", "糖醋", "回锅", "水煮", "酸菜鱼"]):
        return "中式"
    elif any(keyword in name for keyword in ["披萨", "汉堡", "牛排", "意面", "沙拉", "薯条"]):
        return "西式"
    elif any(keyword in name for keyword in ["寿司", "三文鱼", "生鱼片", "日式", "照烧"]):
        return "日式"
    elif any(keyword in name for keyword in ["韩式", "泡菜", "烤肉", "拌饭"]):
        return "韩式"
    else:
        return "中式"  # 默认中式


def get_difficulty_by_name(name):
    """根据食谱名称判断难度"""
    if any(keyword in name for keyword in ["炒", "煮", "蒸", "蛋", "汤"]):
        return "简单"
    elif any(keyword in name for keyword in ["红烧", "糖醋", "烤"]):
        return "中等"
    else:
        return "简单"


def get_cook_time_by_name(name):
    """根据食谱名称判断烹饪时间"""
    if any(keyword in name for keyword in ["蛋", "炒", "汤", "沙拉"]):
        return 20  # 30分钟内
    elif any(keyword in name for keyword in ["蒸", "煮", "红烧"]):
        return 40  # 30-60分钟
    else:
        return 30  # 30分钟内


def update_recipes():
    """更新所有食谱"""
    with app.app_context():
        recipes = Recipe.query.all()
        
        print(f"📊 找到 {len(recipes)} 条食谱")
        
        updated_count = 0
        
        for recipe in recipes:
            # 只有字段为空时才更新
            if not recipe.cuisine:
                recipe.cuisine = get_cuisine_by_name(recipe.recipe_name)
            if not recipe.difficulty:
                recipe.difficulty = get_difficulty_by_name(recipe.recipe_name)
            if recipe.cook_time == 30 and not hasattr(recipe, 'updated'):
                recipe.cook_time = get_cook_time_by_name(recipe.recipe_name)
            
            recipe.updated = True
            updated_count += 1
        
        db.session.commit()
        
        print(f"✅ 已更新 {updated_count} 条食谱")
        
        # 打印一些样例
        print("\n📋 样例数据：")
        sample_recipes = recipes[:5]
        for recipe in sample_recipes:
            print(f"  『{recipe.recipe_name}』 - {recipe.cuisine}/{recipe.difficulty}/{recipe.cook_time}分钟")


if __name__ == "__main__":
    update_recipes()

