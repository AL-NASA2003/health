#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import subprocess
import sys

def check_port(port):
    """检查端口是否被占用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.0)
    try:
        result = sock.connect_ex(('127.0.0.1', port))
        if result == 0:
            print(f"✅ 端口 {port} 被占用")
            return True
        else:
            print(f"❌ 端口 {port} 未被占用")
            return False
    except Exception as e:
        print(f"检查端口时出错: {e}")
        return False
    finally:
        sock.close()

def get_process_on_port(port):
    """Windows下获取占用端口的进程"""
    try:
        # 使用 netstat 找占用该端口的 PID
        cmd = f"netstat -ano | findstr :{port}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("端口占用信息:")
            print(result.stdout.strip())
            
            # 获取PID
            lines = [line for line in result.stdout.strip().split('\n') if line]
            if lines:
                # 最后一列是 PID
                last_line = lines[-1]
                parts = last_line.split()
                if len(parts) > 0:
                    pid = parts[-1]
                    print(f"\n可能的 PID: {pid}")
                    
                    # 获取进程名
                    cmd_tasklist = f"tasklist /FI \"PID eq {pid}\" /FO TABLE"
                    result_tasklist = subprocess.run(cmd_tasklist, shell=True, capture_output=True, text=True)
                    if result_tasklist.returncode == 0:
                        print("进程信息:")
                        print(result_tasklist.stdout)
        else:
            print(f"netstat 未找到端口 {port} 占用信息")
    except Exception as e:
        print(f"获取进程信息出错: {e}")

print("=" * 60)
print("检查 5000 端口占用情况")
print("=" * 60)

check_port(5000)
get_process_on_port(5000)

print("\n" + "=" * 60)
