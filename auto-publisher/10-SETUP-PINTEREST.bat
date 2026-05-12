@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo === SETUP PINTEREST — Configuración automática ===
echo.
echo Antes de continuar, ve a:
echo   https://developers.pinterest.com/apps/
echo.
echo Abre tu app, pestaña Authentication, genera un token con:
echo   boards:read  boards:write  pins:read  pins:write
echo.
echo Cuando tengas el token, pégalo a continuación.
echo.
python setup-pinterest.py
echo.
pause
