from flask import Blueprint, g, request
from app.models.hot_food import HotFood
from app.crawler.xhs_drission_crawler import crawl_xhs_hot_food
from app.utils.common import format_response
# from app.utils.common_util import format_response
from loguru import logger

# 创建蓝图
hot_food_bp = Blueprint("hotfood", __name__)

from app.utils.auth_decorator import login_required

@hot_food_bp.route("/list", methods=["GET"])
def get_hot_food_list():
    """获取热点美食列表"""
    try:
        limit = int(request.args.get("limit", 20))
        hot_foods = HotFood.get_hot_list(limit)
        hot_foods_dict = [hf.to_dict() for hf in hot_foods]
        
        return format_response(data={
            "total": len(hot_foods_dict),
            "list": hot_foods_dict
        })
    except Exception as e:
        logger.error(f"获取热点美食列表失败：{str(e)}")
        return format_response(500, f"获取热点美食列表失败：{str(e)}")

import threading

@hot_food_bp.route("/crawl", methods=["POST"])
@login_required
def manual_crawl():
    """手动触发小红书爬虫"""
    try:
        # 检查 DrissionPage 是否可用
        try:
            from DrissionPage import ChromiumPage
            drission_available = True
        except ImportError:
            drission_available = False
            logger.warning("DrissionPage 未安装，将使用模拟数据")
        
        # 如果不使用强制登录且 DrissionPage 不可用，直接返回模拟数据
        if not drission_available:
            # 使用模拟数据
            from app.models.hot_food import HotFood
            from app import db
            import json
            from datetime import datetime
            
            mock_hot_foods = [
                {
                    "food_name": "日式拉面",
                    "ingre_list": "小麦面粉，猪骨汤，叉烧，鸡蛋，葱",
                    "link": "https://www.xiaohongshu.com/explore/12345",
                    "hot_score": 12800,
                    "source": "小红书",
                    "tags": ["美食", "日式", "拉面"],
                    "image": "https://picsum.photos/seed/ramen/300/200",
                    "desc": "正宗日式拉面，浓郁猪骨汤头，口感丰富",
                    "comments": 342,
                    "collection": 1280
                },
                {
                    "food_name": "泰式冬阴功汤",
                    "ingre_list": "香茅，柠檬叶，辣椒，虾，椰奶",
                    "link": "https://www.xiaohongshu.com/explore/12346",
                    "hot_score": 9500,
                    "source": "小红书",
                    "tags": ["美食", "泰式", "汤"],
                    "image": "https://picsum.photos/seed/tom-yum/300/200",
                    "desc": "酸辣可口的泰式冬阴功汤，开胃又营养",
                    "comments": 215,
                    "collection": 890
                },
                {
                    "food_name": "意式番茄意面",
                    "ingre_list": "意大利面，番茄，洋葱，大蒜，橄榄油",
                    "link": "https://www.xiaohongshu.com/explore/12347",
                    "hot_score": 8200,
                    "source": "小红书",
                    "tags": ["美食", "意式", "意面"],
                    "image": "https://picsum.photos/seed/pasta/300/200",
                    "desc": "经典意式番茄意面，简单美味",
                    "comments": 189,
                    "collection": 756
                }
            ]
            
            # 清空旧数据并保存新数据
            HotFood.query.delete()
            for item in mock_hot_foods:
                hot_food = HotFood(
                    food_name=item['food_name'],
                    ingre_list=item['ingre_list'],
                    link=item['link'],
                    hot_score=item['hot_score'],
                    source=item['source'],
                    tags=json.dumps(item['tags']),
                    image=item['image'],
                    description=item.get('desc', item['ingre_list']),
                    comments=item.get('comments', 0),
                    collection=item.get('collection', 0),
                    create_time=datetime.now()
                )
                hot_food.save()
            
            return format_response(msg="热点美食数据已更新（模拟数据）")
        
        # DrissionPage 可用，异步执行真实爬取
        def crawl_task():
            try:
                logger.info("开始异步爬取热点美食")
                crawl_xhs_hot_food(force_login=False, manual=True)
                logger.info("热点美食爬取完成")
            except Exception as e:
                logger.error(f"异步爬取失败：{str(e)}")
        
        # 启动异步任务
        threading.Thread(target=crawl_task).start()
        return format_response(msg="热点美食爬取任务已启动，正在后台执行")
    except Exception as e:
        logger.error(f"手动爬取失败：{str(e)}")
        return format_response(500, f"爬取失败：{str(e)}")