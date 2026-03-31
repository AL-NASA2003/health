from flask import Blueprint, g, request
from app.utils.common import format_response
from app.utils.auth_decorator import login_required
from app.utils.zhipuai_client import get_zhipuai_client
from app.utils.ai_fallback_manager import get_ai_fallback_manager
from app.models.user import User
from app.models.recipe import Recipe
from loguru import logger

ai_assistant_bp = Blueprint("ai_assistant", __name__)

@ai_assistant_bp.route("/chat", methods=["POST"])
@login_required
def ai_chat():
    """
    AI对话接口 - 带降级策略
    """
    try:
        data = request.get_json() or {}
        messages = data.get("messages", [])
        
        if not messages:
            return format_response(400, "请提供对话内容")
        
        fallback_manager = get_ai_fallback_manager()
        
        try:
            client = get_zhipuai_client()
            response = client.chat(messages)
            return format_response(data={"response": response, "source": "ai"})
        except Exception as ai_err:
            logger.warning(f"AI对话失败，使用降级响应: {ai_err}")
            fallback_response = fallback_manager.get_fallback_chat_response(messages)
            return format_response(data={"response": fallback_response, "source": "fallback"})
        
    except Exception as e:
        logger.error(f"AI对话失败：{str(e)}")
        return format_response(500, f"对话失败：{str(e)}")

@ai_assistant_bp.route("/recipe-recommend", methods=["POST"])
@login_required
def ai_recipe_recommend():
    """
    AI个性化食谱推荐 - 带降级策略
    """
    try:
        user = User.query.get(g.user_id)
        if not user:
            return format_response(404, "用户不存在")
        
        recipes = Recipe.get_all()
        if not recipes:
            return format_response(200, data={"recommendations": [], "source": "no_data"})
        
        fallback_manager = get_ai_fallback_manager()
        
        try:
            logger.info("尝试使用AI推荐食谱")
            client = get_zhipuai_client()
            
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
            
            recommendation = client.generate_recipe_recommendation(user_profile, recipe_list)
            
            if recommendation and "模拟" not in recommendation:
                logger.info("AI推荐成功")
                return format_response(data={"recommendation": recommendation, "source": "ai"})
            else:
                raise Exception("AI返回模拟响应")
                
        except Exception as ai_err:
            logger.warning(f"AI推荐失败，降级到本地算法: {ai_err}")
            recommendation_text, recommend_list = fallback_manager.get_fallback_recipe_recommendation(user, recipes)
            return format_response(data={
                "recommendation": recommendation_text,
                "recommend_list": recommend_list,
                "source": "local_algorithm"
            })
        
    except Exception as e:
        logger.error(f"AI食谱推荐失败：{str(e)}")
        return format_response(500, f"推荐失败：{str(e)}")

@ai_assistant_bp.route("/generate-handbook", methods=["POST"])
@login_required
def ai_generate_handbook():
    """
    AI生成手账内容 - 带降级策略
    """
    try:
        data = request.get_json() or {}
        topic = data.get("topic", "今天的饮食")
        mood = data.get("mood", "开心")
        
        fallback_manager = get_ai_fallback_manager()
        
        try:
            logger.info("尝试使用AI生成手账")
            client = get_zhipuai_client()
            content = client.generate_handbook_content(topic, mood)
            
            if content and "模拟" not in content:
                logger.info("AI生成手账成功")
                return format_response(data={"content": content, "source": "ai"})
            else:
                raise Exception("AI返回模拟响应")
                
        except Exception as ai_err:
            logger.warning(f"AI生成手账失败，使用降级内容: {ai_err}")
            fallback_content = fallback_manager.get_fallback_handbook_content(topic, mood)
            return format_response(data={"content": fallback_content, "source": "fallback"})
        
    except Exception as e:
        logger.error(f"AI生成手账失败：{str(e)}")
        return format_response(500, f"生成失败：{str(e)}")

@ai_assistant_bp.route("/analyze-food", methods=["POST"])
@login_required
def ai_analyze_food():
    """
    AI分析食物营养 - 带降级策略
    """
    try:
        data = request.get_json() or {}
        food_name = data.get("food_name", "")
        
        if not food_name:
            return format_response(400, "请提供食物名称")
        
        fallback_manager = get_ai_fallback_manager()
        
        try:
            logger.info(f"尝试使用AI分析食物: {food_name}")
            client = get_zhipuai_client()
            analysis = client.analyze_nutrition(food_name)
            
            if analysis and "模拟" not in analysis:
                logger.info("AI分析食物成功")
                return format_response(data={"analysis": analysis, "source": "ai"})
            else:
                raise Exception("AI返回模拟响应")
                
        except Exception as ai_err:
            logger.warning(f"AI分析食物失败，使用降级分析: {ai_err}")
            fallback_analysis = fallback_manager.get_fallback_food_analysis(food_name)
            return format_response(data={"analysis": fallback_analysis, "source": "fallback"})
        
    except Exception as e:
        logger.error(f"AI分析食物失败：{str(e)}")
        return format_response(500, f"分析失败：{str(e)}")
