#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试现在的图像生成API
"""
import sys
import os
import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_handbook_templates():
    """测试手账模板API"""
    print("\n" + "="*60)
    print("测试手账模板API")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/image/handbook-templates", timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 成功！")
            print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return True
        else:
            print(f"\n❌ 失败")
            print(f"响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ 异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_zhipu_status():
    """测试智谱网页API状态"""
    print("\n" + "="*60)
    print("测试智谱网页API状态")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/zhipu/status", timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 成功！")
            print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return True
        else:
            print(f"\n❌ 失败")
            print(f"响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ 异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("健康饮食系统 - 图像API测试")
    print("="*60)
    
    # 检查服务是否运行
    try:
        print("\n检查后端服务...")
        response = requests.get("http://localhost:5000", timeout=5)
        print(f"✅ 后端服务运行正常！")
    except Exception as e:
        print(f"❌ 后端服务未运行或连接失败: {str(e)}")
        return
    
    # 运行测试
    results = []
    results.append(("手账模板API", test_handbook_templates()))
    results.append(("智谱网页API状态", test_zhipu_status()))
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name:30s}: {status}")
    
    pass_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    print(f"\n总计: {pass_count}/{total_count} 测试通过")
    
    print("\n" + "="*60)
    print("新增加的智谱网页API功能:")
    print("="*60)
    print("1. GET  /api/zhipu/status - 获取状态")
    print("2. POST /api/zhipu/login - 启动浏览器登录")
    print("3. GET  /api/zhipu/check-login - 检查登录状态")
    print("4. POST /api/zhipu/generate-recipe - 通过网页生成菜谱")
    print("5. POST /api/zhipu/generate-image - 通过网页生成图像")
    
    print("\n" + "="*60)
    print("智谱AI网页爬虫功能特点:")
    print("="*60)
    print("- 类似小红书爬虫，使用浏览器自动化")
    print("- 用户在浏览器中手动登录智谱AI")
    print("- 通过网页版生成菜谱和图像")
    print("- 自动保存和同步数据")
    print("- 有备用方案，即使爬虫失败也能正常运行")
    print("="*60)

if __name__ == "__main__":
    main()
