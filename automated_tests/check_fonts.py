#!/usr/bin/env python3
"""检查系统中可用的字体"""
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontManager

print("=== 系统中可用的字体 ===")
fm = FontManager()
fonts = [f.name for f in fm.ttflist]
print("可用的字体名称:")
for font in sorted(fonts):
    print(f"  - {font}")

print("\n=== 查找常见中文字体 ===")
chinese_fonts = [
    'SimHei', 'Microsoft YaHei', 'SimSun', 'SimKai', 
    'SimFang', 'SimHei', 'KaiTi', 'FangSong', 
    'STSong', 'STKaiti', 'STFangsong', 'STSong',
    'Arial Unicode MS', 'DejaVu Sans'
]

found = []
for font in chinese_fonts:
    if font in fonts:
        found.append(font)
        print(f"✅ 找到字体: {font}")

if found:
    print(f"\n使用字体: {found[0]}")
else:
    print("\n⚠️ 未找到常用中文字体，使用默认字体")