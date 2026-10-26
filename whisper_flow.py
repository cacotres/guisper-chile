# -*- coding: utf-8 -*-
"""
Whisper Flow - Transcriptor Instantáneo por Atajo de Teclado (Headless)
Convierte tu voz en texto y la escribe en el chat/editor activo sin perder el foco.

Atajo Principal: AltGr + L + Ñ
Atajo de Respaldo: F8
"""

import os
import sys
import time
import wave
import queue
import ctypes
from ctypes import wintypes
import subprocess
import threading
import winsound
import numpy as np
import sounddevice as sd
from pynput import keyboard

# Rutas dinámicas portables (relativas a la carpeta del script)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_EXE = os.path.join(BASE_DIR, "main.exe")
TEMP_WAV = os.path.join(BASE_DIR, "temp_dictation.wav")
LOG_FILE = os.path.join(BASE_DIR, "historial_dictado.txt")

# Selección automática del mejor modelo disponible en la carpeta
POSSIBLE_MODELS = [
    "ggml-small.bin",
    "ggml-medium.bin",
    "ggml-base.bin",
    "ggml-tiny.bin",
    "ggml-large-v3.bin"
]

MODEL_PATH = None
for m in POSSIBLE_MODELS:
    cand = os.path.join(BASE_DIR, m)
    if os.path.exists(cand):
        MODEL_PATH = cand
        break

if not MODEL_PATH:
    # Por defecto apuntamos a small
    MODEL_PATH = os.path.join(BASE_DIR, "ggml-small.bin")

# Configuración de audio (16kHz, 16-bit Mono PCM nativo de Whisper)
SAMPLE_RATE = 16000
CHANNELS = 1

# Códigos Virtuales de Teclas en Windows (VK)
VK_RMENU   = 0xA5  # AltGr / Right Alt
VK_MENU    = 0x12  # Alt genérico
VK_L       = 0x4C  # Tecla L
VK_N       = 0xC0  # Tecla Ñ (teclado español / latinoamericano)
VK_CONTROL = 0x11  # Ctrl
VK_V       = 0x56  # V

# Variables de estado
is_recording = False
audio_queue = queue.Queue()
audio_stream = None
processing_lock = threading.Lock()
combo_triggered = False

# API Win32 de 64 bits para manipulación directa del Portapapeles
u32 = ctypes.windll.user32
k32 = ctypes.windll.kernel32

k32.GlobalAlloc.restype = wintypes.HGLOBAL
k32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
k32.GlobalLock.restype = wintypes.LPVOID
k32.GlobalLock.argtypes = [wintypes.HGLOBAL]
k32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
u32.SetClipboardData.restype = wintypes.HANDLE
u32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]

def is_key_down(vk_code: int) -> bool:
    """Verifica si una tecla física está presionada actualmente."""
    return bool(u32.GetAsyncKeyState(vk_code) & 0x8000)

def set_clipboard_text(text: str):
    """Escribe texto en el portapapeles sin alterar el foco de la ventana activa."""
    if u32.OpenClipboard(None):
        try:
            u32.EmptyClipboard()
            data = text.encode("utf-16le") + b"\x00\x00"
            h_mem = k32.GlobalAlloc(0x0002, len(data))
            p_mem = k32.GlobalLock(h_mem)
            ctypes.memmove(p_mem, data, len(data))
            k32.GlobalUnlock(h_mem)
            u32.SetClipboardData(13, h_mem)  # 13 = CF_UNICODETEXT
        finally:
            u32.CloseClipboard()

def paste_clipboard():
    """Simula pulsación de Ctrl + V en la ventana activa actual."""
    KEYEVENTF_KEYUP = 0x0002
    time.sleep(0.08)  # Breve pausa para asegurar estabilidad del foco
    u32.keybd_event(VK_CONTROL, 0, 0, 0)
    u32.keybd_event(VK_V, 0, 0, 0)
    time.sleep(0.03)
    u32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
    u32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

def audio_callback(indata, frames, time_info, status):
    """Callback de audio continuo."""
    if is_recording:
        audio_queue.put(indata.copy())

def start_recording():
    """Inicia la grabación del micrófono."""
    global is_recording, audio_stream
    if is_recording:
        return
    
    # Vaciar cola previa
    while not audio_queue.empty():
        try:
            audio_queue.get_nowait()
        except queue.Empty:
            break
            
    is_recording = True
    # Feedback auditivo: tono agudo (1200 Hz)
    threading.Thread(target=winsound.Beep, args=(1200, 100), daemon=True).start()
    
    try:
        audio_stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            callback=audio_callback
        )
        audio_stream.start()
    except Exception as e:
        is_recording = False
        winsound.Beep(400, 300)
        print(f"[Error Audio Input]: {e}")

