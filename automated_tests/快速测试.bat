@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Running tests...
python automated_test_suite.py
pause
