import requests
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'app', 'static', 'uploads')

print("="*50)
print("静态文件测试")
print("="*50)

# 检查本地文件
print("\n1. 检查本地上传文件:")
if os.path.exists(UPLOAD_DIR):
    files = os.listdir(UPLOAD_DIR)
    print(f"   上传目录存在，包含 {len(files)} 个文件")
    for f in files[:5]:
        print(f"   - {f}")
else:
    print("   上传目录不存在！")

# 测试访问
test_urls = [
    'http://127.0.0.1:5000/static/uploads/1_20260327_030737.jpg',
    'http://192.168.53.139:5000/static/uploads/1_20260327_030737.jpg'
]

print("\n2. 测试HTTP访问:")
for url in test_urls:
    try:
        print(f"\n   测试: {url}")
        response = requests.get(url, timeout=5)
        print(f"   状态码: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"   Content-Length: {response.headers.get('Content-Length', 'N/A')}")
        if response.status_code == 200:
            print("   ✅ 访问成功！")
        else:
            print(f"   ❌ 访问失败")
            print(f"   响应内容: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ 请求异常: {str(e)}")

print("\n" + "="*50)
