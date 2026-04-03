from flask import g, request
from app.models.water_record import WaterRecord
from app.utils.common import validate_params, format_response
from loguru import logger
from flask_restx import Namespace, Resource, fields

# 创建命名空间
water_ns = Namespace('water', description='饮水记录相关操作')

# 定义请求模型
water_record_model = water_ns.model('WaterRecord', {
    'amount': fields.Integer(required=True, description='饮水量(ml)')
})

# 定义响应模型
water_response_model = water_ns.model('WaterResponse', {
    'id': fields.Integer(description='记录ID'),
    'user_id': fields.Integer(description='用户ID'),
    'amount': fields.Integer(description='饮水量(ml)'),
    'create_time': fields.String(description='创建时间')
})

# 导入Token验证装饰器
from app.utils.auth_decorator import login_required

@water_ns.route('/record')
class WaterRecordResource(Resource):
    """饮水记录管理"""
    @login_required
    @water_ns.expect(water_record_model)
    def post(self):
        """添加饮水记录
        请求参数：amount
        """
        # 验证参数
        required_params = ["amount"]
        valid, params = validate_params(required_params)
        if not valid:
            return format_response(**params)
        
        # 创建饮水记录
        from datetime import datetime
        record = WaterRecord(
            user_id=g.user_id,
            amount=params["amount"]
        )
        
        if record.save():
            return format_response(msg="记录添加成功", data=record.to_dict())
        else:
            return format_response(500, "记录添加失败")
    
    @login_required
    def get(self):
        """获取饮水记录
        请求参数：date (可选，格式：YYYY-MM-DD)
        """
        date_str = request.args.get("date")
        
        # 转换日期格式
        from datetime import datetime
        try:
            if date_str:
                date = datetime.strptime(date_str, "%Y-%m-%d")
                records = WaterRecord.get_by_user_and_date(g.user_id, date)
            else:
                records = WaterRecord.get_by_user(g.user_id)
        except Exception as e:
            logger.error(f"日期格式错误：{str(e)}")
            return format_response(400, "日期格式错误，应为YYYY-MM-DD")
        
        records_dict = [r.to_dict() for r in records]
        
        return format_response(data={
            "total": len(records_dict),
            "list": records_dict
        })

@water_ns.route('/record/<int:record_id>')
class WaterRecordDetailResource(Resource):
    """饮水记录详情"""
    @login_required
    def delete(self, record_id):
        """删除饮水记录"""
        record = WaterRecord.query.get(record_id)
        if not record:
            return format_response(404, "记录不存在")
        
        # 验证权限
        if record.user_id != g.user_id:
            return format_response(403, "无权删除该记录")
        
        try:
            from app import db
            db.session.delete(record)
            db.session.commit()
            logger.info(f"饮水记录{record_id}删除成功")
            return format_response(msg="记录删除成功")
        except Exception as e:
            db.session.rollback()
            logger.error(f"记录删除失败：{str(e)}")
            return format_response(500, "记录删除失败")

# 命名空间将在app/__init__.py中注册
