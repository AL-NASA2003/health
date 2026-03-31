from flask import Blueprint, g, request
from app.models.ingredient import Ingredient
from app.utils.common import validate_params, format_response
# from app.utils.common_util import validate_params, format_response
from loguru import logger

# 创建蓝图
ingredient_bp = Blueprint("ingredient", __name__)

from app.utils.auth_decorator import login_required

@ingredient_bp.route("/search", methods=["GET"])
@login_required
def search_ingredient():
    """搜索食材
    请求参数：keyword (关键词，为空时返回所有食材)
    """

    
    keyword = request.args.get("keyword", "")
    
    if keyword:
        ingredients = Ingredient.search_by_name(keyword)
    else:
        # 关键词为空时返回所有食材
        ingredients = Ingredient.query.all()
    
    ingredients_dict = [i.to_dict() for i in ingredients]
    
    return format_response(data={
        "total": len(ingredients_dict),
        "list": ingredients_dict
    })

@ingredient_bp.route("", methods=["POST"])
@login_required
def add_ingredient():
    """添加食材
    请求参数：ingre_name, calorie, protein, carb, fat, category, stock, expire_date
    """

    
    required_params = ["ingre_name", "calorie", "protein", "carb", "fat"]
    valid, params = validate_params(required_params)
    if not valid:
        return format_response(**params)
    
    # 转换日期格式
    expire_date = None
    if "expire_date" in params:
        from datetime import datetime
        try:
            expire_date = datetime.strptime(params["expire_date"], "%Y-%m-%d").date()
        except Exception as e:
            logger.error(f"日期格式错误：{str(e)}")
            return format_response(400, "日期格式错误，应为YYYY-MM-DD")
    
    # 创建食材
    ingredient = Ingredient(
        ingre_name=params["ingre_name"],
        calorie=params["calorie"],
        protein=params["protein"],
        carb=params["carb"],
        fat=params["fat"],
        category=params.get("category", ""),
        stock=params.get("stock", 0.0),
        expire_date=expire_date
    )
    
    if ingredient.save():
        return format_response(msg="食材添加成功", data=ingredient.to_dict())
    else:
        return format_response(500, "食材添加失败")

@ingredient_bp.route("/<int:ingre_id>", methods=["PUT"])
@login_required
def update_ingredient(ingre_id):
    """更新食材信息"""

    
    ingredient = Ingredient.query.get(ingre_id)
    if not ingredient:
        return format_response(404, "食材不存在")
    
    params = request.get_json() or {}
    
    # 更新字段
    if "ingre_name" in params:
        ingredient.ingre_name = params["ingre_name"]
    if "calorie" in params:
        ingredient.calorie = params["calorie"]
    if "protein" in params:
        ingredient.protein = params["protein"]
    if "carb" in params:
        ingredient.carb = params["carb"]
    if "fat" in params:
        ingredient.fat = params["fat"]
    if "category" in params:
        ingredient.category = params["category"]
    if "stock" in params:
        ingredient.stock = params["stock"]
    if "expire_date" in params:
        from datetime import datetime
        try:
            ingredient.expire_date = datetime.strptime(params["expire_date"], "%Y-%m-%d").date()
        except Exception as e:
            logger.error(f"日期格式错误：{str(e)}")
            return format_response(400, "日期格式错误，应为YYYY-MM-DD")
    
    if ingredient.save():
        return format_response(msg="食材更新成功", data=ingredient.to_dict())
    else:
        return format_response(500, "食材更新失败")