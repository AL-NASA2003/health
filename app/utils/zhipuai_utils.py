import os
from loguru import logger
import json

class ZhipuAIUtils:
    """智谱AI工具类"""
    
    def __init__(self):
        """初始化智谱AI工具"""
        try:
            # 导入智谱AI SDK
            from zhipuai import ZhipuAI
            # 获取API密钥
            self.api_key = os.getenv('ZHIPUAI_API_KEY', '0a2b13b2-b311-41c2-a379-3a007a4b128b')
            # 初始化客户端
            self.client = ZhipuAI(api_key=self.api_key)
            logger.info("智谱AI初始化成功")
        except Exception as e:
            logger.error(f"智谱AI初始化失败：{str(e)}")
            self.client = None
    
    def generate_content(self, prompt):
        """生成内容
        Args:
            prompt: 提示词
        Returns:
            生成的内容
        """
        if not self.client:
            logger.error("智谱AI客户端未初始化")
            return None
        
        try:
            # 调用智谱AI生成内容
            response = self.client.chat.completions.create(
                model="glm-4",  # 模型名称
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,  # 温度参数
                max_tokens=2000,  # 最大 tokens
                top_p=0.9  # 核采样概率
            )
            
            # 解析响应
            if response and hasattr(response, 'choices') and len(response.choices) > 0:
                content = response.choices[0].message.content
                logger.info("智谱AI生成内容成功")
                return content
            else:
                logger.error("智谱AI生成内容失败：响应格式错误")
                return None
        except Exception as e:
            logger.error(f"智谱AI生成内容失败：{str(e)}")
            return None
    
    def generate_image(self, prompt, size="1024x1024"):
        """生成图像
        Args:
            prompt: 提示词
            size: 图像尺寸
        Returns:
            生成的图像URL
        """
        if not self.client:
            logger.error("智谱AI客户端未初始化")
            return None
        
        try:
            # 调用智谱AI生成图像
            response = self.client.images.generate(
                model="cogview-3",  # 图像生成模型
                prompt=prompt,
                size=size,
                n=1  # 生成图像数量
            )
            
            # 解析响应
            if response and hasattr(response, 'data') and len(response.data) > 0:
                image_url = response.data[0].url
                logger.info("智谱AI生成图像成功")
                return image_url
            else:
                logger.error("智谱AI生成图像失败：响应格式错误")
                return None
        except Exception as e:
            logger.error(f"智谱AI生成图像失败：{str(e)}")
            return None
