#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试GLM-4.6V-Flash美食图片识别功能
"""
import sys
import os

# 添加项目根目录到路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app import create_app
from app.utils.zhipuai_client import get_zhipuai_client
from loguru import logger

def test_image_recognition():
    """测试美食图片识别功能"""
    app = create_app()
    
    with app.app_context():
        logger.info("=" * 50)
        logger.info("开始测试GLM-4.6V-Flash美食图片识别")
        logger.info("=" * 50)
        
        client = get_zhipuai_client()
        
        # 测试用的美食图片URL
        test_images = [
            "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=chinese%20food%20kung%20pao%20chicken&image_size=square_hd",
            "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=delicious%20salad%20healthy%20food&image_size=square_hd",
            "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=japanese%20sushi%20sashimi%20platter&image_size=square_hd"
        ]
        
        for i, image_url in enumerate(test_images, 1):
            logger.info(f"\n测试图片 {i}: {image_url[:60]}...")
            
            try:
                result = client.analyze_food_image(image_url=image_url)
                
                logger.info(f"✓ 识别成功!")
                logger.info(f"  菜品名称: {result.get('food_name')}")
                logger.info(f"  分类: {result.get('food_type')}")
                logger.info(f"  菜系: {result.get('cuisine')}")
                logger.info(f"  主要食材: {', '.join(result.get('ingredients', []))}")
                logger.info(f"  口味: {result.get('taste')}")
                logger.info(f"  健康评分: {result.get('health_rating')}/5")
                
                nutrition = result.get('nutrition_estimate', {})
                if nutrition:
                    logger.info(f"  营养估算: {nutrition.get('calories')}大卡, 蛋白质{nutrition.get('protein')}g, 碳水{nutrition.get('carb')}g, 脂肪{nutrition.get('fat')}g")
                    
            except Exception as e:
                logger.error(f"✗ 识别失败: {str(e)}")
        
        logger.info("\n" + "=" * 50)
        logger.info("测试完成!")
        logger.info("=" * 50)

if __name__ == "__main__":
    test_image_recognition()
