@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo === RETROLINK — Añade enlaces internos a artículos existentes ===
echo.
echo Esto mejora el SEO de todos los artículos ya publicados.
echo Añade una sección "Artículos relacionados" al final de cada uno.
echo.
python retrolink.py
echo.
pause
