#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 为 HotFood 表添加图片识别字段
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app import create_app
from app import db
from loguru import logger
from sqlalchemy import text


def migrate_database():
    """执行数据库迁移"""
    app = create_app()
    
    with app.app_context():
        try:
            logger.info("开始数据库迁移...")
            
            # 检查是否需要迁移 - 尝试读取表结构
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('hot_food')]
            
            logger.info(f"当前表字段：{columns}")
            
            # 检查是否已有新字段
            new_fields = ['image_description', 'food_type', 'cuisine', 'ingredients', 'nutrition', 'is_healthy', 'health_rating']
            existing_fields = [f for f in new_fields if f in columns]
            missing_fields = [f for f in new_fields if f not in columns]
            
            if not missing_fields:
                logger.info("✅ 所有字段已存在，无需迁移")
                return True
            
            logger.info(f"需要添加字段：{missing_fields}")
            
            # 使用原始 SQL 添加新字段（兼容 SQLite）
            if 'image_description' in missing_fields:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE hot_food ADD COLUMN image_description VARCHAR(200) DEFAULT ''"))
                    conn.commit()
                logger.info("✅ 已添加 image_description")
            
            if 'food_type' in missing_fields:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE hot_food ADD COLUMN food_type VARCHAR(50) DEFAULT '其他'"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_food_type ON hot_food (food_type)"))
                    conn.commit()
                logger.info("✅ 已添加 food_type")
            
            if 'cuisine' in missing_fields:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE hot_food ADD COLUMN cuisine VARCHAR(50) DEFAULT ''"))
                    conn.commit()
                logger.info("✅ 已添加 cuisine")
            
            if 'ingredients' in missing_fields:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE hot_food ADD COLUMN ingredients TEXT DEFAULT ''"))
                    conn.commit()
                logger.info("✅ 已添加 ingredients")
            
            if 'nutrition' in missing_fields:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE hot_food ADD COLUMN nutrition TEXT DEFAULT ''"))
                    conn.commit()
                logger.info("✅ 已添加 nutrition")
            
            if 'is_healthy' in missing_fields:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE hot_food ADD COLUMN is_healthy BOOLEAN DEFAULT 1"))
                    conn.commit()
                logger.info("✅ 已添加 is_healthy")
            
            if 'health_rating' in missing_fields:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE hot_food ADD COLUMN health_rating INTEGER DEFAULT 3"))
                    conn.commit()
                logger.info("✅ 已添加 health_rating")
            
            logger.info("🎉 数据库迁移成功完成！")
            return True
            
        except Exception as e:
            logger.error(f"❌ 迁移失败：{str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False


if __name__ == "__main__":
    migrate_database()
