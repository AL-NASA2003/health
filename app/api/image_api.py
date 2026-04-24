from flask import Blueprint, g, request
from app.utils.common import format_response
from app.utils.auth_decorator import login_required
from loguru import logger
import requests
import os
import random
import threading
import json
from app.config import (
    ZHIPUAI_API_KEY
)
from app.utils.zhipuai_client import get_zhipuai_client

image_bp = Blueprint("image", __name__)

# 手账专属模板和风格
HANDBOOK_TEMPLATES = {
    "cute": {
        "name": "可爱风格",
        "style_prompt": "kawaii style, cute doodles, pastel colors, soft lighting, adorable, whimsical, charming, cute animals and flowers, hand-drawn illustration",
        "fallback_images": [
            "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20kawaii%20handbook%20pastel%20illustration&image_size=square_hd",
            "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=adorable%20cute%20doodle%20journal%20page&image_size=square_hd"
        ]
    },
    "watercolor": {
        "name": "水彩风格",
        "style_prompt": "watercolor painting style, soft brush strokes, delicate, artistic, painterly, elegant, dreamy, transparent, flowing colors",
        "fallback_images": [
            "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=watercolor%20painting%20artistic%20illustration&image_size=square_hd",
            "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=delicate%20watercolor%20art%20journal&image_size=square_hd"
        ]
    },
    "minimal": {
        "name": "简约风格",
        "style_prompt": "minimalist design, clean lines, simple, elegant, modern, aesthetic, Scandinavian style, white background, uncluttered",
        "fallback_images": [
            "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=minimalist%20clean%20elegant%20design&image_size=square_hd",
            "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=simple%20modern%20minimal%20aesthetic&image_size=square_hd"
        ]
    },
    "retro": {
        "name": "复古风格",
        "style_prompt": "retro vintage style, nostalgic, warm tones, film aesthetic, 90s vibe, classic, timeless, analog photography style",
        "fallback_images": [
            "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=retro%20vintage%20nostalgic%20aesthetic&image_size=square_hd",
            "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=vintage%20film%20aesthetic%20style&image_size=square_hd"
        ]
    },
    "food": {
        "name": "美食主题",
        "style_prompt": "food photography, delicious, appetizing, warm lighting, restaurant quality, fresh ingredients, culinary art, gourmet",
        "fallback_images": [
            "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=delicious%20food%20photography%20appetizing&image_size=square_hd",
            "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=gourmet%20culinary%20art%20food&image_size=square_hd"
        ]
    },
    "nature": {
        "name": "自然主题",
        "style_prompt": "nature photography, serene, peaceful, green, sunlight, outdoors, fresh air, trees, flowers, natural beauty, calming",
        "fallback_images": [
            "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=serene%20nature%20green%20peaceful&image_size=square_hd",
            "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=beautiful%20natural%20outdoors%20scenery&image_size=square_hd"
        ]
    }
}

# 预加载的快速占位图片 - 更丰富的分类
FAST_FALLBACK_IMAGES = {
    "food": [
        "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=healthy%20food%20salad%20vegetables%20nutrition&image_size=square_hd",
        "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=balanced%20meal%20chicken%20vegetables%20rice&image_size=square_hd",
        "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=delicious%20soup%20bowl%20hot%20homemade&image_size=square_hd",
        "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=steamed%20fish%20seafood%20healthy%20dish&image_size=square_hd",
        "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=fresh%20vegetable%20stir%20fry%20asian%20cuisine&image_size=square_hd"
    ],
    "fruit": [
        "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=fresh%20fruits%20healthy%20snack%20nutrition&image_size=square_hd",
        "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=juice%20smoothie%20fresh%20fruits%20drink&image_size=square_hd",
        "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=colorful%20fruit%20platter%20apple%20orange%20banana&image_size=square_hd"
    ],
    "breakfast": [
        "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=yogurt%20granola%20breakfast%20healthy%20food&image_size=square_hd",
        "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=eggs%20toast%20breakfast%20healthy%20morning&image_size=square_hd",
        "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=oatmeal%20porridge%20healthy%20breakfast&image_size=square_hd"
    ],
    "dessert": [
        "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=delicious%20cake%20dessert%20sweet%20food&image_size=square_hd",
        "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=ice%20cream%20dessert%20summer%20treat&image_size=square_hd"
    ],
    "other": [
        "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=healthy%20food%20balanced%20nutrition&image_size=square_hd"
    ]
}

# 图像缓存
IMAGE_CACHE = {}
CACHE_LOCK = threading.Lock()


