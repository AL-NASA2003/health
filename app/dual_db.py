#!/usr/bin/env python3
"""
双数据库系统
- 真实数据库：保存爬虫获取的原始数据
- 本地数据库：保存AI筛选和匹配后的最终数据
"""
import os
import json
from datetime import datetime
from loguru import logger
from app import db


class DualDatabase:
    """双数据库管理"""
    
    @staticmethod
    def get_data_mode():
        """获取当前数据模式"""
        return os.environ.get('HEALTH_DATA_MODE', 'VIRTUAL')
    
    @staticmethod
    def is_real_mode():
        """是否是真实数据模式"""
        return DualDatabase.get_data_mode() == 'REAL'
    
    @staticmethod
    def is_virtual_mode():
        """是否是虚拟数据模式"""
        return DualDatabase.get_data_mode() == 'VIRTUAL'


class AIDataFilter:
    """AI数据筛选器"""
    
    @staticmethod
    def filter_hot_foods(raw_data):
        """
        AI筛选热点美食数据
        - 去除低质量数据
        - 去重
        - 按营养价值排序
        - 标签优化
        """
        if not raw_data:
            return []
            
        logger.info(f"🤖 AI 开始筛选数据，原始数据: {len(raw_data)} 条")
        
        filtered_data = []
        
        for item in raw_data:
            # 1. 基础质量检查
            if not AIDataFilter._check_basic_quality(item):
                continue
                
            # 2. 提取和优化标签
            optimized_tags = AIDataFilter._optimize_tags(item)
            
            # 3. 计算营养评分
            nutrition_score = AIDataFilter._calculate_nutrition_score(item)
            
            # 4. 构建筛选后的数据
            filtered_item = {
                'food_name': item.get('food_name', item.get('title', '未知美食')),
                'ingre_list': AIDataFilter._extract_ingredients(item),
                'link': item.get('link', ''),
                'hot_score': item.get('hot_score', item.get('likes', 0)),
                'source': item.get('source', '小红书'),
                'tags': json.dumps(optimized_tags),
                'image': item.get('image', item.get('images', [''])[0] if item.get('images') else ''),
                'description': AIDataFilter._generate_description(item),
                'comments': item.get('comments', 0),
                'collection': item.get('collection', 0),
                'nutrition_score': nutrition_score,
                'is_healthy': AIDataFilter._is_healthy_item(item),
                'create_time': datetime.now()
            }
            
            filtered_data.append(filtered_item)
        
        # 5. 去重
        filtered_data = AIDataFilter._deduplicate(filtered_data)
        
        # 6. 排序（营养评分 + 热度）
        filtered_data.sort(
            key=lambda x: x['nutrition_score'] * 0.7 + x['hot_score'] * 0.3,
            reverse=True
        )
        
        logger.info(f"✅ AI 筛选完成，剩余数据: {len(filtered_data)} 条")
        return filtered_data
    
    @staticmethod
    def _check_basic_quality(item):
        """检查数据基础质量"""
        title = item.get('title', item.get('food_name', ''))
        link = item.get('link', '')
        
        # 标题太短或为空
        if not title or len(title) < 2:
            return False
            
        # 链接无效
        if not link:
            return False
            
        return True
    
    @staticmethod
    def _optimize_tags(item):
        """优化标签"""
        tags = item.get('tags', [])
        
        if not tags:
            tags = ['美食']
            
        # 确保标签是列表
        if isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except:
                tags = [tags]
                
        # 去除重复标签
        tags = list(set(tags))
        
        # 标签数量限制
        if len(tags) > 8:
            tags = tags[:8]
            
        return tags
    
    @staticmethod
    def _calculate_nutrition_score(item):
        """计算营养评分 (0-100)"""
        likes = item.get('likes', item.get('hot_score', 0))
        comments = item.get('comments', 0)
        collection = item.get('collection', 0)
        
        # 简单评分：综合互动度
        score = min(100, likes * 0.5 + comments * 2 + collection * 1)
        
        # 根据标签调整
        tags = item.get('tags', [])
        if isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except:
                tags = []
                
        healthy_keywords = ['健康', '低卡', '减脂', '蔬菜', '水果', '低脂', '低糖']
        for keyword in healthy_keywords:
            if keyword in str(tags):
                score += 10
                
        return min(100, score)
    
    @staticmethod
    def _extract_ingredients(item):
        """提取食材列表"""
        ingre_list = item.get('ingre_list', '')
        
        if not ingre_list:
            title = item.get('title', item.get('food_name', ''))
            ingre_list = title
            
        return ingre_list
    
    @staticmethod
    def _generate_description(item):
        """生成描述"""
        desc = item.get('description', item.get('desc', ''))
        
        if not desc:
            title = item.get('title', item.get('food_name', ''))
            likes = item.get('likes', item.get('hot_score', 0))
            desc = f"{title} - 热度: {likes}"
            
        return desc
    
    @staticmethod
    def _is_healthy_item(item):
        """判断是否是健康食品"""
        title = item.get('title', item.get('food_name', ''))
        tags = item.get('tags', [])
        
        if isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except:
                tags = []
                
        # 健康关键词
        healthy_keywords = ['健康', '低卡', '减脂', '蔬菜', '水果', '低脂', '低糖', '素食', '健身']
        
        # 不健康关键词
        unhealthy_keywords = ['油炸', '高糖', '高油', '垃圾食品', '奶茶', '炸鸡', '薯片']
        
        # 检查健康关键词
        for keyword in healthy_keywords:
            if keyword in title or keyword in str(tags):
                return True
                
        # 检查不健康关键词
        for keyword in unhealthy_keywords:
            if keyword in title or keyword in str(tags):
                return False
                
        # 默认健康
        return True
    
    @staticmethod
    def _deduplicate(data):
        """数据去重"""
        seen_links = set()
        seen_titles = set()
        unique_data = []
        
        for item in data:
            link = item.get('link', '')
            title = item.get('food_name', '')
            
            # 通过链接去重
            if link and link in seen_links:
                continue
                
            # 通过标题去重
            title_key = title[:10] if title else ''
            if title_key and title_key in seen_titles:
                continue
                
            if link:
                seen_links.add(link)
            if title_key:
                seen_titles.add(title_key)
                
            unique_data.append(item)
            
        return unique_data


