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
            debug=app.config["DEBUG"],
            threaded=True
        )
    except Exception as e:
        logger.error(f"应用启动失败：{str(e)}")
        raise e