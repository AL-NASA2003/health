from flask import Blueprint, g, request
from app.utils.common import format_response
from app.utils.auth_decorator import login_required
from loguru import logger
import requests
import os
import random
import threading
from app.config import (
    ZHIPUAI_API_KEY
)

image_bp = Blueprint("image", __name__)

# 预加载的快速占位图片
FAST_FALLBACK_IMAGES = [
    "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=healthy%20food%20salad%20vegetables%20nutrition&image_size=square_hd",
    "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=balanced%20meal%20chicken%20vegetables%20rice&image_size=square_hd",
    "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=fresh%20fruits%20healthy%20snack%20nutrition&image_size=square_hd",
    "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=delicious%20soup%20bowl%20hot%20homemade&image_size=square_hd",
    "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=steamed%20fish%20seafood%20healthy%20dish&image_size=square_hd",
    "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=fresh%20vegetable%20stir%20fry%20asian%20cuisine&image_size=square_hd",
    "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=yogurt%20granola%20breakfast%20healthy%20food&image_size=square_hd",
    "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=juice%20smoothie%20fresh%20fruits%20drink&image_size=square_hd"
]


def get_fast_fallback_image(prompt):
    """获取快速降级图像 - 立即返回"""
    image_url = random.choice(FAST_FALLBACK_IMAGES)
    return format_response(data={
        "image_url": image_url,
        "prompt": prompt,
        "source": "fast_fallback"
    })


def generate_image_async(prompt, size, callback):
    """异步生成图像"""
    try:
        api_url = "https://open.bigmodel.cn/api/paas/v4/images/generations"
        
        headers = {
            "Authorization": f"Bearer {ZHIPUAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "cogview-3-flash",
            "prompt": prompt,
            "size": size
        }
        
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if "data" in result and len(result["data"]) > 0:
                image_url = result["data"][0].get("url")
                if image_url:
                    logger.info(f"异步图像生成成功: {image_url}")
                    callback(image_url)
                    return
        logger.warning("异步图像生成失败")
    except Exception as e:
        logger.error(f"异步图像生成异常: {str(e)}")


@image_bp.route("/generate", methods=["POST"])
@login_required
def generate_image():
    """
    使用智谱AI生成图像
    优先使用智谱AI（12秒超时），失败后使用降级图像
    请求参数：
        - prompt: 图像描述（必填）
        - size: 图像尺寸，可选：1024x1024, 768x1024, 1024x768, 512x512
    """
    try:
        params = request.json or {}
        prompt = params.get("prompt")
        size = params.get("size", "1024x1024")
        
        if not prompt:
            return format_response(400, "请输入图像描述")
        
        logger.info(f"开始生成图像，描述：{prompt}")
        
        # 尝试使用智谱AI（12秒超时）
        try:
            api_url = "https://open.bigmodel.cn/api/paas/v4/images/generations"
            
            headers = {
                "Authorization": f"Bearer {ZHIPUAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "cogview-3-flash",
                "prompt": prompt,
                "size": size
            }
            
            logger.info("使用智谱AI生成图像")
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=8
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if "error" not in result and "data" in result and len(result["data"]) > 0:
                    image_url = result["data"][0].get("url")
                    if image_url:
                        logger.info("智谱AI图像生成成功")
                        return format_response(data={
                            "image_url": image_url,
                            "prompt": prompt,
                            "source": "zhipuai"
                        })
            else:
                logger.warning(f"智谱AI返回错误: {response.status_code}, {response.text}")
        except requests.exceptions.Timeout:
            logger.warning("智谱AI图像生成超时，使用降级图像")
        except Exception as e:
            logger.warning(f"智谱AI图像生成异常: {str(e)}，使用降级图像")
        
        # 智谱AI失败，使用降级图像
        logger.info("使用快速降级图像")
        return get_fast_fallback_image(prompt)
            
    except Exception as e:
        logger.error(f"图像生成异常：{str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return get_fast_fallback_image(prompt)


def get_fallback_image(prompt):
    """获取降级图像（保留原方法用于兼容）"""
    return get_fast_fallback_image(prompt)
