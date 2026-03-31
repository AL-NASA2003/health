from app import db
from datetime import datetime
from loguru import logger

class UserCollection(db.Model):
    """用户收藏模型"""
    __tablename__ = "user_collection"
    __table_args__ = {"comment": "用户收藏表"}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="收藏ID")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, comment="用户ID")
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), nullable=True, comment="食谱ID")
    post_id = db.Column(db.Integer, db.ForeignKey("forum_post.id"), nullable=True, comment="帖子ID")
    hand_account_id = db.Column(db.Integer, db.ForeignKey("hand_account.id"), nullable=True, comment="手账ID")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        """转换为字典，用于接口返回"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "recipe_id": self.recipe_id,
            "post_id": self.post_id,
            "hand_account_id": self.hand_account_id,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @classmethod
    def get_by_user(cls, user_id, collection_type=None, page=1, page_size=10):
        """根据用户ID查询收藏（分页）"""
        offset = (page - 1) * page_size
        query = cls.query.filter_by(user_id=user_id)
        
        if collection_type == "recipe":
            query = query.filter(cls.recipe_id.isnot(None))
        elif collection_type == "post":
            query = query.filter(cls.post_id.isnot(None))
        elif collection_type == "hand_account":
            query = query.filter(cls.hand_account_id.isnot(None))
        
        return query.order_by(cls.create_time.desc()).offset(offset).limit(page_size).all()
    
    @classmethod
    def get_by_user_and_target(cls, user_id, recipe_id=None, post_id=None, hand_account_id=None):
        """根据用户ID和目标ID查询收藏"""
        query = cls.query.filter_by(user_id=user_id)
        
        if recipe_id:
            query = query.filter_by(recipe_id=recipe_id)
        elif post_id:
            query = query.filter_by(post_id=post_id)
        elif hand_account_id:
            query = query.filter_by(hand_account_id=hand_account_id)
        
        return query.first()
    
    def save(self):
        """保存收藏"""
        try:
            db.session.add(self)
            db.session.commit()
            logger.info(f"收藏{self.id}保存成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"收藏保存失败：{str(e)}")
            return False
    
    def delete(self):
        """删除收藏"""
        try:
            db.session.delete(self)
            db.session.commit()
            logger.info(f"收藏{self.id}删除成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"收藏删除失败：{str(e)}")
            return False