def stop_and_process():
    """Detiene la grabación y procesa el audio en segundo plano."""
    global is_recording, audio_stream
    if not is_recording:
        return
    is_recording = False
    
    # Feedback auditivo: tono grave (800 Hz)
    threading.Thread(target=winsound.Beep, args=(800, 120), daemon=True).start()
    
    if audio_stream:
        try:
            audio_stream.stop()
            audio_stream.close()
        except Exception:
            pass
        audio_stream = None

    # Procesar en hilo secundario para mantener el listener responsivo
    threading.Thread(target=transcribe_and_paste, daemon=True).start()

def transcribe_and_paste():
    """Convierte audio a texto y lo inyecta en el campo activo."""
    with processing_lock:
        chunks = []
        while not audio_queue.empty():
            chunks.append(audio_queue.get())
            
        if not chunks:
            return
            
        audio_data = np.concatenate(chunks, axis=0)
        
        # Ignorar clics accidentales menores a 0.3 segundos
        if len(audio_data) < SAMPLE_RATE * 0.3:
            return

        # Guardar audio temporal
        try:
            with wave.open(TEMP_WAV, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(audio_data.tobytes())
        except Exception as e:
            print(f"[Error guardando WAV]: {e}")
            return

        # Ejecutar main.exe (Headless, sin ventanas ni terminales)
        cmd = [
            MAIN_EXE,
            "-m", MODEL_PATH,
            "-l", "es",
            "-nt",
            "-nc",
            "-f", TEMP_WAV
        ]
        
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            )
            raw_text = res.stdout.strip()
            
            # Limpiar marcadores residuales
            cleaned_text = (
                raw_text
                .replace("[SILENCIO]", "")
                .replace("[MÚSICA]", "")
                .replace("[APLAUSOS]", "")
                .strip()
            )
            
            if cleaned_text:
                # 1. Copiar al portapapeles nativo
                set_clipboard_text(cleaned_text)
                
                # 2. Pegar automáticamente en el campo de texto activo
                paste_clipboard()
                
                # 3. Chime de confirmación exitosa (1600 Hz)
                threading.Thread(target=winsound.Beep, args=(1600, 90), daemon=True).start()
                
                # 4. Guardar en log persistente
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(f"[{timestamp}] {cleaned_text}\n")
        except Exception as e:
            winsound.Beep(500, 200)
            winsound.Beep(400, 200)
            print(f"[Error Transcripción]: {e}")

def toggle_dictation():
    """Alterna el estado de grabación."""
    if not is_recording:
        start_recording()
    else:
        stop_and_process()

def check_keys():
    """Evalúa si la combinación AltGr + L + Ñ está activa."""
    global combo_triggered
    alt_active = is_key_down(VK_RMENU) or is_key_down(VK_MENU)
    l_active   = is_key_down(VK_L)
    n_active   = is_key_down(VK_N)
    
    if alt_active and l_active and n_active:
        if not combo_triggered:
            combo_triggered = True
            toggle_dictation()
    else:
        # Reset cuando se liberan las teclas de letras
        if not (l_active and n_active):
            combo_triggered = False

def on_press(key):
    check_keys()
    
    # Respaldo rápido con F8
    if key == keyboard.Key.f8:
        toggle_dictation()

def on_release(key):
    check_keys()

if __name__ == "__main__":
    if not os.path.exists(MAIN_EXE):
        print(f"ERROR: No se encontró el ejecutable del motor en {MAIN_EXE}")
        print("Ejecuta 'instalar.bat' para descargar las dependencias necesarias.")
        sys.exit(1)
        
    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: No se encontró el archivo del modelo en {MODEL_PATH}")
        print("Ejecuta 'instalar.bat' para descargar el modelo GGML.")
        sys.exit(1)

    print("=" * 60)
    print("       WHISPER FLOW - VOICE TO TEXT ANYWHERE")
    print("=" * 60)
    print(f"Atajo principal: [ AltGr + L + Ñ ]")
    print(f"Atajo respaldo:  [ F8 ]")
    print(f"Modelo cargado:  {os.path.basename(MODEL_PATH)}")
    print("=" * 60)
    print("Estado: Escuchando en segundo plano...")
    
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
