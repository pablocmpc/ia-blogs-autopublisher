@echo off
title Dashboard Auto-Publisher IA - EN VIVO
color 0B
echo.
echo  Abriendo Dashboard en tiempo real...
echo  Se abrira el navegador automaticamente.
echo  Ctrl+C para cerrar el servidor.
echo.
cd /d "%~dp0"
python dashboard.py
echo.
pause
