from app import db
from datetime import datetime
from loguru import logger

class HandAccount(db.Model):
    """手账模型"""
    __tablename__ = "hand_account"
    __table_args__ = {"comment": "手账表"}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="手账ID")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, comment="用户ID")
    title = db.Column(db.String(100), nullable=False, comment="手账标题")
    content = db.Column(db.Text, nullable=False, comment="手账内容")
    image = db.Column(db.String(255), default="", comment="手账图片")
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
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @classmethod
    def get_by_user(cls, user_id, limit=100):
        """根据用户ID查询手账"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.create_time.desc()).limit(limit).all()
    
    @classmethod
    def get_by_id(cls, id, user_id):
        """根据ID和用户ID查询手账"""
        return cls.query.filter_by(id=id, user_id=user_id).first()
    
    def save(self):
        """保存手账"""
        try:
            db.session.add(self)
            db.session.commit()
            logger.info(f"手账{self.id}保存成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"手账保存失败：{str(e)}")
            return False
    
    def update(self):
        """更新手账"""
        try:
            db.session.commit()
            logger.info(f"手账{self.id}更新成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"手账更新失败：{str(e)}")
            return False
    
    def delete(self):
        """删除手账"""
        try:
            db.session.delete(self)
            db.session.commit()
            logger.info(f"手账{self.id}删除成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"手账删除失败：{str(e)}")
            return False
