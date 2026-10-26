# 🎙️ Whisper Flow — Voice to Text Anywhere (Windows)

> Dictado por voz instantáneo, acelerado por hardware y **100% offline**, directo al cursor de cualquier aplicación en Windows con un atajo de teclado. Sin consolas, sin suscripciones, sin pérdida de foco.

---

## ⚡ ¿Qué es Whisper Flow?

**Whisper Flow** es una utilidad ligera que corre en segundo plano en Windows. Te permite presionar un atajo en cualquier lugar (Slack, Teams, Visual Studio Code, Cursor, WhatsApp Web, Google Meet o tu navegador), hablar tu idea y, al soltarlo, ver cómo el texto transcrito se escribe solo en tu chat o editor en menos de **1 segundo**.

### 💡 Características Principales
* 🔒 **100% Offline y Privado:** Tu voz nunca sale de tu equipo. Sin telemetría, sin APIs en la nube, seguro para entornos corporativos y políticas de ciberseguridad estrictas.
* 🚀 **Aceleración por GPU Nativa:** Corre sobre DirectX 11 / DirectCompute (compatible con tarjetas dedicadas NVIDIA/AMD y gráficas integradas Intel).
* 🎯 **Cero Pérdida de Foco:** Proceso fantasma (`pythonw.exe`). No abre ventanas ni terminales secundarias que le quiten el foco a tu cursor.
* 🎹 **Atajo Ergonómico:** Diseñado para teclados en español (`AltGr + L + Ñ` o `F8` de respaldo).
* 📋 **Inyección Automática:** Copia al portapapeles y ejecuta `Ctrl + V` automáticamente.
* 💾 **Historial de Respaldo:** Cada dictado se guarda automáticamente con timestamp en `historial_dictado.txt`.

---

## 🛠️ Requisitos Previos

* **Sistema Operativo:** Windows 10 o Windows 11 (64 bits).
* **Python:** Python 3.10 o superior ([Descargar de python.org](https://www.python.org/downloads/) asegurándote de marcar *"Add python.exe to PATH"* durante la instalación).
* **Tarjeta Gráfica:** Cualquier GPU con soporte DirectX 11 (incluso las integradas de procesadores Intel o AMD).

---

## 🚀 Instalación Rápida (1 Clic)

1. **Clona este repositorio** o descárgalo como ZIP:
   ```bash
   git clone https://github.com/tu-usuario/Whisper-Flow.git
   cd Whisper-Flow
   ```
2. **Haz doble clic en `instalar.bat`**.
   * El instalador instalará las librerías necesarias (`sounddevice`, `pynput`, `numpy`).
   * Descargará automáticamente el modelo optimizado para español (`ggml-small.bin`, ~466 MB) desde Hugging Face.
   * Creará dos accesos directos en tu **Escritorio**:
     * **`Iniciar Whisper Flow`**
     * **`Detener Whisper Flow`**
   * Iniciará el servicio de inmediato.

---

## 🎙️ Cómo Usarlo en el Día a Día

1. Haz clic en la caja de texto donde quieras escribir (Slack, Teams, Cursor, Chrome, etc.).
2. Presiona tu atajo: **`AltGr + L + Ñ`** (o pulsa **`F8`**).
   * 🔔 Escucharás un **tono agudo corto** (`1200 Hz`) $\rightarrow$ *Micrófono grabando*.
3. Habla tu idea o código de forma natural.
4. Vuelve a presionar el atajo para detener:
   * 🔔 Escucharás un **tono grave corto** (`800 Hz`) $\rightarrow$ *Procesando audio...*
   * ✨ En ~0.8 segundos escucharás un **chime brillante** (`1600 Hz`) y el texto transcrito aparecerá automáticamente escrito en tu cursor.

---

## ⚙️ Estructura del Repositorio

```
Whisper-Flow/
├── .gitignore              # Excluye modelos pesados (>100MB) y audios temporales
├── LICENSE                 # Licencia MIT de código abierto
├── README.md               # Esta documentación
├── requirements.txt        # Dependencias de Python
├── whisper_flow.py         # Motor principal de orquestación, captura e inyección
├── iniciar.vbs             # Lanzador silencioso en segundo plano (sin consola)
├── detener.bat             # Detenedor seguro del proceso
├── instalar.bat            # Script de instalación automática en 1 clic
├── main.exe                # Motor CLI compilado en C++ (Const-me DirectCompute)
└── Whisper.dll             # Biblioteca de cómputo GPU DirectX 11
```

---

## 🎖️ Créditos y Atribuciones

Este proyecto integra y se construye sobre el trabajo sobresaliente de la comunidad de código abierto:

1. **OpenAI ([openai/whisper](https://github.com/openai/whisper)):**
   * Creadores de la arquitectura fundacional de la red neuronal Whisper y el entrenamiento de los modelos acústicos multilingües.
2. **Georgi Gerganov ([ggerganov/whisper.cpp](https://github.com/ggerganov/whisper.cpp)):**
   * Por la ingeniería de optimización en C/C++ de alto rendimiento y la creación de la especificación de modelos binarios GGML.
3. **Konstantin Mozgovoy ([Const-me/Whisper](https://github.com/Const-me/Whisper)):**
   * Por la implementación nativa en C++ para Windows con aceleración por hardware en **DirectX 11 / DirectCompute**, que permite inferencia en GPU sin necesidad de CUDA ni drivers propietarios. Los binarios `main.exe` y `Whisper.dll` provienen de su release oficial v1.12.0 bajo licencia MIT.
4. **Joaquín Morales & GEMONO:**
   * Por la arquitectura de **Whisper Flow**: orquestación headless silenciosa, captura asíncrona de audio sin bloqueo de hilos, listeners de teclado sin pérdida de foco Win32, inyección nativa en portapapeles y empaquetado para distribución.

---

## 📄 Licencia

Este proyecto está bajo la licencia **MIT**. Consulta el archivo `LICENSE` para más información.
