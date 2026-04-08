#!/usr/bin/env python3
"""
虚拟数据生成脚本
用于生成健康饮食管理系统的测试数据
生成128个测试用例对应的虚拟数据
"""

import sys
import os
import random
from datetime import datetime, timedelta
from loguru import logger

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.user import User
from app.models.diet_record import DietRecord
from app.models.exercise_record import ExerciseRecord
from app.models.water_record import WaterRecord
from app.models.recipe import Recipe
from app.models.user_collection import UserCollection
from app.models.forum_post import ForumPost
from app.models.hand_account import HandAccount
from app.models.user_like import UserLike
from app.models.comment import Comment

# 虚拟数据配置
NICKNAMES = [
    "健康小王", "美食达人", "运动健将", "养生专家", "减脂小白",
    "增肌狂人", "佛系吃货", "营养大师", "健康生活", "美食探索家",
    "瑜伽爱好者", "跑步达人", "健身新手", "素食主义", "低碳水达人",
    "轻食主义", "健康餐食", "营养均衡", "生活健康", "美食分享"
]

FOOD_NAMES = [
    "番茄炒蛋", "红烧排骨", "清蒸鲈鱼", "宫保鸡丁", "麻婆豆腐",
    "水煮牛肉", "糖醋里脊", "蒜蓉西兰花", "蛋炒饭", "牛肉面",
    "燕麦粥", "全麦面包", "鸡胸肉沙拉", "牛油果拌饭", "三文鱼刺身",
    "紫菜蛋花汤", "红烧肉", "清炒时蔬", "煎蛋", "牛奶"
]

FOOD_TYPES = ["主食", "蛋白质", "蔬菜", "水果", "奶制品", "脂肪"]

MEAL_TIMES = ["早餐", "午餐", "晚餐", "加餐"]

HEALTH_GOALS = ["减脂", "增肌", "维持", "塑形"]

DIETARY_PREFERENCES = ["无特殊偏好", "素食", "低碳水", "高蛋白", "地中海饮食"]

EXERCISE_TYPES = ["跑步", "游泳", "骑行", "力量训练", "瑜伽", "跳绳", "快走", "篮球"]

HAND_ACCOUNT_TOPICS = [
    "今天的饮食", "健康打卡", "运动记录", "美食分享", "减脂日记",
    "增肌记录", "生活日常", "营养分析", "烹饪心得", "食材分享"
]

MOODS = ["开心", "平静", "满足", "疲惫", "兴奋", "充实", "焦虑", "放松"]

FORUM_TITLES = [
    "求推荐健康食谱", "减脂期间吃什么", "如何坚持运动", "大家的健身计划",
    "营养师请进", "今天做了一道菜", "分享我的减脂经验", "求增肌方法",
    "健康饮食打卡", "大家都用什么运动APP", "这道菜热量多少",
    "推荐几本健康书籍", "讨论一下低碳水饮食", "怎么做减脂餐好吃"
]


def generate_openid(index):
    """生成唯一的OpenID"""
    return f"test_openid_{index:04d}"


def generate_nickname():
    """生成随机昵称"""
    return random.choice(NICKNAMES) + str(random.randint(1, 999))


def generate_height():
    """生成随机身高(cm)"""
    return round(random.uniform(150, 195), 1)


def generate_weight():
    """生成随机体重(kg)"""
    return round(random.uniform(45, 100), 1)


def generate_age():
    """生成随机年龄"""
    return random.randint(18, 65)


def generate_gender():
    """生成随机性别"""
    return random.randint(1, 2)


def generate_calorie():
    """生成随机热量(大卡)"""
    return round(random.uniform(50, 800), 1)


def generate_protein():
    """生成随机蛋白质(g)"""
    return round(random.uniform(0, 50), 1)


def generate_carb():
    """生成随机碳水(g)"""
    return round(random.uniform(0, 100), 1)


def generate_fat():
    """生成随机脂肪(g)"""
    return round(random.uniform(0, 50), 1)


def generate_date(days_ago=0):
    """生成日期"""
    return (datetime.now() - timedelta(days=days_ago)).date()


def generate_food_name():
    """生成食物名称"""
    return random.choice(FOOD_NAMES)


def generate_food_type():
    """生成食物类型"""
    return random.choice(FOOD_TYPES)


