import sys
from app import create_app
from loguru import logger

# 配置日志
logger.add("app.log", rotation="500 MB")

logger.info("开始启动健康饮食系统服务...")

# 创建应用
logger.info("正在创建应用实例...")
app = create_app()
logger.info(f"应用实例创建成功，DEBUG模式：{app.config['DEBUG']}")

if __name__ == "__main__":
    # 启动应用
    try:
        logger.info("正在启动Flask服务...")
        logger.info(f"服务地址：http://0.0.0.0:5000")
        app.run(
            host="0.0.0.0",
            port=5000,
            debug=app.config["DEBUG"],
            threaded=True
        )
    except Exception as e:
        logger.error(f"应用启动失败：{str(e)}")
        import traceback
        traceback.print_exc()
        raise e