@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Starting full thesis demo...
python thesis_full_demo.py
if errorlevel 1 (
    echo.
    echo [Error] Demo failed, please check
    pause
)
