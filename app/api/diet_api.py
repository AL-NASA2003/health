from flask import g, request
from app.models.diet_record import DietRecord
from app.models.ingredient import Ingredient
from app.models.user_ingredient import UserIngredient
from app.utils.common import validate_params, format_response, calculate_nutrition
from loguru import logger
from flask_restx import Namespace, Resource, fields

# 创建命名空间
diet_ns = Namespace('diet', description='饮食记录相关操作')

# 定义请求模型
diet_record_model = diet_ns.model('DietRecord', {
    'food_name': fields.String(required=True, description='食物名称'),
    'food_type': fields.String(required=True, description='食物类型'),
    'meal_time': fields.String(required=True, description='用餐时间'),
    'weight': fields.Float(required=True, description='重量'),
    'ingredient_id': fields.Integer(description='食材ID')
})

# 定义响应模型
diet_response_model = diet_ns.model('DietResponse', {
    'id': fields.Integer(description='记录ID'),
    'user_id': fields.Integer(description='用户ID'),
    'food_name': fields.String(description='食物名称'),
    'food_type': fields.String(description='食物类型'),
    'meal_time': fields.String(description='用餐时间'),
    'weight': fields.Float(description='重量'),
    'unit': fields.String(description='计量单位'),
    'calorie': fields.Float(description='热量(大卡)'),
    'protein': fields.Float(description='蛋白质(g)'),
    'carb': fields.Float(description='碳水化合物(g)'),
    'fat': fields.Float(description='脂肪(g)'),
    'recipe_id': fields.Integer(description='关联食谱ID'),
    'image': fields.String(description='食物图片'),
    'notes': fields.String(description='备注'),
    'create_date': fields.String(description='记录日期'),
    'create_time': fields.String(description='创建时间')
})

# 导入Token验证装饰器
from app.utils.auth_decorator import login_required

@diet_ns.route('/record')
class DietRecordResource(Resource):
    """饮食记录管理"""
    @login_required
    @diet_ns.expect(diet_record_model)
    def post(self):
        """添加饮食记录
        请求参数：food_name, food_type, meal_time, weight, ingredient_id(可选)
        """
        # 验证参数
        required_params = ["food_name", "food_type", "meal_time", "weight"]
        valid, params = validate_params(required_params)
        if not valid:
            return format_response(**params)
        
        # 调试：打印收到的参数
        print("📝 收到添加记录请求，参数：", params)
        
        # 计算营养成分（如果传了食材ID用食材，否则根据食物类型估算）
        nutrition = {"calorie": 0, "protein": 0, "carb": 0, "fat": 0}
        
        if "ingredient_id" in params:
            ingredient = Ingredient.query.get(params["ingredient_id"])
            if ingredient:
                nutrition = calculate_nutrition(ingredient.to_dict(), params["weight"])
                print("🥗 使用食材计算营养：", nutrition)
        else:
            # 根据食物类型估算营养成分（每100g的平均含量）
            food_type_nutrition = {
                "饮品": {"calorie": 40, "protein": 1, "carb": 9, "fat": 0},
                "菜式": {"calorie": 150, "protein": 8, "carb": 15, "fat": 7},
                "主食": {"calorie": 120, "protein": 4, "carb": 25, "fat": 1},
                "水果": {"calorie": 50, "protein": 0.5, "carb": 12, "fat": 0.2},
                "零食": {"calorie": 200, "protein": 4, "carb": 25, "fat": 10}
            }
            
            # 获取食物类型，默认是"菜式"
            food_type = params.get("food_type", "菜式")
            base_nutrition = food_type_nutrition.get(food_type, food_type_nutrition["菜式"])
            
            # 根据重量计算实际营养成分
            weight = params.get("weight", 100)
            multiplier = weight / 100.0
            
            nutrition = {
                "calorie": round(base_nutrition["calorie"] * multiplier, 1),
                "protein": round(base_nutrition["protein"] * multiplier, 1),
                "carb": round(base_nutrition["carb"] * multiplier, 1),
                "fat": round(base_nutrition["fat"] * multiplier, 1)
            }
            
            print(f"🧮 根据食物类型 '{food_type}' 计算营养：")
            print(f"   重量：{weight}g，倍数：{multiplier}")
            print(f"   营养：{nutrition}")
        
        # 扣减库存（如果传了食材ID）
        if "ingredient_id" in params:
            user_ingredient = UserIngredient.query.filter_by(
                user_id=g.user_id,
                ingredient_id=params["ingredient_id"]
            ).first()
            
            if user_ingredient:
                if user_ingredient.weight < params["weight"]:
                    return format_response(400, "食材库存不足")
                # 扣减库存
                user_ingredient.weight -= params["weight"]
                if user_ingredient.weight <= 0:
                    from app import db
                    db.session.delete(user_ingredient)
        
        # 创建饮食记录
        from datetime import datetime
        record = DietRecord(
            user_id=g.user_id,
            food_name=params["food_name"],
            food_type=params["food_type"],
            meal_time=params["meal_time"],
            weight=params["weight"],
            calorie=nutrition["calorie"],
            protein=nutrition["protein"],
            carb=nutrition["carb"],
            fat=nutrition["fat"],
            create_date=datetime.now().date()
        )
        
        if record.save():
            return format_response(msg="记录添加成功", data=record.to_dict())
        else:
            return format_response(500, "记录添加失败")
    
    @login_required
    def get(self):
        """获取饮食记录
        请求参数：start_date, end_date (可选，格式：YYYY-MM-DD)
        """
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        
        # 转换日期格式
        from datetime import datetime
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
            end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
        except Exception as e:
            logger.error(f"日期格式错误：{str(e)}")
            return format_response(400, "日期格式错误，应为YYYY-MM-DD")
        
        # 调用正确的方法获取饮食记录
        if start_date and end_date:
            # 转换为date对象
            start_date = start_date.date()
            end_date = end_date.date()
            records = DietRecord.get_by_user_and_date(g.user_id, start_date, end_date)
        else:
            records = DietRecord.get_by_user(g.user_id)
        
        records_dict = [r.to_dict() for r in records]
        
        return format_response(data={
            "total": len(records_dict),
            "list": records_dict
        })

