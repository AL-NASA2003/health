from app import db
from datetime import datetime
from loguru import logger

class UserLike(db.Model):
    """用户点赞模型"""
    __tablename__ = "user_like"
    __table_args__ = {"comment": "用户点赞表"}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="点赞ID")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, comment="用户ID")
    hot_food_id = db.Column(db.Integer, db.ForeignKey("hot_food.id"), nullable=True, comment="热点美食ID")
    post_id = db.Column(db.Integer, db.ForeignKey("forum_post.id"), nullable=True, comment="帖子ID")
    comment_id = db.Column(db.Integer, db.ForeignKey("comment.id"), nullable=True, comment="评论ID")
    hand_account_id = db.Column(db.Integer, db.ForeignKey("hand_account.id"), nullable=True, comment="手账ID")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        """转换为字典，用于接口返回"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "hot_food_id": self.hot_food_id,
            "post_id": self.post_id,
            "comment_id": self.comment_id,
            "hand_account_id": self.hand_account_id,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @classmethod
    def get_by_user(cls, user_id, like_type=None, page=1, page_size=10):
        """根据用户ID查询点赞（分页）"""
        offset = (page - 1) * page_size
        query = cls.query.filter_by(user_id=user_id)
        
        if like_type == "hot_food":
            query = query.filter(cls.hot_food_id.isnot(None))
        elif like_type == "post":
            query = query.filter(cls.post_id.isnot(None))
        elif like_type == "comment":
            query = query.filter(cls.comment_id.isnot(None))
        elif like_type == "hand_account":
            query = query.filter(cls.hand_account_id.isnot(None))
        
        return query.order_by(cls.create_time.desc()).offset(offset).limit(page_size).all()
    
    @classmethod
    def get_by_user_and_target(cls, user_id, hot_food_id=None, post_id=None, comment_id=None, hand_account_id=None):
        """根据用户ID和目标ID查询点赞"""
        query = cls.query.filter_by(user_id=user_id)
        
        if hot_food_id:
            query = query.filter_by(hot_food_id=hot_food_id)
        elif post_id:
            query = query.filter_by(post_id=post_id)
        elif comment_id:
            query = query.filter_by(comment_id=comment_id)
        elif hand_account_id:
            query = query.filter_by(hand_account_id=hand_account_id)
        
        return query.first()
    
    def save(self):
        """保存点赞"""
        try:
            db.session.add(self)
            db.session.commit()
            logger.info(f"点赞{self.id}保存成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"点赞保存失败：{str(e)}")
            return False
    
    def delete(self):
        """删除点赞"""
        try:
            db.session.delete(self)
            db.session.commit()
            logger.info(f"点赞{self.id}删除成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"点赞删除失败：{str(e)}")
            return False
