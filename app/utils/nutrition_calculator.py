from loguru import logger

class NutritionCalculator:
    """营养推荐摄入量计算器，用于计算用户的营养需求和生成膳食计划"""
    
    @staticmethod
    def calculate_bmr(weight, height, age, gender):
        """计算基础代谢率(BMR)，即维持基本生理功能所需的最低能量
        
        使用Harris-Benedict公式，这是一种常用的基础代谢率计算方法
        
        Args:
            weight (float): 体重(kg)
            height (float): 身高(cm)
            age (int): 年龄
            gender (str): 性别，"男"或"女"
            
        Returns:
            float: 基础代谢率(大卡/天)
        """
        try:
            if gender == "男":
                # 男性BMR计算公式
                bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
            elif gender == "女":
                # 女性BMR计算公式
                bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
            else:
                # 未知性别，使用男性公式作为默认值
                bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
            return bmr
        except Exception as e:
            logger.error(f"计算BMR失败：{str(e)}")
            return 1500  # 默认值
    
    @staticmethod
    def calculate_tdee(bmr, activity_level=1.2):
        """计算总能量消耗(TDEE)，即一天内消耗的总热量
        
        Args:
            bmr (float): 基础代谢率
            activity_level (float): 活动水平系数
                1.2: 久坐不动
                1.375: 轻度活动
                1.55: 中度活动
                1.725: 高度活动
                1.9: 极度活动
                
        Returns:
            float: 总能量消耗(大卡/天)
        """
        return bmr * activity_level
    
    @staticmethod
    def calculate_nutrition_needs(user):
        """根据用户信息计算营养需求
        
        Args:
            user (User): 用户对象，包含体重、身高、年龄、性别和健康目标等信息
            
        Returns:
            dict: 包含营养需求的字典，包括热量、蛋白质、碳水、脂肪等
        """
        if not user:
            return None
        
        # 计算BMR，使用默认值防止用户信息不完整
        bmr = NutritionCalculator.calculate_bmr(
            user.weight or 60,  # 默认体重60kg
            user.height or 170,  # 默认身高170cm
            user.age or 30,  # 默认年龄30岁
            user.gender
        )
        
        # 计算TDEE，默认活动水平为久坐不动
        tdee = NutritionCalculator.calculate_tdee(bmr)
        
        # 根据健康目标调整热量
        if user.health_goal == "减脂":
            # 减脂：每天减少300-500大卡，这里取400大卡
            calorie_goal = tdee - 400
        elif user.health_goal == "增肌":
            # 增肌：每天增加300-500大卡，这里取400大卡
            calorie_goal = tdee + 400
        else:  # 维持
            # 维持体重：保持TDEE不变
            calorie_goal = tdee
        
        # 计算三大营养素推荐摄入量
        # 蛋白质：根据健康目标调整摄入量
        if user.health_goal == "增肌":
            # 增肌需要更多蛋白质，1.8g/kg体重
            protein_goal = user.weight * 1.8 if user.weight else 108
        else:
            # 一般情况，1.2g/kg体重
            protein_goal = user.weight * 1.2 if user.weight else 72
        
        # 碳水：根据健康目标调整比例
        carb_percentage = 0.5 if user.health_goal != "减脂" else 0.4
        # 1g碳水化合物提供4大卡热量
        carb_goal = (calorie_goal * carb_percentage) / 4
        
        # 脂肪：占总热量的25%
        # 1g脂肪提供9大卡热量
        fat_goal = (calorie_goal * 0.25) / 9
        
        return {
            "calorie": round(calorie_goal),  # 热量目标
            "protein": round(protein_goal),  # 蛋白质目标
            "carb": round(carb_goal),  # 碳水化合物目标
            "fat": round(fat_goal),  # 脂肪目标
            "bmr": round(bmr),  # 基础代谢率
            "tdee": round(tdee)  # 总能量消耗
        }
    
    @staticmethod
    def generate_daily_meal_plan(nutrition_needs):
        """生成每日三餐的营养分配计划
        
        Args:
            nutrition_needs (dict): 营养需求字典，包含热量、蛋白质、碳水、脂肪等信息
            
        Returns:
            dict: 包含三餐营养分配的字典
        """
        if not nutrition_needs:
            return None
        
        # 三餐营养分配比例
        # 早餐：30%，午餐：40%，晚餐：30%
        meal_plan = {
            "breakfast": {
                "calorie": round(nutrition_needs["calorie"] * 0.3),
                "protein": round(nutrition_needs["protein"] * 0.3),
                "carb": round(nutrition_needs["carb"] * 0.3),
                "fat": round(nutrition_needs["fat"] * 0.3)
            },
            "lunch": {
                "calorie": round(nutrition_needs["calorie"] * 0.4),
                "protein": round(nutrition_needs["protein"] * 0.4),
                "carb": round(nutrition_needs["carb"] * 0.4),
                "fat": round(nutrition_needs["fat"] * 0.4)
            },
            "dinner": {
                "calorie": round(nutrition_needs["calorie"] * 0.3),
                "protein": round(nutrition_needs["protein"] * 0.3),
                "carb": round(nutrition_needs["carb"] * 0.3),
                "fat": round(nutrition_needs["fat"] * 0.3)
            }
        }
        
        return meal_plan