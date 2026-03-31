import random
from loguru import logger
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.utils.personalized_recommender import PersonalizedRecommender


class AIFallbackManager:
    """AI降级管理器 - 提供健壮的本地fallback机制"""
    
    @staticmethod
    def get_fallback_chat_response(messages):
        """对话降级响应"""
        try:
            last_message = messages[-1]["content"] if messages else ""
            
            if "食谱" in last_message or "推荐" in last_message:
                return "根据您的健康目标和偏好，我为您准备了个性化的食谱推荐。请查看推荐列表获取详情！"
            elif "营养" in last_message or "热量" in last_message:
                return "营养平衡对健康很重要！建议每餐包含适量的蛋白质、碳水化合物和健康脂肪。"
            elif "运动" in last_message or "锻炼" in last_message:
                return "适量运动配合健康饮食效果更佳！建议每周进行150分钟中等强度有氧运动。"
            else:
                responses = [
                    "感谢您的咨询！我会为您提供专业的健康饮食建议。",
                    "健康生活从良好的饮食习惯开始，有什么我可以帮助您的吗？",
                    "保持均衡饮食和规律作息，是保持健康的关键！"
                ]
                return random.choice(responses)
        except Exception as e:
            logger.error(f"生成对话降级响应失败：{str(e)}")
            return "抱歉，AI服务暂时不可用。请稍后再试！"
    
    @staticmethod
    def get_fallback_recipe_recommendation(user, recipes):
        """食谱推荐降级 - 使用本地算法"""
        try:
            logger.info("使用本地算法进行食谱推荐")
            recommend_list = PersonalizedRecommender.generate_recommendations(user, recipes)
            
            if not recommend_list:
                return "暂时没有合适的推荐，请稍后再试。", []
            
            top_recipes = recommend_list[:3]
            recipe_names = [r["recipe_name"] for r in top_recipes]
            
            recommendation_text = f"根据您的健康数据，为您推荐：{', '.join(recipe_names)}。这些食谱符合您的营养需求和饮食偏好！"
            
            return recommendation_text, recommend_list
        except Exception as e:
            logger.error(f"生成食谱推荐降级响应失败：{str(e)}")
            return "暂时无法为您生成推荐，请稍后再试。", []
    
    @staticmethod
    def get_fallback_handbook_content(topic, mood):
        """手账内容降级 - 本地生成"""
        try:
            templates = [
                f"今天心情{mood}，记录一下关于{topic}的点滴。健康饮食让生活更美好！",
                f"分享今天的{mood}时光，{topic}让我感到很满足。继续保持健康的饮食习惯！",
                f"今日份{mood}，关于{topic}的小确幸。好好吃饭，好好生活！",
                f"{mood}的一天，用{topic}记录生活。健康是最大的财富！",
                f"记录{mood}时刻，{topic}带来的美好。坚持健康饮食，享受生活！"
            ]
            return random.choice(templates)
        except Exception as e:
            logger.error(f"生成手账降级内容失败：{str(e)}")
            return f"今天心情{mood}，记录{topic}的美好时光。"
    
    @staticmethod
    def get_fallback_food_analysis(food_name):
        """食物分析降级 - 本地简单分析"""
        try:
            food_analysis_map = {
                "鸡蛋": "鸡蛋富含优质蛋白质和维生素，是营养均衡的食材。建议每天食用1-2个。",
                "牛奶": "牛奶富含钙质和蛋白质，有助于骨骼健康。建议每天饮用300ml。",
                "苹果": "苹果含有丰富的膳食纤维和维生素C，有益健康。每天一个苹果，医生远离我！",
                "鸡胸肉": "鸡胸肉是低脂高蛋白的优质食材，非常适合健身和减脂人群。",
                "西兰花": "西兰花富含维生素C、K和膳食纤维，是非常健康的蔬菜。",
                "燕麦": "燕麦富含膳食纤维，有助于控制血糖和胆固醇，是很好的早餐选择。",
                "三文鱼": "三文鱼富含Omega-3脂肪酸，对心脑血管健康非常有益。",
                "菠菜": "菠菜富含铁、钙和维生素，是营养丰富的绿叶蔬菜。"
            }
            
            for key, analysis in food_analysis_map.items():
                if key in food_name:
                    return analysis
            
            return f"{food_name}是一种常见的食材，含有丰富的营养成分。建议适量食用，搭配均衡饮食，保持健康的生活方式。"
        except Exception as e:
            logger.error(f"生成食物分析降级内容失败：{str(e)}")
            return f"{food_name}营养丰富，建议适量食用。"
    
    @staticmethod
    def get_fallback_ingredient_recommendation(user, limit=10):
        """食材推荐降级 - 本地生成"""
        try:
            health_goal = user.health_goal if hasattr(user, 'health_goal') else "维持"
            
            if health_goal == "减脂":
                ingredients = Ingredient.query.filter(Ingredient.calorie <= 100).limit(limit).all()
            elif health_goal == "增肌":
                ingredients = Ingredient.query.filter(Ingredient.protein >= 15).limit(limit).all()
            else:
                ingredients = Ingredient.query.limit(limit).all()
            
            return [
                {
                    "ingredient_id": ing.id,
                    "ingre_name": ing.ingre_name,
                    "calorie": ing.calorie,
                    "protein": ing.protein,
                    "carb": ing.carb,
                    "fat": ing.fat,
                    "category": ing.category,
                    "frequency": 0
                } for ing in ingredients
            ]
        except Exception as e:
            logger.error(f"生成食材推荐降级内容失败：{str(e)}")
            return []


# 全局管理器实例
_ai_fallback_manager = None


def get_ai_fallback_manager():
    """获取AI降级管理器单例"""
    global _ai_fallback_manager
    if _ai_fallback_manager is None:
        _ai_fallback_manager = AIFallbackManager()
    return _ai_fallback_manager
