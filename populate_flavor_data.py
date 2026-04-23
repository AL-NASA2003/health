#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能填充食谱风味数据
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app import create_app, db
from app.models.recipe import Recipe
from app.utils.flavor_recommender import guess_flavor_by_name, guess_tags

app = create_app()


def populate_flavor_data():
    """为现有食谱填充风味数据"""
    with app.app_context():
        recipes = Recipe.query.all()
        
        print(f"📊 找到 {len(recipes)} 条食谱")
        
        updated_count = 0
        
        for recipe in recipes:
            # 1. 猜测风味评分
            flavor_data = guess_flavor_by_name(recipe.recipe_name)
            recipe.flavor_sweet = flavor_data['flavor_sweet']
            recipe.flavor_salty = flavor_data['flavor_salty']
            recipe.flavor_spicy = flavor_data['flavor_spicy']
            recipe.flavor_sour = flavor_data['flavor_sour']
            recipe.flavor_umami = flavor_data['flavor_umami']
            
            # 2. 猜测标签
            tags = guess_tags(recipe.recipe_name, recipe.cook_time or 30)
            recipe.is_quick = tags['is_quick']
            recipe.is_featured = tags['is_featured']
            recipe.is_seasonal = tags['is_seasonal']
            
            updated_count += 1
        
        db.session.commit()
        
        print(f"\n✅ 已更新 {updated_count} 条食谱")
        
        # 打印样本
        print("\n📋 样本数据：")
        for recipe in recipes[:5]:
            print(f"  ' {recipe.recipe_name} '")
            print(f"    风味: 甜={recipe.flavor_sweet}, 咸={recipe.flavor_salty}, 辣={recipe.flavor_spicy}")
            print(f"    标签: 快手={recipe.is_quick}, 精选={recipe.is_featured}")
            print()


if __name__ == "__main__":
    populate_flavor_data()
