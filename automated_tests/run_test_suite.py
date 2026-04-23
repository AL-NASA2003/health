#!/usr/bin/env python3
"""
测试套件启动器
功能：
1. 启动后端服务器（如果需要）
2. 运行自动化测试
3. 显示进度
"""

import sys
import os
import subprocess
import time
import socket
from loguru import logger

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def is_port_in_use(port):
    """检查端口是否被占用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        result = sock.connect_ex(('127.0.0.1', port))
        return result == 0
    finally:
        sock.close()


def start_backend_server():
    """启动后端服务器"""
    logger.info("=" * 60)
    logger.info("🚀 启动后端服务器")
    logger.info("=" * 60)
    
    # 检查端口
    if is_port_in_use(5000):
        logger.warning("⚠️  5000端口已被占用，假设服务器已在运行")
        return None
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 启动服务器
    try:
        if sys.platform == 'win32':
            # Windows: 使用 start 命令启动新窗口
            process = subprocess.Popen(
                ['start', '健康饮食后端', '/min', 'python', 'run.py'],
                shell=True,
                cwd=project_root
            )
        else:
            # Linux/Mac: 后台运行
            process = subprocess.Popen(
                ['python', 'run.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=project_root
            )
        
        logger.info("⏳ 等待服务器启动...")
        time.sleep(5)
        
        # 检查是否成功启动
        if is_port_in_use(5000):
            logger.info("✅ 后端服务器启动成功")
            return process
        else:
            logger.warning("⚠️  服务器可能未完全启动，继续尝试...")
            time.sleep(3)
            return process
            
    except Exception as e:
        logger.error(f"❌ 启动服务器失败: {e}")
        return None


def run_tests():
    """运行测试"""
    logger.info("=" * 60)
    logger.info("🧪 运行自动化测试套件")
    logger.info("=" * 60)
    
    try:
        # 导入并运行测试套件
        from automated_test_suite import TestSuite
        success = TestSuite.run()
        return success
    except Exception as e:
        logger.error(f"❌ 运行测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    # 配置日志
    logger.remove()
    logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>", level="INFO")
    
    logger.info("=" * 60)
    logger.info("🚀 健康饮食助手 - 测试套件启动器")
    logger.info("=" * 60)
    
    # 启动服务器
    server_process = start_backend_server()
    
    # 运行测试
    success = run_tests()
    
    # 完成
    logger.info("=" * 60)
    if success:
        logger.info("🎉 所有任务完成！")
    else:
        logger.warning("⚠️  部分任务可能未完成")
    logger.info("=" * 60)
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
