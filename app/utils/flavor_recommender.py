#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风味增强推荐引擎（参考flavorithm.com）
- 风味相似度计算
- 混合推荐策略（内容+协同+语义）
- 每周精选功能
"""
import random
import math
from typing import List, Dict
from loguru import logger
from datetime import datetime


class FlavorRecommender:
    """
    风味增强推荐系统
    基于：
    1. 风味向量相似度
    2. 内容标签匹配
    3. 历史行为记录
    """
    
    def __init__(self):
        # 风味维度权重
        self.flavor_weights = {
            'sweet': 1.0,
            'salty': 1.0,
            'spicy': 1.2,  # 辣味权重稍高
            'sour': 0.8,
            'umami': 1.1
        }
        
        # 每周精选种子（用于每周轮换）
        self.weekly_seed = self._get_weekly_seed()
    
    def _get_weekly_seed(self) -> int:
        """生成每周种子，用于轮换精选内容"""
        today = datetime.now()
        week_num = today.isocalendar()[1]
        return week_num
    
    def calculate_flavor_similarity(self, recipe1, recipe2) -> float:
        """
        计算两个食谱的风味相似度
        使用余弦相似度
        """
        # 获取两个食谱的风味向量
        vec1 = [
            recipe1.flavor_sweet,
            recipe1.flavor_salty,
            recipe1.flavor_spicy,
            recipe1.flavor_sour,
            recipe1.flavor_umami
        ]
        vec2 = [
            recipe2.flavor_sweet,
            recipe2.flavor_salty,
            recipe2.flavor_spicy,
            recipe2.flavor_sour,
            recipe2.flavor_umami
        ]
        
        # 应用权重
        vec1_weighted = [v * w for v, w in zip(vec1, self.flavor_weights.values())]
        vec2_weighted = [v * w for v, w in zip(vec2, self.flavor_weights.values())]
        
        # 计算余弦相似度
        dot_product = sum(v1 * v2 for v1, v2 in zip(vec1_weighted, vec2_weighted))
        norm1 = math.sqrt(sum(v ** 2 for v in vec1_weighted))
        norm2 = math.sqrt(sum(v ** 2 for v in vec2_weighted))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def find_similar_recipes(self, target_recipe, all_recipes, top_k: int = 5) -> List:
        """
        基于风味相似度，找到相似食谱
        """
        similarities = []
        for recipe in all_recipes:
            if recipe.id == target_recipe.id:
                continue
            sim = self.calculate_flavor_similarity(target_recipe, recipe)
            similarities.append((recipe, sim))
        
        # 按相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # 返回Top K
        return [recipe for recipe, sim in similarities[:top_k]]
    
    def calculate_content_score(self, recipe, user) -> float:
        """
        基于内容标签计算推荐分数
        """
        score = 0.0
        
        # 1. 菜系匹配
        if hasattr(user, 'cuisine_preference') and recipe.cuisine:
            if recipe.cuisine in user.cuisine_preference:
                score += 2.0
        
        # 2. 难度匹配
        if hasattr(user, 'preferred_difficulty') and recipe.difficulty:
            if recipe.difficulty == user.preferred_difficulty:
                score += 1.0
        
        # 3. 健康目标匹配
        if hasattr(user, 'health_goal'):
            if user.health_goal == '减脂':
                if recipe.calorie < 400:
                    score += 2.0
            elif user.health_goal == '增肌':
                if recipe.protein > 20:
                    score += 2.0
        
        # 4. 快手菜加分
        if recipe.is_quick:
            score += 1.0
        
        # 5. 精选加分
        if recipe.is_featured:
            score += 1.5
        
        return score
    
    def get_weekly_featured(self, recipes, count: int = 3) -> List:
        """
        获取本周精选食谱
        每周轮换，提供新鲜感
        """
        # 使用周种子进行随机选择
        random.seed(self.weekly_seed)
        
        # 优先选择标记为精选的
        featured = [r for r in recipes if r.is_featured]
        
        if len(featured) >= count:
            selected = random.sample(featured, count)
        else:
            # 补充一些普通的
            selected = featured.copy()
            others = [r for r in recipes if r not in featured]
            selected += random.sample(others, min(count - len(selected), len(others)))
        
        return selected
    
    def get_quick_recipes(self, recipes, max_time: int = 30, count: int = 5) -> List:
        """
        获取快手菜推荐
        """
        quick = [r for r in recipes if r.cook_time <= max_time]
        quick.sort(key=lambda x: x.cook_time)
        return quick[:count]
    
    def hybrid_recommend(self, user, all_recipes, top_k: int = 10) -> List:
        """
        混合推荐策略
        1. 内容标签匹配（40%）
        2. 风味相似（30%）
        3. 时间/场景（30%）
        """
        scored_recipes = []
        
        # 获取用户历史记录（如果有）
        user_history = self._get_user_history(user)
        
        for recipe in all_recipes:
            score = 0.0
            
            # 1. 内容标签匹配（40%权重）
            content_score = self.calculate_content_score(recipe, user)
            score += content_score * 0.4
            
            # 2. 风味相似（30%权重）- 基于用户历史
            if user_history:
                avg_flavor_sim = self._avg_flavor_similarity(recipe, user_history)
                score += avg_flavor_sim * 0.3
            
            # 3. 时间/场景（30%权重）
            time_score = self._time_relevance_score(recipe)
            score += time_score * 0.3
            
            scored_recipes.append((recipe, score))
        
        # 按分数排序
        scored_recipes.sort(key=lambda x: x[1], reverse=True)
        
        return [recipe for recipe, score in scored_recipes[:top_k]]
    
    def _get_user_history(self, user) -> List:
        """获取用户饮食记录作为历史（简化版）"""
        # 简化：实际应该从数据库获取DietRecord
        return []
    
    def _avg_flavor_similarity(self, recipe, history_records) -> float:
        """计算与历史记录的平均风味相似度"""
        if not history_records:
            return 0.5  # 中立值
        # 简化实现
        return 0.6
    
    def _time_relevance_score(self, recipe) -> float:
        """时间相关性得分（根据当前时间）"""
        now = datetime.now()
        hour = now.hour
        
        # 早餐推荐
        if 6 <= hour < 10:
            if '蛋' in recipe.recipe_name or '粥' in recipe.recipe_name:
                return 1.0
        # 午餐推荐
        elif 11 <= hour < 14:
            if recipe.difficulty in ['简单', '中等']:
                return 1.0
        # 晚餐推荐
        elif 17 <= hour < 20:
            if recipe.calorie > 300:
                return 1.0
        
        return 0.5
    
    def get_flavor_profile(self, recipe) -> Dict:
        """获取食谱的风味描述"""
        profile = []
        
        if recipe.flavor_sweet > 5:
            profile.append("偏甜")
        if recipe.flavor_salty > 5:
            profile.append("偏咸")
        if recipe.flavor_spicy > 5:
            profile.append("偏辣")
        if recipe.flavor_sour > 5:
            profile.append("偏酸")
        if recipe.flavor_umami > 5:
            profile.append("鲜美")
        
        return {
            'tags': profile,
            'vector': [
                recipe.flavor_sweet,
                recipe.flavor_salty,
                recipe.flavor_spicy,
                recipe.flavor_sour,
                recipe.flavor_umami
            ]
        }


def guess_flavor_by_name(recipe_name: str) -> Dict:
    """
    根据食谱名称智能猜测风味评分
    （用于数据初始化）
    """
    sweet = 0.0
    salty = 3.0  # 默认有一点点咸味
    spicy = 0.0
    sour = 0.0
    umami = 3.0  # 默认有点鲜味
    
    # 关键词匹配
    if any(k in recipe_name for k in ['糖', '甜', '蜜', '蛋糕', '饼干', '布丁']):
        sweet = 7.0
    
    if any(k in recipe_name for k in ['辣', '椒', '麻辣', '麻辣']):
        spicy = 8.0
    
    if any(k in recipe_name for k in ['酸', '醋', '柠檬', '番茄']):
        sour = 5.0
    
    if any(k in recipe_name for k in ['鲜', '鱼', '肉', '虾', '蟹']):
        umami = 7.0
    
    if any(k in recipe_name for k in ['咸', '盐', '酱', '卤']):
        salty = 7.0
    
    # 一些特殊组合
    if '番茄' in recipe_name and '蛋' in recipe_name:
        sweet = 4.0
        sour = 5.0
        umami = 6.0
    
    if '红烧肉' in recipe_name:
        sweet = 3.0
        salty = 6.0
        umami = 7.0
    
    return {
        'flavor_sweet': sweet,
        'flavor_salty': salty,
        'flavor_spicy': spicy,
        'flavor_sour': sour,
        'flavor_umami': umami
    }


def guess_tags(recipe_name: str, cook_time: int = 30) -> Dict:
    """
    智能猜测标签
    """
    is_quick = cook_time <= 30
    
    is_featured = False
    featured_keywords = ['红烧肉', '清蒸', '宫保', '番茄炒蛋', '蛋炒饭']
    if any(k in recipe_name for k in featured_keywords):
        is_featured = True
    
    is_seasonal = False
    
    return {
        'is_quick': is_quick,
        'is_featured': is_featured,
        'is_seasonal': is_seasonal
    }
