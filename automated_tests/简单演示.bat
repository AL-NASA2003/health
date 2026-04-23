@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Starting demo...
python thesis_full_demo.py
pause
