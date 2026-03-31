from loguru import logger

class NutritionNeedsCalculator:
    """营养需求计算器，用于计算用户的每日营养摄入目标"""
    
    @staticmethod
    def calculate_bmr(user):
        """计算基础代谢率（BMR）- 使用Mifflin-St Jeor方程
        
        Args:
            user (User): 用户对象
            
        Returns:
            float: BMR值（千卡）
        """
        if not user.weight or not user.height or not user.age:
            return 1500
        
        weight = user.weight
        height = user.height
        age = user.age
        
        if user.gender == 1:
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        elif user.gender == 2:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age
        
        return max(bmr, 1000)
    
    @staticmethod
    def get_activity_multiplier(activity_level):
        """获取活动水平乘数
        
        Args:
            activity_level (int): 活动水平 1-5
            
        Returns:
            float: 活动乘数
        """
        multipliers = {
            1: 1.2,
            2: 1.375,
            3: 1.55,
            4: 1.725,
            5: 1.9
        }
        return multipliers.get(activity_level, 1.2)
    
    @staticmethod
    def calculate_tdee(user):
        """计算总能量消耗（TDEE）
        
        Args:
            user (User): 用户对象
            
        Returns:
            float: TDEE值（千卡）
        """
        bmr = NutritionNeedsCalculator.calculate_bmr(user)
        activity_multiplier = NutritionNeedsCalculator.get_activity_multiplier(user.activity_level)
        return bmr * activity_multiplier
    
    @staticmethod
    def calculate_target_calorie(user):
        """根据健康目标计算目标卡路里
        
        Args:
            user (User): 用户对象
            
        Returns:
            float: 目标卡路里（千卡）
        """
        tdee = NutritionNeedsCalculator.calculate_tdee(user)
        
        if user.health_goal == "减脂":
            target = tdee - 500
        elif user.health_goal == "增肌":
            target = tdee + 300
        else:
            target = tdee
        
        return max(target, 1200)
    
    @staticmethod
    def calculate_macronutrients(user, target_calorie=None):
        """计算宏量营养素目标（蛋白质、碳水、脂肪）
        
        Args:
            user (User): 用户对象
            target_calorie (float, optional): 目标卡路里，如果不提供则自动计算
            
        Returns:
            dict: 包含各宏量营养素目标的字典
        """
        if target_calorie is None:
            target_calorie = NutritionNeedsCalculator.calculate_target_calorie(user)
        
        weight = user.weight if user.weight else 60
        
        if user.health_goal == "增肌":
            protein_per_kg = 2.0
            fat_ratio = 0.25
        elif user.health_goal == "减脂":
            protein_per_kg = 2.2
            fat_ratio = 0.30
        else:
            protein_per_kg = 1.6
            fat_ratio = 0.25
        
        protein = weight * protein_per_kg
        protein_calories = protein * 4
        
        fat_calories = target_calorie * fat_ratio
        fat = fat_calories / 9
        
        carb_calories = target_calorie - protein_calories - fat_calories
        carb = carb_calories / 4
        
        return {
            "calorie": round(target_calorie, 1),
            "protein": round(protein, 1),
            "carb": round(max(carb, 50), 1),
            "fat": round(max(fat, 20), 1)
        }
    
    @staticmethod
    def calculate_all(user):
        """计算所有营养需求
        
        Args:
            user (User): 用户对象
            
        Returns:
            dict: 包含所有计算结果的字典
        """
        try:
            bmr = NutritionNeedsCalculator.calculate_bmr(user)
            tdee = NutritionNeedsCalculator.calculate_tdee(user)
            macros = NutritionNeedsCalculator.calculate_macronutrients(user)
            
            activity_level_map = {
                1: "久坐（几乎不运动）",
                2: "轻度（每周1-3次运动）",
                3: "中度（每周3-5次运动）",
                4: "重度（每周6-7次运动）",
                5: "极重度（专业运动员）"
            }
            
            return {
                "bmr": round(bmr, 1),
                "tdee": round(tdee, 1),
                "activity_level": user.activity_level,
                "activity_level_desc": activity_level_map.get(user.activity_level, "未知"),
                "target_calorie": macros["calorie"],
                "target_protein": macros["protein"],
                "target_carb": macros["carb"],
                "target_fat": macros["fat"],
                "health_goal": user.health_goal or "维持",
                "bmi": NutritionNeedsCalculator.calculate_bmi(user.weight, user.height),
                "bmi_category": NutritionNeedsCalculator.get_bmi_category(NutritionNeedsCalculator.calculate_bmi(user.weight, user.height))
            }
        except Exception as e:
            logger.error(f"计算营养需求失败：{str(e)}")
            return {
                "bmr": 1500,
                "tdee": 1800,
                "activity_level": 1,
                "activity_level_desc": "久坐",
                "target_calorie": 1800,
                "target_protein": 96,
                "target_carb": 225,
                "target_fat": 50,
                "health_goal": "维持",
                "bmi": 22,
                "bmi_category": "正常"
            }
    
    @staticmethod
    def calculate_bmi(weight, height):
        """计算BMI
        
        Args:
            weight (float): 体重(kg)
            height (float): 身高(cm)
            
        Returns:
            float: BMI值
        """
        if not weight or not height or height == 0:
            return 22
        height_m = height / 100
        return round(weight / (height_m * height_m), 1)
    
    @staticmethod
    def get_bmi_category(bmi):
        """获取BMI分类
        
        Args:
            bmi (float): BMI值
            
        Returns:
            str: BMI分类
        """
        if bmi < 18.5:
            return "偏瘦"
        elif 18.5 <= bmi < 24:
            return "正常"
        elif 24 <= bmi < 28:
            return "超重"
        else:
            return "肥胖"
