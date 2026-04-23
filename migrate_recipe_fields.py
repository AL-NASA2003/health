
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移：为recipe表添加新字段
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


def add_columns():
    """添加新列到recipe表"""
    with app.app_context():
        # 使用原生SQL来添加列
        # 因为是SQLite，所以用ALTER TABLE
        
        try:
            # 检查列是否存在的简单方法：尝试查询一下
            from sqlalchemy import text
            db.session.execute(text("SELECT cuisine FROM recipe LIMIT 1"))
            print("✅ cuisine列已存在，跳过")
        except:
            print("📝 添加cuisine列...")
            db.session.execute(text("ALTER TABLE recipe ADD COLUMN cuisine VARCHAR(20) DEFAULT ''"))
            print("✅ cuisine列添加成功")
        
        try:
            db.session.execute(text("SELECT difficulty FROM recipe LIMIT 1"))
            print("✅ difficulty列已存在，跳过")
        except:
            print("📝 添加difficulty列...")
            db.session.execute(text("ALTER TABLE recipe ADD COLUMN difficulty VARCHAR(20) DEFAULT ''"))
            print("✅ difficulty列添加成功")
        
        try:
            db.session.execute(text("SELECT cook_time FROM recipe LIMIT 1"))
            print("✅ cook_time列已存在，跳过")
        except:
            print("📝 添加cook_time列...")
            db.session.execute(text("ALTER TABLE recipe ADD COLUMN cook_time INTEGER DEFAULT 30"))
            print("✅ cook_time列添加成功")
        
        db.session.commit()
        print("\n🎉 数据库迁移完成！")


if __name__ == "__main__":
    add_columns()