def get_fast_fallback_image(prompt):
    """获取快速降级图像 - 根据提示词分类"""
    prompt_lower = prompt.lower()
    
    # 根据提示词选择合适的分类
    if any(keyword in prompt_lower for keyword in ['水果', '苹果', '香蕉', 'fruit', 'apple', 'banana', 'orange']):
        category = 'fruit'
    elif any(keyword in prompt_lower for keyword in ['早餐', '早饭', 'breakfast', 'yogurt', 'oatmeal']):
        category = 'breakfast'
    elif any(keyword in prompt_lower for keyword in ['甜点', '蛋糕', '甜品', 'dessert', 'cake', 'sweet']):
        category = 'dessert'
    elif any(keyword in prompt_lower for keyword in ['食物', '美食', 'food', 'meal', 'dish', 'salad']):
        category = 'food'
    else:
        category = 'food'
    
    image_url = random.choice(FAST_FALLBACK_IMAGES.get(category, FAST_FALLBACK_IMAGES['food']))
    return format_response(data={
        "image_url": image_url,
        "prompt": prompt,
        "source": "fast_fallback"
    })


def async_generate_with_zhipu(prompt, size, style, cache_key):
    """后台异步生成智谱AI图像"""
    try:
        from app.utils.zhipuai_client import get_zhipuai_client
        client = get_zhipuai_client()
        
        logger.info(f"后台异步生成图像: {prompt}")
        result = client.generate_image(prompt, size)
        
        if result.get("success") and result.get("image_url"):
            with CACHE_LOCK:
                IMAGE_CACHE[cache_key] = {
                    "image_url": result["image_url"],
                    "source": "cogview-3-flash",
                    "generated": True
                }
            logger.info(f"后台图像生成成功并缓存: {cache_key}")
    except Exception as e:
        logger.warning(f"后台图像生成失败: {str(e)}")
        import traceback
        logger.warning(traceback.format_exc())


