#!/usr/bin/env python3
"""查找字体文件路径"""
from matplotlib import font_manager

print("=== 查找中文字体文件 ===")
chinese_font_names = [
    'SimHei', 'Microsoft YaHei', 'SimSun', 'STSong', 
    'STKaiti', 'FangSong', 'DengXian', 'Noto Sans SC'
]

for f in font_manager.fontManager.ttflist:
    for name in chinese_font_names:
        if name in f.name:
            print(f"✅ {f.name}:")
            print(f"   路径: {f.fname}")