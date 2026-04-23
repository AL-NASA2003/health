#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新组织饮食记录数据，符合正常人类每天摄入逻辑
"""
import sys
import os
from datetime import datetime, timedelta, time
import random
from loguru import logger

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
from app.models.recipe import Recipe


# 早餐食物库
BREAKFAST_FOODS = [
    "燕麦牛奶", "全麦面包", "水煮蛋", "小米粥", "豆浆", "包子", "花卷", "油条", 
    "三明治", "鸡蛋饼", "牛奶燕麦粥", "杂粮粥", "水煮玉米", "茶叶蛋", "皮蛋瘦肉粥",
    "蒸南瓜", "蒸红薯", "鸡蛋羹", "蔬菜蛋卷", "鸡蛋灌饼", "手抓饼", "豆腐脑"
]

# 午餐食物库
LUNCH_FOODS = [
    "红烧排骨", "宫保鸡丁", "鱼香肉丝", "麻婆豆腐", "青椒炒肉", "西红柿炒蛋", 
    "红烧肉", "糖醋里脊", "可乐鸡翅", "蒜蓉西兰花", "清炒时蔬", "蛋炒饭", 
    "扬州炒饭", "西红柿鸡蛋盖饭", "红烧牛肉", "酸辣土豆丝", "西红柿炖牛腩", 
    "鱼香茄子", "茄子炒肉", "干煸豆角", "水煮鱼"
]

# 晚餐食物库
DINNER_FOODS = [
    "水煮鸡胸肉", "清蒸鱼", "清炒虾仁", "蔬菜沙拉", "小米粥", "馒头", 
    "西红柿鸡蛋汤", "紫菜蛋花汤", "冬瓜汤", "萝卜汤", "鸡蛋羹", "水煮青菜", 
    "蒜蓉油麦菜", "蒜蓉生菜", "白灼菜心", "清蒸鲈鱼", "冬瓜排骨汤", "萝卜牛腩汤",
    "番茄鸡蛋面", "蔬菜汤面", "排骨汤面", "牛肉面", "凉拌黄瓜", "拍黄瓜", 
    "凉拌木耳", "凉拌黄瓜木耳", "拍黄瓜皮蛋", "凉拌豆腐丝", "凉拌海带丝"
]

# 加餐食物库
SNACK_FOODS = [
    "苹果", "香蕉", "橙子", "梨", "葡萄", "草莓", "猕猴桃", "芒果", "西瓜", 
    "哈密瓜", "坚果", "腰果", "杏仁", "核桃", "开心果", "碧根果", "酸奶", 
    "纯牛奶", "豆浆", "小番茄", "黄瓜", "圣女果", "小西红柿", "红枣", "桂圆",
    "草莓奶昔", "香蕉奶昔", "西瓜汁", "牛奶燕麦", "酸奶燕麦", "水果沙拉"
]

# 食物类型
FOOD_TYPES = ["主食", "菜式", "水果", "零食", "饮品"]


def get_nutrition(food_name, weight):
    """计算食物营养"""
    if '鸡蛋' in food_name:
        return {
            'calorie': 1.4 * weight, 'protein': 0.12 * weight, 'carb': 0.01 * weight, 'fat': 0.1 * weight}
    elif '肉' in food_name or '排骨' in food_name or '鸡' in food_name or '牛' in food_name:
        return {
            'calorie': 2.0 * weight, 'protein': 0.2 * weight, 'carb': 0.05 * weight, 'fat': 0.15 * weight}
    elif '米饭' in food_name or '面' in food_name or '包' in food_name or '饼' in food_name:
        return {
            'calorie': 3.0 * weight, 'protein': 0.08 * weight, 'carb': 0.6 * weight, 'fat': 0.02 * weight}
    elif '牛奶' in food_name or '豆浆' in food_name or '奶昔' in food_name:
        return {
            'calorie': 0.8 * weight, 'protein': 0.03 * weight, 'carb': 0.05 * weight, 'fat': 0.03 * weight}
    elif '蔬' in food_name or '瓜' in food_name or '菜' in food_name or '青' in food_name:
        return {
            'calorie': 0.4 * weight, 'protein': 0.02 * weight, 'carb': 0.08 * weight, 'fat': 0.01 * weight}
    elif '果' in food_name or '瓜' in food_name:
        return {
            'calorie': 0.5 * weight, 'protein': 0.01 * weight, 'carb': 0.12 * weight, 'fat': 0.0 * weight}
    elif '汤' in food_name or '粥' in food_name:
        return {
            'calorie': 0.6 * weight, 'protein': 0.03 * weight, 'carb': 0.1 * weight, 'fat': 0.02 * weight}
    else:
        return {
            'calorie': 1.5 * weight, 'protein': 0.08 * weight, 'carb': 0.2 * weight, 'fat': 0.08 * weight}


def generate_realistic_daily_records(user_id, date):
    """为指定日期生成真实的饮食记录"""
    records = []
    
    # 早餐 07:00-09:00
    breakfast_hour = random.randint(7, 8)
    breakfast_minute = random.randint(0, 59)
    breakfast_time = datetime.combine(date, time(hour=breakfast_hour, minute=breakfast_minute))
    breakfast_food = random.choice(BREAKFAST_FOODS)
    breakfast_weight = random.randint(150, 300)
    breakfast_nutrition = get_nutrition(breakfast_food, breakfast_weight)
    
    breakfast = DietRecord(
        user_id=user_id,
        food_name=breakfast_food,
        food_type="主食",
        meal_time="早餐",
        weight=breakfast_weight,
        calorie=breakfast_nutrition['calorie'],
        protein=breakfast_nutrition['protein'],
        carb=breakfast_nutrition['carb'],
        fat=breakfast_nutrition['fat'],
        create_date=date,
        create_time=breakfast_time
    )
    records.append(breakfast)
    
    # 午餐 11:30-13:30
    lunch_hour = random.randint(11, 13)
    lunch_minute = random.randint(0, 59)
    lunch_time = datetime.combine(date, time(hour=lunch_hour, minute=lunch_minute))
    lunch_food = random.choice(LUNCH_FOODS)
    lunch_weight = random.randint(200, 400)
    lunch_nutrition = get_nutrition(lunch_food, lunch_weight)
    
    lunch = DietRecord(
        user_id=user_id,
        food_name=lunch_food,
        food_type="菜式",
        meal_time="午餐",
        weight=lunch_weight,
        calorie=lunch_nutrition['calorie'],
        protein=lunch_nutrition['protein'],
        carb=lunch_nutrition['carb'],
        fat=lunch_nutrition['fat'],
        create_date=date,
        create_time=lunch_time
    )
    records.append(lunch)
    
    # 晚餐 17:30-20:00
    dinner_hour = random.randint(17, 19)
    dinner_minute = random.randint(0, 59)
    dinner_time = datetime.combine(date, time(hour=dinner_hour, minute=dinner_minute))
    dinner_food = random.choice(DINNER_FOODS)
    dinner_weight = random.randint(150, 300)
    dinner_nutrition = get_nutrition(dinner_food, dinner_weight)
    
    dinner = DietRecord(
        user_id=user_id,
        food_name=dinner_food,
        food_type="菜式",
        meal_time="晚餐",
        weight=dinner_weight,
        calorie=dinner_nutrition['calorie'],
        protein=dinner_nutrition['protein'],
        carb=dinner_nutrition['carb'],
        fat=dinner_nutrition['fat'],
        create_date=date,
        create_time=dinner_time
    )
    records.append(dinner)
    
    # 可能的加餐 10:00-11:00 或 15:00-16:00 或 20:00-21:00
    if random.random() < 0.7:
        snack_hour = random.choice([10, 15, 20])
        snack_minute = random.randint(0, 59)
        snack_time = datetime.combine(date, time(hour=snack_hour, minute=snack_minute))
        snack_food = random.choice(SNACK_FOODS)
        snack_weight = random.randint(50, 150)
        snack_nutrition = get_nutrition(snack_food, snack_weight)
        
        snack = DietRecord(
            user_id=user_id,
            food_name=snack_food,
            food_type="水果",
            meal_time="加餐",
            weight=snack_weight,
            calorie=snack_nutrition['calorie'],
            protein=snack_nutrition['protein'],
            carb=snack_nutrition['carb'],
            fat=snack_nutrition['fat'],
            create_date=date,
            create_time=snack_time
        )
        records.append(snack)
    
    return records


def reorganize_data():
    """重新组织数据"""
    logger.info("开始重新组织饮食记录数据...")
    
    with app.app_context():
        # 获取或创建用户
        user = User.query.filter_by(id=1).first()
        if not user:
            logger.info("创建测试用户...")
            user = User(
                openid="test_openid_123",
                nickname="健康生活",
                height=175.0,
                weight=70.0,
                age=25,
                gender=1,
                health_goal="维持",
                target_calorie=2000.0,
                target_protein=120.0,
                target_carb=250.0,
                target_fat=60.0
            )
            db.session.add(user)
            db.session.commit()
            logger.info(f"✅ 用户创建成功：{user.nickname}")
        else:
            logger.info(f"处理用户: {user.nickname}")
        
        # 删除现有数据
        old_count = DietRecord.query.filter_by(user_id=1).count()
        logger.info(f"删除 {old_count}条")
        
        # 删除旧数据
        DietRecord.query.filter_by(user_id=1).delete()
        db.session.commit()
        logger.info(f"已删除 {old_count}条旧记录")
        
        # 生成过去90天的数据
        today = datetime.now().date()
        start_date = today - timedelta(days=90)
        
        all_records = []
        for day_offset in range(90):
            current_date = start_date + timedelta(days=day_offset)
            # 生成当天的饮食记录
            daily_records = generate_realistic_daily_records(1, current_date)
            all_records.extend(daily_records)
            
            if (day_offset + 1) % 10 == 0:
                logger.info(f"已生成 {day_offset + 1}天的数据，共 {len(all_records)}条")
        
        # 批量保存
        DietRecord.batch_save(all_records)
        
        # 统计
        new_count = DietRecord.query.filter_by(user_id=1).count()
        logger.info(f"✅ 重新组织完成！共生成 {new_count}条记录")
        
        # 打印统计
        stats = db.session.query(
            DietRecord.meal_time,
            db.func.count(DietRecord.id).label('count'),
            db.func.sum(DietRecord.calorie).label('total_calorie')
        ).filter_by(user_id=1).group_by(DietRecord.meal_time).all()
        
        logger.info("\n📊 数据统计:")
        for meal_time, count, total_calorie in stats:
            logger.info(f"  {meal_time}: {count}条, 总热量 {total_calorie:.0}大卡")
        
        # 按日期统计
        date_stats = db.session.query(
            DietRecord.create_date,
            db.func.count(DietRecord.id).label('count')
        ).filter_by(user_id=1).group_by(DietRecord.create_date).order_by(DietRecord.create_date.desc()).limit(7).all()
        
        logger.info("\n📅 最近7天记录统计:")
        for create_date, count in date_stats:
            logger.info(f"  {create_date}: {count}条")
        
        # 统计平均每天的摄入量
        daily_stats = db.session.query(
            DietRecord.create_date,
            db.func.sum(DietRecord.calorie).label('daily_calorie'),
            db.func.sum(DietRecord.protein).label('daily_protein'),
            db.func.sum(DietRecord.carb).label('daily_carb'),
            db.func.sum(DietRecord.fat).label('daily_fat')
        ).filter_by(user_id=1).group_by(DietRecord.create_date).all()
        
        avg_calorie = sum([ds.daily_calorie for ds in daily_stats]) / len(daily_stats)
        avg_protein = sum([ds.daily_protein for ds in daily_stats]) / len(daily_stats)
        avg_carb = sum([ds.daily_carb for ds in daily_stats]) / len(daily_stats)
        avg_fat = sum([ds.daily_fat for ds in daily_stats]) / len(daily_stats)
        
        logger.info("\n📈 平均每日摄入:")
        logger.info(f"  热量: {avg_calorie:.0}大卡")
        logger.info(f"  蛋白质: {avg_protein:.0}g")
        logger.info(f"  碳水: {avg_carb:.0}g")
        logger.info(f"  脂肪: {avg_fat:.0}g")
        
        logger.info("\n🎉 数据重新组织完成！数据符合正常人类摄入逻辑。")


if __name__ == "__main__":
    reorganize_data()
