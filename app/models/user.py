from app import db
from datetime import datetime
from loguru import logger
from app.utils.encrypt import encrypt_data, decrypt_data

class User(db.Model):
    """用户信息模型，用于存储用户的基本信息和健康相关数据"""
    __tablename__ = "user"  # 数据库表名
    __table_args__ = (
        db.Index('idx_openid', 'openid', unique=True),
        {"comment": "用户信息表，存储用户基本信息和健康数据"}
    )
    
    # 基本字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="用户ID，自增主键")
    openid = db.Column(db.String(100), nullable=False, comment="微信OpenID，用户唯一标识")
    nickname = db.Column(db.String(50), default="", comment="用户昵称")
    avatar = db.Column(db.String(255), default="", comment="用户头像URL")
    
    # 健康相关字段
    height = db.Column(db.Float, default=0.0, comment="身高(cm)")
    weight = db.Column(db.Float, default=0.0, comment="体重(kg)")
    age = db.Column(db.Integer, default=0, comment="年龄")
    gender = db.Column(db.Integer, default=0, comment="性别：0-未知 1-男 2-女")
    waist = db.Column(db.Float, default=0.0, comment="腰围(cm)")
    hip = db.Column(db.Float, default=0.0, comment="臀围(cm)")
    health_goal = db.Column(db.String(50), default="", comment="健康目标：减脂/增肌/维持")
    dietary_preference = db.Column(db.String(100), default="", comment="饮食偏好，如素食、低碳水等")
    
    # 其他字段
    phone = db.Column(db.String(255), default="", comment="手机号（加密存储）")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联关系定义
    # 一个用户对应多条饮食记录，使用cascade="all, delete-orphan"确保删除用户时同时删除相关的饮食记录
    diet_records = db.relationship("DietRecord", backref="user", lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        """将用户对象转换为字典格式，用于API接口返回
        
        Returns:
            dict: 包含用户信息的字典
        """
        # 解密手机号
        phone = ""
        if self.phone:
            try:
                phone = decrypt_data(self.phone)
            except Exception as e:
                logger.warning(f"解密手机号失败：{str(e)}")
                phone = ""
        
        # 转换性别为可读格式
        gender_map = {0: "未知", 1: "男", 2: "女"}
        gender_str = gender_map.get(self.gender, "未知")
        
        return {
            "id": self.id,
            "nickname": self.nickname,
            "avatar": self.avatar,
            "height": self.height,
            "weight": self.weight,
            "age": self.age,
            "gender": gender_str,
            "waist": self.waist,
            "hip": self.hip,
            "health_goal": self.health_goal,
            "dietary_preference": self.dietary_preference,
            "phone": phone,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @classmethod
    def get_by_openid(cls, openid):
        """根据微信OpenID查询用户
        
        Args:
            openid (str): 微信OpenID
            
        Returns:
            User: 用户对象，如果不存在则返回None
        """
        return cls.query.filter_by(openid=openid).first()
    
    def save(self):
        """保存用户信息到数据库
        
        Returns:
            bool: 保存成功返回True，失败返回False
        """
        try:
            # 加密手机号
            if self.phone:
                try:
                    self.phone = encrypt_data(self.phone)
                except Exception as e:
                    logger.warning(f"加密手机号失败：{str(e)}")
            
            db.session.add(self)
            db.session.commit()
            logger.info(f"用户{self.id}保存成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"用户保存失败：{str(e)}")
            return False
    
    @classmethod
    def batch_save(cls, users):
        """批量保存用户信息
        
        Args:
            users: 用户对象列表
            
        Returns:
            bool: 保存成功返回True，失败返回False
        """
        try:
            for user in users:
                if user.phone:
                    try:
                        user.phone = encrypt_data(user.phone)
                    except Exception as e:
                        logger.warning(f"加密手机号失败：{str(e)}")
                db.session.add(user)
            db.session.commit()
            logger.info(f"批量保存用户成功，共{len(users)}条")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"批量保存用户失败：{str(e)}")
            return False