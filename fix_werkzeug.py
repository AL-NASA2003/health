#!/usr/bin/env python3
"""
修复Werkzeug与Flask的兼容性问题
在导入Flask之前，将werkzeug.urls.url_quote映射到werkzeug.urls.quote
"""
import sys
import werkzeug.urls

# 在Werkzeug 3.x中，url_quote被重命名为quote
if not hasattr(werkzeug.urls, 'url_quote'):
    werkzeug.urls.url_quote = werkzeug.urls.quote

# 现在可以安全地导入Flask
from app import create_app
from loguru import logger

# 创建应用
app = create_app()

if __name__ == "__main__":
    # 启动应用
    try:
        app.run(
            host="0.0.0.0",
            port=5000,
            debug=app.config.get("DEBUG", True),
            threaded=True
        )
    except Exception as e:
        logger.error(f"应用启动失败：{str(e)}")
        raise e
