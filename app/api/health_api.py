from flask import g, request
from app.models.health_index_record import HealthIndexRecord
from app.models.user_goal import UserGoal
from app.utils.common import validate_params, format_response
from loguru import logger
from flask_restx import Namespace, Resource, fields

# 创建命名空间
health_ns = Namespace('health', description='健康相关操作')

# 定义请求模型
health_index_model = health_ns.model('HealthIndex', {
    'height': fields.Float(required=True, description='身高(cm)'),
    'weight': fields.Float(required=True, description='体重(kg)'),
    'age': fields.Integer(required=True, description='年龄'),
    'gender': fields.Integer(required=True, description='性别(1男, 0女)'),
    'bmi': fields.Float(required=True, description='BMI指数'),
    'bmi_status': fields.String(required=True, description='BMI状态'),
    'bmr': fields.Integer(required=True, description='基础代谢率'),
    'ideal_weight': fields.String(required=True, description='理想体重'),
    'daily_calories': fields.Integer(required=True, description='每日推荐热量'),
    'health_score': fields.Integer(required=True, description='健康分数')
})

user_goal_model = health_ns.model('UserGoal', {
    'daily_calorie_goal': fields.Integer(required=True, description='每日热量目标'),
    'daily_water_goal': fields.Integer(required=True, description='每日饮水目标'),
    'daily_exercise_goal': fields.Integer(required=True, description='每日运动目标'),
    'health_goal': fields.String(required=True, description='健康目标'),
    'dietary_preference': fields.String(required=True, description='饮食偏好')
})

# 导入Token验证装饰器
from app.utils.auth_decorator import login_required

@health_ns.route('/index/record')
class HealthIndexRecordResource(Resource):
    """健康指数记录管理"""
    @login_required
    @health_ns.expect(health_index_model)
    def post(self):
        """添加健康指数记录"""
        # 验证参数
        required_params = ["height", "weight", "age", "gender", "bmi", "bmi_status", "bmr", "ideal_weight", "daily_calories", "health_score"]
        valid, params = validate_params(required_params)
        if not valid:
            return format_response(**params)
        
        # 创建健康指数记录
        record = HealthIndexRecord(
            user_id=g.user_id,
            height=params["height"],
            weight=params["weight"],
            age=params["age"],
            gender=params["gender"],
            bmi=params["bmi"],
            bmi_status=params["bmi_status"],
            bmr=params["bmr"],
            ideal_weight=params["ideal_weight"],
            daily_calories=params["daily_calories"],
            health_score=params["health_score"]
        )
        
        if record.save():
            return format_response(msg="记录添加成功", data=record.to_dict())
        else:
            return format_response(500, "记录添加失败")
    
    @login_required
    def get(self):
        """获取健康指数记录列表"""
        limit = int(request.args.get("limit", 10))
        records = HealthIndexRecord.get_by_user(g.user_id, limit=limit)
        records_dict = [r.to_dict() for r in records]
        
        return format_response(data={
            "total": len(records_dict),
            "list": records_dict
        })

@health_ns.route('/index/latest')
class HealthIndexLatestResource(Resource):
    """获取最新健康指数记录"""
    @login_required
    def get(self):
        """获取用户最新的健康指数记录"""
        record = HealthIndexRecord.get_latest_by_user(g.user_id)
        if record:
            return format_response(data=record.to_dict())
        else:
            return format_response(404, "暂无健康指数记录")

@health_ns.route('/goal')
class UserGoalResource(Resource):
    """用户目标管理"""
    @login_required
    @health_ns.expect(user_goal_model)
    def post(self):
        """设置用户目标"""
        # 验证参数
        required_params = ["daily_calorie_goal", "daily_water_goal", "daily_exercise_goal", "health_goal", "dietary_preference"]
        valid, params = validate_params(required_params)
        if not valid:
            return format_response(**params)
        
        # 检查用户目标是否已存在
        existing_goal = UserGoal.get_by_user(g.user_id)
        if existing_goal:
            # 更新现有目标
            existing_goal.daily_calorie_goal = params["daily_calorie_goal"]
            existing_goal.daily_water_goal = params["daily_water_goal"]
            existing_goal.daily_exercise_goal = params["daily_exercise_goal"]
            existing_goal.health_goal = params["health_goal"]
            existing_goal.dietary_preference = params["dietary_preference"]
            
            if existing_goal.update():
                return format_response(msg="目标更新成功", data=existing_goal.to_dict())
            else:
                return format_response(500, "目标更新失败")
        else:
            # 创建新目标
            goal = UserGoal(
                user_id=g.user_id,
                daily_calorie_goal=params["daily_calorie_goal"],
                daily_water_goal=params["daily_water_goal"],
                daily_exercise_goal=params["daily_exercise_goal"],
                health_goal=params["health_goal"],
                dietary_preference=params["dietary_preference"]
            )
            
            if goal.save():
                return format_response(msg="目标设置成功", data=goal.to_dict())
            else:
                return format_response(500, "目标设置失败")
    
    @login_required
    def get(self):
        """获取用户目标"""
        goal = UserGoal.get_by_user(g.user_id)
        if goal:
            return format_response(data=goal.to_dict())
        else:
            return format_response(404, "暂无用户目标")

