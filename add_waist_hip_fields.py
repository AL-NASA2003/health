#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""添加腰围和臀围字段到用户表，并完善现有用户数据"""

import sys
import os
import random

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User

def add_waist_hip_fields():
    """添加腰围和臀围字段"""
    app = create_app()
    
    with app.app_context():
        print("="*50)
        print("开始添加腰围和臀围字段")
        print("="*50)
        
        # 1. 检查字段是否已存在
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('user')]
        
        waist_exists = 'waist' in columns
        hip_exists = 'hip' in columns
        
        print(f"\n✅ waist字段: {'已存在' if waist_exists else '不存在'}")
        print(f"hip字段: {'已存在' if hip_exists else '不存在'}")
        
        # 2. 如果字段不存在，通过SQL ALTER TABLE添加
        if not waist_exists:
            print("\n📝 正在添加waist字段...")
            try:
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE user ADD COLUMN waist REAL DEFAULT 0.0 COMMENT '腰围(cm)'"))
                    conn.commit()
                print("✅ waist字段添加成功!")
            except Exception as e:
                print(f"⚠️ waist字段添加可能已存在: {str(e)}")
        
        if not hip_exists:
            print("\n📝 正在添加hip字段...")
            try:
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE user ADD COLUMN hip REAL DEFAULT 0.0 COMMENT '臀围(cm)'"))
                    conn.commit()
                print("✅ hip字段添加成功!")
            except Exception as e:
                print(f"⚠️ hip字段添加可能已存在: {str(e)}")
        
        # 3. 完善现有用户数据
        print("\n" + "="*50)
        print("完善现有用户数据")
        print("="*50)
        
        users = User.query.all()
        print(f"\n📊 共找到 {len(users)} 个用户")
        
        updated_count = 0
        for user in users:
            # 如果用户没有腰围或臀围，根据身高体重计算合理值
            if user.height and user.weight:
                if not user.waist or user.waist == 0:
                    # 根据身高和性别计算合理腰围
                    if user.gender == 1:  # 男性
                        user.waist = round(60 + (user.height - 150) * 0.5 + random.uniform(-5, 5), 1)
                    else:  # 女性
                        user.waist = round(55 + (user.height - 150) * 0.4 + random.uniform(-5, 5), 1)
                
                if not user.hip or user.hip == 0:
                    # 根据身高和性别计算合理臀围
                    if user.gender == 1:  # 男性
                        user.hip = round(80 + (user.height - 150) * 0.4 + random.uniform(-5, 5), 1)
                    else:  # 女性
                        user.hip = round(85 + (user.height - 150) * 0.5 + random.uniform(-5, 5), 1)
                
                # 也补充目标营养
                if not user.target_calorie or user.target_calorie == 0:
                    # 简单计算目标热量
                    if user.gender == 1:  # 男性
                        user.target_calorie = 2000 + (user.weight - 70) * 15
                    else:  # 女性
                        user.target_calorie = 1600 + (user.weight - 55) * 12
                
                if not user.target_protein or user.target_protein == 0:
                    user.target_protein = user.weight * 1.5
                
                if not user.target_carb or user.target_carb == 0:
                    user.target_carb = user.target_calorie * 0.4 / 4
                
                if not user.target_fat or user.target_fat == 0:
                    user.target_fat = user.target_calorie * 0.3 / 9
                
                updated_count += 1
                db.session.add(user)
                print(f"✅ 用户 {user.nickname or user.id} 数据已完善")
                print(f"   腰围: {user.waist}cm, 臀围: {user.hip}cm")
                print(f"   目标热量: {user.target_calorie}kcal")
        
        if updated_count > 0:
            db.session.commit()
            print(f"\n✅ 共完善了 {updated_count} 个用户的数据")
        else:
            print("\n⚠️ 没有用户数据都已完善")
        
        print("\n" + "="*50)
        print("✅ 所有操作完成!")
        print("="*50)
        
        return True

if __name__ == "__main__":
    try:
        success = add_waist_hip_fields()
        if success:
            print("\n🎉 所有任务完成!")
            sys.exit(0)
        else:
            print("\n❌ 任务失败")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
