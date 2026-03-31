from flask import Blueprint, g, request
from app.models.user import User
from app.utils.nutrition_needs_calculator import NutritionNeedsCalculator
from app.utils.common import format_response
from app.utils.auth_decorator import login_required
from loguru import logger

nutrition_bp = Blueprint("nutrition", __name__)

@nutrition_bp.route("/calculate", methods=["POST"])
@login_required
def calculate_nutrition_needs():
    """
    计算用户的营养需求
    
    请求参数：
        - (可选) 更新用户信息的健康数据
    """
    try:
        user = User.query.get(g.user_id)
        if not user:
            return format_response(404, "用户不存在")
        
        data = request.get_json() or {}
        
        if data:
            if "height" in data:
                user.height = float(data.get("height"))
            if "weight" in data:
                user.weight = float(data.get("weight"))
            if "age" in data:
                user.age = int(data.get("age"))
            if "gender" in data:
                user.gender = int(data.get("gender"))
            if "health_goal" in data:
                user.health_goal = data.get("health_goal")
            if "activity_level" in data:
                user.activity_level = int(data.get("activity_level"))
            if "target_weight" in data:
                user.target_weight = float(data.get("target_weight"))
            user.save()
        
        nutrition_data = NutritionNeedsCalculator.calculate_all(user)
        
        if not user.target_calorie or user.target_calorie == 0:
            user.target_calorie = nutrition_data["target_calorie"]
            user.target_protein = nutrition_data["target_protein"]
            user.target_carb = nutrition_data["target_carb"]
            user.target_fat = nutrition_data["target_fat"]
            user.save()
        
        return format_response(data={
            "nutrition_needs": nutrition_data,
            "user_info": user.to_dict()
        })
        
    except Exception as e:
        logger.error(f"计算营养需求失败：{str(e)}")
        return format_response(500, f"计算失败：{str(e)}")

@nutrition_bp.route("/update-targets", methods=["POST"])
@login_required
def update_nutrition_targets():
    """
    更新用户的营养目标（自定义）
    """
    try:
        user = User.query.get(g.user_id)
        if not user:
            return format_response(404, "用户不存在")
        
        data = request.get_json() or {}
        
        if "target_calorie" in data:
            user.target_calorie = float(data.get("target_calorie"))
        if "target_protein" in data:
            user.target_protein = float(data.get("target_protein"))
        if "target_carb" in data:
            user.target_carb = float(data.get("target_carb"))
        if "target_fat" in data:
            user.target_fat = float(data.get("target_fat"))
        
        user.save()
        
        return format_response(data={"user_info": user.to_dict()}, msg="目标更新成功")
        
    except Exception as e:
        logger.error(f"更新营养目标失败：{str(e)}")
        return format_response(500, f"更新失败：{str(e)}")