@health_ns.route('/stat')
class DietStatRecordResource(Resource):
    """饮食统计记录管理"""
    @login_required
    def post(self):
        """添加饮食统计记录"""
        # 验证参数
        required_params = ["record_date", "total_calories", "total_protein", "total_carb", "total_fat", "total_water", "total_exercise_duration", "total_exercise_calories", "net_calories"]
        valid, params = validate_params(required_params)
        if not valid:
            return format_response(**params)
        
        # 转换日期格式
        from datetime import datetime
        try:
            record_date = datetime.strptime(params["record_date"], "%Y-%m-%d").date()
        except Exception as e:
            logger.error(f"日期格式错误：{str(e)}")
            return format_response(400, "日期格式错误，应为YYYY-MM-DD")
        
        # 检查记录是否已存在
        existing_record = DietStatRecord.get_by_user_and_date(g.user_id, record_date)
        if existing_record:
            # 更新现有记录
            existing_record.total_calories = params["total_calories"]
            existing_record.total_protein = params["total_protein"]
            existing_record.total_carb = params["total_carb"]
            existing_record.total_fat = params["total_fat"]
            existing_record.total_water = params["total_water"]
            existing_record.total_exercise_duration = params["total_exercise_duration"]
            existing_record.total_exercise_calories = params["total_exercise_calories"]
            existing_record.net_calories = params["net_calories"]
            
            if existing_record.update():
                return format_response(msg="记录更新成功", data=existing_record.to_dict())
            else:
                return format_response(500, "记录更新失败")
        else:
            # 创建新记录
            from app.models.diet_stat_record import DietStatRecord
            record = DietStatRecord(
                user_id=g.user_id,
                record_date=record_date,
                total_calories=params["total_calories"],
                total_protein=params["total_protein"],
                total_carb=params["total_carb"],
                total_fat=params["total_fat"],
                total_water=params["total_water"],
                total_exercise_duration=params["total_exercise_duration"],
                total_exercise_calories=params["total_exercise_calories"],
                net_calories=params["net_calories"]
            )
            
            if record.save():
                return format_response(msg="记录添加成功", data=record.to_dict())
            else:
                return format_response(500, "记录添加失败")
    
    @login_required
    def get(self):
        """获取饮食统计记录列表"""
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        limit = int(request.args.get("limit", 10))
        
        # 转换日期格式
        from datetime import datetime
        start_date_obj = None
        end_date_obj = None
        
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            except Exception as e:
                logger.error(f"日期格式错误：{str(e)}")
                return format_response(400, "开始日期格式错误，应为YYYY-MM-DD")
        
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            except Exception as e:
                logger.error(f"日期格式错误：{str(e)}")
                return format_response(400, "结束日期格式错误，应为YYYY-MM-DD")
        
        records = DietStatRecord.get_by_user(g.user_id, start_date=start_date_obj, end_date=end_date_obj, limit=limit)
        records_dict = [r.to_dict() for r in records]
        
        return format_response(data={
            "total": len(records_dict),
            "list": records_dict
        })

@health_ns.route('/stat/<date>')
class DietStatRecordDetailResource(Resource):
    """获取指定日期的饮食统计记录"""
    @login_required
    def get(self, date):
        """获取指定日期的饮食统计记录"""
        # 转换日期格式
        from datetime import datetime
        try:
            record_date = datetime.strptime(date, "%Y-%m-%d").date()
        except Exception as e:
            logger.error(f"日期格式错误：{str(e)}")
            return format_response(400, "日期格式错误，应为YYYY-MM-DD")
        
        record = DietStatRecord.get_by_user_and_date(g.user_id, record_date)
        if record:
            return format_response(data=record.to_dict())
        else:
            return format_response(404, "暂无饮食统计记录")

# 命名空间将在app/__init__.py中注册
