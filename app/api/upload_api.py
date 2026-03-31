from flask import request, g
from app.utils.common import format_response
from app.utils.auth_decorator import login_required
from loguru import logger
import os
from datetime import datetime
from flask_restx import Namespace, Resource, fields

# 创建命名空间
upload_ns = Namespace('upload', description='文件上传相关操作')

# 定义响应模型
upload_response_model = upload_ns.model('UploadResponse', {
    'url': fields.String(description='上传文件的URL'),
    'filename': fields.String(description='上传文件的文件名')
})

# 确保上传目录存在
UPLOAD_FOLDER = "app/static/uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@upload_ns.route('/image')
class UploadImage(Resource):
    """上传图片"""
    @login_required
    def post(self):
        """上传图片
        请求参数：file (图片文件)
        """
        try:
            # 检查是否有文件上传
            if 'file' not in request.files:
                return format_response(400, "请选择要上传的文件")
            
            file = request.files['file']
            
            # 检查文件是否为空
            if file.filename == '':
                return format_response(400, "请选择要上传的文件")
            
            # 检查文件类型
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                return format_response(400, "只支持上传图片文件 (png, jpg, jpeg, gif)")
            
            # 生成唯一的文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{g.user_id}_{timestamp}.{ext}"
            
            # 保存文件
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            # 生成文件URL
            file_url = f"/static/uploads/{filename}"
            
            logger.info(f"用户{g.user_id}上传图片成功：{filename}")
            return format_response(data={"url": file_url, "filename": filename})
            
        except Exception as e:
            logger.error(f"图片上传失败：{str(e)}")
            return format_response(500, f"图片上传失败：{str(e)}")

# 命名空间将在app/__init__.py中注册
