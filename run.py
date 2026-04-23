import sys
import os
from app import create_app
from loguru import logger

# 配置日志
logger.add("app.log", rotation="500 MB")

logger.info("=" * 60)
logger.info("健康饮食系统 - 启动准备")
logger.info("=" * 60)

# 1. 显示启动选择器
try:
    from launcher import select_mode
    mode = select_mode()
    logger.info(f"数据模式: {mode}")
except Exception as e:
    logger.warning(f"启动选择器失败: {e}")
    logger.info("默认使用虚拟数据模式")
    mode = "VIRTUAL"
    os.environ['HEALTH_DATA_MODE'] = mode

# 2. 创建应用
logger.info("\n正在创建应用实例...")
app = create_app()
logger.info(f"应用实例创建成功，DEBUG模式：{app.config['DEBUG']}")

# 3. 根据模式初始化数据
if mode == "VIRTUAL":
    logger.info("\n📝 虚拟数据模式 - 初始化本地数据...")
    try:
        with app.app_context():
            from app.models.hot_food import HotFood
            from datetime import datetime
            import json
            
            # 检查是否已有数据
            existing_count = HotFood.query.count()
            if existing_count == 0:
                logger.info("初始化虚拟数据...")
                
                mock_hot_foods = [
                    {
                        "food_name": "日式拉面",
                        "ingre_list": "小麦面粉,猪骨汤,叉烧,鸡蛋,葱",
                        "link": "https://www.xiaohongshu.com/explore/12345",
                        "hot_score": 12800,
                        "source": "小红书",
                        "tags": ["美食", "日式", "拉面"],
                        "image": "https://picsum.photos/seed/ramen/300/200",
                        "description": "正宗日式拉面，浓郁猪骨汤头，口感丰富",
                        "comments": 342,
                        "collection": 1280
                    },
                    {
                        "food_name": "泰式冬阴功汤",
                        "ingre_list": "香茅,柠檬叶,辣椒,虾,椰奶",
                        "link": "https://www.xiaohongshu.com/explore/12346",
                        "hot_score": 9500,
                        "source": "小红书",
                        "tags": ["美食", "泰式", "汤"],
                        "image": "https://picsum.photos/seed/tom-yum/300/200",
                        "description": "酸辣可口的泰式冬阴功汤，开胃又营养",
                        "comments": 215,
                        "collection": 890
                    },
                    {
                        "food_name": "意式番茄意面",
                        "ingre_list": "意大利面,番茄,洋葱,大蒜,橄榄油",
                        "link": "https://www.xiaohongshu.com/explore/12347",
                        "hot_score": 8200,
                        "source": "小红书",
                        "tags": ["美食", "意式", "意面"],
                        "image": "https://picsum.photos/seed/pasta/300/200",
                        "description": "经典意式番茄意面，简单美味",
                        "comments": 189,
                        "collection": 756
                    },
                    {
                        "food_name": "中式红烧肉",
                        "ingre_list": "五花肉,酱油,料酒,冰糖,姜",
                        "link": "https://www.xiaohongshu.com/explore/12348",
                        "hot_score": 15600,
                        "source": "小红书",
                        "tags": ["美食", "中式", "红烧肉"],
                        "image": "https://picsum.photos/seed/braised-pork/300/200",
                        "description": "肥而不腻的中式红烧肉，入口即化",
                        "comments": 520,
                        "collection": 2100
                    },
                    {
                        "food_name": "韩式烤肉",
                        "ingre_list": "牛肉,韩式辣酱,大蒜,芝麻,生菜",
                        "link": "https://www.xiaohongshu.com/explore/12349",
                        "hot_score": 10300,
                        "source": "小红书",
                        "tags": ["美食", "韩式", "烤肉"],
                        "image": "https://picsum.photos/seed/korean-bbq/300/200",
                        "description": "香喷喷的韩式烤肉，配生菜吃超解腻",
                        "comments": 310,
                        "collection": 1350
                    }
                ]
                
                for item in mock_hot_foods:
                    hot_food = HotFood(
                        food_name=item['food_name'],
                        ingre_list=item['ingre_list'],
                        link=item['link'],
                        hot_score=item['hot_score'],
                        source=item['source'],
                        tags=json.dumps(item['tags']),
                        image=item['image'],
                        description=item.get('description', item['ingre_list']),
                        comments=item.get('comments', 0),
                        collection=item.get('collection', 0),
                        create_time=datetime.now()
                    )
                    hot_food.save()
                
                logger.info(f"✅ 虚拟数据初始化完成，共{len(mock_hot_foods)}条")
            else:
                logger.info(f"✅ 已有数据{existing_count}条，跳过初始化")
    except Exception as e:
        logger.error(f"虚拟数据初始化失败: {e}")

logger.info("\n" + "=" * 60)
logger.info("启动完成！")
logger.info("=" * 60)

if __name__ == "__main__":
    # 启动应用
    try:
        logger.info("\n正在启动Flask服务...")
        logger.info(f"服务地址：http://0.0.0.0:5000")
        app.run(
            host="0.0.0.0",
            port=5000,
            debug=app.config["DEBUG"],
            threaded=True
        )
    except Exception as e:
        logger.error(f"应用启动失败：{str(e)}")
        import traceback
        traceback.print_exc()
        raise e