def generate_meal_time():
    """生成用餐时间"""
    return random.choice(MEAL_TIMES)


def generate_health_goal():
    """生成健康目标"""
    return random.choice(HEALTH_GOALS)


def generate_dietary_preference():
    """生成饮食偏好"""
    return random.choice(DIETARY_PREFERENCES)


def generate_exercise_type():
    """生成运动类型"""
    return random.choice(EXERCISE_TYPES)


def generate_exercise_duration():
    """生成运动时长(分钟)"""
    return random.randint(10, 120)


def generate_exercise_calorie():
    """生成运动消耗热量"""
    return random.randint(50, 600)


def generate_water_amount():
    """生成饮水量(ml)"""
    return random.randint(100, 500)


def generate_hand_account_topic():
    """生成手账主题"""
    return random.choice(HAND_ACCOUNT_TOPICS)


def generate_mood():
    """生成心情"""
    return random.choice(MOODS)


def generate_forum_title():
    """生成论坛标题"""
    return random.choice(FORUM_TITLES)


def generate_forum_content():
    """生成论坛内容"""
    contents = [
        "大家好，最近在减脂，有什么好的建议吗？",
        "今天做了一道很好吃的健康餐，分享给大家！",
        "坚持运动一周了，感觉身体状态变好了",
        "求推荐一些简单易做的减脂餐食谱",
        "大家平时都怎么安排健身时间的？",
        "营养师说我蛋白质摄入不够，该怎么补充呢？",
        "记录一下今天的饮食和运动，继续加油！",
        "增肌好难啊，有没有大神分享经验？",
        "健康饮食真的很重要，坚持下来变化很大",
        "想试试低碳水饮食，有什么要注意的吗？"
    ]
    return random.choice(contents)


def generate_comment_content():
    """生成评论内容"""
    comments = [
        "说得太好了！",
        "学习了，谢谢分享！",
        "我也是这么做的",
        "这个方法真的有效",
        "收藏了，以后试试",
        "赞同！",
        "太棒了！",
        "学习学习",
        "加油！",
        "支持一下"
    ]
    return random.choice(comments)


def generate_users(count=32):
    """生成用户数据"""
    logger.info(f"正在生成 {count} 个用户...")
    users = []
    for i in range(count):
        user = User(
            openid=generate_openid(i + 1),
            nickname=generate_nickname(),
            height=generate_height(),
            weight=generate_weight(),
            age=generate_age(),
            gender=generate_gender(),
            health_goal=generate_health_goal(),
            dietary_preference=generate_dietary_preference(),
            create_time=datetime.now() - timedelta(days=random.randint(1, 90))
        )
        users.append(user)
    return users


def generate_diet_records(users, count_per_user=4):
    """生成饮食记录"""
    logger.info(f"正在生成饮食记录，每个用户 {count_per_user} 条...")
    records = []
    for user in users:
        for _ in range(count_per_user):
            record = DietRecord(
                user_id=user.id,
                food_name=generate_food_name(),
                food_type=generate_food_type(),
                meal_time=generate_meal_time(),
                weight=random.randint(50, 300),
                calorie=generate_calorie(),
                protein=generate_protein(),
                carb=generate_carb(),
                fat=generate_fat(),
                create_date=generate_date(random.randint(0, 30)),
                create_time=datetime.now() - timedelta(days=random.randint(0, 30))
            )
            records.append(record)
    return records


def generate_exercise_records(users, count_per_user=2):
    """生成运动记录"""
    logger.info(f"正在生成运动记录，每个用户 {count_per_user} 条...")
    records = []
    for user in users:
        for _ in range(count_per_user):
            record = ExerciseRecord(
                user_id=user.id,
                exercise_type=generate_exercise_type(),
                duration=generate_exercise_duration(),
                calorie=generate_exercise_calorie(),
                create_date=generate_date(random.randint(0, 30)),
                create_time=datetime.now() - timedelta(days=random.randint(0, 30))
            )
            records.append(record)
    return records


def generate_water_records(users, count_per_user=3):
    """生成饮水记录"""
    logger.info(f"正在生成饮水记录，每个用户 {count_per_user} 条...")
    records = []
    for user in users:
        for _ in range(count_per_user):
            record = WaterRecord(
                user_id=user.id,
                amount=generate_water_amount(),
                create_date=generate_date(random.randint(0, 30)),
                create_time=datetime.now() - timedelta(days=random.randint(0, 30))
            )
            records.append(record)
    return records


