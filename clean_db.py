import sys
import os
from app import create_app
from loguru import logger

# 创建应用
app = create_app()

with app.app_context():
    from app.models.hand_account import HandAccount
    from app.models.user import User
    from datetime import datetime
    
    print("=" * 60)
    print("数据库清理工具")
    print("=" * 60)
    
    # 查看用户
    print("\n1. 查看用户...")
    users = User.query.all()
    print(f"找到 {len(users)} 个用户:")
    for u in users:
        print(f"  - 用户ID: {u.id}")
    
    # 查看手账
    print("\n2. 查看手账...")
    handbooks = HandAccount.query.all()
    print(f"找到 {len(handbooks)} 条手账记录:")
    for h in handbooks:
        print(f"  - 手账ID: {h.id}, 用户ID: {h.user_id}, 标题: {h.title}")
        print(f"    图像: {h.image[:80] if h.image else '无'}")
    
    # 删除手账
    print("\n3. 删除所有手账...")
    for h in handbooks:
        h.delete()
    print(f"已删除 {len(handbooks)} 条手账")
    
    # 初始化测试数据
    print("\n4. 初始化新的测试手账...")
    # 用户ID为11的是测试用户（从刚才的输出看到的）
    user_id = 11
    
    mock_handbooks = [
        {
            "title": "健康饮食",
            "content": "今天吃了很多蔬菜水果，感觉很健康！",
            "image": "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=healthy%20food%20vegetables%20fruits&image_size=square_hd"
        },
        {
            "title": "美味早餐",
            "content": "面包+牛奶+鸡蛋，完美的早餐！",
            "image": "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=delicious%20breakfast%20bread%20milk%20eggs&image_size=square_hd"
        }
    ]
    
    for item in mock_handbooks:
        handbook = HandAccount(
            user_id=user_id,
            title=item['title'],
            content=item['content'],
            image=item['image']
        )
        handbook.save()
    
    print(f"已添加 {len(mock_handbooks)} 条测试手账")
    
    print("\n" + "=" * 60)
    print("清理完成！")
    print("=" * 60)
