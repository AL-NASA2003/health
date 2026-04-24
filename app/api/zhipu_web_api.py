#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智谱AI网页版爬虫 API - 通过浏览器自动化生成菜谱和图像
"""
from flask import Blueprint, g, request
from app.utils.common import format_response
from app.utils.auth_decorator import login_required
from loguru import logger
import threading

# 导入网页版爬虫
try:
    from app.crawler.zhipu_ai_web_crawler import (
        get_zhipu_web_crawler,
        generate_recipe_via_web,
        generate_image_via_web
    )
    ZHIPU_WEB_AVAILABLE = True
except Exception as e:
    logger.warning(f"智谱AI网页爬虫导入失败: {str(e)}")
    ZHIPU_WEB_AVAILABLE = False

zhipu_web_bp = Blueprint("zhipu_web", __name__)

# 全局锁，防止多用户同时操作浏览器
_browser_lock = threading.Lock()

@zhipu_web_bp.route("/status", methods=["GET"])
def get_status():
    """获取网页爬虫状态"""
    if not ZHIPU_WEB_AVAILABLE:
        return format_response(500, "网页版爬虫未加载")
    
    status = {
        "available": ZHIPU_WEB_AVAILABLE,
        "locked": _browser_lock.locked(),
        "url": "https://www.zhipuai.cn/zh"
    }
    return format_response(data=status)

@zhipu_web_bp.route("/login", methods=["POST"])
def start_login():
    """启动浏览器用于登录"""
    if not ZHIPU_WEB_AVAILABLE:
        return format_response(500, "网页版爬虫未加载")
    
    try:
        if _browser_lock.locked():
            return format_response(429, "浏览器正在被使用，请稍后再试")
        
        with _browser_lock:
            crawler = get_zhipu_web_crawler()
            
            if not crawler.page:
                crawler._init_browser()
            
            if not crawler.is_logged_in:
                # 提示用户登录（实际上通过消息通知）
                return format_response(data={
                    "message": "浏览器已启动，请在浏览器中完成登录后调用/check-login",
                    "action": "login"
                })
            else:
                return format_response(data={
                    "message": "已经登录，无需再次登录",
                    "logged_in": True
                })
                
    except Exception as e:
        logger.error(f"启动登录失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return format_response(500, f"启动失败: {str(e)}")

@zhipu_web_bp.route("/check-login", methods=["GET"])
def check_login():
    """检查登录状态"""
    if not ZHIPU_WEB_AVAILABLE:
        return format_response(500, "网页版爬虫未加载")
    
    try:
        crawler = get_zhipu_web_crawler()
        logged_in = crawler.check_login_status()
        
        return format_response(data={
            "logged_in": logged_in,
            "message": "已登录" if logged_in else "未登录"
        })
        
    except Exception as e:
        logger.error(f"检查登录失败: {str(e)}")
        return format_response(500, f"检查失败: {str(e)}")

@zhipu_web_bp.route("/generate-recipe", methods=["POST"])
@login_required
def web_generate_recipe():
    """通过网页版生成个性化菜谱"""
    if not ZHIPU_WEB_AVAILABLE:
        return format_response(500, "网页版爬虫未加载")
    
    try:
        data = request.get_json() or {}
        
        user_id = g.user_id if hasattr(g, 'user_id') else None
        user_info = data.get('user_info', {})
        ingredients = data.get('ingredients', [])
        preference = data.get('preference', '')
        
        if not user_info and user_id:
            # 如果没有提供用户信息，尝试从数据库获取
            from app.models.user import User
            user = User.query.get(user_id)
            if user:
                user_info = {
                    'health_goal': user.health_goal or '保持健康',
                    'dietary_preference': user.dietary_preference or '无特殊偏好',
                    'calorie_target': user.target_calories or 2000
                }
        
        if _browser_lock.locked():
            logger.info("浏览器被占用，使用备用生成方案")
            recipe = _get_mock_recipe(user_info)
            return format_response(data={
                "recipe": recipe,
                "source": "fallback"
            })
        
        with _browser_lock:
            # 获取爬虫实例
            crawler = get_zhipu_web_crawler()
            
            if not crawler.is_logged_in:
                return format_response(403, "需要先登录智谱AI网页版")
            
            # 生成菜谱
            recipe = crawler.generate_recipe(user_info, ingredients, preference)
            
            return format_response(data={
                "recipe": recipe,
                "source": "zhipu_web"
            })
            
    except Exception as e:
        logger.error(f"网页版菜谱生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # 失败时使用备用方案
        user_info = (request.get_json() or {}).get('user_info', {})
        recipe = _get_mock_recipe(user_info)
        return format_response(data={
            "recipe": recipe,
            "source": "fallback"
        })

@zhipu_web_bp.route("/generate-image", methods=["POST"])
@login_required
def web_generate_image():
    """通过网页版生成图像"""
    if not ZHIPU_WEB_AVAILABLE:
        return format_response(500, "网页版爬虫未加载")
    
    try:
        data = request.get_json() or {}
        
        prompt = data.get('prompt', '')
        style = data.get('style', 'food')
        size = data.get('size', '1024x1024')
        
        if not prompt:
            return format_response(400, "请提供图像描述")
        
        if _browser_lock.locked():
            logger.info("浏览器被占用，使用备用图像生成")
            image = _get_mock_image(prompt, style)
            return format_response(data=image)
        
        with _browser_lock:
            crawler = get_zhipu_web_crawler()
            
            if not crawler.is_logged_in:
                return format_response(403, "需要先登录智谱AI网页版")
            
            image = crawler.generate_image(prompt, style, size)
            
            return format_response(data=image)
            
    except Exception as e:
        logger.error(f"网页版图像生成失败: {str(e)}")
        
        prompt = (request.get_json() or {}).get('prompt', '')
        style = (request.get_json() or {}).get('style', 'food')
        image = _get_mock_image(prompt, style)
        return format_response(data=image)

def _get_mock_recipe(user_info):
    """获取备用菜谱"""
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

def _get_mock_image(prompt, style):
    """获取备用图像"""
    prompt_encoded = prompt.replace(' ', '_')[:30]
    return {
        "success": True,
        "image_url": f"https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt={prompt_encoded}&image_size=square_hd",
        "source": "fallback_generator",
        "model": "fallback_image",
        "prompt": prompt
    }
