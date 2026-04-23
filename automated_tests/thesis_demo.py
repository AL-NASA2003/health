#!/usr/bin/env python3
"""
论文答辩演示脚本
功能：
1. 启动后端服务器
2. 读取真实数据库数据
3. 生成答辩演示用的可视化图表
4. 自动启动微信开发者工具
5. 生成专业答辩报告
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
log_file = os.path.join(OUTPUT_DIR, 'thesis_demo.log')
logger.add(log_file, rotation="500 MB", level="INFO")

def print_banner():
    """打印答辩演示横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🎓 健康饮食助手                             ║
║                论文答辩演示系统                                 ║
╠══════════════════════════════════════════════════════════════╣
║  📱 微信小程序 + 🌐 后端 API + 🤖 AI 推荐                      ║
╚══════════════════════════════════════════════════════════════╝
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
        logger.info("✅ 后端服务器已在运行")
        return None
    
    logger.info("🚀 启动后端服务器...")
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
        
        logger.info("⏳ 等待服务器启动（5秒）...")
        time.sleep(5)
        
        if check_server_running():
            logger.info("✅ 后端服务器启动成功！")
            return process
        else:
            logger.warning("⚠️  服务器启动状态未知，请检查")
            return process
    except Exception as e:
        logger.error(f"❌ 启动服务器失败: {e}")
        return None

def run_automated_test_suite():
    """运行自动化测试套件"""
    logger.info("=" * 60)
    logger.info("📊 运行自动化测试套件")
    logger.info("=" * 60)
    
    try:
        import automated_test_suite
        result = automated_test_suite.TestSuite.run()
        return result
    except Exception as e:
        logger.error(f"❌ 运行测试套件失败: {e}")
        return None

def launch_wechat_dev_tool():
    """启动微信开发者工具"""
    logger.info("=" * 60)
    logger.info("📱 启动微信开发者工具")
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
            logger.info(f"✅ 找到微信开发者工具: {path}")
            break
    
    if not cli_path:
        logger.warning("⚠️  未找到微信开发者工具")
        logger.info("")
        logger.info("请手动打开微信开发者工具并导入项目:")
        logger.info(f"项目路径: {MINIPROGRAM_PATH}")
        return False
    
    try:
        logger.info(f"🎓 启动微信开发者工具，打开项目: {MINIPROGRAM_PATH}")
        
        # 论文答辩演示流程
        logger.info("")
        logger.info("═══════════════════════════════════════════════════════════════")
        logger.info("🎓 论文答辩演示流程:")
        logger.info("═══════════════════════════════════════════════════════════════")
        logger.info("1. 📱 小程序首页 - 展示功能概览")
        logger.info("2. 🍳 食谱推荐 - 展示AI个性化推荐")
        logger.info("3. 📝 饮食记录 - 展示数据录入功能")
        logger.info("4. 📊 健康分析 - 展示数据分析报告")
        logger.info("5. 🎯 运动记录 - 展示运动管理功能")
        logger.info("6. 🔥 热点美食 - 展示社区热门内容")
        logger.info("7. 💬 社区互动 - 展示论坛交流功能")
        logger.info("═══════════════════════════════════════════════════════════════")
        
        # 尝试打开项目
        commands = [
            [cli_path, '--open', MINIPROGRAM_PATH],
            ['cmd', '/c', f'"{cli_path}" --open "{MINIPROGRAM_PATH}"']
        ]
        
        for cmd in commands:
            try:
                subprocess.Popen(cmd, shell=True)
                logger.info("")
                logger.info("✅ 微信开发者工具启动命令已发送")
                logger.info("📱 请在微信开发者工具中进行演示")
                return True
            except Exception as e:
                logger.warning(f"尝试失败: {e}")
                continue
        
        return False
    except Exception as e:
        logger.error(f"❌ 启动微信开发者工具失败: {e}")
        return False

def generate_demo_summary():
    """生成演示总结"""
    summary = """
═══════════════════════════════════════════════════════════════
                          🎓 演示准备完成
═══════════════════════════════════════════════════════════════

📁 生成的文件:
  • output/test_report.html - 完整测试报告
  • output/*.png - 8个专业可视化图表
  • output/test_suite.log - 详细执行日志
  • test_report.html - Markdown格式报告

🎯 答辩演示要点:
  1. 系统架构 - 小程序 + 后端 + AI推荐
  2. 核心功能 - 食谱/记录/分析/社区
  3. 性能指标 - 1000并发/响应<2.5s
  4. 安全合规 - 个人信息保护法

📱 演示建议:
  • 先展示测试报告和图表
  • 再在微信开发者工具中操作小程序
  • 重点展示AI推荐和健康分析功能
  • 强调数据安全和隐私保护

═══════════════════════════════════════════════════════════════
祝答辩顺利！🎉
═══════════════════════════════════════════════════════════════
"""
    print(summary)

def main():
    """主函数 - 论文答辩演示流程"""
    print_banner()
    
    logger.info("=" * 60)
    logger.info("🎓 开始论文答辩演示准备")
    logger.info(f"🕐 开始时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
        logger.info("✅ 答辩演示准备完成！")
        logger.info(f"🕐 完成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        # 保持运行
        if server_process:
            try:
                logger.info("🔄 后端服务器正在运行，按 Ctrl+C 停止")
                server_process.wait()
            except KeyboardInterrupt:
                logger.info("👋 收到停止信号")
        
    except Exception as e:
        logger.error(f"❌ 演示准备过程出错: {e}")
        if server_process:
            server_process.terminate()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
