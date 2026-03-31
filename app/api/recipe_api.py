from flask import Blueprint, g, request
from app.models.recipe import Recipe
from app.models.user import User
from app.models.user_collection import UserCollection
from app.utils.common import format_response
from app.utils.nutrition_calculator import NutritionCalculator
from app.utils.health_index_calculator import HealthIndexCalculator
from loguru import logger

# 创建蓝图
recipe_bp = Blueprint("recipe", __name__)

from app.utils.auth_decorator import login_required

@recipe_bp.route("/list", methods=["GET"])
@login_required
def get_recipe_list():
    """获取所有食谱"""
    recipes = Recipe.get_all()
    recipes_dict = [r.to_dict() for r in recipes]
    
    return format_response(data={
        "total": len(recipes_dict),
        "list": recipes_dict
    })

@recipe_bp.route("/search", methods=["GET"])
@login_required
def search_recipe():
    """食谱模糊搜索"""
    keyword = request.args.get("keyword", "")
    recipes = Recipe.query.filter(Recipe.recipe_name.contains(keyword)).all()
    return format_response(data={"list": [r.to_dict() for r in recipes]})

@recipe_bp.route("/recommend", methods=["POST"])
@login_required
def recommend_recipe():
    """AI 个性化食谱推荐（简化版，移除 API 调用）"""
    # 获取用户信息
    user = User.query.get(g.user_id)
    if not user or not user.health_goal:
        return format_response(400, "用户健康目标未设置，无法推荐")
    
    # 计算营养需求
    nutrition_needs = NutritionCalculator.calculate_nutrition_needs(user)
    daily_meal_plan = NutritionCalculator.generate_daily_meal_plan(nutrition_needs)
    
    # 构建用户画像
    user_profile = (
        f"{user.age}岁，{'男' if user.gender == 1 else '女'}，身高{user.height}cm，体重{user.weight}kg，"
        f"健康目标{user.health_goal}，饮食偏好{user.dietary_preference or '清淡'}，"
        f"每日推荐热量{nutrition_needs['calorie']}大卡"
    )
    
    # 获取所有食谱
    recipes = Recipe.get_all()
    if not recipes:
        return format_response(404, "暂无食谱数据")
    
    # 使用健康指数计算器生成推荐（本地计算，无需 API 调用）
    recommend_list = HealthIndexCalculator.generate_personalized_recipe_recommendations(user, recipes)
    
    return format_response(data={
        "user_profile": user_profile,
        "nutrition_needs": nutrition_needs,
        "daily_meal_plan": daily_meal_plan,
        "recommend_list": recommend_list
    })

@recipe_bp.route("/collection", methods=["POST"])
@login_required
def add_collection():
    """添加食谱收藏"""
    params = request.get_json() or {}
    recipe_id = params.get("recipe_id")
    
    if not recipe_id:
        return format_response(400, "缺少食谱ID")
    
    # 检查食谱是否存在
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return format_response(404, "食谱不存在")
    
    # 检查是否已经收藏
    existing_collection = UserCollection.get_by_user_and_target(g.user_id, recipe_id=recipe_id)
    if existing_collection:
        return format_response(400, "已经收藏过该食谱")
    
    # 添加收藏
    collection = UserCollection(user_id=g.user_id, recipe_id=recipe_id)
    if collection.save():
        return format_response(msg="收藏成功")
    else:
        return format_response(500, "收藏失败")

@recipe_bp.route("/collection", methods=["DELETE"])
@login_required
def remove_collection():
    """取消食谱收藏"""
    params = request.get_json() or {}
    recipe_id = params.get("recipe_id")
    
    if not recipe_id:
        return format_response(400, "缺少食谱ID")
    
    # 查找收藏记录
    collection = UserCollection.get_by_user_and_target(g.user_id, recipe_id=recipe_id)
    if not collection:
        return format_response(404, "未找到收藏记录")
    
    # 删除收藏
    if collection.delete():
        return format_response(msg="取消收藏成功")
    else:
        return format_response(500, "取消收藏失败")

