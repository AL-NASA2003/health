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
    
    # ============ 公式1：本地加权评分公式 ============
    
    @staticmethod
    def calculate_nutrient_match_score(recipe_nutrient, target_nutrient):
        """
        计算单一营养素匹配度
        S_nutrient = max(0, 1 - |recipe_nutrient - target_nutrient| / target_nutrient)
        """
        if target_nutrient <= 0:
            return 0.0
        diff = abs(recipe_nutrient - target_nutrient)
        return max(0.0, 1.0 - (diff / target_nutrient))
    
    @staticmethod
    def calculate_health_goal_bonus(recipe, health_goal):
        """
        健康目标加分项 P_goal
        - 减脂目标：calorie <= 300 → 加5分
        - 增肌目标：protein >= 15 → 加5分
        - 其他：加0分
        """
        if health_goal == "减脂" and recipe.calorie <= 300:
            return 5.0
        elif health_goal == "增肌" and recipe.protein >= 15:
            return 5.0
        else:
            return 0.0
    
    @staticmethod
    def calculate_local_weighted_score(recipe, user, nutrition_needs):
        """
        本地加权评分公式 Score_local = w1*S_calorie + w2*S_protein + w3*S_carb + w4*S_fat + w5*P_goal
        其中 w1+w2+w3+w4+w5 = 1（归一化）
        """
        # 设置权重系数（归一化）
        w1 = 0.30  # 热量权重
        w2 = 0.25  # 蛋白质权重
        w3 = 0.20  # 碳水权重
        w4 = 0.15  # 脂肪权重
        w5 = 0.10  # 健康目标权重
        
        # 每餐目标营养素（每日目标/3）
        target_calorie = user.target_calorie if user.target_calorie and user.target_calorie > 0 else nutrition_needs.get("calorie", 1800)
        target_protein = user.target_protein if user.target_protein and user.target_protein > 0 else nutrition_needs.get("protein", 96)
        target_carb = user.target_carb if user.target_carb and user.target_carb > 0 else nutrition_needs.get("carb", 225)
        target_fat = user.target_fat if user.target_fat and user.target_fat > 0 else nutrition_needs.get("fat", 50)
        
        meal_target_calorie = target_calorie / 3
        meal_target_protein = target_protein / 3
        meal_target_carb = target_carb / 3
        meal_target_fat = target_fat / 3
        
        # 计算各营养素匹配度
        s_calorie = PersonalizedRecommender.calculate_nutrient_match_score(recipe.calorie, meal_target_calorie)
        s_protein = PersonalizedRecommender.calculate_nutrient_match_score(recipe.protein, meal_target_protein)
        s_carb = PersonalizedRecommender.calculate_nutrient_match_score(recipe.carb, meal_target_carb)
        s_fat = PersonalizedRecommender.calculate_nutrient_match_score(recipe.fat, meal_target_fat)
        
        # 计算健康目标加分
        p_goal = PersonalizedRecommender.calculate_health_goal_bonus(recipe, user.health_goal)
        
        # 计算最终评分（归一化到0-100）
        base_score = (w1 * s_calorie + w2 * s_protein + w3 * s_carb + w4 * s_fat) * 100
        bonus_score = p_goal
        
        return base_score + bonus_score
    
    # ============ 公式2：AI推荐相似度计算 ============
    
    @staticmethod
    def build_user_embedding_vector(user, nutrition_needs):
        """
        构建用户画像嵌入向量
        包含：年龄、性别、身高、体重、健康目标、饮食偏好、营养需求
        """
        embedding = {}
        
        # 年龄特征
        if user.age:
            age_normalized = min(user.age / 100.0, 1.0)
            embedding["age"] = age_normalized
        
        # 性别特征
        embedding["gender_male"] = 1.0 if user.gender == 1 else 0.0
        embedding["gender_female"] = 1.0 if user.gender == 0 else 0.0
        
        # 身高体重特征
        if user.height:
            embedding["height"] = user.height / 250.0
        if user.weight:
            embedding["weight"] = user.weight / 200.0
        
        # 健康目标特征
        health_goals = ["减脂", "增肌", "维持"]
        for goal in health_goals:
            embedding[f"goal_{goal}"] = 1.0 if user.health_goal == goal else 0.0
        
        # 营养需求特征
        target_calorie = user.target_calorie if user.target_calorie and user.target_calorie > 0 else nutrition_needs.get("calorie", 1800)
        target_protein = user.target_protein if user.target_protein and user.target_protein > 0 else nutrition_needs.get("protein", 96)
        target_carb = user.target_carb if user.target_carb and user.target_carb > 0 else nutrition_needs.get("carb", 225)
        target_fat = user.target_fat if user.target_fat and user.target_fat > 0 else nutrition_needs.get("fat", 50)
        
        embedding["target_calorie"] = target_calorie / 5000.0
        embedding["target_protein"] = target_protein / 300.0
        embedding["target_carb"] = target_carb / 500.0
        embedding["target_fat"] = target_fat / 200.0
        
        return embedding
    
    @staticmethod
    def build_recipe_embedding_vector(recipe):
        """
        构建食谱特征嵌入向量
        包含：营养素、口味、烹饪方式、菜系、难度
        """
        embedding = {}
        
        # 营养素特征
        embedding["calorie"] = recipe.calorie / 1000.0
        embedding["protein"] = recipe.protein / 100.0
        embedding["carb"] = recipe.carb / 200.0
        embedding["fat"] = recipe.fat / 100.0
        
        # 口味特征
        flavors = ["清淡", "麻辣", "甜", "咸", "酸", "鲜"]
        for flavor in flavors:
            embedding[f"flavor_{flavor}"] = 1.0 if recipe.flavor == flavor else 0.0
        
        # 烹饪方式特征
        cook_types = ["炒", "煮", "蒸", "烤", "煎", "炖"]
        for ct in cook_types:
            embedding[f"cook_type_{ct}"] = 1.0 if recipe.cook_type == ct else 0.0
        
        # 菜系特征
        cuisines = ["中式", "西式", "日式", "韩式"]
        for cuisine in cuisines:
            embedding[f"cuisine_{cuisine}"] = 1.0 if recipe.cuisine == cuisine else 0.0
        
        # 难度特征
        difficulties = ["简单", "中等", "困难"]
        for diff in difficulties:
            embedding[f"difficulty_{diff}"] = 1.0 if recipe.difficulty == diff else 0.0
        
        return embedding
    
    @staticmethod
    def calculate_cosine_similarity_embedding(vec1, vec2):
        """
        计算两个嵌入向量的余弦相似度
        Similarity = (u · r) / (||u|| * ||r||)
        """
        all_keys = set(vec1.keys()) | set(vec2.keys())
        
        # 计算点积
        dot_product = 0.0
        for key in all_keys:
            dot_product += vec1.get(key, 0.0) * vec2.get(key, 0.0)
        
        # 计算二范数
        norm1 = math.sqrt(sum(v**2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v**2 for v in vec2.values()))
        
        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    @staticmethod
    def calculate_ai_similarity_score(recipe, user, nutrition_needs):
        """
        计算AI推荐相似度评分
        基于用户画像和食谱特征的余弦相似度
        """
        user_embedding = PersonalizedRecommender.build_user_embedding_vector(user, nutrition_needs)
        recipe_embedding = PersonalizedRecommender.build_recipe_embedding_vector(recipe)
        similarity = PersonalizedRecommender.calculate_cosine_similarity_embedding(user_embedding, recipe_embedding)
        return similarity * 100.0
    
    # ============ 其他辅助方法 ============
    
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
            
            for recipe in recipes:
                # 使用新的本地加权评分公式
                local_weighted_score = PersonalizedRecommender.calculate_local_weighted_score(recipe, user, nutrition_needs)
                
                # 使用新的AI相似度评分
                ai_similarity_score = PersonalizedRecommender.calculate_ai_similarity_score(recipe, user, nutrition_needs)
                
                # 其他评分
                behavior_score = PersonalizedRecommender.calculate_behavior_based_score(recipe, user_ingredient_preferences)
                similarity_score = PersonalizedRecommender.calculate_similarity_based_score(recipe, user_liked_recipes)
                collaborative_score = PersonalizedRecommender.calculate_collaborative_score(recipe, user.id, user_recipe_matrix, similar_users)
                
                # 综合评分权重
                local_weight = 0.50  # 本地加权评分权重
                ai_weight = 0.30  # AI相似度权重
                behavior_weight = 0.10  # 行为评分权重
                collaborative_weight = 0.10  # 协同过滤权重
                
                final_score = (local_weighted_score * local_weight +
                              ai_similarity_score * ai_weight +
                              behavior_score * behavior_weight +
                              collaborative_score * collaborative_weight)
                
                recipe_scores.append((recipe, final_score, {
                    "local_weighted_score": round(local_weighted_score, 2),
                    "ai_similarity_score": round(ai_similarity_score, 2),
                    "behavior_score": round(behavior_score, 2),
                    "similarity_score": round(similarity_score, 2),
                    "collaborative_score": round(collaborative_score, 2)
                }))
            
            recipe_scores.sort(key=lambda x: x[1], reverse=True)
            
            # 确保返回的食谱包含图片等所有字段
            result = []
            for r in recipe_scores[:10]:
                recipe_dict = r[0].to_dict()
                recipe_dict["score"] = round(r[1], 2)
                recipe_dict["score_detail"] = r[2]
                recipe_dict["data_available"] = {
                    "behavior": has_behavior_data,
                    "similarity": has_similarity_data,
                    "collaborative": has_collaborative_data
                }
                result.append(recipe_dict)
            
            return result
            
        except Exception as e:
            logger.error(f"生成推荐失败：{str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []
