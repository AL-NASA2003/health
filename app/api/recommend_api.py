# 导入必要的库和模块
from flask import Blueprint, g, request, jsonify  # Flask 相关功能
from app import db
from app.models.user import User  # 用户模型
from app.models.recipe import Recipe  # 食谱模型
from app.models.diet_record import DietRecord  # 饮食记录模型
from app.utils.zhipuai_client import get_zhipuai_client  # 智谱AI客户端
from app.utils.common import format_response  # 统一响应格式化函数
from app.utils.health_index_calculator import HealthIndexCalculator  # 健康指数计算器
from app.utils.nutrition_needs_calculator import NutritionNeedsCalculator  # 营养需求计算器
from app.utils.personalized_recommender import PersonalizedRecommender  # 增强版推荐系统
from app.utils.flavor_recommender import FlavorRecommender  # 风味增强推荐系统（新增）
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
    个性化食谱推荐 - 智能降级策略+筛选功能（参考aigconly.com/recipe-generator）
    1. 优先尝试AI推荐
    2. AI失败时使用本地算法（基于内容+行为+相似度）
    3. 支持筛选：菜系、难度、用时、食材
    """
    try:
        # 获取请求参数（筛选条件）
        data = request.get_json() or {}
        
        cuisine = data.get("cuisine", "")  # 菜系：中式/西式/日式/韩式
        difficulty = data.get("difficulty", "")  # 难度：简单/中等/困难
        cook_time = data.get("cook_time", "")  # 用时：30分钟内/30-60分钟/60分钟以上
        ingredients = data.get("ingredients", [])  # 食材列表
        
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
        
        # 构建查询
        query = Recipe.query
        
        # 菜系筛选
        if cuisine:
            query = query.filter(Recipe.cuisine == cuisine)
        
        # 难度筛选
        if difficulty:
            query = query.filter(Recipe.difficulty == difficulty)
        
        # 用时筛选
        if cook_time == "30分钟内":
            query = query.filter(Recipe.cook_time <= 30)
        elif cook_time == "30-60分钟":
            query = query.filter(Recipe.cook_time > 30, Recipe.cook_time <= 60)
        elif cook_time == "60分钟以上":
            query = query.filter(Recipe.cook_time > 60)
        
        # 食材筛选（简单实现：包含任一食材）
        if ingredients:
            from app.models.recipe import RecipeIngredient
            recipe_ids = db.session.query(RecipeIngredient.recipe_id) \
                .filter(RecipeIngredient.ingredient_id.in_(ingredients)) \
                .distinct()
            query = query.filter(Recipe.id.in_(recipe_ids))
        
        recipes = query.all()
        
        if not recipes:
            return format_response(200, data={
                "recommend_list": [],
                "recommend_method": "no_data",
                "filters": {
                    "cuisine": cuisine,
                    "difficulty": difficulty,
                    "cook_time": cook_time,
                    "ingredients": ingredients
                }
            })
        
        recommend_list = None
        recommend_method = "local_algorithm"
        ai_error = None
        
        # 优先尝试AI推荐
        try:
            logger.info("尝试使用AI推荐")
            client = get_zhipuai_client()
            
            # 获取所有可用食谱标题（用于AI推荐参考）
            all_recipe_titles = [recipe.recipe_name for recipe in recipes[:30]]  # 给AI参考前30个食谱
            title_list_str = ", ".join(all_recipe_titles)
            
            # 构建用户信息
            user_profile = (
                f"{user.age}岁，{'男' if user.gender == 1 else '女'}，身高{user.height}cm，体重{user.weight}kg，"
                f"健康目标{user.health_goal}，饮食偏好{user.dietary_preference or '清淡'}"
            )
            
            # 调用AI获取推荐 - 修改Prompt让AI直接从已有食谱中选择
            logger.info(f"向AI提供 {len(all_recipe_titles)} 个食谱供选择")
            
            # 重新定义一个更适合的Prompt来让AI从已有食谱中选择
            ai_prompt = f"""你是一位专业的营养师和食谱推荐专家。请根据以下用户信息，从给定的食谱列表中为用户推荐3个最适合的食谱。

