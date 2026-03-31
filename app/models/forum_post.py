from app import db
from datetime import datetime
from loguru import logger

class ForumPost(db.Model):
    """论坛帖子模型"""
    __tablename__ = "forum_post"
    __table_args__ = {"comment": "论坛帖子表"}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="帖子ID")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, comment="用户ID")
    title = db.Column(db.String(100), nullable=False, comment="帖子标题")
    content = db.Column(db.Text, nullable=False, comment="帖子内容")
    image = db.Column(db.String(255), default="", comment="帖子图片")
    category = db.Column(db.String(50), default="", comment="帖子分类")
    likes = db.Column(db.Integer, default=0, comment="点赞数")
    views = db.Column(db.Integer, default=0, comment="浏览数")
    is_top = db.Column(db.Boolean, default=False, comment="是否置顶")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    def to_dict(self):
        """转换为字典，用于接口返回"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content,
            "image": self.image,
            "category": self.category,
            "likes": self.likes,
            "views": self.views,
            "is_top": self.is_top,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @classmethod
    def get_all(cls, page=1, page_size=10):
        """获取所有帖子（分页）"""
        offset = (page - 1) * page_size
        return cls.query.order_by(cls.is_top.desc(), cls.create_time.desc()).offset(offset).limit(page_size).all()
    
    @classmethod
    def get_by_user(cls, user_id, page=1, page_size=10):
        """根据用户ID查询帖子（分页）"""
        offset = (page - 1) * page_size
        return cls.query.filter_by(user_id=user_id).order_by(cls.create_time.desc()).offset(offset).limit(page_size).all()
    
    @classmethod
    def get_by_id(cls, id):
        """根据ID查询帖子"""
        return cls.query.filter_by(id=id).first()
    
    def save(self):
        """保存帖子"""
        try:
            db.session.add(self)
            db.session.commit()
            logger.info(f"帖子{self.id}保存成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"帖子保存失败：{str(e)}")
            return False
    
    def update(self):
        """更新帖子"""
        try:
            db.session.commit()
            logger.info(f"帖子{self.id}更新成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"帖子更新失败：{str(e)}")
            return False
    
    def delete(self):
        """删除帖子"""
        try:
            db.session.delete(self)
            db.session.commit()
            logger.info(f"帖子{self.id}删除成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"帖子删除失败：{str(e)}")
            return False
    
    def increment_views(self):
        """增加浏览数"""
        try:
            self.views += 1
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"增加浏览数失败：{str(e)}")
            return False
