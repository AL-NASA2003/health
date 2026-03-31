from app import db
from datetime import datetime
from loguru import logger

class UserIngredient(db.Model):
    """用户食材模型"""
    __tablename__ = "user_ingredient"
    __table_args__ = {"comment": "用户食材表"}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="ID")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, comment="用户ID")
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredient.id"), nullable=False, comment="食材ID")
    weight = db.Column(db.Float, default=0.0, comment="库存重量")
    unit = db.Column(db.String(20), default="g", comment="单位")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    def to_dict(self):
        """转换为字典，用于接口返回"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "ingredient_id": self.ingredient_id,
            "weight": self.weight,
            "unit": self.unit,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @classmethod
    def get_by_user(cls, user_id):
        """根据用户ID查询食材列表"""
        return cls.query.filter_by(user_id=user_id).all()
    
    @classmethod
    def get_by_user_and_ingredient(cls, user_id, ingredient_id):
        """根据用户ID和食材ID查询"""
        return cls.query.filter_by(user_id=user_id, ingredient_id=ingredient_id).first()
    
    def save(self):
        """保存用户食材"""
        try:
            db.session.add(self)
            db.session.commit()
            logger.info(f"用户食材{self.id}保存成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"用户食材保存失败：{str(e)}")
            return False
    
    def update(self):
        """更新用户食材"""
        try:
            db.session.commit()
            logger.info(f"用户食材{self.id}更新成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"用户食材更新失败：{str(e)}")
            return False
    
    def delete(self):
        """删除用户食材"""
        try:
            db.session.delete(self)
            db.session.commit()
            logger.info(f"用户食材{self.id}删除成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"用户食材删除失败：{str(e)}")
            return False
