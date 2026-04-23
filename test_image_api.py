#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试图像生成API
"""
import sys
import os
import requests
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app.config import ZHIPUAI_API_KEY
from app import create_app

def test_cogview_api():
    """直接测试智谱AI的CogView-3-Flash API"""
    print("=" * 60)
    print("测试智谱AI CogView-3-Flash API")
    print("=" * 60)
    
    api_url = "https://open.bigmodel.cn/api/paas/v4/images/generations"
    
    headers = {
        "Authorization": f"Bearer {ZHIPUAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "cogview-3-flash",
        "prompt": "A beautiful food photography, delicious healthy meal",
        "size": "1024x1024"
    }
    
    print(f"\n请求URL: {api_url}")
    print(f"请求模型: {payload['model']}")
    print(f"提示词: {payload['prompt']}")
    print(f"API Key: {ZHIPUAI_API_KEY[:20]}...")
    
    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"\n响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if "data" in result and len(result["data"]) > 0:
                image_url = result["data"][0].get("url")
                print(f"\n✅ 生成成功!")
                print(f"图片URL: {image_url}")
                return True
            elif "error" in result:
                print(f"\n❌ API错误: {result['error']}")
                return False
        else:
            print(f"\n❌ 请求失败")
            print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ 异常: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False


def test_backend_api():
    """测试后端API是否正常运行"""
    print("\n" + "=" * 60)
    print("测试后端API")
    print("=" * 60)
    
    # 先测试根路径
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        print(f"\n根路径状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"根路径响应: {response.json()}")
        else:
            print("后端服务可能未运行，请先启动后端")
            return False
    except:
        print("后端服务可能未运行，请先启动后端")
        return False
    
    return True


def main():
    print("健康饮食系统 - 图像生成API测试")
    print("=" * 60)
    
    # 先测试智谱AI API
    cogview_ok = test_cogview_api()
    
    print(f"\n智谱AI API测试结果: {'✅ 成功' if cogview_ok else '❌ 失败'}")
    
    # 测试后端
    backend_ok = test_backend_api()
    print(f"\n后端API测试结果: {'✅ 正常' if backend_ok else '❌ 异常'}")
    
    print("\n" + "=" * 60)
    if cogview_ok:
        print("图像生成API已就绪!")
    else:
        print("请检查API Key配置或网络连接")
    print("=" * 60)


if __name__ == "__main__":
    main()
