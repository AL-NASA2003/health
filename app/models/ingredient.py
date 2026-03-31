from app import db
from loguru import logger

class Ingredient(db.Model):
    """食材信息模型"""
    __tablename__ = "ingredient"
    __table_args__ = {"comment": "食材信息表"}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="食材ID")
    ingre_name = db.Column(db.String(100), nullable=False, comment="食材名称")
    calorie = db.Column(db.Float, nullable=False, comment="每100g热量(大卡)")
    protein = db.Column(db.Float, nullable=False, comment="每100g蛋白质(g)")
    carb = db.Column(db.Float, nullable=False, comment="每100g碳水(g)")
    fat = db.Column(db.Float, nullable=False, comment="每100g脂肪(g)")
    category = db.Column(db.String(50), default="", comment="食材分类：蔬菜/肉类/水果等")
    stock = db.Column(db.Float, default=0.0, comment="全局库存(g)")
    unit = db.Column(db.String(20), default="g", comment="单位")
    image = db.Column(db.String(255), default="", comment="食材图片")
    expire_date = db.Column(db.Date, nullable=True, comment="保质期")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "ingre_name": self.ingre_name,
            "calorie": self.calorie,
            "protein": self.protein,
            "carb": self.carb,
            "fat": self.fat,
            "category": self.category,
            "stock": self.stock,
            "unit": self.unit,
            "image": self.image,
            "expire_date": self.expire_date.strftime("%Y-%m-%d") if self.expire_date else ""
        }
    
    @classmethod
    def search_by_name(cls, keyword):
        """模糊搜索食材"""
        return cls.query.filter(cls.ingre_name.like(f"%{keyword}%")).limit(20).all()
    
    def save(self):
        """保存食材信息"""
        try:
            db.session.add(self)
            db.session.commit()
            logger.info(f"食材{self.ingre_name}保存成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"食材保存失败：{str(e)}")
            return False