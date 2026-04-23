from app import db
from datetime import datetime
from loguru import logger

class HotFood(db.Model):
    """热点美食模型"""
    __tablename__ = "hot_food"
    __table_args__ = (
        db.Index('idx_hot_score', 'hot_score'),
        db.Index('idx_food_type', 'food_type'),
        {"comment": "小红书热点美食表"}
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="ID")
    food_name = db.Column(db.String(100), nullable=False, comment="美食名称")
    ingre_list = db.Column(db.String(500), default="", comment="食材组成")
    link = db.Column(db.String(255), nullable=False, comment="小红书链接")
    hot_score = db.Column(db.Integer, default=0, comment="热度值")
    source = db.Column(db.String(50), default="小红书", comment="来源")
    tags = db.Column(db.Text, default="", comment="标签")
    image = db.Column(db.String(255), default="", comment="图片链接")
    description = db.Column(db.String(500), default="", comment="描述")
    comments = db.Column(db.Integer, default=0, comment="评论数")
    collection = db.Column(db.Integer, default=0, comment="收藏数")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="爬取时间")
    
    # 图片识别新增字段
    image_description = db.Column(db.String(200), default="", comment="AI识别的图片描述")
    food_type = db.Column(db.String(50), default="其他", comment="美食分类（主食/菜式/水果/零食/饮品等）")
    cuisine = db.Column(db.String(50), default="", comment="菜系（中式/西式/日式/韩式/泰式等）")
    ingredients = db.Column(db.Text, default="", comment="识别出的食材列表（JSON格式）")
    nutrition = db.Column(db.Text, default="", comment="营养信息估算（JSON格式）")
    is_healthy = db.Column(db.Boolean, default=True, comment="是否健康")
    health_rating = db.Column(db.Integer, default=3, comment="健康评分 1-5")
    
    def to_dict(self):
        """转换为字典"""
        import json
        result = {
            "id": self.id,
            "title": self.food_name,  # 前端使用的字段名
            "desc": self.ingre_list,  # 前端使用的字段名
            "likes": self.hot_score,  # 前端使用的字段名
            "source": self.source,
            "link": self.link,
            "tags": json.loads(self.tags) if self.tags else [],
            "image": self.image,
            "description": self.description,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "comments": self.comments,
            "collection": self.collection,
            "image_description": self.image_description,
            "food_type": self.food_type,
            "cuisine": self.cuisine,
            "is_healthy": self.is_healthy,
            "health_rating": self.health_rating
        }
        
        # 解析 JSON 字段
        if self.ingredients:
            try:
                result["ingredients"] = json.loads(self.ingredients)
            except Exception:
                result["ingredients"] = []
        else:
            result["ingredients"] = []
        
        if self.nutrition:
            try:
                result["nutrition"] = json.loads(self.nutrition)
            except Exception:
                result["nutrition"] = None
        else:
            result["nutrition"] = None
        
        return result
    
    @classmethod
    def get_hot_list(cls, limit=20):
        """获取热点美食列表（按热度排序）"""
        return cls.query.order_by(cls.hot_score.desc()).limit(limit).all()
    
    def save(self):
        """保存热点美食"""
        try:
            db.session.add(self)
            db.session.commit()
            logger.info(f"热点美食{self.food_name}保存成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"热点美食保存失败：{str(e)}")
            return False
