@echo off
title Space Shooter Game
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python space_shooter.py
pause
