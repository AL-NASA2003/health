#!/usr/bin/env python3
"""
微信开发者工具自动化演示脚本
功能：
1. 自动启动微信开发者工具
2. 自动编译小程序
3. 自动展示每个页面
4. 提供清晰的演示流程指导
"""

import sys
import os
import subprocess
import time
import datetime
import json
from loguru import logger

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
MINIPROGRAM_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "miniprogram")

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 配置日志
log_file = os.path.join(OUTPUT_DIR, 'wechat_demo.log')
logger.add(log_file, rotation="500 MB", level="INFO")

class WeChatMiniProgramAutomator:
    """微信小程序自动化演示器"""
    
    def __init__(self):
        self.miniprogram_path = MINIPROGRAM_PATH
        self.pages = self.get_pages_list()
        
    def find_wechat_dev_tool(self):
        """查找微信开发者工具"""
        logger.info("=" * 60)
        logger.info("🔍 查找微信开发者工具")
        logger.info("=" * 60)
        
        # 常见安装路径
        possible_paths = [
            "C:\\Program Files (x86)\\Tencent\\微信web开发者工具\\cli.bat",
            "C:\\Program Files\\Tencent\\微信web开发者工具\\cli.bat",
            os.path.expanduser("~\\AppData\\Local\\Programs\\微信web开发者工具\\cli.bat"),
            "D:\\微信web开发者工具\\cli.bat",
            "E:\\微信web开发者工具\\cli.bat",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"✅ 找到微信开发者工具: {path}")
                return path
        
        # 尝试查找注册表
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Tencent\微信web开发者工具")
            install_path = winreg.QueryValueEx(key, "InstallPath")[0]
            cli_path = os.path.join(install_path, "cli.bat")
            if os.path.exists(cli_path):
                logger.info(f"✅ 从注册表找到微信开发者工具: {cli_path}")
                return cli_path
        except Exception:
            pass
        
        logger.warning("⚠️  未找到微信开发者工具")
        return None
    
    def get_pages_list(self):
        """获取小程序页面列表"""
        logger.info("📄 读取小程序页面配置")
        
        app_json_path = os.path.join(self.miniprogram_path, "app.json")
        if not os.path.exists(app_json_path):
            logger.warning("⚠️  未找到 app.json")
            return []
        
        try:
            with open(app_json_path, 'r', encoding='utf-8') as f:
                app_config = json.load(f)
            
            pages = app_config.get('pages', [])
            logger.info(f"✅ 找到 {len(pages)} 个页面")
            return pages
        except Exception as e:
            logger.error(f"❌ 读取页面配置失败: {e}")
            return []
    
    def launch_wechat_dev_tool(self, cli_path):
        """启动微信开发者工具并打开项目"""
        logger.info("=" * 60)
        logger.info("🚀 启动微信开发者工具")
        logger.info("=" * 60)
        
        try:
            # 使用微信开发者工具CLI打开项目
            cmd = [cli_path, '--open', self.miniprogram_path]
            logger.info(f"执行命令: {' '.join(cmd)}")
            
            process = subprocess.Popen(cmd, shell=True)
            logger.info("✅ 微信开发者工具启动命令已发送")
            
            # 等待工具启动
            logger.info("⏳ 等待微信开发者工具启动（10秒）...")
            time.sleep(10)
            
            return process
        except Exception as e:
            logger.error(f"❌ 启动微信开发者工具失败: {e}")
            return None
    
    def print_demo_guide(self):
        """打印演示指南"""
        guide = """
╔══════════════════════════════════════════════════════════════╗
║                    🎓 论文答辩演示指南                          ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  📱 第一步：确认小程序已编译                                    ║
║  ─────────────────────────────────────────────────────         ║
║     在微信开发者工具中，点击"编译"按钮                          ║
║     确保控制台无报错，模拟器已显示小程序                          ║
║                                                               ║
║  🎯 第二步：按顺序演示各页面                                    ║
║  ─────────────────────────────────────────────────────         ║
║  1️⃣  首页 (pages/index/index)                                   ║
║     ── 展示系统概览和主要功能入口                               ║
║                                                               ║
║  2️⃣  食谱页 (pages/recipe/recipe)                               ║
║     ── 浏览食谱列表，点击查看详情                               ║
║     ── 演示食谱推荐功能                                         ║
║                                                               ║
║  3️⃣  饮食记录 (pages/diet/diet)                                ║
║     ── 记录今日饮食摄入                                        ║
║     ── 查看饮食统计和分析                                      ║
║                                                               ║
║  4️⃣  热点美食 (pages/hotfood/hotfood)                          ║
║     ── 展示社区热门内容                                        ║
║     ── 浏览小红书美食推荐                                      ║
║                                                               ║
║  5️⃣  社区论坛 (pages/forum/forum)                               ║
║     ── 查看帖子列表，演示互动功能                              ║
║                                                               ║
║  6️⃣  健康分析 (pages/health/health)                             ║
║     ── 展示个人健康指标                                        ║
║     ── 查看营养摄入分析                                        ║
║                                                               ║
║  7️⃣  用户中心 (pages/user/user)                                 ║
║     ── 展示个人信息和设置                                      ║
║                                                               ║
║  ⚡ 第三步：性能和安全说明                                      ║
║  ─────────────────────────────────────────────────────         ║
║  • 打开测试报告：automated_tests/output/test_report.html       ║
║  • 展示API测试结果和性能曲线                                    ║
║  • 说明数据安全和隐私保护措施                                   ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(guide)
    
    def print_page_list(self):
        """打印页面列表"""
        logger.info("=" * 60)
        logger.info("📄 小程序页面列表")
        logger.info("=" * 60)
        
        for idx, page in enumerate(self.pages, 1):
            logger.info(f"{idx}. {page}")
        
        logger.info("=" * 60)
    
    def manual_demo_mode(self):
        """手动演示模式"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║               📋 手动操作指南（如果自动启动失败）                 ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  1️⃣  打开微信开发者工具                                         ║
