@echo off
chcp 65001 >nul
title Health Diet Assistant - Auto Thesis Demo
cls

echo.
echo ==================================================
echo     Health Diet Assistant - Auto Thesis Demo
echo ==================================================
echo.

cd /d "%~dp0"

echo Starting auto thesis demo...
echo.

python thesis_auto_demo.py

if errorlevel 1 (
    echo.
    echo [Error] Auto demo failed, please check
    pause
)
