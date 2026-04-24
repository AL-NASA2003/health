#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智谱AI网页版爬虫 - 通过浏览器自动化生成菜谱和图像
使用DrissionPage驱动浏览器操作智谱AI官网
"""
import time
import json
import threading
from loguru import logger
from DrissionPage import ChromiumPage, ChromiumOptions
from typing import Dict, Optional, List, Any
from datetime import datetime
import os

# 全局配置
ZHIPU_URL = "https://www.zhipuai.cn/zh"
ZHIPU_CHAT_URL = "https://chatglm.cn"
CHROME_PATH = None  # 如果需要指定Chrome路径

# 全局浏览器实例
_browser_instance = None
_browser_lock = threading.Lock()

class ZhipuAiWebCrawler:
    """智谱AI网页版爬虫"""
    
    def __init__(self, headless: bool = False):
        self.page: Optional[ChromiumPage] = None
        self.headless = headless
        self.is_logged_in = False
        self.session_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zhipu_sessions")
        os.makedirs(self.session_dir, exist_ok=True)
    
    def _init_browser(self) -> bool:
        """初始化浏览器"""
        try:
            logger.info("正在初始化浏览器...")
            
            # 配置浏览器选项
            options = ChromiumOptions()
            if self.headless:
                options.headless()
            options.set_user_agent(
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # 尝试加载已有的用户数据目录
            user_data_dir = os.path.join(self.session_dir, "zhipu_profile")
            if os.path.exists(user_data_dir):
                options.set_user_data_path(user_data_dir)
                logger.info(f"加载用户配置: {user_data_dir}")
            else:
                logger.info("首次运行，将创建新的用户配置")
            
            # 初始化页面
            self.page = ChromiumPage(options)
            self.page.set.load_timeout(30)
            logger.info("浏览器初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"浏览器初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def check_login_status(self) -> bool:
        """检查登录状态"""
        if not self.page:
            return False
        
        try:
            # 访问智谱AI聊天页面
            self.page.get(ZHIPU_CHAT_URL)
            time.sleep(2)
            
            # 检查是否有登录按钮
            login_button = self.page.ele('text:登录', timeout=3)
            if login_button:
                logger.warning("未登录状态，请先登录智谱AI")
                self.is_logged_in = False
                return False
            
            # 检查是否有用户头像或其他已登录的特征
            user_element = self.page.ele('.user-avatar', timeout=3) or \
                          self.page.ele('.avatar', timeout=3) or \
                          self.page.ele('.profile', timeout=3)
            
            if user_element or self.page.url != ZHIPU_CHAT_URL:
                self.is_logged_in = True
                logger.info("已登录状态")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"检查登录状态失败: {str(e)}")
            return False
    
    def manual_login_prompt(self) -> bool:
        """提示用户手动登录"""
        if not self.page:
            self._init_browser()
        
        logger.info("=" * 60)
        logger.info("请在浏览器中手动登录智谱AI")
        logger.info("=" * 60)
        logger.info("步骤:")
        logger.info("1. 在打开的浏览器中访问智谱AI官网")
        logger.info("2. 完成登录流程")
        logger.info("3. 登录成功后，按回车键继续...")
        logger.info("=" * 60)
        
        self.page.get(ZHIPU_URL)
        input("请在浏览器中登录完成后，按回车键继续...")
        
        # 重新检查登录状态
        self.is_logged_in = self.check_login_status()
        if self.is_logged_in:
            logger.info("登录成功！")
            return True
        else:
            logger.warning("登录状态未检测到，请重试")
            return False
    
    def generate_recipe(self, 
                        user_info: Dict[str, Any], 
                        ingredients: Optional[List[str]] = None,
                        preference: Optional[str] = None) -> Dict[str, Any]:
        """
        通过网页版智谱AI生成个性化菜谱
        
        Args:
            user_info: 用户信息（健康目标、饮食偏好等）
            ingredients: 可选的冰箱食材
            preference: 可选的特殊要求
            
        Returns:
            包含菜谱信息的字典
        """
        if not self.is_logged_in:
            logger.warning("未登录，请先登录")
            return self._get_mock_recipe(user_info)
        
        try:
            logger.info("开始生成个性化菜谱...")
            
            # 构建提示词
            prompt = self._build_recipe_prompt(user_info, ingredients, preference)
            logger.info(f"生成提示词: {prompt[:100]}...")
            
            # 访问聊天页面
            self.page.get(ZHIPU_CHAT_URL)
            time.sleep(2)
            
            # 找到输入框并发送消息
            input_box = self.page.ele('tag:textarea', timeout=10) or \
                       self.page.ele('tag:div[contenteditable="true"]', timeout=10)
            
            if not input_box:
                logger.error("未找到输入框")
                return self._get_mock_recipe(user_info)
            
            input_box.input(prompt)
            time.sleep(1)
            
            # 找到发送按钮并点击
            send_button = self.page.ele('text:发送', timeout=5) or \
                         self.page.ele('@type=submit', timeout=5)
            if send_button:
                send_button.click()
            
            # 等待回复生成
            logger.info("等待AI回复...")
            ai_response = self._wait_for_response()
            
            if ai_response:
                recipe = self._parse_recipe_response(ai_response)
                logger.info(f"成功生成菜谱: {recipe.get('name', '未知')}")
                return recipe
            else:
                logger.warning("获取回复失败，使用备用方案")
                return self._get_mock_recipe(user_info)
                
        except Exception as e:
            logger.error(f"生成菜谱失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._get_mock_recipe(user_info)
    
    def generate_image(self, 
                        prompt: str, 
                        style: str = "food", 
                        size: str = "1024x1024") -> Dict[str, Any]:
        """
        通过网页版智谱AI生成图像
        
        Args:
            prompt: 图像描述
            style: 图像风格
            size: 图像尺寸
            
        Returns:
            包含图像URL的字典
        """
        if not self.is_logged_in:
            logger.warning("未登录，请先登录")
            return self._get_mock_image(prompt, style)
        
        try:
            logger.info(f"开始生成图像: {prompt[:50]}...")
            
            # 尝试访问图像生成页面
            self.page.get(f"{ZHIPU_CHAT_URL}/images")
            time.sleep(3)
            
            # 找到图像生成输入框
            image_input = self.page.ele('tag:textarea', timeout=10) or \
                         self.page.ele('tag:div[contenteditable="true"]', timeout=10)
            
            if image_input:
                image_input.input(prompt)
                time.sleep(1)
                
                # 点击生成按钮
                generate_btn = self.page.ele('text:生成', timeout=5)
                if generate_btn:
                    generate_btn.click()
                
                # 等待图像生成
                logger.info("等待图像生成...")
                image_url = self._wait_for_image()
                
                if image_url:
                    return {
                        "success": True,
                        "image_url": image_url,
                        "source": "zhipu_web",
                        "model": "web_image_generator",
                        "prompt": prompt
                    }
            
            # 如果专用图像生成页面不行，尝试对话式图像生成
            logger.info("尝试对话式图像生成...")
            return self._generate_image_via_chat(prompt, style)
            
        except Exception as e:
            logger.error(f"生成图像失败: {str(e)}")
            return self._get_mock_image(prompt, style)
    
    def _build_recipe_prompt(self, user_info, ingredients, preference):
        """构建菜谱生成提示词"""
        parts = []
        parts.append("请为我生成一个健康的个性化菜谱，要求：")
        parts.append(f"- 健康目标: {user_info.get('health_goal', '保持健康')}")
        parts.append(f"- 饮食偏好: {user_info.get('dietary_preference', '无特殊偏好')}")
        
        if user_info.get('calorie_target'):
            parts.append(f"- 目标热量: {user_info['calorie_target']}kcal")
        
        if ingredients:
            parts.append(f"- 可用食材: {', '.join(ingredients)}")
        
        if preference:
            parts.append(f"- 特殊要求: {preference}")
        
        parts.append("")
        parts.append("请以JSON格式返回，包含以下字段：")
        parts.append("name: 菜名")
        parts.append("description: 简介")
        parts.append("ingredients: 食材列表（数组）")
        parts.append("steps: 制作步骤（数组）")
        parts.append("nutrition: 营养成分（包含calorie, protein, carb, fat）")
        parts.append("difficulty: 难度（简单/中等/困难）")
        parts.append("time: 所需时间")
        parts.append("health_score: 健康评分0-100")
        
        return "\n".join(parts)
    
    def _wait_for_response(self, timeout: int = 60) -> Optional[str]:
        """等待AI回复"""
        start_time = time.time()
        last_content = ""
        
        while time.time() - start_time < timeout:
            try:
                # 查找AI回复区域
                response_elements = self.page.eles('.assistant-message') or \
                                  self.page.eles('.chat-message.assistant') or \
                                  self.page.eles('.response-container')
                
                if response_elements:
                    latest_response = response_elements[-1]
                    current_content = latest_response.text
                    
                    if len(current_content) > len(last_content) + 10:
                        # 内容还在增长
                        last_content = current_content
                    elif len(current_content) > 50:
                        # 内容稳定，可能完成了
                        logger.info("AI回复完成")
                        return current_content
                
                time.sleep(2)
                
            except Exception as e:
                logger.debug(f"等待回复中: {str(e)}")
                time.sleep(2)
        
        logger.warning("等待回复超时")
        return None
    
    def _wait_for_image(self, timeout: int = 120) -> Optional[str]:
        """等待图像生成"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # 查找生成的图像
                image_elements = self.page.eles('tag:img')
                
                for img in image_elements:
                    src = img.attr('src')
                    if src and ('generated' in src or 'ai_image' in src):
                        return src
                
                time.sleep(2)
                
            except Exception as e:
                logger.debug(f"等待图像中: {str(e)}")
                time.sleep(2)
        
        return None
    
    def _generate_image_via_chat(self, prompt: str, style: str) -> Dict[str, Any]:
        """通过聊天生成图像"""
        try:
            image_prompt = f"请帮我生成一张图片：{prompt}"
            if style:
                image_prompt += f"，风格：{style}"
            
            self.page.get(ZHIPU_CHAT_URL)
            time.sleep(2)
            
            input_box = self.page.ele('tag:textarea', timeout=10)
            if input_box:
                input_box.input(image_prompt)
                time.sleep(1)
                
                send_button = self.page.ele('text:发送', timeout=5)
                if send_button:
                    send_button.click()
                
                time.sleep(10)  # 等待生成图像
                
                # 查找对话中的图像
                images = self.page.eles('tag:img')
                for img in images[-5:]:  # 检查最近的图片
                    src = img.attr('src')
                    if src and len(src) > 50:
                        return {
                            "success": True,
                            "image_url": src,
                            "source": "zhipu_web_chat",
                            "prompt": prompt
                        }
            
            return self._get_mock_image(prompt, style)
            
        except Exception as e:
            logger.error(f"聊天式图像生成失败: {str(e)}")
            return self._get_mock_image(prompt, style)
    
    def _parse_recipe_response(self, response: str) -> Dict[str, Any]:
        """解析AI回复中的菜谱信息"""
        try:
            # 尝试提取JSON
            import re
            json_match = re.search(r'\{[^{}]*\}', response)
            if json_match:
                recipe = json.loads(json_match.group())
                return recipe
        except:
            pass
        
        # 如果无法提取JSON，返回结构化解析结果
        return self._get_mock_recipe({})
    
    def _get_mock_recipe(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """获取备用菜谱（当网页爬虫不可用时）"""
        recipes = [
            {
                "name": "时蔬炒鸡胸肉",
                "description": "低脂高蛋白，适合减脂增肌",
                "ingredients": ["鸡胸肉", "西兰花", "胡萝卜", "蒜末", "橄榄油"],
                "steps": [
                    "鸡胸肉切小块，用盐和黑胡椒腌制",
                    "西兰花切小朵，胡萝卜切片",
                    "热锅倒油，爆香蒜末",
                    "加入鸡肉翻炒至变色",
                    "加入蔬菜，大火快速翻炒",
                    "调味后出锅"
                ],
                "nutrition": {"calorie": 350, "protein": 35, "carb": 15, "fat": 8},
                "difficulty": "简单",
                "time": "20分钟",
                "health_score": 85
            },
            {
                "name": "紫薯燕麦粥",
                "description": "营养丰富，健康早餐选择",
                "ingredients": ["紫薯", "燕麦片", "牛奶", "蜂蜜"],
                "steps": [
                    "紫薯去皮切块，蒸熟",
                    "燕麦片煮至软糯",
                    "加入蒸好的紫薯和牛奶",
                    "煮至浓稠，加蜂蜜调味"
                ],
                "nutrition": {"calorie": 280, "protein": 10, "carb": 45, "fat": 5},
                "difficulty": "简单",
                "time": "25分钟",
                "health_score": 90
            }
        ]
        
        import random
        return random.choice(recipes)
    
    def _get_mock_image(self, prompt: str, style: str) -> Dict[str, Any]:
        """获取备用图像（当网页爬虫不可用时）"""
        prompt_encoded = prompt.replace(' ', '_')[:30]
        return {
            "success": True,
            "image_url": f"https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt={prompt_encoded}&image_size=square_hd",
            "source": "fallback_generator",
            "model": "fallback_image",
            "prompt": prompt
        }
    
    def close(self):
        """关闭浏览器"""
        if self.page:
            try:
                self.page.quit()
                logger.info("浏览器已关闭")
            except:
                pass
    
    def __enter__(self):
        self._init_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# 全局实例
_crawler_instance = None

def get_zhipu_web_crawler() -> ZhipuAiWebCrawler:
    """获取智谱AI网页爬虫单例"""
    global _crawler_instance
    if _crawler_instance is None:
        _crawler_instance = ZhipuAiWebCrawler(headless=False)
    return _crawler_instance

def generate_recipe_via_web(user_info, ingredients=None, preference=None):
    """通过网页版生成菜谱（便捷函数）"""
    try:
        crawler = get_zhipu_web_crawler()
        return crawler.generate_recipe(user_info, ingredients, preference)
    except Exception as e:
        logger.error(f"网页版菜谱生成失败: {str(e)}")
        return _get_mock_recipe(user_info)

def generate_image_via_web(prompt, style="food", size="1024x1024"):
    """通过网页版生成图像（便捷函数）"""
    try:
        crawler = get_zhipu_web_crawler()
        return crawler.generate_image(prompt, style, size)
    except Exception as e:
        logger.error(f"网页版图像生成失败: {str(e)}")
        return _get_mock_image(prompt, style)

# 为了向后兼容添加的辅助函数
def _get_mock_recipe(user_info):
    return ZhipuAiWebCrawler()._get_mock_recipe(user_info)

def _get_mock_image(prompt, style):
    return ZhipuAiWebCrawler()._get_mock_image(prompt, style)

if __name__ == "__main__":
    # 测试代码
    print("=" * 60)
    print("智谱AI网页版爬虫 - 测试模式")
    print("=" * 60)
    
    crawler = ZhipuAiWebCrawler(headless=False)
    
    try:
        if crawler._init_browser():
            if not crawler.check_login_status():
                crawler.manual_login_prompt()
            
            if crawler.is_logged_in:
                print("\n测试菜谱生成...")
                test_user = {"health_goal": "减脂", "dietary_preference": "清淡"}
                recipe = crawler.generate_recipe(test_user)
                print(f"生成的菜谱: {recipe}")
                
                print("\n测试图像生成...")
                image = crawler.generate_image("健康美味的水果沙拉")
                print(f"生成的图像: {image}")
    
    finally:
        crawler.close()