║                                                               ║
║  2️⃣  选择"导入项目"                                            ║
║                                                               ║
║  3️⃣  选择项目目录：                                             ║
║     %s
║                                                               ║
║  4️⃣  点击"编译"按钮                                             ║
║                                                               ║
║  5️⃣  在模拟器中开始演示各页面                                   ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
        """ % self.miniprogram_path)
        
        print("\n\n请按任意键继续查看详细演示流程...")
        try:
            input()
        except:
            pass
    
    def run(self):
        """运行完整演示流程"""
        print_banner()
        
        logger.info("=" * 60)
        logger.info("🎓 微信小程序自动化演示")
        logger.info(f"🕐 开始时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        # 1. 查找微信开发者工具
        cli_path = self.find_wechat_dev_tool()
        
        # 2. 打印页面列表
        self.print_page_list()
        
        # 3. 打印演示指南
        self.print_demo_guide()
        
        # 4. 尝试自动启动
        wechat_process = None
        if cli_path:
            wechat_process = self.launch_wechat_dev_tool(cli_path)
        else:
            self.manual_demo_mode()
        
        # 5. 总结
        print("\n")
        logger.info("=" * 60)
        logger.info("✅ 演示准备完成！")
        logger.info("=" * 60)
        logger.info("\n")
        logger.info("📝 下一步操作：")
        logger.info("  1. 在微信开发者工具中确认小程序已编译")
        logger.info("  2. 按照上面的指南演示各个功能")
        logger.info("  3. 同时展示测试报告和可视化图表")
        logger.info("  4. 准备回答评委提问")
        logger.info("\n")
        logger.info("🎓 祝你答辩顺利！")
        
        # 保持运行
        if wechat_process:
            try:
                wechat_process.wait()
            except KeyboardInterrupt:
                logger.info("👋 演示结束")
        
        return True

def print_banner():
    """打印横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🎓 健康饮食助手                             ║
║               微信小程序演示自动化系统                          ║
╠══════════════════════════════════════════════════════════════╣
║  📱 自动启动 + 📋 页面演示 + 🎯 答辩指南                        ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """主函数"""
    automator = WeChatMiniProgramAutomator()
    success = automator.run()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
