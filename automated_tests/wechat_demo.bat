@echo off
chcp 65001 >nul
title 健康饮食助手 - 微信小程序演示
cls

echo.
echo ==================================================
echo           健康饮食助手 - 微信小程序演示
echo ==================================================
echo.

cd /d "%~dp0"

echo 正在启动微信小程序自动化演示...
echo.

python wechat_demo_auto.py

if errorlevel 1 (
    echo.
    echo [错误] 演示启动失败，请检查错误信息
    pause
)
