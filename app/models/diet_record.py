from app import db
from datetime import datetime
from loguru import logger

class DietRecord(db.Model):
    """饮食记录模型"""
    __tablename__ = "diet_record"
    __table_args__ = (
        db.Index('idx_user_date', 'user_id', 'create_date'),
        db.Index('idx_user_id', 'user_id'),
        db.Index('idx_create_date', 'create_date'),
        {"comment": "饮食记录表"}
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="记录ID")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, comment="用户ID")
    food_name = db.Column(db.String(100), nullable=False, comment="食物名称")
    food_type = db.Column(db.String(20), default="", comment="食物类型")
    meal_time = db.Column(db.String(20), default="", comment="用餐时间")
    weight = db.Column(db.Float, default=0.0, comment="重量")
    unit = db.Column(db.String(10), default="g", comment="计量单位")
    calorie = db.Column(db.Float, default=0.0, comment="热量(大卡)")
    protein = db.Column(db.Float, default=0.0, comment="蛋白质(g)")
    carb = db.Column(db.Float, default=0.0, comment="碳水化合物(g)")
    fat = db.Column(db.Float, default=0.0, comment="脂肪(g)")
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), default=0, comment="关联食谱ID")
    image = db.Column(db.String(255), default="", comment="食物图片")
    notes = db.Column(db.Text, default="", comment="备注")
    create_date = db.Column(db.Date, nullable=False, comment="记录日期")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        """转换为字典，用于接口返回"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "food_name": self.food_name,
            "food_type": self.food_type,
            "meal_time": self.meal_time,
            "weight": self.weight,
            "unit": self.unit,
            "calorie": self.calorie,
            "protein": self.protein,
            "carb": self.carb,
            "fat": self.fat,
            "recipe_id": self.recipe_id,
            "image": self.image,
            "notes": self.notes,
            "create_date": self.create_date.strftime("%Y-%m-%d") if self.create_date else "",
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @classmethod
    def get_by_user_and_date(cls, user_id, start_date, end_date):
        """根据用户ID和日期范围查询饮食记录"""
        return cls.query.filter(
            cls.user_id == user_id,
            cls.create_date >= start_date,
            cls.create_date <= end_date
        ).order_by(cls.create_time.desc()).all()
    
    @classmethod
    def get_by_user(cls, user_id, limit=100):
        """根据用户ID查询饮食记录"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.create_time.desc()).limit(limit).all()
    
    def save(self):
        """保存饮食记录"""
        try:
            db.session.add(self)
            db.session.commit()
            logger.info(f"饮食记录{self.id}保存成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"饮食记录保存失败：{str(e)}")
            return False
    
    def update(self):
        """更新饮食记录"""
        try:
            db.session.commit()
            logger.info(f"饮食记录{self.id}更新成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"饮食记录更新失败：{str(e)}")
            return False
    
    def delete(self):
        """删除饮食记录"""
        try:
            db.session.delete(self)
            db.session.commit()
            logger.info(f"饮食记录{self.id}删除成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"饮食记录删除失败：{str(e)}")
            return False
    
    @classmethod
    def batch_save(cls, records):
        """批量保存饮食记录
        
        Args:
            records: 饮食记录对象列表
            
        Returns:
            bool: 保存成功返回True，失败返回False
        """
        try:
            for record in records:
                db.session.add(record)
            db.session.commit()
            logger.info(f"批量保存饮食记录成功，共{len(records)}条")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"批量保存饮食记录失败：{str(e)}")
            return False
