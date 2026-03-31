#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化食谱数据
"""

from app import create_app, db
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.models.recipe import RecipeIngredient
from loguru import logger

# 创建应用
app = create_app()

# 在应用上下文中运行
with app.app_context():
    # 先添加一些食材
    ingredients = [
        {"ingre_name": "鸡胸肉", "calorie": 165, "protein": 31.0, "carb": 0.0, "fat": 3.6, "category": "肉类"},
        {"ingre_name": "西兰花", "calorie": 34, "protein": 2.8, "carb": 7.0, "fat": 0.4, "category": "蔬菜"},
        {"ingre_name": "燕麦", "calorie": 389, "protein": 16.9, "carb": 66.0, "fat": 6.9, "category": "谷物"},
        {"ingre_name": "鲈鱼", "calorie": 105, "protein": 18.6, "carb": 0.0, "fat": 3.1, "category": "鱼类"},
        {"ingre_name": "番茄", "calorie": 18, "protein": 0.9, "carb": 3.9, "fat": 0.2, "category": "蔬菜"},
        {"ingre_name": "鸡蛋", "calorie": 155, "protein": 13.0, "carb": 1.1, "fat": 11.0, "category": "蛋类"},
        {"ingre_name": "牛奶", "calorie": 42, "protein": 3.4, "carb": 5.0, "fat": 1.0, "category": "乳制品"},
        {"ingre_name": "苹果", "calorie": 52, "protein": 0.3, "carb": 13.8, "fat": 0.2, "category": "水果"},
        {"ingre_name": "香蕉", "calorie": 89, "protein": 1.1, "carb": 22.8, "fat": 0.3, "category": "水果"},
        {"ingre_name": "大米", "calorie": 130, "protein": 2.7, "carb": 28.2, "fat": 0.3, "category": "谷物"}
    ]
    
    for ingre_data in ingredients:
        ingre = Ingredient.query.filter_by(ingre_name=ingre_data["ingre_name"]).first()
        if not ingre:
            ingre = Ingredient(**ingre_data)
            db.session.add(ingre)
            logger.info(f"添加食材：{ingre_data['ingre_name']}")
    
    # 提交食材数据
    db.session.commit()
    
    # 然后添加一些食谱
    recipes = [
        {
            "recipe_name": "低脂鸡胸肉沙拉",
            "calorie": 280,
            "protein": 32.0,
            "carb": 15.0,
            "fat": 8.0,
            "flavor": "清淡",
            "cook_type": "凉拌",
            "suitable_crowd": "减脂人群",
            "cook_step": "1. 鸡胸肉切块腌制10分钟\n2. 煎至两面金黄\n3. 与蔬菜混合，淋上橄榄油和柠檬汁",
            "ingredients": [
                {"ingre_name": "鸡胸肉", "weight": 100, "unit": "g"},
                {"ingre_name": "西兰花", "weight": 150, "unit": "g"}
            ]
        },
        {
            "recipe_name": "清蒸鲈鱼",
            "calorie": 180,
            "protein": 28.0,
            "carb": 5.0,
            "fat": 6.0,
            "flavor": "清淡",
            "cook_type": "清蒸",
            "suitable_crowd": "所有人群",
            "cook_step": "1. 鲈鱼洗净，划几刀\n2. 放入葱姜蒜，淋上料酒\n3. 大火蒸10-12分钟\n4. 出锅淋上蒸鱼豉油",
            "ingredients": [
                {"ingre_name": "鲈鱼", "weight": 200, "unit": "g"}
            ]
        },
        {
            "recipe_name": "燕麦蓝莓粥",
            "calorie": 220,
            "protein": 8.0,
            "carb": 42.0,
            "fat": 4.0,
            "flavor": "清淡",
            "cook_type": "煮",
            "suitable_crowd": "早餐",
            "cook_step": "1. 燕麦加水煮开\n2. 小火慢煮15分钟\n3. 加入蓝莓和蜂蜜\n4. 搅拌均匀即可",
            "ingredients": [
                {"ingre_name": "燕麦", "weight": 50, "unit": "g"}
            ]
        },
        {
            "recipe_name": "西兰花炒虾仁",
            "calorie": 200,
            "protein": 25.0,
            "carb": 10.0,
            "fat": 8.0,
            "flavor": "清淡",
            "cook_type": "炒",
            "suitable_crowd": "健身人群",
            "cook_step": "1. 虾仁去壳去虾线\n2. 西兰花切小朵焯水\n3. 热锅少油，先炒虾仁\n4. 加入西兰花翻炒，调味即可",
            "ingredients": [
                {"ingre_name": "西兰花", "weight": 100, "unit": "g"},
                {"ingre_name": "鸡蛋", "weight": 50, "unit": "g"}
            ]
        },
        {
            "recipe_name": "番茄牛腩",
            "calorie": 350,
            "protein": 22.0,
            "carb": 18.0,
            "fat": 20.0,
            "flavor": "酸甜",
            "cook_type": "炖",
            "suitable_crowd": "增肌人群",
            "cook_step": "1. 牛腩切块焯水\n2. 番茄切块\n3. 热锅炒番茄出汁\n4. 加入牛腩炖煮1小时",
            "ingredients": [
                {"ingre_name": "鸡胸肉", "weight": 150, "unit": "g"},
                {"ingre_name": "番茄", "weight": 100, "unit": "g"}
            ]
        }
    ]
    
    for recipe_data in recipes:
        recipe = Recipe.query.filter_by(recipe_name=recipe_data["recipe_name"]).first()
        if not recipe:
            # 创建食谱
            ingredients_data = recipe_data.pop("ingredients")
            recipe = Recipe(**recipe_data)
            db.session.add(recipe)
            db.session.flush()  # 获取食谱ID
            
            # 添加食材关联
            for ingre_data in ingredients_data:
                ingre = Ingredient.query.filter_by(ingre_name=ingre_data["ingre_name"]).first()
                if ingre:
                    recipe_ingredient = RecipeIngredient(
                        recipe_id=recipe.id,
                        ingredient_id=ingre.id,
                        weight=ingre_data["weight"],
                        unit=ingre_data["unit"]
                    )
                    db.session.add(recipe_ingredient)
                    logger.info(f"添加食谱食材：{recipe_data['recipe_name']} - {ingre_data['ingre_name']}")
            
            logger.info(f"添加食谱：{recipe_data['recipe_name']}")
    
    # 提交食谱数据
    db.session.commit()
    logger.info("食谱数据初始化完成！")
