import re
import math
from collections import Counter, defaultdict
from loguru import logger
from app.models.diet_record import DietRecord
from app.models.user_collection import UserCollection
from app.models.user import User
from app.models.recipe import Recipe
from app.utils.nutrition_calculator import NutritionCalculator

class PersonalizedRecommender:
    """增强版个性化推荐系统 - 结合多种推荐算法"""
    
    @staticmethod
    def clean_text(text):
        """清理文本，用于相似度计算"""
        if not text:
            return ""
        text = re.sub(r'[\s\t\n\r.,;!?()\[\]{}:"\'`~@#$%^&*+=|\\/]', '', text.lower())
        return text
    
    @staticmethod
    def get_character_ngrams(text, n=2):
        """获取字符n-gram，用于中文文本相似度"""
        text = PersonalizedRecommender.clean_text(text)
        if len(text) < n:
            return [text]
        return [text[i:i+n] for i in range(len(text)-n+1)]
    
    @staticmethod
    def cosine_similarity(vec1, vec2):
        """计算余弦相似度"""
        dot_product = sum(vec1.get(k, 0) * vec2.get(k, 0) for k in set(vec1.keys()) & set(vec2.keys()))
        norm1 = math.sqrt(sum(v**2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v**2 for v in vec2.values()))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)
    
    @staticmethod
    def text_similarity(text1, text2):
        """计算文本相似度 - 基于n-gram和余弦相似度"""
        ngrams1 = Counter(PersonalizedRecommender.get_character_ngrams(text1))
        ngrams2 = Counter(PersonalizedRecommender.get_character_ngrams(text2))
        return PersonalizedRecommender.cosine_similarity(ngrams1, ngrams2)
    
    @staticmethod
    def get_user_ingredient_preferences(user_id, limit=20):
        """获取用户的食材偏好 - 基于历史饮食记录"""
        try:
            diet_records = DietRecord.get_by_user(user_id, limit=limit)
            if not diet_records:
                return {}
            
            ingredient_counter = Counter()
            for record in diet_records:
                if record.food_name:
                    ingredient_counter[record.food_name] += 1
            
            return dict(ingredient_counter)
        except Exception as e:
            logger.error(f"获取用户食材偏好失败：{str(e)}")
            return {}
    
    @staticmethod
    def get_user_liked_recipes(user_id, limit=20):
        """获取用户喜欢的食谱 - 基于收藏记录"""
        try:
            collections = UserCollection.get_by_user(user_id, collection_type="recipe", page=1, page_size=limit)
            if not collections:
                return []
            
            recipe_ids = [c.recipe_id for c in collections if c.recipe_id]
            if not recipe_ids:
                return []
            
            recipes = Recipe.query.filter(Recipe.id.in_(recipe_ids)).all()
            return recipes
        except Exception as e:
            logger.error(f"获取用户喜欢的食谱失败：{str(e)}")
            return []
    
    @staticmethod
    def build_user_recipe_matrix(limit_users=50, limit_records=100):
        """构建用户-食谱交互矩阵 - 用于协同过滤"""
        try:
            user_recipe_matrix = defaultdict(lambda: defaultdict(int))
            
            all_records = DietRecord.query.filter(DietRecord.recipe_id > 0).limit(limit_records).all()
            
            for record in all_records:
                if record.recipe_id:
                    user_recipe_matrix[record.user_id][record.recipe_id] += 1
            
            return user_recipe_matrix
        except Exception as e:
            logger.error(f"构建用户-食谱矩阵失败：{str(e)}")
            return defaultdict(lambda: defaultdict(int))
    
    @staticmethod
    def calculate_user_similarity(user_id1, user_id2, user_recipe_matrix):
        """计算两个用户之间的相似度 - 基于Jaccard系数"""
        try:
            recipes1 = set(user_recipe_matrix[user_id1].keys())
            recipes2 = set(user_recipe_matrix[user_id2].keys())
            
            if not recipes1 or not recipes2:
                return 0.0
            
            intersection = recipes1 & recipes2
            union = recipes1 | recipes2
            
            return len(intersection) / len(union)
        except Exception as e:
            logger.error(f"计算用户相似度失败：{str(e)}")
            return 0.0
    
    @staticmethod
    def find_similar_users(user_id, user_recipe_matrix, top_k=5):
        """找到与目标用户最相似的K个用户"""
        try:
            similarities = []
            all_user_ids = list(user_recipe_matrix.keys())
            
            for other_user_id in all_user_ids:
                if other_user_id != user_id:
                    sim = PersonalizedRecommender.calculate_user_similarity(user_id, other_user_id, user_recipe_matrix)
                    if sim > 0:
                        similarities.append((other_user_id, sim))
            
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:top_k]
        except Exception as e:
            logger.error(f"查找相似用户失败：{str(e)}")
            return []
    
    @staticmethod
    def calculate_collaborative_score(recipe, user_id, user_recipe_matrix, similar_users):
        """
        计算协同过滤推荐评分
        基于相似用户的行为
        """
        try:
            if not similar_users or not recipe.id:
                return 50.0
            
            total_score = 0.0
            total_weight = 0.0
            
            for similar_user_id, similarity in similar_users:
                if recipe.id in user_recipe_matrix[similar_user_id]:
                    interaction_count = user_recipe_matrix[similar_user_id][recipe.id]
                    weight = similarity * min(interaction_count, 3)
                    total_score += weight
                    total_weight += similarity
            
            if total_weight == 0:
                return 50.0
            
            normalized_score = (total_score / total_weight) * 50
            return min(normalized_score + 50, 100)
        except Exception as e:
            logger.error(f"计算协同过滤评分失败：{str(e)}")
            return 50.0
    
    @staticmethod
    def calculate_content_based_score(recipe, user, nutrition_needs):
        """
        基于内容的推荐评分
        结合：营养匹配、食材偏好、口味匹配
        """
        score = 0
        
        target_calorie = user.target_calorie if user.target_calorie and user.target_calorie > 0 else nutrition_needs.get("calorie", 1800)
        target_protein = user.target_protein if user.target_protein and user.target_protein > 0 else nutrition_needs.get("protein", 96)
        target_carb = user.target_carb if user.target_carb and user.target_carb > 0 else nutrition_needs.get("carb", 225)
        target_fat = user.target_fat if user.target_fat and user.target_fat > 0 else nutrition_needs.get("fat", 50)
        
        meal_target_calorie = target_calorie / 3
        meal_target_protein = target_protein / 3
        meal_target_carb = target_carb / 3
        meal_target_fat = target_fat / 3
        
        calorie_diff = abs(recipe.calorie - meal_target_calorie)
        calorie_score = max(0, 30 - (calorie_diff / meal_target_calorie) * 30)
        score += calorie_score
        
        protein_diff = abs(recipe.protein - meal_target_protein)
        protein_score = max(0, 25 - (protein_diff / max(meal_target_protein, 1)) * 25)
        score += protein_score
        
        carb_diff = abs(recipe.carb - meal_target_carb)
        carb_score = max(0, 20 - (carb_diff / max(meal_target_carb, 1)) * 20)
        score += carb_score
        
        fat_diff = abs(recipe.fat - meal_target_fat)
        fat_score = max(0, 15 - (fat_diff / max(meal_target_fat, 1)) * 15)
        score += fat_score
        
        if user.health_goal == "减脂" and recipe.calorie <= meal_target_calorie:
            score += 5
        elif user.health_goal == "增肌" and recipe.protein >= meal_target_protein:
            score += 5
        else:
            score += 2.5
        
        ingredient_count = len([i for i in recipe.ingre_list.split(',') if i.strip()])
        diversity_score = min(ingredient_count / 8, 1) * 3
        score += diversity_score
        
        if hasattr(user, 'dietary_preference') and user.dietary_preference:
            if user.dietary_preference in recipe.flavor:
                score += 2
            else:
                score += 1
        else:
            score += 2
        
        return min(score, 100)
    
    @staticmethod
    def calculate_behavior_based_score(recipe, user_ingredient_preferences):
        """
        基于行为的推荐评分
        根据用户历史饮食记录中的食材偏好
        """
        if not user_ingredient_preferences:
            return 50
        
        score = 0
        recipe_ingredients = [i.strip() for i in recipe.ingre_list.split(',') if i.strip()]
        
        for ing in recipe_ingredients:
            if ing in user_ingredient_preferences:
                score += user_ingredient_preferences[ing] * 10
        
        max_possible_score = sum(user_ingredient_preferences.values()) * 10
        if max_possible_score > 0:
            score = (score / max_possible_score) * 100
        
        return min(score, 100)
    
    @staticmethod
    def calculate_similarity_based_score(recipe, user_liked_recipes=None):
        """
        基于相似度的推荐评分
        计算与用户喜欢的食谱的相似度
        """
        if not user_liked_recipes:
            return 50
        
        total_similarity = 0
        count = 0
        
        recipe_text = f"{recipe.recipe_name} {recipe.ingre_list} {recipe.flavor} {recipe.cook_type}"
        
        for liked_recipe in user_liked_recipes:
            liked_text = f"{liked_recipe.recipe_name} {liked_recipe.ingre_list} {liked_recipe.flavor} {liked_recipe.cook_type}"
            similarity = PersonalizedRecommender.text_similarity(recipe_text, liked_text)
            total_similarity += similarity
            count += 1
        
        if count > 0:
            return (total_similarity / count) * 100
        
        return 50
    
    @staticmethod
    def generate_recommendations(user, recipes, use_ai=True):
        """
        生成综合推荐 - 结合多种算法
        
        Args:
            user: 用户对象
            recipes: 食谱列表
            use_ai: 是否尝试使用AI增强推荐
            
        Returns:
            list: 推荐的食谱列表
        """
        try:
            nutrition_needs = NutritionCalculator.calculate_nutrition_needs(user)
            user_ingredient_preferences = PersonalizedRecommender.get_user_ingredient_preferences(user.id)
            user_liked_recipes = PersonalizedRecommender.get_user_liked_recipes(user.id)
            
            user_recipe_matrix = PersonalizedRecommender.build_user_recipe_matrix()
            similar_users = PersonalizedRecommender.find_similar_users(user.id, user_recipe_matrix)
            
            recipe_scores = []
            
            has_behavior_data = len(user_ingredient_preferences) > 0
            has_similarity_data = len(user_liked_recipes) > 0
            has_collaborative_data = len(similar_users) > 0
            
            if has_behavior_data and has_similarity_data and has_collaborative_data:
                content_weight = 0.35
                behavior_weight = 0.25
                similarity_weight = 0.20
                collaborative_weight = 0.20
            elif has_behavior_data and has_similarity_data:
                content_weight = 0.4
                behavior_weight = 0.35
                similarity_weight = 0.25
                collaborative_weight = 0.0
            elif has_collaborative_data:
                content_weight = 0.4
                behavior_weight = 0.1
                similarity_weight = 0.1
                collaborative_weight = 0.4
            elif has_behavior_data:
                content_weight = 0.5
                behavior_weight = 0.4
                similarity_weight = 0.1
                collaborative_weight = 0.0
            elif has_similarity_data:
                content_weight = 0.5
                behavior_weight = 0.1
                similarity_weight = 0.4
                collaborative_weight = 0.0
            else:
                content_weight = 0.7
                behavior_weight = 0.1
                similarity_weight = 0.1
                collaborative_weight = 0.1
            
            for recipe in recipes:
                content_score = PersonalizedRecommender.calculate_content_based_score(recipe, user, nutrition_needs)
                behavior_score = PersonalizedRecommender.calculate_behavior_based_score(recipe, user_ingredient_preferences)
                similarity_score = PersonalizedRecommender.calculate_similarity_based_score(recipe, user_liked_recipes)
                collaborative_score = PersonalizedRecommender.calculate_collaborative_score(recipe, user.id, user_recipe_matrix, similar_users)
                
                final_score = (content_score * content_weight) + (behavior_score * behavior_weight) + (similarity_score * similarity_weight) + (collaborative_score * collaborative_weight)
                
                recipe_scores.append((recipe, final_score, {
                    "content_score": round(content_score, 2),
                    "behavior_score": round(behavior_score, 2),
                    "similarity_score": round(similarity_score, 2),
                    "collaborative_score": round(collaborative_score, 2),
                    "weights": {
                        "content": round(content_weight, 2),
                        "behavior": round(behavior_weight, 2),
                        "similarity": round(similarity_weight, 2),
                        "collaborative": round(collaborative_weight, 2)
                    }
                }))
            
            recipe_scores.sort(key=lambda x: x[1], reverse=True)
            
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
                "score": round(r[1], 2),
                "score_detail": r[2],
                "data_available": {
                    "behavior": has_behavior_data,
                    "similarity": has_similarity_data,
                    "collaborative": has_collaborative_data
                }
            } for r in recipe_scores[:10]]
            
        except Exception as e:
            logger.error(f"生成推荐失败：{str(e)}")
            return []
