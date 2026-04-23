#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移：添加风味评分字段
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app import create_app, db

app = create_app()


def migrate_flavor_columns():
    """迁移：添加风味评分相关字段"""
    with app.app_context():
        # 检查表是否有这些列
        # SQLite 不支持直接检查列，我们用try/except方式
        
        # 要添加的列
        columns_to_add = [
            # (列名, 类型定义)
            ('flavor_sweet', 'FLOAT DEFAULT 0.0'),
            ('flavor_salty', 'FLOAT DEFAULT 0.0'),
            ('flavor_spicy', 'FLOAT DEFAULT 0.0'),
            ('flavor_sour', 'FLOAT DEFAULT 0.0'),
            ('flavor_umami', 'FLOAT DEFAULT 0.0'),
            ('is_quick', 'BOOLEAN DEFAULT 0'),
            ('is_featured', 'BOOLEAN DEFAULT 0'),
            ('is_seasonal', 'BOOLEAN DEFAULT 0')
        ]
        
        for col_name, col_def in columns_to_add:
            try:
                # 尝试执行 ALTER TABLE
                db.session.execute(
                    db.text(f"ALTER TABLE recipe ADD COLUMN {col_name} {col_def}")
                )
                db.session.commit()
                print(f"✅ 添加列 {col_name} 成功")
            except Exception as e:
                # 可能列已存在，忽略错误
                db.session.rollback()
                print(f"ℹ️  列 {col_name} 已存在或添加失败: {str(e)[:50]}")
        
        print("\n🎉 风味评分字段迁移完成！")


if __name__ == "__main__":
    migrate_flavor_columns()
