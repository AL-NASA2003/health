#!/usr/bin/env python3
"""手动触发小红书爬虫脚本"""

import sys
import os

# 添加项目根目录
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.crawler.xhs_drission_crawler import crawl_xhs_hot_food
from loguru import logger

def main():
    print("=" * 60)
    print("健康饮食管理系统 - 小红书爬虫手动触发")
    print("=" * 60)
    print()
    
    # 创建应用上下文
    app = create_app()
    
    with app.app_context():
        print("请选择爬取模式：")
        print("1. 普通模式（不强制登录）")
        print("2. 强制登录模式")
        print()
        
        choice = input("请输入选项 (1/2): ").strip()
        
        force_login = False
        if choice == "2":
            force_login = True
        
        print()
        print("=" * 60)
        print("开始爬取小红书热点美食...")
        print(f"强制登录: {force_login}")
        print("=" * 60)
        print()
        
        try:
            result = crawl_xhs_hot_food(force_login=force_login, manual=True)
            
            if result:
                logger.info("✓ 爬取任务完成！")
            else:
                logger.warning("⚠️  爬取任务返回 False")
                
        except Exception as e:
            logger.error(f"✗ 爬取失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == "__main__":
    main()
