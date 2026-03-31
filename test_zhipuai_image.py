#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智谱AI图像生成测试脚本
"""
import sys
import requests
import json
import time


# 从配置文件导入
sys.path.insert(0, '.')
from app.config import ZHIPUAI_API_KEY


def test_zhipuai_image_generation():
    """测试智谱AI图像生成"""
    print("=" * 60)
    print("智谱AI图像生成测试")
    print("=" * 60)
    print(f"API Key: {ZHIPUAI_API_KEY[:15]}...")
    print()

    api_url = "https://open.bigmodel.cn/api/paas/v4/images/generations"
    
    headers = {
        "Authorization": f"Bearer {ZHIPUAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "cogview-3-flash",
        "prompt": "一盘美味的红烧肉，色泽诱人，香气扑鼻",
        "size": "1024x1024"
    }

    print("请求参数:")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print()

    try:
        print("正在发送请求（15秒超时）...")
        start_time = time.time()
        
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=15
        )
        
        elapsed_time = time.time() - start_time
        print(f"响应时间: {elapsed_time:.2f}秒")
        print(f"响应状态码: {response.status_code}")
        print()

        if response.status_code == 200:
            result = response.json()
            print("✓ 请求成功!")
            print()
            print("完整响应内容:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print()
            
            if "data" in result and len(result["data"]) > 0:
                image_data = result["data"][0]
                print("图像数据:")
                print(f"  URL: {image_data.get('url', 'N/A')}")
                print(f"  b64_json: {'存在' if image_data.get('b64_json') else '不存在'}")
                print(f"  revised_prompt: {image_data.get('revised_prompt', 'N/A')}")
                return True
            else:
                print("✗ 响应中没有data字段或data为空")
                return False
        else:
            print("✗ 请求失败")
            print(f"响应内容: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print("✗ 请求超时")
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
    print("║" + " " * 15 + "智谱AI图像生成测试" + " " * 22 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    success = test_zhipuai_image_generation()
    
    print()
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    if success:
        print("✓ 智谱AI图像生成API正常!")
        return 0
    else:
        print("✗ 智谱AI图像生成API有问题")
        return 1


if __name__ == "__main__":
    sys.exit(main())
