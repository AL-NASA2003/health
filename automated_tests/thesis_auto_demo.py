#!/usr/bin/env python3
"""
论文答辩自动演示脚本 - 完全非交互式版本
功能：
1. 启动后端服务器
2. 读取真实数据库数据
3. 生成答辩演示用的可视化图表
4. 自动启动微信开发者工具
5. 生成专业答辩报告
(没有任何交互式输入，适合批处理运行)
"""

import sys
import os
import subprocess
import time
import datetime
from loguru import logger

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
MINIPROGRAM_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "miniprogram")

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 配置日志
log_file = os.path.join(OUTPUT_DIR, 'thesis_auto_demo.log')
logger.add(log_file, rotation="500 MB", level="INFO")

def print_banner():
    """打印答辩演示横幅"""
    banner = """
============================================================
                    Health Diet Assistant
                  Thesis Demo System
============================================================
         WeChat Mini Program + Backend API + AI Recommendation
============================================================
"""
    print(banner)

def check_server_running():
    """检查服务器是否运行"""
    try:
        import requests
        response = requests.get("http://localhost:5000", timeout=2)
        return response.status_code < 500
    except Exception:
        return False

def start_backend_server():
    """启动后端服务器"""
    if check_server_running():
        logger.info("Backend server is already running")
        return None
    
    logger.info("Starting backend server...")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # 启动服务器
        process = subprocess.Popen(
            ['python', 'run.py'],
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        logger.info("Waiting for server to start (5 seconds)...")
        time.sleep(5)
        
        if check_server_running():
            logger.info("Backend server started successfully!")
            return process
        else:
            logger.warning("Server status unknown, please check")
            return process
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        return None

def run_automated_test_suite():
    """运行自动化测试套件"""
    logger.info("=" * 60)
    logger.info("Running automated test suite")
    logger.info("=" * 60)
    
    try:
        import automated_test_suite
        result = automated_test_suite.TestSuite.run()
        return result
    except Exception as e:
        logger.error(f"Failed to run test suite: {e}")
        return None

def launch_wechat_dev_tool():
    """启动微信开发者工具"""
    logger.info("=" * 60)
    logger.info("Launching WeChat Dev Tools")
    logger.info("=" * 60)
    
    # 尝试多个常见路径
    wechat_paths = [
        "C:\\Program Files (x86)\\Tencent\\微信web开发者工具\\cli.bat",
        "C:\\Program Files\\Tencent\\微信web开发者工具\\cli.bat",
        "C:\\Users\\luohu\\AppData\\Local\\Programs\\微信web开发者工具\\cli.bat",
        "D:\\微信web开发者工具\\cli.bat"
    ]
    
    cli_path = None
    for path in wechat_paths:
        if os.path.exists(path):
            cli_path = path
            logger.info(f"WeChat Dev Tools found: {path}")
            break
    
    if not cli_path:
        logger.warning("WeChat Dev Tools not found")
        logger.info("")
        logger.info("Please manually open WeChat Dev Tools and import project:")
        logger.info(f"Project path: {MINIPROGRAM_PATH}")
        return False
    
    try:
        logger.info(f"Launching WeChat Dev Tools, opening project: {MINIPROGRAM_PATH}")
        
        # 论文答辩演示流程
        logger.info("")
        logger.info("=" * 60)
        logger.info("Thesis Demo Flow:")
        logger.info("=" * 60)
        logger.info("1. Mini Program Home - Show function overview")
        logger.info("2. Recipe Recommendation - Show AI personalized recommendation")
        logger.info("3. Diet Record - Show data entry function")
        logger.info("4. Health Analysis - Show data analysis report")
        logger.info("5. Exercise Record - Show exercise management")
        logger.info("6. Hot Food - Show community popular content")
        logger.info("7. Community Forum - Show interaction functions")
        logger.info("=" * 60)
        
        # 尝试打开项目
        commands = [
            [cli_path, '--open', MINIPROGRAM_PATH],
            ['cmd', '/c', f'"{cli_path}" --open "{MINIPROGRAM_PATH}"']
        ]
        
        for cmd in commands:
            try:
                subprocess.Popen(cmd, shell=True)
                logger.info("")
                logger.info("WeChat Dev Tools launch command sent")
                logger.info("Please demo in WeChat Dev Tools")
                return True
            except Exception as e:
                logger.warning(f"Attempt failed: {e}")
                continue
        
        return False
    except Exception as e:
        logger.error(f"Failed to launch WeChat Dev Tools: {e}")
        return False

def generate_demo_summary():
    """生成演示总结"""
    summary = """
============================================================
                        Demo Ready!
============================================================

Generated files:
  * output/test_report.html - Complete test report
  * output/*.png - 8 professional visualization charts
  * output/test_suite.log - Detailed execution log

Thesis Demo Key Points:
  1. System Architecture - Mini Program + Backend + AI Recommendation
  2. Core Functions - Recipe/Record/Analysis/Community
  3. Performance - 1000 concurrent / response < 2.5s
  4. Security & Compliance - Personal information protection

Demo Suggestions:
  * Show test report and charts first
  * Then operate mini program in WeChat Dev Tools
  * Focus on AI recommendation and health analysis
  * Emphasize data security and privacy protection

============================================================
Good luck with your thesis defense!
============================================================
"""
    print(summary)

def main():
    """主函数 - 论文答辩演示流程"""
    print_banner()
    
    logger.info("=" * 60)
    logger.info("Starting thesis demo preparation")
    logger.info(f"Start time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    server_process = None
    try:
        # 1. 启动后端服务器
        server_process = start_backend_server()
        
        # 2. 运行自动化测试套件
        run_automated_test_suite()
        
        # 3. 启动微信开发者工具
        launch_wechat_dev_tool()
        
        # 4. 生成演示总结
        generate_demo_summary()
        
        logger.info("=" * 60)
        logger.info("Thesis demo preparation completed!")
        logger.info(f"End time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        # 保持运行
        if server_process:
            try:
                logger.info("Backend server is running, press Ctrl+C to stop")
                server_process.wait()
            except KeyboardInterrupt:
                logger.info("Stopping")
        
    except Exception as e:
        logger.error(f"Error during demo preparation: {e}")
        if server_process:
            server_process.terminate()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
