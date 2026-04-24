#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智谱AI网页版爬虫 - 启动和测试工具
用于启动浏览器、登录、测试菜谱和图像生成
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.crawler.zhipu_ai_web_crawler import ZhipuAiWebCrawler
from loguru import logger

def main():
    print("=" * 60)
    print("智谱AI网页版爬虫 - 启动工具")
    print("=" * 60)
    print()
    
    # 创建爬虫实例
    crawler = ZhipuAiWebCrawler(headless=False)
    
    try:
        # 初始化浏览器
        print("1. 正在初始化浏览器...")
        if not crawler._init_browser():
            print("❌ 浏览器初始化失败")
            return
        
        print("✅ 浏览器初始化成功")
        print()
        
        # 检查登录状态
        print("2. 检查登录状态...")
        if not crawler.check_login_status():
            print("⚠️  未检测到登录状态")
            print()
            print("=" * 60)
            print("请在浏览器中完成以下步骤：")
            print("=" * 60)
            print("1. 在打开的浏览器中访问 https://chatglm.cn")
            print("2. 使用手机扫码或账号密码登录智谱AI")
            print("3. 登录成功后，按回车键继续...")
            print("=" * 60)
            print()
            
            # 访问登录页面
            crawler.page.get("https://chatglm.cn")
            
            # 等待用户输入
            input("登录完成后，按回车键继续...")
            
            # 再次检查登录状态
            print()
            print("3. 重新检查登录状态...")
            crawler.is_logged_in = crawler.check_login_status()
        
        if crawler.is_logged_in:
            print("✅ 登录成功！")
            print()
            
            # 测试功能
            print("=" * 60)
            print("选择要测试的功能：")
            print("=" * 60)
            print("1. 测试菜谱生成")
            print("2. 测试图像生成")
            print("3. 保持浏览器运行并退出")
            print("4. 退出")
            print()
            
            choice = input("请输入选项 (1-4): ").strip()
            
            if choice == "1":
                print()
                print("测试菜谱生成...")
                test_user = {
                    "health_goal": "减脂",
                    "dietary_preference": "清淡",
                    "calorie_target": 1800
                }
                test_ingredients = ["鸡胸肉", "西兰花", "胡萝卜"]
                
                recipe = crawler.generate_recipe(test_user, test_ingredients)
                print()
                print("=" * 60)
                print("生成的菜谱：")
                print("=" * 60)
                import json
                print(json.dumps(recipe, ensure_ascii=False, indent=2))
                
            elif choice == "2":
                print()
                prompt = input("请输入图像描述（例如：健康美味的水果沙拉）: ").strip()
                if not prompt:
                    prompt = "健康美味的水果沙拉"
                
                print(f"正在生成图像: {prompt}...")
                image = crawler.generate_image(prompt, style="food")
                print()
                print("=" * 60)
                print("生成结果：")
                print("=" * 60)
                import json
                print(json.dumps(image, ensure_ascii=False, indent=2))
                
            elif choice == "3":
                print()
                print("保持浏览器运行中...")
                print("您可以在浏览器中继续使用智谱AI")
                print("按 Ctrl+C 退出...")
                try:
                    import time
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print()
                    print("正在退出...")
            
            elif choice == "4":
                print()
                print("正在退出...")
            
            else:
                print("无效选项")
        
        else:
            print()
            print("❌ 登录状态检测失败，请重试")
    
    except Exception as e:
        print()
        print(f"❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        print()
        print("正在关闭浏览器...")
        crawler.close()
        print("浏览器已关闭")
        print()
        print("=" * 60)
        print("程序结束")
        print("=" * 60)

if __name__ == "__main__":
    main()
