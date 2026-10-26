@echo off
title Detener Whisper Flow
echo Deteniendo Whisper Flow en segundo plano...
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*whisper_flow.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
echo.
echo [OK] Proceso detenido con exito.
timeout /t 2 >nul
