import json
import base64
import time
from loguru import logger
from app.config import (
    ZHIPUAI_API_KEY,
    ZHIPUAI_BASE_URL,
    ZHIPUAI_CHAT_MODEL,
    ZHIPUAI_VISION_MODEL,
    ZHIPUAI_THINKING_MODEL,
    ZHIPUAI_IMAGE_MODEL,
    ZHIPUAI_EMBEDDING_MODEL,
    ZHIPUAI_RERANK_MODEL
)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    logger.warning("OpenAI SDK不可用，将使用备用方式")
    OPENAI_AVAILABLE = False

try:
    from zhipuai import ZhipuAI
    ZHIPUAI_SDK_AVAILABLE = True
except ImportError:
    logger.warning("ZhipuAI SDK不可用，将使用备用方式")
    ZHIPUAI_SDK_AVAILABLE = False


class ZhipuAIClient:
    """智谱AI客户端 - 使用智谱免费模型 - 完整API支持
    
    支持功能:
    - 对话补全（glm-4.7）
    - 图像识别（glm-4.6v-flash）
    - 图像生成（cogview-3-flash）
    - 文本嵌入（embedding-2）
    - 文本重排序（rerank）
    - 文档解析（glm-ocr）
    """
    
    def __init__(self):
        self.api_key = ZHIPUAI_API_KEY
        self.base_url = ZHIPUAI_BASE_URL
        self.image_base_url = "https://open.bigmodel.cn/api/paas/v4/images/generations"
        
        # 免费模型配置
        self.chat_model = ZHIPUAI_CHAT_MODEL
        self.vision_model = ZHIPUAI_VISION_MODEL
        self.thinking_model = ZHIPUAI_THINKING_MODEL
        self.image_model = ZHIPUAI_IMAGE_MODEL
        self.embedding_model = ZHIPUAI_EMBEDDING_MODEL
        self.rerank_model = ZHIPUAI_RERANK_MODEL
        
        self.client = None
        self.zhipu_client = None
        
        if self.api_key and self.api_key != 'your_zhipuai_api_key':
            if OPENAI_AVAILABLE:
                try:
                    self.client = OpenAI(
                        api_key=self.api_key,
                        base_url=self.base_url
                    )
                    logger.info(f"智谱AI客户端初始化成功(OpenAI SDK)")
                except Exception as e:
                    logger.warning(f"OpenAI SDK初始化失败: {e}")
            
            if ZHIPUAI_SDK_AVAILABLE and not self.client:
                try:
                    self.zhipu_client = ZhipuAI(api_key=self.api_key)
                    logger.info(f"智谱AI客户端初始化成功(ZhipuAI SDK)")
                except Exception as e:
                    logger.warning(f"ZhipuAI SDK初始化失败: {e}")
    
    def chat(self, messages, temperature=0.7, max_tokens=2000, 
             use_vision=False, use_thinking=False, stream=False):
        """调用智谱AI进行对话
        
        Args:
            messages(list):消息列表
            temperature(float):温度参数
            max_tokens(int):最大生成token数量
            use_vision(bool):是否使用视觉模型
            use_thinking(bool):是否使用思维链
            stream(bool):是否流式输出
        Returns:
            str:AI回复内容
        """
        if not self.api_key or self.api_key == 'your_zhipuai_api_key':
            logger.warning("智谱AI API Key未配置，使用模拟响应")
            return self._mock_response(messages)
        
        try:
            # 选择模型
            model = self.chat_model
            if use_thinking:
                model = self.thinking_model
            elif use_vision:
                model = self.vision_model
            
            logger.info(f"调用智谱AI，模型: {model}")
            
            extra_body = {}
            if use_thinking:
                extra_body = {
                    "thinking": {
                        "type": "enabled"
                    }
                }
            
            # 首选OpenAI SDK
            if self.client:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream,
                    extra_body=extra_body
                )
                
                if stream:
                    return self._handle_stream(response)
                
                if response.choices and len(response.choices) > 0:
                    ai_response = response.choices[0].message.content
                    logger.info(f"智谱AI调用成功(OpenAI SDK)")
                    return ai_response
            
            # 备选智谱AI SDK
            elif self.zhipu_client:
                response = self.zhipu_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream
                )
                
                if stream:
                    return self._handle_stream(response)
                
                if response.choices and len(response.choices) > 0:
                    ai_response = response.choices[0].message.content
                    logger.info(f"智谱AI调用成功(ZhipuAI SDK)")
                    return ai_response
            
            # 使用HTTP请求方式
            return self._chat_http(messages, model, temperature, max_tokens)
                
        except Exception as e:
            logger.error(f"智谱AI调用异常: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return self._mock_response(messages)
    
    def _chat_http(self, messages, model, temperature, max_tokens):
        """使用HTTP直接调用API"""
        import requests
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = requests.post(
                f"{self.base_url}chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    ai_response = result["choices"][0]["message"]["content"]
                    logger.info(f"智谱AI调用成功(HTTP)")
                    return ai_response
            
            logger.error(f"API调用失败: {response.status_code} - {response.text}")
            return self._mock_response(messages)
            
        except Exception as e:
            logger.error(f"HTTP调用异常: {str(e)}")
            return self._mock_response(messages)
    
    def _handle_stream(self, response):
        """处理流式响应"""
        full_content = ""
        for chunk in response:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta.content:
                    full_content += delta.content
        return full_content
    
    def generate_image(self, prompt, size="1280x1280", quality="hd"):
        """使用cogview-3-flash生成图片
        
        Args:
            prompt(str):图片描述
            size(str):图片尺寸，推荐：1280x1280, 1568x1056, 1056x1568, 1472x1088, 1088x1472, 1728x960, 960x1728
            quality(str):图片质量，hd（高质量）
        
        Returns:
            dict:包含图片URL的字典
        """
        if not self.api_key or self.api_key == 'your_zhipuai_api_key':
            logger.warning("智谱AI API Key未配置，使用模拟响应")
            return self._mock_image_generate(prompt)
        
        try:
            logger.info(f"开始生成图片，模型: {self.image_model}")
            
            # 首选OpenAI SDK
            if self.client:
                response = self.client.images.generate(
                    model=self.image_model,
                    prompt=prompt,
                    size=size,
                    quality=quality
                )
                
                if response.data and len(response.data) > 0:
                    image_url = response.data[0].url
                    logger.info(f"图片生成成功(OpenAI SDK): {image_url}")
                    return {
                        "success": True,
                        "image_url": image_url,
                        "model": self.image_model,
                        "prompt": prompt
                    }
            
            # 备选智谱AI SDK
            elif self.zhipu_client:
                response = self.zhipu_client.images.generate(
                    model=self.image_model,
                    prompt=prompt,
                    size=size,
                    quality=quality
                )
                
                if response.data and len(response.data) > 0:
                    image_url = response.data[0].url
                    logger.info(f"图片生成成功(ZhipuAI SDK): {image_url}")
                    return {
                        "success": True,
                        "image_url": image_url,
                        "model": self.image_model,
                        "prompt": prompt
                    }
            
            # 使用HTTP方式
            return self._generate_image_http(prompt, size, quality)
                
        except Exception as e:
            logger.error(f"图片生成异常: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return self._mock_image_generate(prompt)
    
    def _generate_image_http(self, prompt, size, quality):
        """使用HTTP生成图片"""
        import requests
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.image_model,
                "prompt": prompt,
                "size": size,
                "quality": quality
            }
            
            response = requests.post(
                self.image_base_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if "data" in result and len(result["data"]) > 0:
                    image_url = result["data"][0].url
                    logger.info(f"图片生成成功(HTTP): {image_url}")
                    return {
                        "success": True,
                        "image_url": image_url,
                        "model": self.image_model,
                        "prompt": prompt
                    }
            
            logger.error(f"图片生成失败: {response.status_code} - {response.text}")
            return self._mock_image_generate(prompt)
            
        except Exception as e:
            logger.error(f"HTTP图片生成异常: {str(e)}")
            return self._mock_image_generate(prompt)
    
    def get_embeddings(self, texts, dimensions=1024):
        """获取文本嵌入向量
        
        Args:
            texts(str或list):文本或文本列表
            dimensions(int):向量维度（embedding-2固定1024）
        
        Returns:
            dict:包含嵌入向量的字典
        """
        if not self.api_key or self.api_key == 'your_zhipuai_api_key':
            logger.warning("智谱AI API Key未配置，使用模拟响应")
            return self._mock_embedding(texts)
        
        try:
            import requests
            
            logger.info(f"获取文本嵌入，模型: {self.embedding_model}")
            
            if isinstance(texts, str):
                texts = [texts]
            
            payload = {
                "model": self.embedding_model,
                "input": texts,
                "dimensions": dimensions
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.post(
                f"{self.base_url}embeddings",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("文本嵌入获取成功")
                return {
                    "success": True,
                    "data": result["data"],
                    "model": self.embedding_model,
                    "usage": result.get("usage", {})
                }
            
            logger.error(f"嵌入获取失败: {response.status_code} - {response.text}")
            return self._mock_embedding(texts)
                
        except Exception as e:
            logger.error(f"嵌入获取异常: {str(e)}")
            return self._mock_embedding(texts)
    
    def rerank(self, query, documents, top_n=5):
        """文本重排序
        
        Args:
            query(str):查询文本
            documents(list):候选文本列表
            top_n(int):返回前n个结果
        
        Returns:
            dict:排序结果
        """
        if not self.api_key or self.api_key == 'your_zhipuai_api_key':
            logger.warning("智谱AI API Key未配置，使用模拟响应")
            return self._mock_rerank(query, documents)
        
        try:
            import requests
            
            logger.info(f"文本重排序，模型: {self.rerank_model}")
            
            payload = {
                "model": self.rerank_model,
                "query": query,
                "documents": documents,
                "top_n": top_n
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.post(
                f"{self.base_url}rerank",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("文本重排序成功")
                return {
                    "success": True,
                    "results": result["results"],
                    "model": self.rerank_model,
                    "usage": result.get("usage", {})
                }
            
            logger.error(f"重排序失败: {response.status_code} - {response.text}")
            return self._mock_rerank(query, documents)
                
        except Exception as e:
            logger.error(f"重排序异常: {str(e)}")
            return self._mock_rerank(query, documents)
    
    def analyze_food_image(self, image_url=None, image_path=None, use_thinking=False):
        """分析美食图片
        
        Args:
            image_url(str):图片URL
            image_path(str):本地图片路径
            use_thinking(bool):是否使用思维链
        
        Returns:
            dict:分析结果
        """
        if not self.api_key or self.api_key == 'your_zhipuai_api_key':
            logger.warning("智谱AI API Key未配置，使用模拟响应")
            return self._mock_food_analysis()
        
        try:
            # 构建图片内容
            image_content = None
            if image_path:
                with open(image_path, 'rb') as f:
                    image_base64 = base64.b64encode(f.read()).decode('utf-8')
                    image_content = f"data:image/jpeg;base64,{image_base64}"
            elif image_url:
                image_content = image_url
            
            if not image_content:
                logger.error("没有提供图片URL或路径")
                return self._mock_food_analysis()
            
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
注意：只返回JSON，不要返回其他内容。
"""
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": thinking_prompt},
                        {"type": "image_url", "image_url": {"url": image_content}}
                    ]
                }
            ]
            
            logger.info(f"开始分析美食图片，模型: {self.vision_model}")
            response = self.chat(messages, temperature=0.3, max_tokens=2000,
                                 use_vision=True, use_thinking=use_thinking)
            
            try:
                result = self._parse_json_response(response)
                logger.info(f"美食图片分析成功: {result.get('food_name')}")
                return result
            except Exception as e:
                logger.error(f"解析分析结果失败: {str(e)}")
                return self._mock_food_analysis()
                
        except Exception as e:
            logger.error(f"美食图片分析异常: {str(e)}")
            return self._mock_food_analysis()
    
    def generate_recipe_recommendation(self, user_profile, fridge_ingredients=None):
        """生成个性化食谱推荐"""
        user_info = f"""
用户信息：
- 年龄：{user_profile.get('age', '未知')}岁
- 身高：{user_profile.get('height', '未知')}cm
- 体重：{user_profile.get('weight', '未知')}kg
- 健康目标：{user_profile.get('health_goal', '维持健康')}
- 饮食偏好：{user_profile.get('dietary_preference', '无特殊偏好')}
- 目标热量：{user_profile.get('target_calorie', 2000)}kcal
"""
        
        ingredients_info = ""
        if fridge_ingredients and len(fridge_ingredients) > 0:
            ingredients_info = f"\n冰箱可用食材：{', '.join(fridge_ingredients)}"
        
        prompt = f"""你是一位专业的营养师和食谱推荐专家。请根据以下用户信息，为用户推荐3个个性化的健康食谱。

{user_info}{ingredients_info}

请严格以JSON格式返回推荐结果，格式如下：
{{
  "recommendations": [
    {{
      "recipe_name": "食谱名称",
      "description": "简要描述",
      "ingredients": ["食材1", "食材2"],
      "cooking_steps": ["步骤1", "步骤2"],
      "nutrition": {{
        "calorie": 400,
        "protein": 30,
        "carb": 35,
        "fat": 15
      }},
      "cooking_time": "20分钟",
      "difficulty": "简单",
      "reason": "推荐理由"
    }}
  ]
}}
重要要求：
1. 只返回JSON，不要返回任何其他文字
2. 不要使用Markdown格式，不要用```包裹
3. 确保JSON格式完全正确，字符串用双引号
4. nutrition中的数值用整数类型
"""
        
        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, temperature=0.3, max_tokens=3000)
        
        try:
            result = self._parse_json_response(response)
            logger.info("食谱推荐生成成功")
            return result
        except Exception as e:
            logger.error(f"解析推荐结果失败: {str(e)}")
            return self._mock_recipe_recommendation()
    
    def generate_handbook_content(self, topic, mood="开心"):
        """生成手账内容"""
        prompt = f"""请帮我写一段关于"{topic}"的手账内容，心情是{mood}。
要求：
1. 内容温馨、积极向上
2. 100-200字左右
3. 适合记录在健康饮食手账中
"""
        
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, temperature=0.8, max_tokens=500)
    
    def analyze_nutrition(self, food_name):
        """分析食物营养"""
        prompt = f"""请分析"{food_name}"的营养价值，以JSON格式返回：
{{
  "food_name": "{food_name}",
  "nutrition_facts": {{
    "calorie": 100,
    "protein": 5,
    "carb": 15,
    "fat": 3,
    "fiber": 2,
    "vitamins": ["维生素A", "维生素C"]
  }},
  "health_benefits": "健康功效描述",
  "suitable_people": ["一般人群", "健身爱好者"],
  "recommended_intake": "适量食用",
  "cooking_suggestions": "烹饪建议"
}}
重要要求：
1. 只返回JSON，不要返回任何其他文字
2. 不要使用Markdown格式
"""
        
        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, temperature=0.5, max_tokens=400)
        
        try:
            return self._parse_json_response(response)
        except Exception as e:
            logger.error(f"解析营养分析失败: {str(e)}")
            return self._mock_nutrition_analysis(food_name)
    
    def _parse_json_response(self, response_text):
        """智能解析AI返回的JSON响应"""
        text = response_text.strip()
        
        # 移除Markdown包裹
        if text.startswith("```json"):
            text = text[7:].strip()
        elif text.startswith("```"):
            text = text[3:].strip()
        
        if text.endswith("```"):
            text = text[:-3].strip()
        
        # 提取JSON部分
        start_idx = text.find("{")
        end_idx = text.rfind("}")
        
        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            json_str = text[start_idx:end_idx+1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                logger.warning(f"直接解析失败，尝试清理: {json_str[:200]}")
                
                cleaned = json_str.replace("'", '"')
                try:
                    return json.loads(cleaned)
                except json.JSONDecodeError:
                    pass
        
        raise ValueError(f"无法解析JSON响应: {text[:300]}")
    
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
    
    def _mock_recipe_recommendation(self):
        """模拟食谱推荐响应"""
        logger.info("使用模拟食谱推荐响应")
        return {
            "recommendations": [
                {
                    "recipe_name": "时蔬炒鸡胸肉",
                    "description": "低脂高蛋白，营养均衡",
                    "ingredients": ["鸡胸肉", "西兰花", "胡萝卜", "蒜末"],
                    "cooking_steps": ["鸡胸肉切丁腌制", "蔬菜切好备用", "热锅炒香蒜末", "加入鸡肉和蔬菜翻炒", "调味出锅"],
                    "nutrition": {
                        "calorie": 380,
                        "protein": 35,
                        "carb": 20,
                        "fat": 10
                    },
                    "cooking_time": "25分钟",
                    "difficulty": "简单",
                    "reason": "适合减脂目标，蛋白质含量充足"
                },
                {
                    "recipe_name": "紫薯燕麦粥",
                    "description": "健康早餐选择",
                    "ingredients": ["紫薯", "燕麦", "牛奶", "蜂蜜"],
                    "cooking_steps": ["紫薯切块蒸熟", "燕麦煮软", "加入紫薯和牛奶", "调味后食用"],
                    "nutrition": {
                        "calorie": 280,
                        "protein": 12,
                        "carb": 45,
                        "fat": 6
                    },
                    "cooking_time": "20分钟",
                    "difficulty": "简单",
                    "reason": "富含膳食纤维，早餐好选择"
                }
            ]
        }
    
    def _mock_nutrition_analysis(self, food_name):
        """模拟营养分析响应"""
        logger.info("使用模拟营养分析响应")
        return {
            "food_name": food_name,
            "nutrition_facts": {
                "calorie": 150,
                "protein": 8,
                "carb": 20,
                "fat": 4,
                "fiber": 3,
                "vitamins": ["维生素A", "维生素C"]
            },
            "health_benefits": "营养丰富，有益健康",
            "suitable_people": ["一般人群", "健身爱好者"],
            "recommended_intake": "适量食用",
            "cooking_suggestions": "健康烹饪方式"
        }
    
    def _mock_embedding(self, texts):
        """模拟嵌入响应"""
        logger.info("使用模拟嵌入响应")
        if isinstance(texts, str):
            texts = [texts]
        
        mock_embeddings = [
            {
                "index": i,
                "object": "embedding",
                "embedding": [0.1] * 1024
            }
            for i in range(len(texts))
        ]
        
        return {
            "success": True,
            "data": mock_embeddings,
            "model": self.embedding_model,
            "usage": {"total_tokens": 0}
        }
    
    def _mock_rerank(self, query, documents):
        """模拟重排序响应"""
        logger.info("使用模拟重排序响应")
        results = [
            {
                "document": doc,
                "index": i,
                "relevance_score": 1.0 - (i * 0.1)
            }
            for i, doc in enumerate(documents[:5])
        ]
        
        return {
            "success": True,
            "results": results,
            "model": self.rerank_model,
            "usage": {"total_tokens": 0}
        }
    
    def _mock_response(self, messages):
        """模拟响应"""
        logger.info("使用模拟响应")
        
        if messages and len(messages) > 0:
            content = messages[-1].get("content", "")
            
            if isinstance(content, list):
                text_parts = [c.get("text", "") for c in content if c.get("type") == "text"]
                content = " ".join(text_parts)
            
            if "饮食" in content or "健康" in content:
                return """健康饮食对我们的身体至关重要。它能提供充足的营养，维持我们的免疫系统，预防慢性疾病，并帮助保持适当的体重。

建议多吃水果、蔬菜、全谷物和瘦肉蛋白，同时限制加工食品、过多的盐和糖的摄入。记得保持饮食的多样性，这样才能获得全面的营养。"""
            elif "食谱" in content or "菜谱" in content:
                return """一份健康的食谱应该包含适当的营养平衡。可以考虑做一份蔬菜沙拉配烤鸡胸肉，清爽又健康。

搭配一些粗粮主食和适量的水果，就能构成一份营养完整的美味佳肴。记得少油少盐，健康第一！"""
        
        return "这是一个模拟的AI响应。请配置智谱AI API Key以获得真实的AI服务。"


# 全局客户端实例
_zhipuai_client = None


def get_zhipuai_client():
    """获取智谱AI客户端单例"""
    global _zhipuai_client
    if _zhipuai_client is None:
        _zhipuai_client = ZhipuAIClient()
    return _zhipuai_client
