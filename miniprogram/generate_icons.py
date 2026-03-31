"""
生成 TabBar 图标
"""
from PIL import Image, ImageDraw
import os

def create_icon(filename, color, icon_type):
    """创建图标"""
    size = 81
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制圆角矩形背景
    radius = 10
    draw.rounded_rectangle([(0, 0), (size-1, size-1)], radius=radius, fill=color)
    
    # 根据类型绘制不同的图标
    center = size // 2
    
    if icon_type == 'home':
        # 绘制房子图标
        points = [
            (center, 20),      # 顶部
            (60, 35),          # 右上
            (60, 60),          # 右下
            (20, 60),          # 左下
            (20, 35),          # 左上
        ]
        draw.polygon(points, outline='white', width=3)
        # 门
        draw.rectangle([(35, 45), (45, 60)], outline='white', width=2)
        
    elif icon_type == 'diet':
        # 绘制餐具图标
        # 叉子
        draw.line([(25, 25), (25, 55)], fill='white', width=3)
        for i in range(3):
            draw.line([(20, 30+i*8), (30, 30+i*8)], fill='white', width=2)
        # 勺子
        draw.ellipse([(45, 25), (65, 45)], outline='white', width=3)
        draw.line([(55, 45), (55, 60)], fill='white', width=3)
        
    elif icon_type == 'recipe':
        # 绘制书本图标
        draw.rectangle([(20, 20), (60, 60)], outline='white', width=3)
        draw.line([(40, 20), (40, 60)], fill='white', width=2)
        # 页面线条
        for i in range(3):
            draw.line([(25, 30+i*10), (37, 30+i*10)], fill='white', width=2)
            draw.line([(43, 30+i*10), (55, 30+i*10)], fill='white', width=2)
            
    elif icon_type == 'hot':
        # 绘制火焰图标
        points = [
            (center, 15),
            (55, 35),
            (50, 55),
            (center, 65),
            (30, 55),
            (25, 35),
        ]
        draw.polygon(points, outline='white', width=3)
        # 内部火焰
        inner_points = [
            (center, 30),
            (45, 40),
            (42, 50),
            (center, 55),
            (38, 50),
            (35, 40),
        ]
        draw.polygon(inner_points, outline='white', width=2)
    
    # 保存
    img.save(filename, 'PNG')
    print(f'创建图标: {filename}')

def main():
    # 图标目录
    tab_dir = 'images/tab'
    os.makedirs(tab_dir, exist_ok=True)
    
    # 定义图标
    icons = [
        ('home', '首页'),
        ('diet', '饮食'),
        ('recipe', '食谱'),
        ('hot', '热点'),
    ]
    
    # 颜色
    inactive_color = '#999999'
    active_color = '#4CAF50'
    
    # 创建图标
    for icon_name, icon_desc in icons:
        # 未选中状态
        create_icon(
            f'{tab_dir}/{icon_name}.png',
            inactive_color,
            icon_name
        )
        # 选中状态
        create_icon(
            f'{tab_dir}/{icon_name}_active.png',
            active_color,
            icon_name
        )
    
    print('\n所有图标创建完成！')

if __name__ == '__main__':
    main()
