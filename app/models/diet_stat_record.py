from app import db
from datetime import datetime, date
from loguru import logger

class DietStatRecord(db.Model):
    """饮食统计记录模型"""
    __tablename__ = "diet_stat_record"
    __table_args__ = (
        db.Index('idx_user_id_diet_stat', 'user_id'),
        db.Index('idx_record_date_diet_stat', 'record_date'),
        {"comment": "饮食统计记录表"}
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="记录ID")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, comment="用户ID")
    record_date = db.Column(db.Date, nullable=False, comment="记录日期")
    total_calories = db.Column(db.Integer, nullable=False, comment="总热量")
    total_protein = db.Column(db.Float, nullable=False, comment="总蛋白质")
    total_carb = db.Column(db.Float, nullable=False, comment="总碳水")
    total_fat = db.Column(db.Float, nullable=False, comment="总脂肪")
    total_water = db.Column(db.Integer, nullable=False, comment="总饮水量")
    total_exercise_duration = db.Column(db.Integer, nullable=False, comment="总运动时长")
    total_exercise_calories = db.Column(db.Integer, nullable=False, comment="总运动消耗热量")
    net_calories = db.Column(db.Integer, nullable=False, comment="净热量")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        """转换为字典，用于接口返回"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "record_date": self.record_date.strftime("%Y-%m-%d"),
            "total_calories": self.total_calories,
            "total_protein": self.total_protein,
            "total_carb": self.total_carb,
            "total_fat": self.total_fat,
            "total_water": self.total_water,
            "total_exercise_duration": self.total_exercise_duration,
            "total_exercise_calories": self.total_exercise_calories,
            "net_calories": self.net_calories,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @classmethod
    def get_by_user_and_date(cls, user_id, record_date):
        """根据用户ID和日期查询饮食统计记录"""
        return cls.query.filter(
            cls.user_id == user_id,
            cls.record_date == record_date
        ).first()
    
    @classmethod
    def get_by_user(cls, user_id, start_date=None, end_date=None, limit=100):
        """根据用户ID查询饮食统计记录"""
        query = cls.query.filter_by(user_id=user_id)
        if start_date:
            query = query.filter(cls.record_date >= start_date)
        if end_date:
            query = query.filter(cls.record_date <= end_date)
        return query.order_by(cls.record_date.desc()).limit(limit).all()
    
    def save(self):
        """保存饮食统计记录"""
        try:
            db.session.add(self)
            db.session.commit()
            logger.info(f"饮食统计记录{self.id}保存成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"饮食统计记录保存失败：{str(e)}")
            return False
    
    def update(self):
        """更新饮食统计记录"""
        try:
            db.session.commit()
            logger.info(f"饮食统计记录{self.id}更新成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"饮食统计记录更新失败：{str(e)}")
            return False
