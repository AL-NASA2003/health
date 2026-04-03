#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
导入SQL文件到SQLite数据库
"""
import sqlite3
import os
from loguru import logger

def import_sql_file(db_path, sql_file):
    """导入SQL文件到SQLite数据库"""
    try:
        # 连接到SQLite数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 读取SQL文件
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # 执行SQL脚本
        cursor.executescript(sql_script)
        
        # 提交事务
        conn.commit()
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        logger.info(f"成功导入SQL文件: {sql_file}")
        return True
    except Exception as e:
        logger.error(f"导入SQL文件失败: {sql_file}, 错误: {str(e)}")
        return False

def main():
    """主函数"""
    # 数据库路径
    db_path = "health_food.db"
    
    # SQL文件路径
    sql_files = [
        "health_food_db_sqlite.sql",
        "mock_data_sqlite.sql"
    ]
    
    # 检查数据库文件是否存在
    if os.path.exists(db_path):
        logger.info(f"数据库文件 {db_path} 已存在，将删除并重新创建")
        # 删除现有数据库文件
        try:
            os.remove(db_path)
            logger.info(f"已删除现有数据库文件: {db_path}")
        except Exception as e:
            logger.error(f"删除数据库文件失败: {str(e)}")
            return
    else:
        logger.info(f"数据库文件 {db_path} 不存在，将创建新数据库")
    
    # 导入SQL文件
    for sql_file in sql_files:
        if os.path.exists(sql_file):
            logger.info(f"开始导入SQL文件: {sql_file}")
            success = import_sql_file(db_path, sql_file)
            if not success:
                logger.error(f"导入 {sql_file} 失败，停止执行")
                return
        else:
            logger.error(f"SQL文件不存在: {sql_file}")
            return
    
    logger.info("所有SQL文件导入成功！")

if __name__ == "__main__":
    main()
