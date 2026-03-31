import os
import datetime
from app import db
from app.crawler.xhs_crawler import crawl_xhs_hot_food
from loguru import logger

def backup_database():
    """数据库备份
    使用mysqldump命令，需确保环境变量中有mysql路径
    """
    try:
        # 备份文件名
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        backup_file = os.path.join(
            backup_dir,
            f"health_food_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        )
        
        # 构造备份命令
        from app.config import config_map, env
        config = config_map[env]
        cmd = (
            f"mysqldump -h{config.MYSQL_HOST} -P{config.MYSQL_PORT} "
            f"-u{config.MYSQL_USER} -p{config.MYSQL_PWD} "
            f"{config.MYSQL_DB} > {backup_file}"
        )
        
        # 执行备份
        import subprocess
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"数据库备份成功，文件：{backup_file}")
        else:
            logger.error(f"数据库备份失败：{result.stderr}")
            
    except Exception as e:
        logger.error(f"数据库备份任务执行失败：{str(e)}")

# 导出爬虫任务（从crawler模块）
__all__ = ["crawl_xhs_hot_food", "backup_database"]