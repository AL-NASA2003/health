from app import db
from datetime import datetime
from loguru import logger

class HealthIndexRecord(db.Model):
    """健康指数记录模型"""
    __tablename__ = "health_index_record"
    __table_args__ = (
        db.Index('idx_user_id_health', 'user_id'),
        db.Index('idx_create_time_health', 'create_time'),
        {"comment": "健康指数记录表"}
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="记录ID")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, comment="用户ID")
    height = db.Column(db.Float, nullable=False, comment="身高(cm)")
    weight = db.Column(db.Float, nullable=False, comment="体重(kg)")
    age = db.Column(db.Integer, nullable=False, comment="年龄")
    gender = db.Column(db.Integer, nullable=False, comment="性别(1男, 0女)")
    bmi = db.Column(db.Float, nullable=False, comment="BMI指数")
    bmi_status = db.Column(db.String(20), nullable=False, comment="BMI状态")
    bmr = db.Column(db.Integer, nullable=False, comment="基础代谢率")
    ideal_weight = db.Column(db.String(20), nullable=False, comment="理想体重")
    daily_calories = db.Column(db.Integer, nullable=False, comment="每日推荐热量")
    health_score = db.Column(db.Integer, nullable=False, comment="健康分数")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        """转换为字典，用于接口返回"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "height": self.height,
            "weight": self.weight,
            "age": self.age,
            "gender": self.gender,
            "bmi": self.bmi,
            "bmi_status": self.bmi_status,
            "bmr": self.bmr,
            "ideal_weight": self.ideal_weight,
            "daily_calories": self.daily_calories,
            "health_score": self.health_score,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @classmethod
    def get_by_user(cls, user_id, limit=100):
        """根据用户ID查询健康指数记录"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.create_time.desc()).limit(limit).all()
    
    @classmethod
    def get_latest_by_user(cls, user_id):
        """获取用户最新的健康指数记录"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.create_time.desc()).first()
    
    def save(self):
        """保存健康指数记录"""
        try:
            db.session.add(self)
            db.session.commit()
            logger.info(f"健康指数记录{self.id}保存成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"健康指数记录保存失败：{str(e)}")
            return False
