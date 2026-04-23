from flask import Blueprint, g, request
from app.utils.common import format_response
from app.utils.auth_decorator import login_required
from loguru import logger
import base64
import os
from app.config import ZHIPUAI_API_KEY

ocr_bp = Blueprint("ocr", __name__)


def get_fallback_text(image_info):
    """降级响应：当OCR失败时返回默认提示"""
    return "图片文字识别服务暂时不可用，请稍后重试。如需识别菜单或食材信息，可以手动输入。"


@ocr_bp.route("/recognize", methods=["POST"])
@login_required
def ocr_recognize():
    """
    智谱AI OCR图片文字识别
    支持识别菜单、食材、营养标签等图片中的文字
    请求参数：
        - file: 图片文件
        - image_base64: base64编码的图片（可选）
    """
    try:
        logger.info(f"用户{g.user_id}请求OCR识别")
        
        # 获取图片数据
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return format_response(400, "请选择要上传的图片")
            
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
            if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                return format_response(400, "只支持图片文件 (png, jpg, jpeg, gif, bmp, webp)")
            
            image_data = file.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
        elif request.json and 'image_base64' in request.json:
            image_base64 = request.json.get('image_base64')
        else:
            return format_response(400, "请提供图片文件或base64编码")
        
        logger.info(f"图片base64长度：{len(image_base64)}")
        
        # 尝试使用智谱AI OCR
        try:
            import requests
            import json
            
            api_url = "https://open.bigmodel.cn/api/paas/v4/image/recognize"
            
            headers = {
                "Authorization": f"Bearer {ZHIPUAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "glm-4-v-plus",
                "image": image_base64,
                "prompt": "请识别这张图片中的所有文字内容，包括菜品名称、食材、价格、营养信息等。如果是菜单，请完整识别所有菜品和价格。"
            }
            
            logger.info("调用智谱AI OCR服务")
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"OCR响应：{json.dumps(result, ensure_ascii=False)[:200]}")
                
                if 'choices' in result and len(result['choices']) > 0:
                    message = result['choices'][0]['message']
                    recognized_text = message.get('content', '')
                    
                    if recognized_text and len(recognized_text.strip()) > 0:
                        logger.info("智谱AI OCR识别成功")
                        return format_response(data={
                            "text": recognized_text,
                            "source": "zhipuai"
                        }, message="文字识别成功")
            
            logger.warning(f"智谱AI OCR失败，状态码：{response.status_code}")
            
        except requests.exceptions.Timeout:
            logger.warning("智谱AI OCR超时")
        except ImportError as e:
            logger.warning(f"缺少依赖：{e}")
        except Exception as e:
            logger.warning(f"智谱AI OCR异常：{str(e)}")
        
        # 使用降级响应
        logger.info("使用OCR降级响应")
        fallback_text = get_fallback_text("图片")
        
        return format_response(data={
            "text": fallback_text,
            "source": "fallback"
        }, message="使用降级响应")
        
    except Exception as e:
        logger.error(f"OCR服务异常：{str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return format_response(500, f"识别服务异常：{str(e)}")


@ocr_bp.route("/recognize-menu", methods=["POST"])
@login_required
def ocr_recognize_menu():
    """
    专门识别菜单图片 - 优化菜单识别
    """
    try:
        logger.info(f"用户{g.user_id}请求菜单识别")
        
        if 'file' not in request.files:
            return format_response(400, "请选择菜单图片")
        
        file = request.files['file']
        if file.filename == '':
            return format_response(400, "请选择要上传的菜单图片")
        
        image_data = file.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # 尝试使用智谱AI
        try:
            import requests
            import json
            
            api_url = "https://open.bigmodel.cn/api/paas/v4/image/recognize"
            
            headers = {
                "Authorization": f"Bearer {ZHIPUAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "glm-4-v-plus",
                "image": image_base64,
                "prompt": "请识别这张菜单图片中的所有菜品名称和价格，以JSON格式返回，格式为[{\"name\":\"菜名\",\"price\":\"价格\"}]。只返回JSON，不要有其他文字。"
            }
            
            logger.info("调用智谱AI菜单识别")
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    message = result['choices'][0]['message']
                    recognized_text = message.get('content', '')
                    
                    if recognized_text:
                        # 尝试解析JSON
                        try:
                            # 清理可能的格式问题
                            json_start = recognized_text.find('[')
                            json_end = recognized_text.rfind(']') + 1
                            if json_start >= 0 and json_end > json_start:
                                json_str = recognized_text[json_start:json_end]
                                menu_data = json.loads(json_str)
                                return format_response(data={
                                    "menu_items": menu_data,
                                    "full_text": recognized_text,
                                    "source": "zhipuai"
                                }, message="菜单识别成功")
                        except Exception as e:
                            logger.warning(f"菜单JSON解析失败：{e}")
                            return format_response(data={
                                "full_text": recognized_text,
                                "source": "zhipuai"
                            }, message="菜单识别成功")
            
            logger.warning("菜单识别失败")
            
        except Exception as e:
            logger.warning(f"菜单识别异常：{e}")
        
        # 降级响应
        return format_response(data={
            "full_text": "菜单识别服务暂时不可用，请手动输入菜品信息。",
            "source": "fallback"
        }, message="使用降级响应")
        
    except Exception as e:
        logger.error(f"菜单识别异常：{str(e)}")
        return format_response(500, f"菜单识别服务异常")
