from app import db
from datetime import datetime
from loguru import logger

class HotFood(db.Model):
    """热点美食模型"""
    __tablename__ = "hot_food"
    __table_args__ = (
        db.Index('idx_hot_score', 'hot_score'),
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
    
    def to_dict(self):
        """转换为字典"""
        import json
        return {
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
            "collection": self.collection
        }
    
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