用户信息：
- 年龄：{user.age}岁
- 身高：{user.height}cm
- 体重：{user.weight}kg
- 健康目标：{user.health_goal or '维持健康'}
- 饮食偏好：{user.dietary_preference or '无特殊偏好'}
- 目标热量：{user.target_calorie or 2000}kcal

可用食谱列表：
{title_list_str}

请严格以JSON格式返回推荐结果，格式如下：
{{
  "recommendations": [
    {{
      "title": "食谱名称（必须是上面列表中存在的完整名称）",
      "reason": "推荐理由，说明为什么这个食谱适合该用户"
    }}
  ]
}}
重要要求：
1. 只返回JSON，不要返回任何其他文字
2. 不要使用Markdown格式，不要用```包裹
3. 确保JSON格式完全正确，字符串用双引号
4. title必须完全匹配食谱列表中的名称，不要修改或简化
5. 推荐3个最适合的食谱
"""
            
            messages = [{"role": "user", "content": ai_prompt}]
            ai_response = client.chat(messages, temperature=0.3, max_tokens=2000)
            
            # 解析AI响应
            try:
                result = client._parse_json_response(ai_response)
            except Exception:
                result = client._mock_recipe_recommendation()
            
            # 如果AI返回了推荐，使用AI结果
            if result.get("recommendations") and len(result["recommendations"]) > 0:
                ai_recommendations = result["recommendations"]
                
                # 从数据库中匹配对应的食谱 - 使用正确的键名
                recipe_titles = [rec.get("title", "") for rec in ai_recommendations]
                matched_recipes = Recipe.query.filter(Recipe.recipe_name.in_(recipe_titles)).all()
                
                if matched_recipes and len(matched_recipes) > 0:
                    recommend_list = PersonalizedRecommender.generate_recommendations(user, matched_recipes)
                    recommend_method = "ai_recommend"
                    logger.info(f"AI推荐成功，匹配到 {len(recommend_list)} 个食谱")
                    
                    # 将AI推荐理由补充到返回结果中
                    for rec in recommend_list:
                        for ai_rec in ai_recommendations:
                            if ai_rec.get("title") == rec.get("recipe_name"):
                                rec["ai_reason"] = ai_rec.get("reason", "")
                else:
                    # 如果没有匹配到，使用本地算法，但记录AI尝试
                    ai_error = "AI推荐成功，但未完全匹配到食谱，使用本地算法补充"
                    logger.warning(ai_error)
                    recommend_method = "ai_fallback"
                    recommend_list = PersonalizedRecommender.generate_recommendations(user, recipes)
            else:
                ai_error = "AI未返回推荐结果"
                logger.warning(ai_error)
                
        except Exception as e:
            ai_error = f"AI推荐失败：{str(e)}"
            logger.error(ai_error)
            import traceback
            logger.error(traceback.format_exc())
        
        # 如果AI失败或没有返回，使用本地算法
        if not recommend_list:
            logger.info("使用本地算法推荐")
            recommend_list = PersonalizedRecommender.generate_recommendations(user, recipes)
        
        health_data = HealthIndexCalculator.calculate_health_index(user)
        
        # 转换字段名，适配前端期望的格式
        if nutrition_needs:
            nutrition_needs_frontend = {
                "calorie": nutrition_needs.get("target_calorie"),
                "protein": nutrition_needs.get("target_protein"),
                "carb": nutrition_needs.get("target_carb"),
                "fat": nutrition_needs.get("target_fat")
            }
        else:
            nutrition_needs_frontend = None
        
        user_profile = (
            f"{user.age}岁，{'男' if user.gender == 1 else '女'}，身高{user.height}cm，体重{user.weight}kg，"
            f"健康目标{user.health_goal}，饮食偏好{user.dietary_preference or '清淡'}"
        )
        
        # 筛选选项（返回给前端）
        filter_options = {
            "cuisine": ["全部", "中式", "西式", "日式", "韩式"],
            "difficulty": ["全部", "简单", "中等", "困难"],
            "cook_time": ["全部", "30分钟内", "30-60分钟", "60分钟以上"]
        }
        
        return format_response(data={
            "user_profile": user_profile,
            "health_data": health_data,
            "nutrition_needs": nutrition_needs_frontend,
            "recommend_list": recommend_list,
            "total": len(recommend_list),
            "recommend_method": recommend_method,
            "ai_error": ai_error,
            "filters": {
                "cuisine": cuisine,
                "difficulty": difficulty,
                "cook_time": cook_time,
                "ingredients": ingredients
            },
            "filter_options": filter_options
        })
        
    except Exception as e:
        logger.error(f"推荐食谱失败：{str(e)}")
        import traceback
        logger.error(traceback.format_exc())
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


# ============ 新增：风味增强推荐API（参考flavorithm.com）===========

@recommend_bp.route("/weekly-featured", methods=["GET"])
@login_required
def get_weekly_featured():
    """
    获取本周精选食谱（每周轮换）
    参考：flavorithm.com 每周精选功能
    """
    try:
        from app.utils.flavor_recommender import FlavorRecommender
        
        recommender = FlavorRecommender()
        recipes = Recipe.get_all()
        
        if not recipes:
            return format_response(200, data={"featured_list": [], "total": 0})
        
        # 获取每周精选
        featured_recipes = recommender.get_weekly_featured(recipes, count=3)
        
        featured_list = [r.to_dict() for r in featured_recipes]
        
        logger.info(f"返回本周精选食谱：{len(featured_list)} 条")
        
        return format_response(data={
            "featured_list": featured_list,
            "total": len(featured_list),
            "week_tag": recommender.weekly_seed
        })
        
    except Exception as e:
        logger.error(f"获取本周精选失败：{str(e)}")
        return format_response(500, f"服务器内部错误：{str(e)}")


@recommend_bp.route("/similar-recipes/<int:recipe_id>", methods=["GET"])
@login_required
def get_similar_recipes(recipe_id):
    """
    获取相似食谱（基于风味相似度）
    """
    try:
        from app.utils.flavor_recommender import FlavorRecommender
        
        target_recipe = Recipe.query.get(recipe_id)
        if not target_recipe:
            return format_response(404, "食谱不存在")
        
        recommender = FlavorRecommender()
        all_recipes = Recipe.get_all()
        
        similar_recipes = recommender.find_similar_recipes(target_recipe, all_recipes, top_k=5)
        
        # 构建响应
        similar_list = []
        for i, recipe in enumerate(similar_recipes):
            # 计算相似度（用于展示）
            sim = recommender.calculate_flavor_similarity(target_recipe, recipe)
            recipe_dict = recipe.to_dict()
            recipe_dict['similarity_score'] = round(sim, 2)
            similar_list.append(recipe_dict)
        
        return format_response(data={
            "target_recipe": target_recipe.to_dict(),
            "similar_list": similar_list,
            "total": len(similar_list)
        })
        
    except Exception as e:
        logger.error(f"获取相似食谱失败：{str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return format_response(500, f"服务器内部错误：{str(e)}")


@recommend_bp.route("/quick-recipes", methods=["GET"])
@login_required
def get_quick_recipes():
    """
    获取快手菜推荐（30分钟内）
    """
    try:
        from app.utils.flavor_recommender import FlavorRecommender
        
        max_time = request.args.get('max_time', 30, type=int)
        count = request.args.get('count', 5, type=int)
        
        recommender = FlavorRecommender()
        recipes = Recipe.get_all()
        
        quick_recipes = recommender.get_quick_recipes(recipes, max_time=max_time, count=count)
        
        return format_response(data={
            "quick_list": [r.to_dict() for r in quick_recipes],
            "total": len(quick_recipes),
            "max_time": max_time
        })
        
    except Exception as e:
        logger.error(f"获取快手菜失败：{str(e)}")
        return format_response(500, f"服务器内部错误：{str(e)}")


@recommend_bp.route("/flavor-profile/<int:recipe_id>", methods=["GET"])
def get_flavor_profile(recipe_id):
    """
    获取食谱的风味标签
    """
    try:
        from app.utils.flavor_recommender import FlavorRecommender
        
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return format_response(404, "食谱不存在")
        
        recommender = FlavorRecommender()
        profile = recommender.get_flavor_profile(recipe)
        
        return format_response(data={
            "recipe_id": recipe_id,
            "flavor_tags": profile['tags'],
            "flavor_vector": profile['vector']
        })
        
    except Exception as e:
        logger.error(f"获取风味标签失败：{str(e)}")
        return format_response(500, f"服务器内部错误：{str(e)}")


@recommend_bp.route("/hybrid-recommend", methods=["POST"])
@login_required
def hybrid_recommend():
    """
    混合推荐（风味+内容+行为）
    """
    try:
        from app.utils.flavor_recommender import FlavorRecommender
        
        data = request.get_json() or {}
        
        user = User.query.get(g.user_id)
        if not user:
            return format_response(404, "用户不存在")
        
        recipes = Recipe.get_all()
        
        if not recipes:
            return format_response(200, data={"recommend_list": [], "total": 0})
        
        recommender = FlavorRecommender()
        recommended = recommender.hybrid_recommend(user, recipes, top_k=8)
        
        recommend_list = [r.to_dict() for r in recommended]
        
        return format_response(data={
            "recommend_list": recommend_list,
            "total": len(recommend_list),
            "algorithm": "hybrid_flavor"
        })
        
    except Exception as e:
        logger.error(f"混合推荐失败：{str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return format_response(500, f"服务器内部错误：{str(e)}")


@recommend_bp.route("/ai-recipe", methods=["POST"])
@login_required
def ai_recommend_recipe():
    """
    AI智能食谱推荐（使用GLM-5.1模型）
    1. 获取用户健康信息
    2. 可选：获取冰箱食材
    3. 调用智谱AI生成个性化食谱
    """
    try:
        data = request.get_json() or {}
        use_fridge = data.get("use_fridge", False)
        
        user = User.query.get(g.user_id)
        if not user:
            return format_response(404, "用户不存在")
        
        # 构建用户信息
        user_profile = {
            "age": user.age,
            "height": user.height,
            "weight": user.weight,
            "health_goal": user.health_goal or "维持健康",
            "dietary_preference": user.dietary_preference or "清淡",
            "target_calorie": user.target_calorie or 2000
        }
        
        # 获取冰箱食材（如果需要）
        fridge_ingredients = []
        if use_fridge:
            from app.models.user_ingredient import UserIngredient
            user_ingredients = UserIngredient.query.filter_by(user_id=user.id).all()
            fridge_ingredients = [ui.ingre_name for ui in user_ingredients]
        
        logger.info(f"AI食谱推荐请求：用户={user.id}, 冰箱食材={len(fridge_ingredients)}个")
        
        # 调用智谱AI生成推荐
        client = get_zhipuai_client()
        result = client.generate_recipe_recommendation(user_profile, fridge_ingredients)
        
        return format_response(data={
            "recommendations": result.get("recommendations", []),
            "user_profile": user_profile,
            "fridge_ingredients": fridge_ingredients,
            "source": "zhipu_ai"
        })
        
    except Exception as e:
        logger.error(f"AI食谱推荐失败：{str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return format_response(500, f"服务器内部错误：{str(e)}")


