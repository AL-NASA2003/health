@echo off
chcp 65001 >nul
title 健康饮食助手 - 自动化测试
cls

echo.
echo ==================================================
echo           健康饮食助手 - 自动化测试
echo ==================================================
echo.

cd /d "%~dp0"

echo 正在启动自动化测试...
echo.

python automated_test_suite.py

if errorlevel 1 (
    echo.
    echo [错误] 测试启动失败，请检查错误信息
    pause
)
