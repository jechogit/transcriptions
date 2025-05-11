# Audio Transcription and Word-Level Subtitle Generator

Este script procesa videos de YouTube para generar transcripciones con subtítulos a nivel de palabra, perfectos para usar con Audacity.

## Características

- Descarga audio de videos de YouTube
- Transcribe el audio usando whisper.cpp
- Genera subtítulos a nivel de palabra (SRT)
- Crea segmentos de audio con sus respectivos subtítulos
- Mantiene la sincronización precisa entre audio y texto
- Organiza los archivos por video en carpetas separadas

## Requisitos

- Python 3.9+
- FFmpeg
- whisper.cpp (compilado)
- Modelo GGML (ggml-large-v3.bin)

## Dependencias de Python

```
yt-dlp
moviepy
srt
```

## Instalación

1. Clona este repositorio:
```bash
git clone [URL_DEL_REPOSITORIO]
cd [NOMBRE_DEL_REPOSITORIO]
```

2. Crea y activa un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Asegúrate de tener FFmpeg instalado:
```bash
# En macOS:
brew install ffmpeg

# En Ubuntu/Debian:
sudo apt-get install ffmpeg
```

5. Compila whisper.cpp y coloca el binario en el directorio del proyecto:
```bash
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp
make
cp main ../whisper-cli
```

## Uso

1. Coloca tu modelo GGML (ggml-large-v3.bin) en el directorio del proyecto
2. Modifica la URL del video en el script
3. Ejecuta el script:
```bash
python script.py
```

## Estructura de Salida

```
output/
└── [VIDEO_ID]/
    ├── metadata.json
    ├── [VIDEO_ID].mp3
    ├── transcription.srt
    └── sentences/
        ├── sentence_001.wav
        ├── sentence_001.srt
        ├── sentence_002.wav
        ├── sentence_002.srt
        └── labels.txt
```

## Notas

- Los segmentos de audio se generan con una duración entre 2 y 10 segundos
- Cada archivo SRT contiene los timestamps precisos para cada palabra
- Los archivos de etiquetas están en formato compatible con Audacity

## Licencia

MIT 