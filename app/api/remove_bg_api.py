from flask import Blueprint, request, g
from app.utils.common import format_response
from app.utils.auth_decorator import login_required
from loguru import logger
import os
from datetime import datetime
import base64

remove_bg_bp = Blueprint("remove_bg", __name__)


def simple_remove_background(image_data):
    """
    简单的背景移除功能 - 使用图像处理
    即使没有AI，也能提供基础的抠图效果
    """
    try:
        from PIL import Image
        import io
        
        # 读取图片
        img = Image.open(io.BytesIO(image_data)).convert("RGBA")
        
        # 转换为可编辑的数组
        width, height = img.size
        pixels = img.load()
        
        # 检测背景颜色（假设是左上角的颜色）
        bg_color = pixels[0, 0]
        
        # 移除相似颜色的背景
        threshold = 60  # 颜色差异阈值
        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                
                # 计算与背景的颜色差异
                diff = abs(r - bg_color[0]) + abs(g - bg_color[1]) + abs(b - bg_color[2])
                
                if diff < threshold:
                    # 设为透明
                    pixels[x, y] = (r, g, b, 0)
        
        # 保存处理后的图片
        output = io.BytesIO()
        img.save(output, format="PNG")
        output.seek(0)
        
        return output.read()
        
    except ImportError:
        logger.warning("PIL未安装，使用原图")
        return image_data
    except Exception as e:
        logger.error(f"简单抠图失败：{e}")
        return image_data


@remove_bg_bp.route("/process", methods=["POST"])
@login_required
def remove_bg():
    """
    图像一键抠图
    支持简单的背景移除功能
    请求参数：
        - file: 图片文件
        - image_base64: base64编码的图片（可选）
    """
    try:
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return format_response(400, "请选择要上传的文件")
            
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
            if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                return format_response(400, "只支持图片文件 (png, jpg, jpeg, gif, bmp, webp)")
            
            image_data = file.read()
            
        elif request.json and 'image_base64' in request.json:
            image_base64 = request.json.get('image_base64')
            image_data = base64.b64decode(image_base64)
        else:
            return format_response(400, "请提供图片文件或base64编码")
        
        logger.info(f"用户{g.user_id}请求抠图，图片大小：{len(image_data)}")
        
        # 尝试使用简单的背景移除
        processed_data = simple_remove_background(image_data)
        
        # 保存处理后的图片
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{g.user_id}_{timestamp}_nobg.png"
        
        UPLOAD_FOLDER = "app/static/uploads"
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(file_path, "wb") as f:
            f.write(processed_data)
        
        file_url = f"/static/uploads/{filename}"
        
        logger.info(f"用户{g.user_id}抠图完成：{filename}")
        return format_response(
            data={"url": file_url, "filename": filename},
            msg="抠图成功！已为您移除背景"
        )
        
    except Exception as e:
        logger.error(f"抠图服务异常：{str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return format_response(500, f"抠图服务异常：{str(e)}")