class DataSynchronizer:
    """数据同步器 - 从真实数据库同步到本地数据库"""
    
    @staticmethod
    def sync_hot_foods_to_local():
        """同步热点美食从真实数据库到本地数据库"""
        try:
            from app.models.hot_food import HotFood
            
            logger.info("🔄 开始同步数据到本地数据库...")
            
            # 1. 从真实数据库获取数据
            all_hot_foods = HotFood.query.all()
            
            if not all_hot_foods:
                logger.warning("真实数据库中暂无数据")
                return False
                
            raw_data = [hf.to_dict() for hf in all_hot_foods]
            
            # 2. AI筛选
            filtered_data = AIDataFilter.filter_hot_foods(raw_data)
            
            if not filtered_data:
                logger.warning("AI筛选后无有效数据")
                return False
                
            # 3. 清空本地数据库并保存筛选后的数据
            HotFood.query.delete()
            
            for item in filtered_data:
                hot_food = HotFood(
                    food_name=item['food_name'],
                    ingre_list=item['ingre_list'],
                    link=item['link'],
                    hot_score=item['hot_score'],
                    source=item['source'],
                    tags=item['tags'],
                    image=item['image'],
                    description=item['description'],
                    comments=item['comments'],
                    collection=item['collection'],
                    create_time=item['create_time']
                )
                hot_food.save()
                
            logger.info(f"✅ 数据同步完成，本地数据库已更新: {len(filtered_data)} 条")
            return True
            
        except Exception as e:
            logger.error(f"数据同步失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