@recipe_bp.route("/collection/list", methods=["GET"])
@login_required
def get_collection_list():
    """获取用户收藏的食谱"""
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    
    collections = UserCollection.get_by_user(g.user_id, collection_type="recipe", page=page, page_size=page_size)
    
    # 构造返回数据
    recipe_list = []
    for collection in collections:
        recipe = Recipe.query.get(collection.recipe_id)
        if recipe:
            recipe_dict = recipe.to_dict()
            recipe_dict["collection_time"] = collection.create_time.strftime("%Y-%m-%d %H:%M:%S")
            recipe_list.append(recipe_dict)
    
    return format_response(data={
        "total": len(recipe_list),
        "list": recipe_list
    })

@recipe_bp.route("/detail/<int:recipe_id>", methods=["GET"])
@login_required
def get_recipe_detail(recipe_id):
    """获取食谱详情"""
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return format_response(404, "食谱不存在")
    
    # 检查是否已收藏
    is_collected = False
    collection = UserCollection.get_by_user_and_target(g.user_id, recipe_id=recipe_id)
    if collection:
        is_collected = True
    
    recipe_dict = recipe.to_dict()
    recipe_dict["is_collected"] = is_collected
    
    return format_response(data=recipe_dict)

@recipe_bp.route("/personalized", methods=["POST"])
@login_required
def get_personalized_recipes():
    """基于拥有食材的个性化菜谱推荐"""
    params = request.get_json() or {}
    ingredients = params.get("ingredients", [])
    health_goals = params.get("health_goals", "健康饮食")
    calorie_limit = params.get("calorie_limit", 500)
    
    if not ingredients:
        return format_response(400, "请提供拥有的食材列表")
    
    try:
        # 导入数据处理器
        from app.utils.data_processor import FoodDataProcessor
        processor = FoodDataProcessor()
        
        # 生成个性化菜谱推荐
        recipes = processor.get_personalized_recipes(ingredients, health_goals, calorie_limit)
        
        if not recipes:
            return format_response(404, "未能生成个性化菜谱推荐")
        
        return format_response(data={
            "ingredients": ingredients,
            "health_goals": health_goals,
            "calorie_limit": calorie_limit,
            "recipes": recipes
        })
    except Exception as e:
        logger.error(f"生成个性化菜谱失败：{str(e)}")
        return format_response(500, f"生成个性化菜谱失败：{str(e)}")

@recipe_bp.route("/ingredient-search", methods=["POST"])
@login_required
def search_recipes_by_ingredients():
    """基于食材的小红书搜索和个性化推荐"""
    params = request.get_json() or {}
    ingredients = params.get("ingredients", [])
    health_goals = params.get("health_goals", "健康饮食")
    calorie_limit = params.get("calorie_limit", 500)
    
    if not ingredients:
        return format_response(400, "请提供拥有的食材列表")
    
    try:
        # 导入小红书爬虫
        from app.crawler.xhs_drission_crawler import XHSDrissionCrawler
        # 导入数据处理器
        from app.utils.data_processor import FoodDataProcessor
        
        # 初始化爬虫
        crawler = XHSDrissionCrawler()
        
        # 根据食材搜索小红书菜谱
        search_results = crawler.search_by_ingredients(ingredients)
        
        # 处理搜索结果并生成个性化推荐
        processor = FoodDataProcessor()
        final_results = processor.process_ingredient_based_recipes(ingredients, search_results, health_goals, calorie_limit)
        
        # 关闭爬虫
        crawler.close()
        
        return format_response(data={
            "ingredients": ingredients,
            "health_goals": health_goals,
            "calorie_limit": calorie_limit,
            "search_results": final_results.get('search_results', []),
            "personalized_recipes": final_results.get('personalized_recipes', [])
        })
    except Exception as e:
        logger.error(f"基于食材搜索菜谱失败：{str(e)}")
        return format_response(500, f"基于食材搜索菜谱失败：{str(e)}")