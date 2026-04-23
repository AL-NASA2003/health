from app import db
from datetime import datetime
from loguru import logger

class Recipe(db.Model):
    """食谱信息模型，用于存储食谱的详细信息"""
    __tablename__ = "recipe"  # 数据库表名
    __table_args__ = {"comment": "食谱信息表，存储食谱的详细信息"}
    
    # 基本字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="食谱ID，自增主键")
    recipe_name = db.Column(db.String(100), nullable=False, comment="食谱名称")
    
    # 营养成分字段
    calorie = db.Column(db.Float, nullable=False, comment="每份热量(大卡)")
    protein = db.Column(db.Float, nullable=False, comment="每份蛋白质(g)")
    carb = db.Column(db.Float, nullable=False, comment="每份碳水(g)")
    fat = db.Column(db.Float, nullable=False, comment="每份脂肪(g)")
    
    # 食谱属性字段
    flavor = db.Column(db.String(20), default="", comment="口味：清淡/麻辣/甜")
    cook_type = db.Column(db.String(20), default="", comment="烹饪方式：炒/煮/蒸")
    suitable_crowd = db.Column(db.String(50), default="", comment="适合人群")
    cook_step = db.Column(db.Text, nullable=False, comment="烹饪步骤")
    image = db.Column(db.String(255), default="", comment="食谱图片")
    ingre_list = db.Column(db.String(500), default="", comment="食材组成")
    
    # 新增字段：参考aigconly.com/recipe-generator
    cuisine = db.Column(db.String(20), default="", comment="菜系：中式/西式/日式/韩式")
    difficulty = db.Column(db.String(20), default="", comment="难度：简单/中等/困难")
    cook_time = db.Column(db.Integer, default=30, comment="烹饪时间(分钟)")
    
    # 新增字段：风味评分系统（参考flavorithm.com）
    flavor_sweet = db.Column(db.Float, default=0.0, comment="甜味评分 0-10")
    flavor_salty = db.Column(db.Float, default=0.0, comment="咸味评分 0-10")
    flavor_spicy = db.Column(db.Float, default=0.0, comment="辣味评分 0-10")
    flavor_sour = db.Column(db.Float, default=0.0, comment="酸味评分 0-10")
    flavor_umami = db.Column(db.Float, default=0.0, comment="鲜味评分 0-10")
    
    # 其他标签
    is_quick = db.Column(db.Boolean, default=False, comment="是否快手菜")
    is_featured = db.Column(db.Boolean, default=False, comment="是否精选")
    is_seasonal = db.Column(db.Boolean, default=False, comment="是否当季")
    
    # 时间字段
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联关系
    # 一个食谱对应多种食材，使用cascade="all, delete-orphan"确保删除食谱时同时删除相关的食材关联
    ingredients = db.relationship('RecipeIngredient', backref='recipe', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        """将食谱对象转换为字典格式，用于API接口返回
        
        Returns:
            dict: 包含食谱信息的字典
        """
        # 构建食材列表
        ingre_list = []
        for ri in self.ingredients:
            if ri.ingredient:
                ingre_list.append(f"{ri.ingredient.ingre_name}{ri.weight}{ri.unit}")
        
        # 将 cook_step 转换为 steps 数组
        steps = []
        if self.cook_step:
            # 按换行符分割，并过滤掉空行
            step_lines = self.cook_step.split('\n')
            for line in step_lines:
                line = line.strip()
                if line:
                    # 移除步骤编号前缀（如 "1. "、"2. " 等）
                    if len(line) > 2 and line[1] in ('.', '、', ' '):
                        line = line[2:].strip()
                    steps.append(line)
        
        return {
            "id": self.id,
            "recipe_name": self.recipe_name,
            "ingre_list": ", ".join(ingre_list),
            "cook_step": self.cook_step,
            "steps": steps,
            "calorie": self.calorie,
            "protein": self.protein,
            "carb": self.carb,
            "fat": self.fat,
            "flavor": self.flavor,
            "cook_type": self.cook_type,
            "suitable_crowd": self.suitable_crowd,
            "image": self.image,
            # 新增字段
            "cuisine": self.cuisine,
            "difficulty": self.difficulty,
            "cook_time": self.cook_time,
            # 新增：风味评分（参考flavorithm.com）
            "flavor_sweet": self.flavor_sweet,
            "flavor_salty": self.flavor_salty,
            "flavor_spicy": self.flavor_spicy,
            "flavor_sour": self.flavor_sour,
            "flavor_umami": self.flavor_umami,
            # 新增：标签
            "is_quick": self.is_quick,
            "is_featured": self.is_featured,
            "is_seasonal": self.is_seasonal,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @classmethod
    def get_all(cls):
        """获取所有食谱
        
        Returns:
            list: 食谱对象列表
        """
        return cls.query.all()
    
    def save(self):
        """保存食谱信息到数据库
        
        Returns:
            bool: 保存成功返回True，失败返回False
        """
        try:
            db.session.add(self)
            db.session.commit()
            logger.info(f"食谱{self.recipe_name}保存成功")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"食谱保存失败：{str(e)}")
            return False

class RecipeIngredient(db.Model):
    """食谱食材关联模型，用于存储食谱与食材的多对多关系"""
    __tablename__ = "recipe_ingredient"  # 数据库表名
    __table_args__ = {"comment": "食谱食材关联表，存储食谱与食材的多对多关系"}
    
    # 基本字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="关联ID，自增主键")
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), nullable=False, comment="食谱ID")
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredient.id"), nullable=False, comment="食材ID")
    weight = db.Column(db.Float, default=0, comment="食材用量")
    unit = db.Column(db.String(10), default="g", comment="计量单位")
    
    # 关联关系
    # 关联到食材表，通过backref可以从食材对象访问关联的食谱食材关系
    ingredient = db.relationship('Ingredient', backref='recipe_ingredients', lazy=True)
    
    def to_dict(self):
        """将食谱食材关联对象转换为字典格式
        
        Returns:
            dict: 包含食谱食材关联信息的字典
        """
        return {
            "id": self.id,
            "recipe_id": self.recipe_id,
            "ingredient_id": self.ingredient_id,
            "weight": self.weight,
            "unit": self.unit,
            "ingredient_name": self.ingredient.ingre_name if self.ingredient else ""
        }