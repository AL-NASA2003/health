#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文心大模型API检测脚本
"""
import sys
import os
import requests
import json

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import (
    ERNIE_API_KEY,
    ERNIE_SECRET_KEY,
    ERNIE_ACCESS_TOKEN_URL,
    ERNIE_EMBEDDING_URL,
    ERNIE_IMAGE_GENERATE_URL
)


def get_access_token():
    """获取文心大模型访问令牌"""
    print("=" * 60)
    print("步骤1: 获取访问令牌")
    print("=" * 60)
    print(f"API Key: {ERNIE_API_KEY[:10]}...")
    print(f"Secret Key: {ERNIE_SECRET_KEY[:10]}...")
    print(f"Token URL: {ERNIE_ACCESS_TOKEN_URL}")
    print()

    url = f"{ERNIE_ACCESS_TOKEN_URL}?grant_type=client_credentials&client_id={ERNIE_API_KEY}&client_secret={ERNIE_SECRET_KEY}"

    try:
        response = requests.post(url, timeout=10)
        print(f"响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if 'access_token' in result:
                token = result['access_token']
                print(f"✓ 获取访问令牌成功!")
                print(f"  Token长度: {len(token)}")
                print()
                return token
            else:
                print(f"✗ 响应中未找到access_token")
                print(f"  响应内容: {result}")
                return None
        else:
            print(f"✗ 获取访问令牌失败")
            print(f"  响应内容: {response.text}")
            return None
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")
        return None


def test_embedding_api(access_token):
    """测试文本嵌入API"""
    print("=" * 60)
    print("步骤2: 测试文本嵌入API")
    print("=" * 60)
    print(f"API URL: {ERNIE_EMBEDDING_URL}")
    print()

    url = f"{ERNIE_EMBEDDING_URL}?access_token={access_token}"
    
    payload = {
        "input": "健康饮食",
        "model": "embedding-v1"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if 'error_code' in result:
                print(f"✗ API返回错误:")
                print(f"  错误码: {result['error_code']}")
                print(f"  错误信息: {result.get('error_msg', '未知错误')}")
            else:
                print(f"✓ 文本嵌入API调用成功!")
                print(f"  响应内容: {json.dumps(result, ensure_ascii=False)[:200]}...")
            return True
        else:
            print(f"✗ 文本嵌入API调用失败")
            print(f"  响应内容: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")
        return False


def test_image_generate_api(access_token):
    """测试图像生成API"""
    print("=" * 60)
    print("步骤3: 测试图像生成API")
    print("=" * 60)
    print(f"API URL: {ERNIE_IMAGE_GENERATE_URL}")
    print()

    url = f"{ERNIE_IMAGE_GENERATE_URL}?access_token={access_token}"
    
    payload = {
        "prompt": "一盘美味的红烧肉",
        "width": 1024,
        "height": 1024
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if 'error_code' in result:
                print(f"✗ API返回错误:")
                print(f"  错误码: {result['error_code']}")
                print(f"  错误信息: {result.get('error_msg', '未知错误')}")
            else:
                print(f"✓ 图像生成API调用成功!")
                print(f"  响应内容: {json.dumps(result, ensure_ascii=False)[:200]}...")
            return True
        else:
            print(f"✗ 图像生成API调用失败")
            print(f"  响应内容: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")
        return False


def main():
    """主函数"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "文心大模型API检测" + " " * 25 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    # 步骤1: 获取访问令牌
    access_token = get_access_token()

    if not access_token:
        print("\n")
        print("✗ 获取访问令牌失败，无法继续测试")
        print("请检查:")
        print("  1. API Key 和 Secret Key 是否正确")
        print("  2. 网络连接是否正常")
        print("  3. 百度智能云服务是否已开通")
        return 1

    # 步骤2: 测试文本嵌入API
    embedding_success = test_embedding_api(access_token)
    print()

    # 步骤3: 测试图像生成API
    image_success = test_image_generate_api(access_token)
    print()

    # 总结
    print("=" * 60)
    print("检测总结")
    print("=" * 60)
    print(f"访问令牌获取: {'✓ 成功' if access_token else '✗ 失败'}")
    print(f"文本嵌入API:   {'✓ 成功' if embedding_success else '✗ 失败'}")
    print(f"图像生成API:   {'✓ 成功' if image_success else '✗ 失败'}")
    print()

    if access_token and (embedding_success or image_success):
        print("✓ 文心大模型API可用!")
        return 0
    else:
        print("✗ 文心大模型API调用存在问题，请检查配置")
        return 1


if __name__ == "__main__":
    sys.exit(main())
