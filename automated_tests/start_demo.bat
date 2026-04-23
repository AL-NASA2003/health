@echo off
chcp 65001 >nul
title Health Diet Assistant - Thesis Demo
cls

echo.
echo ==================================================
echo     Health Diet Assistant - Thesis Demo
echo ==================================================
echo.

cd /d "%~dp0"

echo Starting thesis demo...
echo.

python thesis_demo.py

if errorlevel 1 (
    echo.
    echo [Error] Demo failed, please check
    pause
)
