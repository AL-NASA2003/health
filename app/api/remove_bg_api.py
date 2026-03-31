from flask import Blueprint, request, g
from app.utils.common import format_response
from app.utils.auth_decorator import login_required
from loguru import logger
import os
from datetime import datetime

remove_bg_bp = Blueprint("remove_bg", __name__)


@remove_bg_bp.route("/process", methods=["POST"])
@login_required
def remove_bg():
    """
    图像一键抠图（降级版本）
    由于智谱AI不提供抠图功能，此API暂时返回原图
    请求参数：
        - image: 图片文件或base64编码
    """
    try:
        import base64
        
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return format_response(400, "请选择要上传的文件")
            
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
            if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                return format_response(400, "只支持图片文件 (png, jpg, jpeg, gif, bmp, webp)")
            
            image_data = file.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
        elif request.json and 'image_base64' in request.json:
            image_base64 = request.json.get('image_base64')
        else:
            return format_response(400, "请提供图片文件或base64编码")
        
        logger.info(f"用户{g.user_id}请求抠图，图片大小：{len(image_base64)}")
        
        # 由于智谱AI不提供抠图功能，暂时直接保存原图
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{g.user_id}_{timestamp}_original.png"
        
        UPLOAD_FOLDER = "app/static/uploads"
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(image_base64))
        
        file_url = f"/static/uploads/{filename}"
        
        logger.info(f"用户{g.user_id}保存原图：{filename}")
        return format_response(
            data={"url": file_url, "filename": filename},
            message="抠图功能暂不可用，已保存原图"
        )
            
    except Exception as e:
        logger.error(f"抠图服务异常：{str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return format_response(500, f"抠图服务异常：{str(e)}")
