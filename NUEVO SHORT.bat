@echo off
cd /d "%~dp0"
title Nuevo short
set /p TEMA=Tema del short: 
python scripts\nuevo_episodio.py "%TEMA%" 2>nul || py scripts\nuevo_episodio.py "%TEMA%"
timeout /t 3 >nul