def generate_forum_posts(users, count=20):
    """生成论坛帖子"""
    logger.info(f"正在生成 {count} 个论坛帖子...")
    posts = []
    for _ in range(count):
        user = random.choice(users)
        post = ForumPost(
            user_id=user.id,
            title=generate_forum_title(),
            content=generate_forum_content(),
            create_time=datetime.now() - timedelta(days=random.randint(0, 30)),
            view_count=random.randint(10, 500),
            like_count=random.randint(0, 50)
        )
        posts.append(post)
    return posts


def generate_hand_accounts(users, count_per_user=2):
    """生成手账"""
    logger.info(f"正在生成手账，每个用户 {count_per_user} 条...")
    accounts = []
    for user in users:
        for _ in range(count_per_user):
            account = HandAccount(
                user_id=user.id,
                topic=generate_hand_account_topic(),
                mood=generate_mood(),
                content=f"今天是美好的一天，记录一下我的健康生活。{generate_hand_account_topic()}真的很重要！",
                create_time=datetime.now() - timedelta(days=random.randint(0, 30))
            )
            accounts.append(account)
    return accounts


def generate_comments(users, posts, count=40):
    """生成评论"""
    logger.info(f"正在生成 {count} 条评论...")
    comments = []
    for _ in range(count):
        user = random.choice(users)
        post = random.choice(posts)
        comment = Comment(
            user_id=user.id,
            post_id=post.id,
            content=generate_comment_content(),
            create_time=datetime.now() - timedelta(days=random.randint(0, 30))
        )
        comments.append(comment)
    return comments


def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("开始生成虚拟测试数据")
    logger.info("=" * 50)

    # 创建Flask应用
    app = create_app()

    with app.app_context():
        # 清空现有数据
        logger.info("清空现有数据库数据...")
        db.drop_all()
        db.create_all()

        # 1. 生成用户数据 (32个用户)
        users = generate_users(32)
        db.session.add_all(users)
        db.session.commit()
        logger.info(f"✓ 成功生成 {len(users)} 个用户")

        # 2. 生成饮食记录 (每个用户4条，共128条)
        diet_records = generate_diet_records(users, 4)
        db.session.add_all(diet_records)
        db.session.commit()
        logger.info(f"✓ 成功生成 {len(diet_records)} 条饮食记录")

        # 3. 生成运动记录
        exercise_records = generate_exercise_records(users, 2)
        db.session.add_all(exercise_records)
        db.session.commit()
        logger.info(f"✓ 成功生成 {len(exercise_records)} 条运动记录")

        # 4. 生成饮水记录
        water_records = generate_water_records(users, 3)
        db.session.add_all(water_records)
        db.session.commit()
        logger.info(f"✓ 成功生成 {len(water_records)} 条饮水记录")

        # 5. 生成论坛帖子
        forum_posts = generate_forum_posts(users, 20)
        db.session.add_all(forum_posts)
        db.session.commit()
        logger.info(f"✓ 成功生成 {len(forum_posts)} 个论坛帖子")

        # 6. 生成手账
        hand_accounts = generate_hand_accounts(users, 2)
        db.session.add_all(hand_accounts)
        db.session.commit()
        logger.info(f"✓ 成功生成 {len(hand_accounts)} 条手账")

        # 7. 生成评论
        comments = generate_comments(users, forum_posts, 40)
        db.session.add_all(comments)
        db.session.commit()
        logger.info(f"✓ 成功生成 {len(comments)} 条评论")

        logger.info("=" * 50)
        logger.info("虚拟数据生成完成！")
        logger.info("=" * 50)
        logger.info(f"总用户数: {len(users)}")
        logger.info(f"总饮食记录数: {len(diet_records)}")
        logger.info(f"总运动记录数: {len(exercise_records)}")
        logger.info(f"总饮水记录数: {len(water_records)}")
        logger.info(f"总论坛帖子数: {len(forum_posts)}")
        logger.info(f"总手账数: {len(hand_accounts)}")
        logger.info(f"总评论数: {len(comments)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"生成虚拟数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
