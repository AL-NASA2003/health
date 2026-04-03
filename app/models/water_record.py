from app import db
from datetime import datetime
from loguru import logger

class WaterRecord(db.Model):
    """饮水记录模型"""
    __tablename__ = "water_record"
    __table_args__ = (
        db.Index('idx_user_id_water', 'user_id'),
        db.Index('idx_create_time_water', 'create_time'),
        {"comment": "饮水记录表"}
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="记录ID")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, comment="用户ID")
    amount = db.Column(db.Integer, nullable=False, comment="饮水量(ml)")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        """转换为字典，用于接口返回"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": self.amount,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @classmethod
    def get_by_user_and_date(cls, user_id, date):
        """根据用户ID和日期查询饮水记录"""
        start_date = date
        end_date = date.replace(hour=23, minute=59, second=59)
        return cls.query.filter(
            cls.user_id == user_id,
            cls.create_time >= start_date,
            cls.create_time <= end_date
        ).order_by(cls.create_time.desc()).all()
    
    @classmethod
    def get_by_user(cls, user_id, limit=100):
        """根据用户ID查询饮水记录"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.create_time.desc()).limit(limit).all()
    
    def save(self):
        """保存饮水记录"""
        try:
            db.session.add(self)
            db.session.commit()
            logger.info(f"饮水记录{self.id}保存成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"饮水记录保存失败：{str(e)}")
            return False
    
    def update(self):
        """更新饮水记录"""
        try:
            db.session.commit()
            logger.info(f"饮水记录{self.id}更新成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"饮水记录更新失败：{str(e)}")
            return False
    
    def delete(self):
        """删除饮水记录"""
        try:
            db.session.delete(self)
            db.session.commit()
            logger.info(f"饮水记录{self.id}删除成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"饮水记录删除失败：{str(e)}")
            return False