@diet_ns.route('/record/<int:record_id>')
class DietRecordDetailResource(Resource):
    """饮食记录详情"""
    @login_required
    def get(self, record_id):
        """获取单条饮食记录详情"""
        record = DietRecord.query.get(record_id)
        if not record:
            return format_response(404, "记录不存在")
        
        # 验证权限
        if record.user_id != g.user_id:
            return format_response(403, "无权查看该记录")
        
        return format_response(data=record.to_dict())
    
    @login_required
    @diet_ns.expect(diet_record_model)
    def put(self, record_id):
        """更新饮食记录"""
        record = DietRecord.query.get(record_id)
        if not record:
            return format_response(404, "记录不存在")
        
        # 验证权限
        if record.user_id != g.user_id:
            return format_response(403, "无权编辑该记录")
        
        # 获取参数
        params = request.json or {}
        
        # 计算营养成分（如果传了食材ID）
        nutrition = {"calorie": record.calorie, "protein": record.protein, "carb": record.carb, "fat": record.fat}
        if "ingredient_id" in params or "weight" in params:
            ingredient_id = params.get("ingredient_id")
            weight = params.get("weight", record.weight)
            
            if ingredient_id:
                ingredient = Ingredient.query.get(ingredient_id)
                if ingredient:
                    nutrition = calculate_nutrition(ingredient.to_dict(), weight)
        
        # 更新字段
        if "food_name" in params:
            record.food_name = params["food_name"]
        if "food_type" in params:
            record.food_type = params["food_type"]
        if "meal_time" in params:
            record.meal_time = params["meal_time"]
        if "weight" in params:
            record.weight = params["weight"]
        if "ingredient_id" in params:
            record.ingredient_id = params["ingredient_id"]
        
        # 更新营养成分
        record.calorie = nutrition["calorie"]
        record.protein = nutrition["protein"]
        record.carb = nutrition["carb"]
        record.fat = nutrition["fat"]
        
        if record.update():
            return format_response(msg="记录更新成功", data=record.to_dict())
        else:
            return format_response(500, "记录更新失败")
    
    @login_required
    def delete(self, record_id):
        """删除饮食记录"""
        record = DietRecord.query.get(record_id)
        if not record:
            return format_response(404, "记录不存在")
        
        # 验证权限
        if record.user_id != g.user_id:
            return format_response(403, "无权删除该记录")
        
        try:
            from app import db
            db.session.delete(record)
            db.session.commit()
            logger.info(f"饮食记录{record_id}删除成功")
            return format_response(msg="记录删除成功")
        except Exception as e:
            db.session.rollback()
            logger.error(f"记录删除失败：{str(e)}")
            return format_response(500, "记录删除失败")

# 命名空间将在app/__init__.py中注册