@echo off
chcp 65001 >nul
set DEEPSEEK_API_KEY=你的DeepSeek密钥
set PYTHONIOENCODING=utf-8
python "%~dp0cli.py"
pause
