#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
百度智能云千帆API测试脚本
"""
import sys
import requests
import json


# 从配置文件导入
sys.path.insert(0, '.')
from app.config import QIANFAN_OPENAI_API_KEY, QIANFAN_OPENAI_BASE_URL


def test_chat_completion():
    """测试聊天完成API"""
    print("=" * 60)
    print("测试千帆聊天完成API")
    print("=" * 60)
    print(f"API Key: {QIANFAN_OPENAI_API_KEY[:40]}...")
    print(f"Base URL: {QIANFAN_OPENAI_BASE_URL}")
    print()

    url = f"{QIANFAN_OPENAI_BASE_URL}/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {QIANFAN_OPENAI_API_KEY}"
    }
    
    payload = {
        "model": "ernie-3.5-8k",
        "messages": [
            {
                "role": "user",
                "content": "你好，请介绍一下你自己"
            }
        ]
    }

    try:
        print("正在发送请求...")
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
        print(f"响应状态码: {response.status_code}")
        print()

        if response.status_code == 200:
            result = response.json()
            print("✓ API调用成功!")
            print()
            print("响应内容:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print()
            if "choices" in result and len(result["choices"]) > 0:
                print("AI回复:")
                print(result["choices"][0]["message"]["content"])
            return True
        else:
            print("✗ API调用失败")
            print(f"响应内容: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_image_generation():
    """测试图像生成API"""
    print()
    print("=" * 60)
    print("测试千帆图像生成API")
    print("=" * 60)
    print()

    url = f"{QIANFAN_OPENAI_BASE_URL}/images/generations"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {QIANFAN_OPENAI_API_KEY}"
    }
    
    payload = {
        "model": "ernie-4.0-turbo",
        "prompt": "一盘美味的红烧肉，色泽诱人，香气扑鼻",
        "width": 1024,
        "height": 1024
    }

    try:
        print("正在发送请求...")
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60
        )
        print(f"响应状态码: {response.status_code}")
        print()

        if response.status_code == 200:
            result = response.json()
            print("✓ 图像生成API调用成功!")
            print()
            print("响应内容:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return True
        else:
            print("✗ 图像生成API调用失败")
            print(f"响应内容: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 18 + "千帆API测试" + " " * 28 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    # 测试聊天API
    chat_success = test_chat_completion()
    
    # 测试图像生成API
    image_success = test_image_generation()
    
    # 总结
    print()
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"聊天API:   {'✓ 成功' if chat_success else '✗ 失败'}")
    print(f"图像生成API: {'✓ 成功' if image_success else '✗ 失败'}")
    print()

    if chat_success or image_success:
        print("✓ 千帆API可用!")
        print()
        print("建议：")
        print("1. 如果API Key权限未配置，请在百度智能云控制台")
        print("   点击'配置权限'，选择'千帆ModelBuilder'或'所有资源'")
        return 0
    else:
        print("✗ 千帆API调用存在问题")
        print()
        print("请检查：")
        print("1. API Key是否正确")
        print("2. API Key是否已配置权限")
        print("3. 网络连接是否正常")
        return 1


if __name__ == "__main__":
    sys.exit(main())
