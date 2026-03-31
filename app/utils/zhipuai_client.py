import requests
import json
from loguru import logger
from app.config import ZHIPUAI_API_KEY

class ZhipuAIClient:
    """智谱AI客户端 - 使用GLM-4.7-Flash模型"""
    
    def __init__(self):
        self.api_key = ZHIPUAI_API_KEY
        self.base_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        self.model = "GLM-4.7-Flash"
    
    def chat(self, messages, temperature=0.7, max_tokens=2000):
        """
        调用智谱AI进行对话
        
        Args:
            messages (list): 消息列表，格式如 [{"role": "user", "content": "你好"}]
            temperature (float): 温度参数，0-1之间
            max_tokens (int): 最大生成token数
            
        Returns:
            str: AI的回复内容
        """
        if not self.api_key or self.api_key == "your_zhipuai_api_key":
            logger.warning("智谱AI API Key未配置，使用模拟响应")
            return self._mock_response(messages)
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            logger.info(f"调用智谱AI，模型: {self.model}")
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                logger.info("智谱AI调用成功")
                return ai_response
            else:
                logger.error(f"智谱AI调用失败: {response.status_code} - {response.text}")
                return self._mock_response(messages)
                
        except Exception as e:
            logger.error(f"智谱AI调用异常: {str(e)}")
            return self._mock_response(messages)
    
    def generate_recipe_recommendation(self, user_profile, recipes):
        """
        生成个性化食谱推荐
        
        Args:
            user_profile (dict): 用户信息
            recipes (list): 食谱列表
            
        Returns:
            str: AI生成的推荐内容
        """
        user_info = f"""
        用户信息：
        - 年龄：{user_profile.get('age', '未知')}岁
        - 性别：{user_profile.get('gender', '未知')}
        - 身高：{user_profile.get('height', '未知')}cm
        - 体重：{user_profile.get('weight', '未知')}kg
        - 健康目标：{user_profile.get('health_goal', '维持')}
        - 饮食偏好：{user_profile.get('dietary_preference', '无特殊偏好')}
        """
        
        recipes_info = "\n".join([
            f"{i+1}. {r.get('recipe_name', '未知')} - 热量:{r.get('calorie', 0)}kcal, "
            f"蛋白质:{r.get('protein', 0)}g, 碳水:{r.get('carb', 0)}g, 脂肪:{r.get('fat', 0)}g"
            for i, r in enumerate(recipes[:5])
        ])
        
        prompt = f"""
        你是一位专业的营养师。请根据以下用户信息，从给出的食谱中为用户推荐最合适的3个食谱，并简要说明推荐理由。
        
        {user_info}
        
        可选食谱：
        {recipes_info}
        
        请以JSON格式返回，格式如下：
        {{
            "recommendations": [
                {{
                    "rank": 1,
                    "recipe_name": "食谱名称",
                    "reason": "推荐理由"
                }}
            ]
        }}
        """
        
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, temperature=0.3, max_tokens=1000)
    
    def generate_handbook_content(self, topic, mood="开心"):
        """
        生成手账内容
        
        Args:
            topic (str): 手账主题
            mood (str): 心情
            
        Returns:
            str: AI生成的手账内容
        """
        prompt = f"""
        请帮我写一段关于"{topic}"的手账内容，心情是{mood}。
        要求：
        1. 内容温馨、积极向上
        2. 100-200字左右
        3. 适合记录在健康饮食手账中
        """
        
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, temperature=0.8, max_tokens=500)
    
    def analyze_nutrition(self, food_name):
        """
        分析食物营养
        
        Args:
            food_name (str): 食物名称
            
        Returns:
            str: 营养分析内容
        """
        prompt = f"""
        请分析"{food_name}"的营养价值，包括：
        1. 主要营养成分
        2. 健康功效
        3. 适合人群
        4. 食用建议
        
        请用简洁明了的语言回答，200字以内。
        """
        
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, temperature=0.5, max_tokens=400)
    
    def _mock_response(self, messages):
        """模拟响应 - 当API Key未配置时使用"""
        logger.info("使用模拟响应")
        return "这是一个模拟的AI响应。请配置智谱AI API Key以获得真实的AI服务。"

# 全局客户端实例
_zhipuai_client = None

def get_zhipuai_client():
    """获取智谱AI客户端单例"""
    global _zhipuai_client
    if _zhipuai_client is None:
        _zhipuai_client = ZhipuAIClient()
    return _zhipuai_client
