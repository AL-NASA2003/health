#!/usr/bin/env python3
"""
启动选择器
提供两个选项：
1. 使用网页爬取真实数据
2. 使用本地虚拟数据
"""
import sys
import os

# 尝试使用 tkinter 创建 GUI 选择器
try:
    import tkinter as tk
    from tkinter import messagebox, ttk
    tk_available = True
except ImportError:
    tk_available = False


class Launcher:
    """启动选择器"""
    
    def __init__(self):
        self.choice = None  # 1: 真实数据, 2: 虚拟数据
        self.root = None
        
    def show_gui(self):
        """显示图形界面选择器"""
        if not tk_available:
            return self.show_cli()
            
        self.root = tk.Tk()
        self.root.title("健康饮食系统 - 启动选择")
        self.root.geometry("500x350")
        self.root.resizable(False, False)
        
        # 居中显示
        self._center_window()
        
        # 标题
        title_label = tk.Label(
            self.root, 
            text="请选择数据模式", 
            font=("Microsoft YaHei", 18, "bold")
        )
        title_label.pack(pady=30)
        
        # 按钮1: 真实数据
        btn_real = tk.Button(
            self.root,
            text="🌐 使用网页爬取真实数据",
            font=("Microsoft YaHei", 14),
            width=30,
            height=3,
            bg="#4CAF50",
            fg="white",
            relief=tk.RAISED,
            command=lambda: self._select_choice(1)
        )
        btn_real.pack(pady=10)
        
        # 按钮2: 虚拟数据
        btn_virtual = tk.Button(
            self.root,
            text="📝 使用本地虚拟数据",
            font=("Microsoft YaHei", 14),
            width=30,
            height=3,
            bg="#2196F3",
            fg="white",
            relief=tk.RAISED,
            command=lambda: self._select_choice(2)
        )
        btn_virtual.pack(pady=10)
        
        # 说明标签
        info_text = (
            "真实数据模式：\n"
            "• 定时从网页爬取数据\n"
            "• 数据保存到真实数据库\n"
            "• AI智能筛选并匹配到本地数据库\n\n"
            "虚拟数据模式：\n"
            "• 使用本地预置数据\n"
            "• 快速启动，无需网络\n"
            "• 适合开发和演示"
        )
        info_label = tk.Label(
            self.root,
            text=info_text,
            font=("Microsoft YaHei", 9),
            justify=tk.LEFT
        )
        info_label.pack(pady=20)
        
        self.root.mainloop()
        
        return self.choice
        
    def show_cli(self):
        """显示命令行选择器"""
        print("=" * 60)
        print("健康饮食系统 - 启动选择")
        print("=" * 60)
        print()
        print("请选择数据模式：")
        print()
        print("  [1] 使用网页爬取真实数据")
        print("  [2] 使用本地虚拟数据")
        print()
        
        while True:
            choice = input("请输入选项 (1/2): ").strip()
            if choice in ["1", "2"]:
                break
            print("无效选项，请重新输入！")
        
        return int(choice)
        
    def _select_choice(self, choice):
        """选择选项"""
        self.choice = choice
        self.root.destroy()
        
    def _center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))


def select_mode():
    """选择启动模式"""
    launcher = Launcher()
    choice = launcher.show_gui()
    
    if choice == 1:
        print("\n✅ 已选择：使用网页爬取真实数据")
        mode = "REAL"
    elif choice == 2:
        print("\n✅ 已选择：使用本地虚拟数据")
        mode = "VIRTUAL"
    else:
        print("\n⚠️  未选择，默认使用本地虚拟数据")
        mode = "VIRTUAL"
    
    # 保存模式选择到环境变量
    os.environ['HEALTH_DATA_MODE'] = mode
    return mode


if __name__ == "__main__":
    select_mode()
