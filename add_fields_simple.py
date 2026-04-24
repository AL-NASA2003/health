#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""简单版：添加腰围和臀围字段到用户表"""

import sqlite3
import random
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "health_food.db")

def add_fields():
    """添加字段到数据库"""
    print("="*50)
    print("开始添加腰围和臀围字段")
    print("="*50)
    
    # 1. 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 2. 检查表结构
    cursor.execute("PRAGMA table_info(user)")
    columns = [col[1] for col in cursor.fetchall()]
    
    print(f"\n当前user表字段: {', '.join(columns)}")
    
    waist_exists = 'waist' in columns
    hip_exists = 'hip' in columns
    
    print(f"\nwaist字段: {'已存在' if waist_exists else '不存在'}")
    print(f"hip字段: {'已存在' if hip_exists else '不存在'}")
    
    # 3. 添加字段
    if not waist_exists:
        print("\n📝 添加waist字段...")
        cursor.execute("ALTER TABLE user ADD COLUMN waist REAL DEFAULT 0.0")
        print("✅ waist字段添加成功!")
    
    if not hip_exists:
        print("\n📝 添加hip字段...")
        cursor.execute("ALTER TABLE user ADD COLUMN hip REAL DEFAULT 0.0")
        print("✅ hip字段添加成功!")
    
    # 4. 提交修改
    conn.commit()
    
    # 5. 检查是否所有用户都有目标营养数据
    cursor.execute("SELECT id, height, weight, age, gender FROM user")
    users = cursor.fetchall()
    
    print(f"\n📊 共找到 {len(users)} 个用户")
    
    updated_count = 0
    for user in users:
        user_id, height, weight, age, gender = user
        
        # 获取当前数据
        cursor.execute(
            "SELECT waist, hip, target_calorie, target_protein, target_carb, target_fat FROM user WHERE id = ?",
            (user_id,)
        )
        current = cursor.fetchone()
        waist, hip, target_calorie, target_protein, target_carb, target_fat = current
        
        needs_update = False
        
        # 更新腰围
        if not waist or waist == 0:
            if height and height > 0:
                if gender == 1:  # 男
                    waist = round(60 + (height - 150) * 0.5 + random.uniform(-5, 5), 1)
                else:  # 女
                    waist = round(55 + (height - 150) * 0.4 + random.uniform(-5, 5), 1)
                needs_update = True
        
        # 更新臀围
        if not hip or hip == 0:
            if height and height > 0:
                if gender == 1:  # 男
                    hip = round(80 + (height - 150) * 0.4 + random.uniform(-5, 5), 1)
                else:  # 女
                    hip = round(85 + (height - 150) * 0.5 + random.uniform(-5, 5), 1)
                needs_update = True
        
        # 更新目标营养
        if not target_calorie or target_calorie == 0:
            if weight and weight > 0:
                if gender == 1:
                    target_calorie = 2000 + (weight - 70) * 15
                else:
                    target_calorie = 1600 + (weight - 55) * 12
                needs_update = True
        
        if not target_protein or target_protein == 0:
            if weight and weight > 0:
                target_protein = weight * 1.5
                needs_update = True
        
        if not target_carb or target_carb == 0:
            if target_calorie and target_calorie > 0:
                target_carb = target_calorie * 0.4 / 4
                needs_update = True
        
        if not target_fat or target_fat == 0:
            if target_calorie and target_calorie > 0:
                target_fat = target_calorie * 0.3 / 9
                needs_update = True
        
        if needs_update:
            cursor.execute("""
                UPDATE user 
                SET waist = ?, hip = ?, target_calorie = ?, target_protein = ?, target_carb = ?, target_fat = ?
                WHERE id = ?
            """, (waist, hip, target_calorie, target_protein, target_carb, target_fat, user_id))
            
            updated_count += 1
            print(f"✅ 用户 {user_id} 数据已完善")
            print(f"   腰围: {waist}cm, 臀围: {hip}cm")
            print(f"   目标热量: {target_calorie}kcal")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ 共完善了 {updated_count} 个用户的数据")
    print("\n" + "="*50)
    print("✅ 所有操作完成!")
    print("="*50)
    
    return True

if __name__ == "__main__":
    try:
        success = add_fields()
        if success:
            print("\n🎉 所有任务完成!")
            exit(0)
        else:
            print("\n❌ 任务失败")
            exit(1)
    except Exception as e:
        print(f"\n❌ 发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
