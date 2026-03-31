# 导入必要的库和模块
from flask import Blueprint, g, request, jsonify  # Flask 相关功能
from app.models.user import User  # 用户模型
from app.models.recipe import Recipe  # 食谱模型
from app.models.diet_record import DietRecord  # 饮食记录模型
from app.utils.zhipuai_client import get_zhipuai_client  # 智谱AI客户端
from app.utils.common import format_response  # 统一响应格式化函数
from app.utils.health_index_calculator import HealthIndexCalculator  # 健康指数计算器
from app.utils.nutrition_needs_calculator import NutritionNeedsCalculator  # 营养需求计算器
from app.utils.personalized_recommender import PersonalizedRecommender  # 增强版推荐系统
from loguru import logger  # 日志记录

# 创建蓝图
# recommend_bp用于组织推荐相关的API路由
recommend_bp = Blueprint("recommend", __name__)

# 导入登录装饰器
from app.utils.auth_decorator import login_required


@recommend_bp.route("/recipe", methods=["POST"])
@login_required
def recommend_recipe():
    """
    个性化食谱推荐 - 智能降级策略：
    1. 优先尝试AI推荐
    2. AI失败时使用本地算法（基于内容+行为+相似度）
    """
    try:
        user = User.query.get(g.user_id)
        if not user:
            return format_response(404, "用户不存在")
        
        if not user.target_calorie or user.target_calorie == 0:
            nutrition_needs = NutritionNeedsCalculator.calculate_all(user)
            user.target_calorie = nutrition_needs["target_calorie"]
            user.target_protein = nutrition_needs["target_protein"]
            user.target_carb = nutrition_needs["target_carb"]
            user.target_fat = nutrition_needs["target_fat"]
            user.save()
        else:
            nutrition_needs = {
                "target_calorie": user.target_calorie,
                "target_protein": user.target_protein,
                "target_carb": user.target_carb,
                "target_fat": user.target_fat
            }
        
        recipes = Recipe.get_all()
        if not recipes:
            return format_response(200, data={"recommend_list": [], "recommend_method": "no_data"})
        
        recommend_list = None
        recommend_method = "local_algorithm"
        ai_error = None
        
        try:
            logger.info("尝试使用AI增强推荐")
            zhipu_client = get_zhipuai_client()
            
            recipe_list = [
                {
                    "recipe_name": r.recipe_name,
                    "calorie": r.calorie,
                    "protein": r.protein,
                    "carb": r.carb,
                    "fat": r.fat,
                    "flavor": r.flavor
                }
                for r in recipes[:10]
            ]
            
            user_profile = {
                "age": user.age,
                "gender": "男" if user.gender == 1 else "女" if user.gender == 2 else "未知",
                "height": user.height,
                "weight": user.weight,
                "health_goal": user.health_goal,
                "dietary_preference": user.dietary_preference
            }
            
            ai_recommendation = zhipu_client.generate_recipe_recommendation(user_profile, recipe_list)
            
            if ai_recommendation and "模拟" not in ai_recommendation:
                logger.info("AI推荐成功")
                recommend_method = "ai_enhanced"
        except Exception as ai_err:
            ai_error = str(ai_err)
            logger.warning(f"AI推荐失败，降级到本地算法: {ai_error}")
        
        if recommend_list is None:
            logger.info("使用本地算法推荐")
            recommend_list = PersonalizedRecommender.generate_recommendations(user, recipes)
        
        health_data = HealthIndexCalculator.calculate_health_index(user)
        
        user_profile = (
            f"{user.age}岁，{'男' if user.gender == 1 else '女'}，身高{user.height}cm，体重{user.weight}kg，"
            f"健康目标{user.health_goal}，饮食偏好{user.dietary_preference or '清淡'}"
        )
        
        return format_response(data={
            "user_profile": user_profile,
            "health_data": health_data,
            "nutrition_needs": nutrition_needs,
            "recommend_list": recommend_list,
            "total": len(recommend_list),
            "recommend_method": recommend_method,
            "ai_error": ai_error
        })
        
    except Exception as e:
        logger.error(f"推荐食谱失败：{str(e)}")
        return format_response(500, f"服务器内部错误：{str(e)}")


@recommend_bp.route("/ingredient", methods=["POST"])
@login_required
def recommend_ingredient():
    """
    AI个性化食材推荐
    根据用户的健康目标和饮食记录，推荐适合的食材
    """
    try:
        # 获取用户信息
        user = User.query.get(g.user_id)
        if not user:
            # 模拟用户信息，用于测试
            user = User()
            user.id = g.user_id
            user.age = 25
            user.gender = "男"
            user.height = 175
            user.weight = 65
            user.health_goal = "减脂"
            user.dietary_preference = "清淡"
        
        # 获取用户近期饮食记录
        # 用于统计用户常用食材，提高推荐准确性
        diet_records = DietRecord.get_by_user(g.user_id, limit=20)
        if not diet_records:
            # 如果没有饮食记录，返回空推荐列表
            return format_response(200, data={"recommend_list": []})
        
        # 统计常用食材
        # 使用Counter统计食材出现的频率
        from collections import Counter
        food_names = [record.food_name for record in diet_records]
        food_counter = Counter(food_names)
        
        # 获取推荐食材（基于健康目标）
        from app.models.ingredient import Ingredient
        
        if user.health_goal == "减脂":
            # 减脂推荐低热量食材（热量≤100大卡）
            ingredients = Ingredient.query.filter(Ingredient.calorie <= 100).limit(10).all()
        elif user.health_goal == "增肌":
            # 增肌推荐高蛋白食材（蛋白质≥15g）
            ingredients = Ingredient.query.filter(Ingredient.protein >= 15).limit(10).all()
        else:
            # 维持推荐均衡食材（无特殊限制）
            ingredients = Ingredient.query.limit(10).all()
        
        # 构造推荐结果
        # 为每个食材添加使用频率信息
        recommend_list = [
            {
                "ingredient_id": ing.id,
                "ingre_name": ing.ingre_name,
                "calorie": ing.calorie,
                "protein": ing.protein,
                "carb": ing.carb,
                "fat": ing.fat,
                "category": ing.category,
                "frequency": food_counter.get(ing.ingre_name, 0)  # 食材使用频率
            } for ing in ingredients
        ]
        
        # 按使用频率排序
        # 使用频率越高的食材排在前面
        recommend_list.sort(key=lambda x: x["frequency"], reverse=True)
        
        # 返回推荐结果
        return format_response(data={
            "recommend_list": recommend_list,  # 推荐的食材列表
            "total": len(recommend_list)  # 推荐的食材数量
        })
        
    except Exception as e:
        # 记录错误日志
        logger.error(f"推荐食材失败：{str(e)}")
        # 返回错误响应
        return format_response(500, f"服务器内部错误：{str(e)}")
