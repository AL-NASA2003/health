import requests
import json
import base64
from loguru import logger
from app.config import ZHIPUAI_API_KEY

class ZhipuAIClient:
    """智谱AI客户端 - 支持GLM-4.7-Flash、GLM-4.6V-Flash、GLM-4.1V-Thinking-Flash和CogView-3-Flash"""
    
    def __init__(self):
        self.api_key = ZHIPUAI_API_KEY
        self.base_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        self.image_generate_url = "https://open.bigmodel.cn/api/paas/v4/images/generations"
        self.model = "GLM-4.7-Flash"
        self.vision_model = "GLM-4.6V-Flash"
        self.vision_thinking_model = "GLM-4.1V-Thinking-Flash"
        self.image_model = "cogview-3-flash"
    
    def chat(self, messages, temperature=0.7, max_tokens=2000, use_vision=False, use_thinking=False):
        """
        调用智谱AI进行对话
        
        Args:
            messages (list): 消息列表，格式如 [{"role": "user", "content": "你好"}]
            temperature (float): 温度参数，0-1之间
            max_tokens (int): 最大生成token数
            use_vision (bool): 是否使用视觉模型
            use_thinking (bool): 是否使用思维链视觉模型
            
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
            
            model_to_use = self.model
            if use_thinking:
                model_to_use = self.vision_thinking_model
            elif use_vision:
                model_to_use = self.vision_model
            
            payload = {
                "model": model_to_use,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            logger.info(f"调用智谱AI，模型: {payload['model']}")
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    if "message" in result["choices"][0]:
                        ai_response = result["choices"][0]["message"]["content"]
                        logger.info("智谱AI调用成功")
                        return ai_response
                logger.error(f"响应格式异常: {result}")
                return self._mock_response(messages)
            else:
                logger.error(f"智谱AI调用失败: {response.status_code} - {response.text}")
                return self._mock_response(messages)
                
        except Exception as e:
            logger.error(f"智谱AI调用异常: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return self._mock_response(messages)
    
    def generate_image(self, prompt, size="1024x1024", style=None):
        """
        使用CogView-3-Flash生成图片
        
        Args:
            prompt (str): 图片描述
            size (str): 图片尺寸，推荐值：1024x1024, 768x1344, 864x1152, 1344x768, 1152x864, 1440x720, 720x1440
            style (str): 风格描述（可选）
            
        Returns:
            dict: 包含图片URL的字典
        """
        if not self.api_key or self.api_key == "your_zhipuai_api_key":
            logger.warning("智谱AI API Key未配置，使用模拟响应")
            return self._mock_image_generate(prompt)
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            full_prompt = prompt
            if style:
                full_prompt = f"{style}, {style}"
            
            payload = {
                "model": self.image_model,
                "prompt": full_prompt,
                "size": size
            }
            
            logger.info(f"开始生成图片，模型: {self.image_model}")
            response = requests.post(
                self.image_generate_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if "data" in result and len(result["data"]) > 0:
                    image_url = result["data"][0]["url"]
                    logger.info(f"图片生成成功: {image_url}")
                    return {
                        "success": True,
                        "image_url": image_url,
                        "model": self.image_model,
                        "prompt": prompt
                    }
                else:
                    logger.error(f"图片生成响应格式异常: {result}")
                    return self._mock_image_generate(prompt)
            else:
                logger.error(f"图片生成失败: {response.status_code} - {response.text}")
                return self._mock_image_generate(prompt)
                
        except Exception as e:
            logger.error(f"图片生成异常: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return self._mock_image_generate(prompt)
    
    def analyze_food_image(self, image_url=None, image_path=None, use_thinking=True):
        """
        分析美食图片，进行识别和分类
        
        Args:
            image_url (str): 图片URL
            image_path (str): 本地图片路径
            use_thinking (bool): 是否使用思维链模型进行更深入分析
            
        Returns:
            dict: 分析结果，包含食物名称、分类、营养信息等
        """
        if not self.api_key or self.api_key == "your_zhipuai_api_key":
            logger.warning("智谱AI API Key未配置，使用模拟响应")
            return self._mock_food_analysis()
        
        try:
            # 构建图片内容
            image_content = None
            if image_path:
                # 读取本地图片并编码为base64
                with open(image_path, 'rb') as f:
                    image_base64 = base64.b64encode(f.read()).decode('utf-8')
                    image_content = f"data:image/jpeg;base64,{image_base64}"
            elif image_url:
                image_content = image_url
            
            if not image_content:
                logger.error("没有提供图片URL或路径")
                return self._mock_food_analysis()
            
            # 构建消息
            thinking_prompt = """请分析这张美食图片，以JSON格式返回以下信息：
{
    "food_name": "菜品名称",
    "food_type": "菜品分类（如：主食、菜式、水果、零食、饮品等）",
    "cuisine": "菜系（如：中式、西式、日式、韩式、泰式等）",
    "ingredients": ["主要食材1", "主要食材2"],
    "taste": "口味描述",
    "nutrition_estimate": {
        "calorie": 400,
        "protein": 25,
        "carb": 30,
        "fat": 20
    },
    "is_healthy": true/false,
    "health_rating": 3
}
注意：只返回JSON，不要返回其他内容。"""
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": thinking_prompt},
                        {"type": "image_url", "image_url": {"url": image_content}}
                    ]
                }
            ]
            
            model_name = self.vision_thinking_model if use_thinking else self.vision_model
            logger.info(f"开始分析美食图片，模型: {model_name}")
            response = self.chat(messages, temperature=0.3, max_tokens=2000, 
                                 use_vision=True, use_thinking=use_thinking)
            
            # 尝试解析JSON
            try:
                # 清理响应内容
                response_clean = response.strip()
                if response_clean.startswith('```json'):
                    response_clean = response_clean[7:]
                if response_clean.startswith('```'):
                    response_clean = response_clean[3:]
                if response_clean.endswith('```'):
                    response_clean = response_clean[:-3]
                
                result = json.loads(response_clean.strip())
                logger.info(f"美食图片分析成功: {result.get('food_name')}")
                return result
            except Exception as e:
                logger.error(f"解析分析结果失败: {str(e)}")
                logger.error(f"原始响应: {response}")
                return self._mock_food_analysis()
                
        except Exception as e:
            logger.error(f"美食图片分析异常: {str(e)}")
            return self._mock_food_analysis()
    
    def _mock_food_analysis(self):
        """模拟美食图片分析响应"""
        logger.info("使用模拟美食分析响应")
        return {
            "food_name": "美味佳肴",
            "food_type": "菜式",
            "cuisine": "中式",
            "ingredients": ["肉类", "蔬菜"],
            "taste": "咸鲜可口",
            "nutrition_estimate": {
                "calorie": 400,
                "protein": 25,
                "carb": 30,
                "fat": 20
            },
            "is_healthy": True,
            "health_rating": 3
        }
    
    def _mock_image_generate(self, prompt):
        """模拟图片生成响应"""
        logger.info("使用模拟图片生成响应")
        prompt_encoded = prompt.replace(' ', '_')[:30]
        return {
            "success": True,
            "image_url": f"https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt={prompt_encoded}&image_size=square_hd",
            "model": "mock_image_generator",
            "prompt": prompt
        }
    
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
        """模拟响应 - 当API Key未配置或调用失败时使用"""
        logger.info("使用模拟响应")
        
        if messages and len(messages) > 0:
            content = messages[-1].get("content", "")
            
            if isinstance(content, list):
                # 多模态请求，提取文本
                text_parts = [c.get("text", "") for c in content if c.get("type") == "text"]
                content = " ".join(text_parts)
            
            if "饮食" in content or "健康" in content:
                return """健康饮食对我们的身体至关重要。它能提供充足的营养，维持我们的免疫系统，预防慢性疾病，并帮助保持适当的体重。

建议多吃水果、蔬菜、全谷物和瘦肉蛋白，同时限制加工食品、过多的盐和糖的摄入。记得保持饮食的多样性，这样才能获得全面的营养。"""
            elif "食谱" in content or "菜谱" in content:
                return """一份健康的食谱应该包含适当的营养平衡。可以考虑做一份蔬菜沙拉配烤鸡胸肉，清爽又健康。

搭配一些粗粮主食和适量的水果，就能构成一顿营养完整的美味佳肴。记得少油少盐，健康第一！"""
        
        return "这是一个模拟的AI响应。请配置智谱AI API Key以获得真实的AI服务。"

# 全局客户端实例
_zhipuai_client = None

def get_zhipuai_client():
    """获取智谱AI客户端单例"""
    global _zhipuai_client
    if _zhipuai_client is None:
        _zhipuai_client = ZhipuAIClient()
    return _zhipuai_client
