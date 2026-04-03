from app import db
from datetime import datetime
from loguru import logger

class UserGoal(db.Model):
    """用户目标模型"""
    __tablename__ = "user_goal"
    __table_args__ = (
        db.Index('idx_user_id_goal', 'user_id'),
        {"comment": "用户目标表"}
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="目标ID")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True, comment="用户ID")
    daily_calorie_goal = db.Column(db.Integer, nullable=False, comment="每日热量目标")
    daily_water_goal = db.Column(db.Integer, nullable=False, comment="每日饮水目标")
    daily_exercise_goal = db.Column(db.Integer, nullable=False, comment="每日运动目标")
    health_goal = db.Column(db.String(50), nullable=False, comment="健康目标")
    dietary_preference = db.Column(db.String(50), nullable=False, comment="饮食偏好")
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    def to_dict(self):
        """转换为字典，用于接口返回"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "daily_calorie_goal": self.daily_calorie_goal,
            "daily_water_goal": self.daily_water_goal,
            "daily_exercise_goal": self.daily_exercise_goal,
            "health_goal": self.health_goal,
            "dietary_preference": self.dietary_preference,
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @classmethod
    def get_by_user(cls, user_id):
        """根据用户ID查询用户目标"""
        return cls.query.filter_by(user_id=user_id).first()
    
    def save(self):
        """保存用户目标"""
        try:
            db.session.add(self)
            db.session.commit()
            logger.info(f"用户目标{self.id}保存成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"用户目标保存失败：{str(e)}")
            return False
    
    def update(self):
        """更新用户目标"""
        try:
            self.update_time = datetime.now()
            db.session.commit()
            logger.info(f"用户目标{self.id}更新成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"用户目标更新失败：{str(e)}")
            return False
