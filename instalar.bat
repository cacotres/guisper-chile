@echo off
setlocal enabledelayedexpansion
title Instalador de Whisper Flow
color 0A

echo ======================================================================
echo                 INSTALADOR DE WHISPER FLOW PARA WINDOWS
echo     Transcripcion de voz instantanea en cualquier aplicacion (Offline)
echo ======================================================================
echo.

:: 1. Comprobar Python
echo [*] Verificando instalacion de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python no esta instalado o no esta en el PATH de Windows.
    echo Por favor instala Python 3.10 o superior marcando "Add python.exe to PATH".
    echo Descarga: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo [OK] Python detectado correctamente.
echo.

:: 2. Instalar dependencias
echo [*] Instalando librerias de Python requeridas (sounddevice, pynput, numpy)...
python -m pip install -r requirements.txt --quiet --user
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Hubo un problema instalando las dependencias.
    pause
    exit /b 1
)
echo [OK] Librerias instaladas correctamente.
echo.

:: 3. Comprobar o descargar modelo GGML
set "MODEL_FILE=ggml-small.bin"
if not exist "%~dp0%MODEL_FILE%" (
    echo [*] No se detecto el modelo de lenguaje en la carpeta.
    echo [*] Descargando modelo optimizado (%MODEL_FILE%, ~466 MB) desde Hugging Face...
    echo [*] Esto tardara entre 15 y 45 segundos dependiendo de tu conexion...
    echo.
    curl.exe -L -# -o "%~dp0%MODEL_FILE%" "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin"
    if not exist "%~dp0%MODEL_FILE%" (
        color 0C
        echo [ERROR] Fallo la descarga del modelo. Puedes descargarlo manualmente desde:
        echo https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin
        echo y guardarlo dentro de esta misma carpeta.
        pause
        exit /b 1
    )
    echo.
    echo [OK] Modelo descargado con exito.
) else (
    echo [OK] Modelo %MODEL_FILE% ya existe en la carpeta.
)
echo.

:: 4. Generar accesos directos en el Escritorio
echo [*] Creando accesos directos en tu Escritorio...
set "VBS_TEMP=%temp%\create_whisper_shortcuts.vbs"
(
    echo Set oWS = WScript.CreateObject("WScript.Shell"^)
    echo sDesk = oWS.SpecialFolders("Desktop"^)
    echo.
    echo Set oLnk1 = oWS.CreateShortcut(sDesk ^& "\Iniciar Whisper Flow.lnk"^)
    echo oLnk1.TargetPath = "wscript.exe"
    echo oLnk1.Arguments = """" ^& "%~dp0iniciar.vbs" ^& """"
    echo oLnk1.WorkingDirectory = "%~dp0"
    echo oLnk1.Description = "Iniciar Whisper Flow (Atajo AltGr + L + Ñ)"
    echo oLnk1.Save
    echo.
    echo Set oLnk2 = oWS.CreateShortcut(sDesk ^& "\Detener Whisper Flow.lnk"^)
    echo oLnk2.TargetPath = "%~dp0detener.bat"
    echo oLnk2.WorkingDirectory = "%~dp0"
    echo oLnk2.Description = "Detener proceso Whisper Flow"
    echo oLnk2.Save
) > "%VBS_TEMP%"

cscript.exe //NoLogo "%VBS_TEMP%"
if exist "%VBS_TEMP%" del "%VBS_TEMP%"
echo [OK] Accesos directos creados en tu Escritorio:
echo     - Iniciar Whisper Flow
echo     - Detener Whisper Flow
echo.

:: 5. Iniciar inmediatamente
echo ======================================================================
echo                      INSTALACION COMPLETADA
echo ======================================================================
echo Atajo principal:   AltGr + L + N
echo Atajo de respaldo: F8
echo.
echo Presiona cualquier tecla para encender Whisper Flow ahora mismo...
pause >nul

wscript.exe "%~dp0iniciar.vbs"
echo.
echo [*] Whisper Flow esta activo en segundo plano. Ya puedes probarlo en cualquier chat.
timeout /t 3 >nul
exit /b 0