@image_bp.route("/generate", methods=["POST"])
@login_required
def generate_image():
    """
    优化版图像生成：先返回降级图像，后台异步生成AI图像
    请求参数：
        - prompt: 图像描述（必填）
        - size: 图像尺寸，可选：1024x1024, 768x1024, 1024x768, 512x512
        - style: 风格（可选）：photographic(摄影), cartoon(卡通), painting(绘画)
        - use_cache: 是否使用缓存（默认true）
    """
    try:
        params = request.json or {}
        prompt = params.get("prompt")
        size = params.get("size", "512x512")  # 默认使用更小尺寸加速
        style = params.get("style", "photographic")
        use_cache = params.get("use_cache", True)
        
        if not prompt:
            return format_response(400, "请输入图像描述")
        
        cache_key = f"{prompt}_{size}_{style}"
        logger.info(f"图像生成请求: {prompt}")
        
        # 检查缓存
        if use_cache:
            with CACHE_LOCK:
                if cache_key in IMAGE_CACHE:
                    cached = IMAGE_CACHE[cache_key]
                    if cached.get("generated"):
                        logger.info("使用缓存的AI图像")
                        return format_response(data={
                            "image_url": cached["image_url"],
                            "prompt": prompt,
                            "source": "zhipuai_cached"
                        })
        
        # 立即返回降级图像（小于100ms响应）
        fallback_response = get_fast_fallback_image(prompt)
        
        # 后台异步生成AI图像
        if ZHIPUAI_API_KEY:
            thread = threading.Thread(
                target=async_generate_with_zhipu,
                args=(prompt, size, style, cache_key),
                daemon=True
            )
            thread.start()
            logger.info("后台AI图像生成已启动")
        
        return fallback_response
            
    except Exception as e:
        logger.error(f"图像生成异常：{str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return get_fast_fallback_image(prompt)


@image_bp.route("/generate-recipe", methods=["POST"])
@login_required
def generate_recipe_image():
    """
    专门生成食谱图片 - 预定义模板
    请求参数：
        - recipe_name: 食谱名称
        - ingredients: 食材列表（可选）
        - style: 风格（可选）
    """
    try:
        params = request.json or {}
        recipe_name = params.get("recipe_name", "美食")
        style = params.get("style", "photographic")
        
        food_prompt = f"delicious {recipe_name}, professional food photography, restaurant quality, fresh ingredients, appetizing"
        
        logger.info(f"生成食谱图片：{recipe_name}")
        
        # 使用通用接口
        params_copy = params.copy()
        params_copy["prompt"] = food_prompt
        params_copy["style"] = style
        
        # 临时替换request.json
        original_json = request.json
        request.json = params_copy
        try:
            result = generate_image()
            return result
        finally:
            request.json = original_json
        
    except Exception as e:
        logger.error(f"食谱图片生成异常：{str(e)}")
        return get_fast_fallback_image(recipe_name)


def get_fallback_image(prompt):
    """获取降级图像（保留原方法用于兼容）"""
    return get_fast_fallback_image(prompt)


@image_bp.route("/analyze-food", methods=["POST"])
@login_required
def analyze_food_image():
    """
    使用GLM-4.6V-Flash分析美食图片
    请求参数：
        - image_url: 图片URL（优先使用）
        - image_base64: base64编码的图片（可选）
        - image_path: 本地图片路径（可选，开发环境使用）
    """
    try:
        params = request.json or {}
        image_url = params.get("image_url")
        image_base64 = params.get("image_base64")
        image_path = params.get("image_path")
        
        if not image_url and not image_base64 and not image_path:
            return format_response(400, "请提供图片URL、base64或路径")
        
        logger.info("开始美食图片分析")
        
        client = get_zhipuai_client()
        
        # 优先使用URL
        if image_url:
            result = client.analyze_food_image(image_url=image_url)
        # 其次使用base64
        elif image_base64:
            # 保存base64到临时文件
            import tempfile
            import base64
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
                # 处理base64数据
                if image_base64.startswith('data:image'):
                    # 移除data:image/jpeg;base64,前缀
                    image_base64 = image_base64.split(',')[1]
                f.write(base64.b64decode(image_base64))
                temp_path = f.name
            
            try:
                result = client.analyze_food_image(image_path=temp_path)
            finally:
                # 清理临时文件
                try:
                    os.unlink(temp_path)
                except:
                    pass
        # 最后使用本地路径
        else:
            result = client.analyze_food_image(image_path=image_path)
        
        logger.info(f"美食图片分析完成: {result.get('food_name')}")
        return format_response(data=result)
            
    except Exception as e:
        logger.error(f"美食图片分析异常：{str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return format_response(500, f"分析失败: {str(e)}")


@image_bp.route("/batch-analyze-food", methods=["POST"])
@login_required
def batch_analyze_food_images():
    """
    批量分析美食图片
    请求参数：
        - images: 图片列表，每个元素包含 image_url 或 image_base64
    """
    try:
        params = request.json or {}
        images = params.get("images", [])
        
        if not images:
            return format_response(400, "请提供图片列表")
        
        logger.info(f"开始批量分析 {len(images)} 张美食图片")
        
        results = []
        client = get_zhipuai_client()
        
        for i, img_info in enumerate(images):
            try:
                image_url = img_info.get("image_url")
                result = client.analyze_food_image(image_url=image_url)
                results.append({
                    "index": i,
                    "success": True,
                    "analysis": result
                })
            except Exception as e:
                logger.error(f"第 {i} 张图片分析失败: {str(e)}")
                results.append({
                    "index": i,
                    "success": False,
                    "error": str(e)
                })
        
        success_count = sum(1 for r in results if r["success"])
        logger.info(f"批量分析完成: {success_count}/{len(images)} 成功")
        
        return format_response(data={
            "total": len(images),
            "success": success_count,
            "failed": len(images) - success_count,
            "results": results
        })
            
    except Exception as e:
        logger.error(f"批量分析异常：{str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return format_response(500, f"批量分析失败：{str(e)}")


@image_bp.route("/generate-handbook", methods=["POST"])
@login_required
def generate_handbook_image():
    """
    使用CogView-3-Flash生成手账专属图片
    请求参数：
        - prompt: 图片描述（必填）
        - style: 风格模板（可选：cute, watercolor, minimal, retro, food, nature）
        - size: 图片尺寸（可选：512x512, 1024x1024, 1024x1536, 1536x1024）
        - mood: 心情（可选：happy, sad, excited, calm等）
    """
    import time
    try:
        params = request.json or {}
        prompt = params.get("prompt")
        style = params.get("style", "cute")
        size = params.get("size", "1024x1024")
        mood = params.get("mood", "")
        
        if not prompt:
            return format_response(400, "请输入图片描述")
        
        # 获取风格模板
        template = HANDBOOK_TEMPLATES.get(style, HANDBOOK_TEMPLATES["cute"])
        style_prompt = template["style_prompt"]
        
        # 构建增强提示词
        enhanced_prompt = build_handbook_prompt(prompt, style_prompt, mood)
        cache_key = f"handbook_{prompt}_{style}_{size}"
        
        logger.info(f"生成手账图片: {prompt}, 风格: {template['name']}")
        
        # 检查缓存
        with CACHE_LOCK:
            if cache_key in IMAGE_CACHE:
                cached = IMAGE_CACHE[cache_key]
                if cached.get("generated"):
                    logger.info("使用缓存的手账图片")
                    return format_response(data={
                        "image_url": cached["image_url"],
                        "prompt": prompt,
                        "style": style,
                        "source": "cogview_cached"
                    })
        
        # 直接同步使用CogView-3-Flash生成
        if ZHIPUAI_API_KEY:
            try:
                client = get_zhipuai_client()
                logger.info(f"CogView-3-Flash生成中: {prompt[:50]}...")
                
                # 记录开始时间
                start_time = time.time()
                
                result = client.generate_image(enhanced_prompt, size)
                
                # 计算耗时
                end_time = time.time()
                generate_time = round(end_time - start_time, 1)
                
                if result.get("success") and result.get("image_url"):
                    # 缓存结果
                    with CACHE_LOCK:
                        IMAGE_CACHE[cache_key] = {
                            "image_url": result["image_url"],
                            "source": "cogview-3-flash",
                            "generated": True
                        }
                    logger.info(f"CogView-3-Flash手账图片生成成功! 耗时: {generate_time}秒")
                    
                    return format_response(data={
                        "image_url": result["image_url"],
                        "prompt": prompt,
                        "style": style,
                        "source": "cogview",
                        "generate_time": generate_time
                    })
            except Exception as e:
                logger.error(f"CogView-3-Flash调用失败: {str(e)}")
        
        # 如果AI生成失败，返回降级图像
        fallback_url = random.choice(template["fallback_images"])
        logger.info("使用降级图像")
        
        return format_response(data={
            "image_url": fallback_url,
            "prompt": prompt,
            "style": style,
            "source": "fallback"
        })
            
    except Exception as e:
        logger.error(f"手账图片生成异常：{str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        # 返回默认手账图片
        fallback_url = random.choice(HANDBOOK_TEMPLATES["cute"]["fallback_images"])
        return format_response(data={
            "image_url": fallback_url,
            "source": "emergency_fallback"
        })


@image_bp.route("/handbook-templates", methods=["GET"])
def get_handbook_templates():
    """
    获取手账模板列表
    """
    templates_info = []
    for key, template in HANDBOOK_TEMPLATES.items():
        templates_info.append({
            "key": key,
            "name": template["name"],
            "preview_image": template["fallback_images"][0]
        })
    
    return format_response(data={
        "templates": templates_info,
        "total": len(templates_info)
    })


def build_handbook_prompt(base_prompt, style_prompt, mood=""):
    """
    构建手账图片生成提示词
    """
    mood_descriptions = {
        "happy": "bright, cheerful, sunny, joyful atmosphere",
        "sad": "soft, melancholic, gentle blue tones, peaceful",
        "excited": "vibrant, energetic, dynamic, bold colors",
        "calm": "serene, peaceful, soothing, muted tones",
        "grateful": "warm, cozy, heartfelt, golden hour lighting",
        "motivated": "inspiring, uplifting, positive, energizing"
    }
    
    mood_prompt = mood_descriptions.get(mood, "")
    
    # 手账通用提示词增强
    handbook_enhancer = """
    journal page aesthetic, diary illustration, scrapbook style, 
    perfect for health and wellness journal, beautiful composition, 
    high quality, detailed, professional illustration
    """
    
    # 组合完整提示词
    full_prompt = f"""
    {base_prompt}, 
    {style_prompt},
    {mood_prompt},
    {handbook_enhancer}
    """
    
    return full_prompt.strip()


def async_generate_handbook_with_cogview(prompt, size, cache_key):
    """
    后台异步使用CogView-3-Flash生成手账图片
    """
    try:
        from app.utils.zhipuai_client import get_zhipuai_client
        client = get_zhipuai_client()
        
        logger.info(f"CogView-3-Flash生成中: {prompt[:50]}...")
        result = client.generate_image(prompt, size)
        
        if result.get("success") and result.get("image_url"):
            with CACHE_LOCK:
                IMAGE_CACHE[cache_key] = {
                    "image_url": result["image_url"],
                    "source": "cogview-3-flash",
                    "generated": True
                }
            logger.info(f"CogView-3-Flash手账图片生成成功!")
        else:
            logger.error(f"CogView-3-Flash调用失败")
                
    except Exception as e:
        logger.error(f"CogView-3-Flash生成异常: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


# 添加一个测试路由，用于调试
@image_bp.route("/test", methods=["GET"])
def test_route():
    """测试路由"""
    return format_response(data={"message": "Image API is working!", "time": __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
