import re
import jieba
import jieba.analyse
import json
from collections import Counter
import pandas as pd
from loguru import logger
from app.utils.text_utils import calculate_hotness_score

class FoodDataProcessor:
    """美食数据处理器"""
    
    def __init__(self):
        # 菜品关键词词典
        self.food_keywords = {
            "红烧肉": ["红烧肉", "红烧猪肉", "东坡肉", "扣肉"],
            "拉面": ["拉面", "日式拉面", "兰州拉面", "牛肉拉面"],
            "火锅": ["火锅", "麻辣火锅", "涮锅", "海底捞"],
            "披萨": ["披萨", "pizza", "意式披萨", "芝士披萨"],
            "寿司": ["寿司", "刺身", "日本料理", "手握寿司"],
            "烤肉": ["烤肉", "烧烤", "BBQ", "韩式烤肉"],
            "炸鸡": ["炸鸡", "韩式炸鸡", "啤酒炸鸡"],
            "奶茶": ["奶茶", "珍珠奶茶", "奶盖茶", "果茶"],
            "蛋糕": ["蛋糕", "生日蛋糕", "奶油蛋糕", "慕斯蛋糕"],
            "冰淇淋": ["冰淇淋", "雪糕", "冰棍", "冰棒"],
            "沙拉": ["沙拉", "蔬菜沙拉", "水果沙拉", "凯撒沙拉"],
            "三明治": ["三明治", "汉堡", "热狗", "帕尼尼"],
            "意面": ["意面", "意大利面", "番茄意面", " Alfredo意面"],
            "炒饭": ["炒饭", "蛋炒饭", "扬州炒饭", "海鲜炒饭"],
            "汤": ["汤", "鸡汤", "排骨汤", "番茄汤"],
            "饺子": ["饺子", "水饺", "蒸饺", "煎饺"],
            "包子": ["包子", "肉包", "菜包", "豆沙包"],
            "油条": ["油条", "油炸鬼", "油馍"],
            "豆浆": ["豆浆", "黄豆浆", "黑豆浆"],
            "粥": ["粥", "白粥", "小米粥", "八宝粥"]
        }
        
        # 停用词列表
        self.stop_words = set([
            "的", "了", "是", "在", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这",
            "美食", "好吃", "推荐", "超级", "非常", "特别", "喜欢", "爱", "棒", "赞", "绝", "绝了", "太", "很", "真", "好", "不错", "味道", "口感", "感觉", "觉得", "体验", "分享", "种草", "打卡"
        ])
    
    def clean_text(self, text):
        """清洗文本"""
        if not text:
            return ""
        # 去除特殊字符
        text = re.sub(r'[\s\n\r\t]+', ' ', text)
        text = re.sub(r'[^一-龥a-zA-Z0-9]', ' ', text)
        # 去除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def extract_keywords(self, text, topK=20):
        """提取关键词"""
        if not text:
            return []
        # 清洗文本
        cleaned_text = self.clean_text(text)
        if not cleaned_text:
            return []
        # 使用jieba提取关键词
        keywords = jieba.analyse.extract_tags(cleaned_text, topK=topK, withWeight=True)
        # 过滤停用词
        filtered_keywords = [(word, weight) for word, weight in keywords if word not in self.stop_words]
        return filtered_keywords
    
    def classify_food(self, text):
        """将文本归类到具体菜品"""
        if not text:
            return "其他"
        # 清洗文本
        cleaned_text = self.clean_text(text)
        if not cleaned_text:
            return "其他"
        # 计算每个菜品的匹配度
        scores = {}
        for food, keywords in self.food_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in cleaned_text:
                    score += 1
            if score > 0:
                scores[food] = score
        # 返回得分最高的菜品
        if scores:
            return max(scores, key=scores.get)
        return "其他"
    
    def extract_food_from_description(self, description):
        """从图片描述中提取菜品名称"""
        if not description:
            return "其他"
        
        # 清洗描述文本
        cleaned_desc = self.clean_text(description)
        
        # 遍历菜品关键词，尝试匹配
        for food, keywords in self.food_keywords.items():
            for keyword in keywords:
                if keyword in cleaned_desc:
                    return food
        
        # 如果没有匹配到，返回一个默认菜品类型
        return "美食"
    
    def calculate_hotness_score(self, title, likes, comments, collection):
        """计算热度评分（简化版）"""
        # 直接使用本地计算
        return calculate_hotness_score(likes, comments, collection)
    
    def get_image_description(self, image_url):
        """获取图片描述（简化版，返回空字符串）"""
        # 移除图片识别功能
        logger.warning(f"图片识别功能已禁用：{image_url}")
        return ""
    
    def get_personalized_recipes(self, ingredients, health_goals, calorie_limit):
        """获取个性化菜谱推荐（简化版，返回空列表）"""
        # 移除 AI 菜谱生成功能
        logger.warning(f"AI 菜谱生成功能已禁用")
        return []
    
    def process_ingredient_based_recipes(self, ingredients, search_results, health_goals, calorie_limit):
        """处理基于食材的搜索结果并生成个性化推荐"""
        if not ingredients:
            return []
        
        # 1. 处理搜索结果
        processed_results = []
        if search_results:
            for item in search_results:
                # 计算热度评分
                title = item.get('title', '')
                likes = item.get('likes', 0)
                comments = item.get('comments', 0)
                collection = item.get('collection', 0)
                hotness_score = self.calculate_hotness_score(title, likes, comments, collection)
                
                # 优先使用图片识别结果
                image_description = item.get('image_description', '')
                if not image_description and item.get('images'):
                    image_url = item['images'][0]
                    image_description = self.get_image_description(image_url)
                    item['image_description'] = image_description
                
                # 合并文本
                text = image_description if image_description else (title + ' ' + ' '.join(item.get('tags', [])))
                
                # 提取关键词
                keywords = self.extract_keywords(text)
                
                # 归类菜品
                food_type = self.classify_food(text)
                if food_type == "其他" and image_description:
                    food_type = self.extract_food_from_description(image_description)
                
                # 添加处理后的字段
                processed_item = item.copy()
                processed_item['keywords'] = [kw[0] for kw in keywords]
                processed_item['food_type'] = food_type
                processed_item['hotness_score'] = hotness_score
                processed_results.append(processed_item)
            
            # 按热度排序
            processed_results.sort(key=lambda x: x.get('hotness_score', 0), reverse=True)
        
        # 2. 生成个性化菜谱
        personalized_recipes = self.get_personalized_recipes(ingredients, health_goals, calorie_limit)
        
        # 3. 合并结果
        final_results = {
            'search_results': processed_results[:10],  # 取前10个搜索结果
            'personalized_recipes': personalized_recipes
        }
        
        return final_results
    
    def process_hot_foods(self, hot_items):
        """处理热点美食数据"""
        if not hot_items:
            return []
        
        processed_items = []
        for item in hot_items:
            # 1. 计算热度评分
            title = item.get('title', '')
            likes = item.get('likes', 0)
            comments = item.get('comments', 0)
            collection = item.get('collection', 0)
            hotness_score = self.calculate_hotness_score(title, likes, comments, collection)
            
            # 2. 优先使用图片识别结果进行分类
            image_description = item.get('image_description', '')
            if not image_description and item.get('images'):
                # 尝试获取图片描述（使用本地方法）
                image_url = item['images'][0]
                image_description = self.get_image_description(image_url)
                item['image_description'] = image_description
            
            # 3. 合并文本（图片描述优先）
            text = image_description if image_description else (title + ' ' + ' '.join(item.get('tags', [])))
            
            # 4. 提取关键词
            keywords = self.extract_keywords(text)
            
            # 5. 归类到具体菜品（避免分类为其他）
            food_type = self.classify_food(text)
            if food_type == "其他" and image_description:
                # 尝试从图片描述中提取菜品名称
                food_type = self.extract_food_from_description(image_description)
            
            # 6. 添加处理后的字段
            processed_item = item.copy()
            processed_item['keywords'] = [kw[0] for kw in keywords]
            processed_item['food_type'] = food_type
            processed_item['hotness_score'] = hotness_score
            processed_items.append(processed_item)
        
        # 按热度评分排序
        processed_items.sort(key=lambda x: x.get('hotness_score', 0), reverse=True)
        
        return processed_items
    
    def process_comments(self, comments):
        """处理评论数据"""
        if not comments:
            return []
        
        processed_comments = []
        for comment in comments:
            # 清洗评论内容
            cleaned_content = self.clean_text(comment.get('content', ''))
            # 提取关键词
            keywords = self.extract_keywords(cleaned_content, topK=10)
            # 添加处理后的字段
            processed_comment = comment.copy()
            processed_comment['cleaned_content'] = cleaned_content
            processed_comment['keywords'] = [kw[0] for kw in keywords]
            processed_comments.append(processed_comment)
        
        return processed_comments
    
    def get_food_statistics(self, processed_items):
        """获取菜品统计数据"""
        if not processed_items:
            return {}
        
        # 统计菜品分布
        food_counter = Counter([item.get('food_type', '其他') for item in processed_items])
        
        # 统计关键词
        all_keywords = []
        for item in processed_items:
            all_keywords.extend(item.get('keywords', []))
        keyword_counter = Counter(all_keywords)
        
        # 统计评论数、点赞数和热度评分
        total_comments = sum(item.get('comments', 0) for item in processed_items)
        total_likes = sum(item.get('likes', 0) for item in processed_items)
        total_hotness = sum(item.get('hotness_score', 0) for item in processed_items)
        
        statistics = {
            'food_distribution': dict(food_counter),
            'top_keywords': dict(keyword_counter.most_common(20)),
            'total_items': len(processed_items),
            'total_comments': total_comments,
            'total_likes': total_likes,
            'total_hotness': total_hotness,
            'average_likes': round(total_likes / len(processed_items), 2) if processed_items else 0,
            'average_hotness': round(total_hotness / len(processed_items), 2) if processed_items else 0
        }
        
        return statistics
    
    def save_statistics_to_excel(self, statistics, filename="food_statistics.xlsx"):
        """保存统计数据到Excel"""
        try:
            # 创建DataFrame
            data = []
            
            # 菜品分布
            for food, count in statistics.get('food_distribution', {}).items():
                data.append([food, count, 'food_distribution'])
            
            # 关键词
            for keyword, count in statistics.get('top_keywords', {}).items():
                data.append([keyword, count, 'keywords'])
            
            df = pd.DataFrame(data, columns=['名称', '数量', '类型'])
            
            # 保存到Excel
            df.to_excel(filename, index=False)
            logger.info(f"统计数据已保存到 {filename}")
            return filename
        except Exception as e:
            logger.error(f"保存统计数据失败：{str(e)}")
            return None
    
    def merge_similar_keywords(self, keywords):
        """合并相似关键词"""
        if not keywords:
            return {}
        
        # 简单的相似词合并规则
        similar_groups = {
            "好吃": ["好吃", "美味", "好吃到爆", "超好吃"],
            "推荐": ["推荐", "强烈推荐", "种草", "安利"],
            "喜欢": ["喜欢", "爱", "大爱", "超爱"],
            "口感": ["口感", "味道", "口感好", "味道好"],
            "性价比": ["性价比", "划算", "便宜", "实惠"],
            "环境": ["环境", "氛围", "环境好", "氛围好"],
            "服务": ["服务", "服务好", "态度好", "服务周到"]
        }
        
        merged_keywords = {}
        for group, similar_words in similar_groups.items():
            count = 0
            for word in similar_words:
                if word in keywords:
                    count += keywords[word]
            if count > 0:
                merged_keywords[group] = count
        
        # 添加未匹配的关键词
        for word, count in keywords.items():
            found = False
            for similar_words in similar_groups.values():
                if word in similar_words:
                    found = True
                    break
            if not found:
                merged_keywords[word] = count
        
        return merged_keywords

def process_food_data(hot_items):
    """处理美食数据的主函数"""
    processor = FoodDataProcessor()
    
    # 处理热点美食数据
    processed_items = processor.process_hot_foods(hot_items)
    
    # 获取统计数据
    statistics = processor.get_food_statistics(processed_items)
    
    # 合并相似关键词
    statistics['top_keywords'] = processor.merge_similar_keywords(statistics.get('top_keywords', {}))
    
    # 保存统计数据
    processor.save_statistics_to_excel(statistics)
    
    return processed_items, statistics