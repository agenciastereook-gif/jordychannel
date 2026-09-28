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
echo Revisando Node...
call npm --version >nul 2>&1 || (
  echo Instalando Node...
  winget install -e --id OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements
  echo.
  echo Cerra esta ventana y volve a abrir INSTALAR.bat para terminar.
  pause
  exit /b
)
echo Instalando herramientas (transcripcion y armado de video)...
python -m pip install --upgrade faster-whisper imageio-ffmpeg yt-dlp 2>nul || py -m pip install --upgrade faster-whisper imageio-ffmpeg yt-dlp
echo Instalando ChatGPT (Codex), Claude Code y Gemini para Estudio...
call npm install -g @openai/codex @anthropic-ai/claude-code
winget install -e --id Google.AntigravityCLI --accept-source-agreements --accept-package-agreements
echo.
echo Listo. Si es la primera vez, conecta tus cuentas (una sola vez):
echo   - ChatGPT:  codex login
echo   - Claude:   claude   (y adentro escribi /login)
echo   - Gemini:   agy      (y entra con tu cuenta de Google)
echo Despues abri ESTUDIO.pyw
pause
