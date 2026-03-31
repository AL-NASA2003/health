import os

# 打印当前目录
print('当前目录:', os.getcwd())

# 检查项目结构
print('\n项目结构:')
for root, dirs, files in os.walk('.'):
    level = root.replace('.', '').count(os.sep)
    indent = ' ' * 4 * level
    print(f'{indent}{os.path.basename(root)}/')
    subindent = ' ' * 4 * (level + 1)
    for file in files[:5]:  # 只显示前5个文件
        print(f'{subindent}{file}')
    if len(files) > 5:
        print(f'{subindent}... 等 {len(files) - 5} 个文件')