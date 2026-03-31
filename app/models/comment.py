from app import db
from datetime import datetime
from loguru import logger

class Comment(db.Model):
    """评论模型"""
    __tablename__ = "comment"
    __table_args__ = {"comment": "评论表"}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="评论ID")
    post_id = db.Column(db.Integer, db.ForeignKey("forum_post.id"), nullable=False, comment="帖子ID")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, comment="用户ID")
    content = db.Column(db.Text, nullable=False, comment="评论内容")
    likes = db.Column(db.Integer, default=0, comment="点赞数")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        """转换为字典，用于接口返回"""
        return {
            "id": self.id,
            "post_id": self.post_id,
            "user_id": self.user_id,
            "content": self.content,
            "likes": self.likes,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @classmethod
    def get_by_post(cls, post_id, page=1, page_size=20):
        """根据帖子ID查询评论（分页）"""
        offset = (page - 1) * page_size
        return cls.query.filter_by(post_id=post_id).order_by(cls.create_time.desc()).offset(offset).limit(page_size).all()
    
    @classmethod
    def get_by_user(cls, user_id, page=1, page_size=20):
        """根据用户ID查询评论（分页）"""
        offset = (page - 1) * page_size
        return cls.query.filter_by(user_id=user_id).order_by(cls.create_time.desc()).offset(offset).limit(page_size).all()
    
    @classmethod
    def get_by_id(cls, id):
        """根据ID查询评论"""
        return cls.query.filter_by(id=id).first()
    
    def save(self):
        """保存评论"""
        try:
            db.session.add(self)
            db.session.commit()
            logger.info(f"评论{self.id}保存成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"评论保存失败：{str(e)}")
            return False
    
    def update(self):
        """更新评论"""
        try:
            db.session.commit()
            logger.info(f"评论{self.id}更新成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"评论更新失败：{str(e)}")
            return False
    
    def delete(self):
        """删除评论"""
        try:
            db.session.delete(self)
            db.session.commit()
            logger.info(f"评论{self.id}删除成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"评论删除失败：{str(e)}")
            return False
