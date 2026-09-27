@echo off
cd /d "%~dp0"
title Instalar
echo Revisando Python...
python --version >nul 2>&1 || py --version >nul 2>&1 || (
  echo Instalando Python...
  winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
  echo.
  echo Cerra esta ventana y volve a abrir INSTALAR.bat para terminar.
  pause
  exit /b
)
echo Instalando herramientas (transcripcion y armado de video)...
python -m pip install --upgrade faster-whisper imageio-ffmpeg 2>nul || py -m pip install --upgrade faster-whisper imageio-ffmpeg
echo.
echo Listo. Ya podes usar NUEVO SHORT.bat
pause
