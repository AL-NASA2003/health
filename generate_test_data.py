
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成1000条测试数据脚本
"""
import sys
import os
from datetime import datetime, timedelta
import random

# 添加项目根目录到路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# 禁用Token验证，开发模式
os.environ['DISABLE_TOKEN_VERIFY'] = 'True'

# 初始化Flask应用上下文
from app import create_app
app = create_app()

from app import db
from app.models.diet_record import DietRecord
from app.models.user import User


# 食物名称列表
FOOD_NAMES = [
    "红烧排骨", "清蒸鲈鱼", "宫保鸡丁", "鱼香肉丝", "麻婆豆腐",
    "红烧肉", "糖醋里脊", "可乐鸡翅", "蒜蓉西兰花", "清炒时蔬",
    "蛋炒饭", "牛肉面", "包子", "饺子", "馒头",
    "牛奶", "酸奶", "豆浆", "苹果", "香蕉",
    "橙子", "梨", "葡萄", "西瓜", "草莓",
    "鸡蛋", "番茄炒蛋", "煮鸡蛋", "茶叶蛋", "蛋羹",
    "鸡胸肉沙拉", "蔬菜沙拉", "水果沙拉", "意面", "披萨",
    "汉堡", "薯条", "炸鸡", "烤鸡肉", "牛排",
    "三文鱼", "寿司", "生鱼片", "炒河粉", "炒饭",
    "麻辣烫", "火锅", "串串香", "烤串", "烤肉",
    "蛋花汤", "番茄鸡蛋汤", "紫菜蛋花汤", "冬瓜汤", "萝卜汤",
    "红烧肉", "糖醋排骨", "回锅肉", "水煮肉片", "酸菜鱼",
    "西红柿炒鸡蛋", "青椒肉丝", "茄子炒肉", "豆角炒肉", "莲藕炒肉",
    "奶茶", "咖啡", "果汁", "可乐", "雪碧",
    "薯片", "饼干", "蛋糕", "面包", "巧克力",
    "火腿肠", "午餐肉", "香肠", "培根", "腊肉",
    "黄瓜", "西红柿", "白菜", "土豆", "胡萝卜",
    "西兰花", "生菜", "菠菜", "油麦菜", "空心菜"
]

# 食物类型
FOOD_TYPES = ["主食", "菜式", "水果", "零食", "饮品"]

# 用餐时间
MEAL_TIMES = ["早餐", "午餐", "晚餐", "加餐"]


def generate_random_date(start_date, end_date):
    """生成随机日期"""
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    return start_date + timedelta(days=random_days)


def calculate_nutrition(food_type, weight):
    """根据食物类型和重量计算营养成分"""
    # 默认营养成分（每100g）
    nutrition_data = {
        "主食": {"calorie": 120, "protein": 4, "carb": 25, "fat": 1},
        "菜式": {"calorie": 150, "protein": 8, "carb": 15, "fat": 7},
        "水果": {"calorie": 50, "protein": 0.5, "carb": 12, "fat": 0.2},
        "零食": {"calorie": 200, "protein": 4, "carb": 25, "fat": 10},
        "饮品": {"calorie": 40, "protein": 1, "carb": 9, "fat": 0}
    }
    
    base = nutrition_data.get(food_type, nutrition_data["菜式"])
    multiplier = weight / 100.0
    
    return {
        "calorie": round(base["calorie"] * multiplier, 1),
        "protein": round(base["protein"] * multiplier, 1),
        "carb": round(base["carb"] * multiplier, 1),
        "fat": round(base["fat"] * multiplier, 1)
    }


def generate_test_data(user_id=1, count=1000):
    """生成测试数据"""
    print(f"📊 开始生成 {count} 条测试数据...")
    
    # 日期范围（过去90天到今天）
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)
    
    records = []
    
    for i in range(count):
        # 随机选择食物
        food_name = random.choice(FOOD_NAMES)
        food_type = random.choice(FOOD_TYPES)
        meal_time = random.choice(MEAL_TIMES)
        weight = random.randint(50, 400)
        
        # 计算营养
        nutrition = calculate_nutrition(food_type, weight)
        
        # 随机日期
        record_date = generate_random_date(start_date, end_date)
        
        # 随机时间（07:00 - 22:00）
        hour = random.randint(7, 22)
        minute = random.randint(0, 59)
        create_time = datetime.combine(record_date, datetime.min.time()) + timedelta(hours=hour, minutes=minute)
        
        # 创建记录
        record = DietRecord(
            user_id=user_id,
            food_name=food_name,
            food_type=food_type,
            meal_time=meal_time,
            weight=weight,
            unit="g",
            calorie=nutrition["calorie"],
            protein=nutrition["protein"],
            carb=nutrition["carb"],
            fat=nutrition["fat"],
            recipe_id=0,
            image="",
            notes="",
            create_date=record_date,
            create_time=create_time
        )
        
        records.append(record)
        
        # 每100条打印一次进度
        if (i + 1) % 100 == 0:
            print(f"✅ 已生成 {i + 1}/{count} 条记录")
    
    return records


def main():
    with app.app_context():
        # 检查用户是否存在
        user = User.query.filter_by(id=1).first()
        if not user:
            print("⚠️ 用户1不存在，创建默认用户...")
            user = User(
                username="test_user",
                password="123456",
                nickname="测试用户",
                phone="13800138000",
                avatar="",
                gender="男",
                age=25,
                height=175.0,
                weight=70.0,
                create_time=datetime.now()
            )
            db.session.add(user)
            db.session.commit()
            print(f"✅ 用户创建成功，ID: {user.id}")
        
        # 生成1000条数据
        records = generate_test_data(user_id=1, count=1000)
        
        # 批量保存
        print(f"💾 开始保存数据...")
        success = DietRecord.batch_save(records)
        
        if success:
            print(f"🎉 成功插入 {len(records)} 条数据！")
            
            # 查询统计
            total_count = DietRecord.query.filter_by(user_id=1).count()
            print(f"📊 数据库中共有 {total_count} 条饮食记录")
        else:
            print(f"❌ 数据保存失败！")


if __name__ == "__main__":
    main()

