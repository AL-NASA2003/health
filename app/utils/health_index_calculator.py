from loguru import logger
from app.models.diet_record import DietRecord
from app.utils.nutrition_calculator import NutritionCalculator

class HealthIndexCalculator:
    """健康指数计算器，用于计算用户的健康指数并生成更精准的食谱推荐"""
    
    @staticmethod
    def calculate_health_index(user):
        """计算用户的健康指数（简化版）
        
        Args:
            user (User): 用户对象
            
        Returns:
            dict: 包含健康指数和相关指标的字典
        """
        try:
            # 计算基础健康指标
            bmi = HealthIndexCalculator.calculate_bmi(user.weight, user.height)
            
            # 综合健康指数（基于 BMI）
            health_index = HealthIndexCalculator.calculate_overall_health_index(bmi)
            
            return {
                "health_index": round(health_index, 2),
                "bmi": round(bmi, 2),
                "bmi_category": HealthIndexCalculator.get_bmi_category(bmi),
                "recommendations": HealthIndexCalculator.get_health_recommendations(health_index, bmi)
            }
        except Exception as e:
            logger.error(f"计算健康指数失败：{str(e)}")
            return {
                "health_index": 50,
                "bmi": 22,
                "bmi_category": "正常",
                "recommendations": ["保持健康的生活方式"]
            }
    
    @staticmethod
    def calculate_bmi(weight, height):
        """计算 BMI 指数
        
        Args:
            weight (float): 体重 (kg)
            height (float): 身高 (cm)
            
        Returns:
            float: BMI 指数
        """
        if not weight or not height or height == 0:
            return 22
        
        height_m = height / 100
        return weight / (height_m * height_m)
    
    @staticmethod
    def get_bmi_category(bmi):
        """获取 BMI 分类
        
        Args:
            bmi (float): BMI 指数
            
        Returns:
            str: BMI 分类
        """
        if bmi < 18.5:
            return "偏瘦"
        elif 18.5 <= bmi < 24:
            return "正常"
        elif 24 <= bmi < 28:
            return "超重"
        else:
            return "肥胖"
    
    @staticmethod
    def calculate_overall_health_index(bmi):
        """计算综合健康指数（简化版）
        
        Args:
            bmi (float): BMI 指数
            
        Returns:
            float: 综合健康指数（0-100）
        """
        # BMI 得分（100 分）
        if 18.5 <= bmi < 24:
            return 100
        elif bmi < 18.5 or 24 <= bmi < 28:
            return 70
        else:
            return 50
    
    @staticmethod
    def get_health_recommendations(health_index, bmi):
        """获取健康建议（简化版）
        
        Args:
            health_index (float): 健康指数
            bmi (float): BMI 指数
            
        Returns:
            list: 健康建议列表
        """
        recommendations = []
        
        if health_index < 60:
            recommendations.append("建议咨询医生或营养师，制定个性化的健康计划")
        
        if bmi < 18.5:
            recommendations.append("增加营养摄入，适当增加体重")
        elif bmi >= 28:
            recommendations.append("控制饮食，增加运动量，减少体重")
        
        if health_index >= 80:
            recommendations.append("保持良好的生活习惯和饮食习惯")
        
        return recommendations
    
    @staticmethod
    def generate_personalized_recipe_recommendations(user, recipes):
        """生成个性化食谱推荐（简化版，移除 API 调用）
        
        Args:
            user (User): 用户对象
            recipes (list): 食谱列表
            
        Returns:
            list: 推荐的食谱列表
        """
        # 计算营养需求
        nutrition_needs = NutritionCalculator.calculate_nutrition_needs(user)
        
        recipe_scores = []
        
        for recipe in recipes:
            # 直接计算健康评分，移除 AI 相似度计算
            health_score = HealthIndexCalculator.calculate_recipe_score(
                recipe, user, nutrition_needs
            )
            
            recipe_scores.append((recipe, health_score))
        
        # 按分数排序
        recipe_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 返回前 10 个推荐食谱
        return [{
            "recipe_id": r[0].id,
            "recipe_name": r[0].recipe_name,
            "ingre_list": r[0].ingre_list,
            "cook_step": r[0].cook_step,
            "calorie": r[0].calorie,
            "protein": r[0].protein,
            "carb": r[0].carb,
            "fat": r[0].fat,
            "flavor": r[0].flavor,
            "cook_type": r[0].cook_type,
            "suitable_crowd": r[0].suitable_crowd,
            "score": round(r[1], 2)
        } for r in recipe_scores[:10]]
    
    @staticmethod
    def calculate_recipe_score(recipe, user, nutrition_needs):
        """计算食谱的推荐分数 - 根据用户目标摄入量优化
        
        Args:
            recipe (Recipe): 食谱对象
            user (User): 用户对象
            nutrition_needs (dict): 营养需求
            
        Returns:
            float: 推荐分数
        """
        score = 0
        
        target_calorie = user.target_calorie if user.target_calorie and user.target_calorie > 0 else nutrition_needs.get("calorie", 1800)
        target_protein = user.target_protein if user.target_protein and user.target_protein > 0 else nutrition_needs.get("protein", 96)
        target_carb = user.target_carb if user.target_carb and user.target_carb > 0 else nutrition_needs.get("carb", 225)
        target_fat = user.target_fat if user.target_fat and user.target_fat > 0 else nutrition_needs.get("fat", 50)
        
        # 一餐的营养目标（按每日目标的1/3计算）
        meal_target_calorie = target_calorie / 3
        meal_target_protein = target_protein / 3
        meal_target_carb = target_carb / 3
        meal_target_fat = target_fat / 3
        
        # 卡路里匹配度（30分）
        calorie_diff = abs(recipe.calorie - meal_target_calorie)
        calorie_score = max(0, 30 - (calorie_diff / meal_target_calorie) * 30)
        score += calorie_score
        
        # 蛋白质匹配度（25分）
        protein_diff = abs(recipe.protein - meal_target_protein)
        protein_score = max(0, 25 - (protein_diff / max(meal_target_protein, 1)) * 25)
        score += protein_score
        
        # 碳水化合物匹配度（20分）
        carb_diff = abs(recipe.carb - meal_target_carb)
        carb_score = max(0, 20 - (carb_diff / max(meal_target_carb, 1)) * 20)
        score += carb_score
        
        # 脂肪匹配度（15分）
        fat_diff = abs(recipe.fat - meal_target_fat)
        fat_score = max(0, 15 - (fat_diff / max(meal_target_fat, 1)) * 15)
        score += fat_score
        
        # 健康目标特殊加分（5分）
        if user.health_goal == "减脂" and recipe.calorie <= meal_target_calorie:
            score += 5
        elif user.health_goal == "增肌" and recipe.protein >= meal_target_protein:
            score += 5
        else:
            score += 2.5
        
        # 饮食多样性（3分）
        ingredient_count = len([i for i in recipe.ingre_list.split(',') if i.strip()])
        diversity_score = min(ingredient_count / 8, 1) * 3
        score += diversity_score
        
        # 口味偏好（2分）
        if hasattr(user, 'dietary_preference') and user.dietary_preference:
            if user.dietary_preference in recipe.flavor:
                score += 2
            else:
                score += 1
        else:
            score += 2
        
        return min(score, 100)
