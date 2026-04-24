#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加测试数据脚本
按照日期每天各添加7条数据，在论坛、手账、我的记录中都添加
"""

import sys
import os
from datetime import datetime, timedelta
import random

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app import db
from app.models.forum_post import ForumPost
from app.models.hand_account import HandAccount
from app.models.diet_record import DietRecord
from app.models.user import User

# 测试数据内容
forum_titles = [
    "分享我的健康饮食心得",
    "今天的减脂餐真不错",
    "健身打卡第100天",
    "周末的轻食早餐",
    "分享一个超好吃的沙拉配方",
    "我的健康生活记录",
    "减脂期这样吃真的有效",
    "今日份的健身餐",
    "健康生活从早餐开始",
    "周末在家做美食",
    "分享我的减脂历程",
    "今天的营养餐记录",
    "健身打卡，继续加油",
    "美味又健康的午餐",
    "分享我的健康食谱"
]

forum_contents = [
    "今天尝试了一个新的健康餐配方，真的太好吃了！低脂高蛋白，营养均衡，强烈推荐给大家！",
    "健身打卡第N天，感觉状态越来越好，继续保持！",
    "周末在家做了一顿健康大餐，虽然花了不少时间，但真的很有成就感！",
    "分享一个我常吃的沙拉配方，简单又营养，非常适合减脂期！",
    "健康生活最重要的就是坚持，虽然偶尔也会想偷懒，但整体还是要保持规律！",
    "今天的减脂餐是鸡胸肉+西兰花+糙米饭，好吃又健康！",
    "分享一下我的早餐食谱，燕麦+水果+酸奶，营养满分！",
    "健身和饮食结合，效果真的翻倍！大家一起加油！",
    "最近发现了一个超棒的轻食餐厅，味道好而且健康！",
    "记录一下我这一周的健康饮食，感觉整个人都清爽了！",
    "周末和朋友一起做健康餐，大家都很喜欢这种健康的生活方式！",
    "分享我的减脂历程，从XXX斤到现在，真的很有成就感！",
    "今天尝试了一下素食，感觉也很不错，以后可以多尝试！",
    "健身后的营养餐，补充蛋白质很重要！",
    "分享一下我平时的健康零食选择，嘴馋的时候也能吃！"
]

handbook_titles = [
    "美好的一天",
    "健康早餐记录",
    "健身打卡",
    "周末美食",
    "减脂日记",
    "营养午餐",
    "轻食主义",
    "健康生活",
    "美食分享",
    "运动记录",
    "早餐打卡",
    "美味午餐",
    "健康晚餐",
    "周末时光",
    "营养均衡"
]

handbook_contents = [
    "今天早起做了一顿营养早餐，开启美好的一天！全麦面包、煎蛋、牛油果，营养满分！",
    "健身打卡！今天的状态很好，感觉力量又增加了，继续坚持！",
    "周末在家研究了一个新的健康食谱，味道真的太棒了，分享给大家！",
    "记录一下今天的减脂餐，虽然简单但很营养，继续保持！",
    "今天和朋友一起去健身，然后一起吃了健康餐，开心！",
    "尝试了一个新的轻食沙拉配方，真的太好吃了，健康又美味！",
    "健康生活从每一天开始，坚持记录，坚持运动，保持积极的心态！",
    "今天做了一顿丰盛又健康的午餐，有蔬菜有蛋白质，营养均衡！",
    "分享一下我这一周的健康饮食记录，感觉整个人都轻松了！",
    "健身后的营养餐很重要，及时补充蛋白质和碳水，帮助恢复！",
    "周末的早餐时光，慢慢享受自己做的健康美食，真的很治愈！",
    "今天尝试了一下素食餐，味道很不错，以后可以经常尝试！",
    "记录一下我的减脂进度，虽然慢但一直在前进，继续加油！",
    "和朋友分享了健康饮食的心得，大家都很感兴趣，一起变得更健康！",
    "今天的晚餐是清蒸鱼+蔬菜，简单又健康，味道也很好！"
]

food_names = [
    "鸡胸肉沙拉", "全麦面包", "燕麦粥", "清蒸鱼",
    "糙米饭", "西兰花", "煎蛋", "牛油果",
    "水果拼盘", "希腊酸奶", "蔬菜汤", "烤鸡胸肉",
    "藜麦沙拉", "紫薯", "玉米", "虾仁炒时蔬"
]

food_types = ["早餐", "午餐", "晚餐", "加餐"]


def get_random_image():
    """获取随机图片URL"""
    images = [
        "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=healthy%20food%20salad&image_size=square_hd",
        "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=delicious%20breakfast%20healthy&image_size=square_hd",
        "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=nutrition%20lunch%20balanced%20meal&image_size=square_hd",
        "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=healthy%20dinner%20vegetables&image_size=square_hd",
        "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=fitness%20meal%20protein&image_size=square_hd"
    ]
    return random.choice(images)


def add_test_data():
    """添加测试数据"""
    app = create_app()
    
    with app.app_context():
        print("🚀 开始添加测试数据...")
        
        # 获取测试用户
        user = User.query.filter_by(openid="test_openid").first()
        if not user:
            print("❌ 找不到测试用户，请先登录")
            return False
        
        user_id = user.id
        print(f"👤 使用用户ID: {user_id}")
        
        # 生成过去7天的日期
        days = 7
        items_per_day = 7
        
        for day_offset in range(days):
            date = datetime.now() - timedelta(days=day_offset)
            date_str = date.strftime("%Y-%m-%d")
            
            print(f"\n📅 正在添加 {date_str} 的数据...")
            
            # 每天添加7条论坛帖子
            print(f"   📝 添加 {items_per_day} 条论坛帖子...")
            for i in range(items_per_day):
                # 当天的随机时间
                random_hour = random.randint(0, 23)
                random_minute = random.randint(0, 59)
                random_second = random.randint(0, 59)
                post_time = datetime(date.year, date.month, date.day, random_hour, random_minute, random_second)
                
                post = ForumPost(
                    user_id=user_id,
                    title=random.choice(forum_titles),
                    content=random.choice(forum_contents),
                    image=get_random_image() if random.random() > 0.3 else None,
                    likes=random.randint(0, 20),
                    views=random.randint(10, 100),
                    create_time=post_time,
                    update_time=post_time
                )
                db.session.add(post)
            
            # 每天添加7条手账
            print(f"   📔 添加 {items_per_day} 条手账...")
            for i in range(items_per_day):
                random_hour = random.randint(0, 23)
                random_minute = random.randint(0, 59)
                random_second = random.randint(0, 59)
                post_time = datetime(date.year, date.month, date.day, random_hour, random_minute, random_second)
                
                handbook = HandAccount(
                    user_id=user_id,
                    title=random.choice(handbook_titles),
                    content=random.choice(handbook_contents),
                    image=get_random_image(),
                    create_time=post_time,
                    update_time=post_time
                )
                db.session.add(handbook)
            
            # 每天添加7条饮食记录
            print(f"   🍎 添加 {items_per_day} 条饮食记录...")
            for i in range(items_per_day):
                random_hour = random.randint(6, 22)
                random_minute = random.randint(0, 59)
                random_second = random.randint(0, 59)
                record_time = datetime(date.year, date.month, date.day, random_hour, random_minute, random_second)
                
                # 随机热量
                calorie = random.randint(200, 600)
                protein = random.randint(10, 40)
                carb = random.randint(20, 60)
                fat = random.randint(5, 25)
                
                diet_record = DietRecord(
                    user_id=user_id,
                    food_name=random.choice(food_names),
                    food_type=random.choice(food_types),
                    meal_time=random.choice(food_types),
                    weight=random.randint(100, 300),
                    unit="g",
                    calorie=calorie,
                    protein=protein,
                    carb=carb,
                    fat=fat,
                    image=get_random_image() if random.random() > 0.4 else None,
                    create_date=date,
                    create_time=record_time
                )
                db.session.add(diet_record)
            
            print(f"   ✅ {date_str} 数据添加完成")
        
        # 提交所有数据
        db.session.commit()
        print(f"\n🎉 测试数据添加完成！")
        print(f"📊 共添加 {days * items_per_day} 条论坛帖子")
        print(f"📊 共添加 {days * items_per_day} 条手账")
        print(f"📊 共添加 {days * items_per_day} 条饮食记录")
        print(f"📊 总计 {days * items_per_day * 3} 条数据")
        
        return True


if __name__ == "__main__":
    try:
        success = add_test_data()
        if success:
            print("\n✅ 数据添加成功！")
        else:
            print("\n❌ 数据添加失败！")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
