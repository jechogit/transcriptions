# YouTube Audio Processing Tools

Este repositorio contiene dos herramientas para procesar audio de YouTube:

1. **Procesador de Video Completo**: Genera subtítulos a nivel de palabra para todo el video
2. **Extractor de Segmentos**: Extrae y transcribe segmentos específicos de un video

## Características

### Procesador de Video Completo (`script.py`)
- Descarga y procesa videos completos de YouTube
- Genera subtítulos a nivel de palabra (SRT)
- Divide el audio en segmentos de 2-10 segundos
- Crea archivos de etiquetas para Audacity
- Organiza los archivos por video en carpetas separadas

### Extractor de Segmentos (`extract_segment.py`)
- Extrae segmentos específicos de videos de YouTube
- Descarga solo la parte del audio que necesitas
- Genera subtítulos a nivel de palabra (SRT)
- Mantiene la sincronización precisa entre audio y texto
- Guarda metadatos del segmento extraído

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
git clone https://github.com/jechogit/transcriptions.git
cd transcriptions
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

### 1. Procesar Video Completo

```bash
python script.py [URL] [OPCIONES]
```

#### Argumentos
- `URL`: URL del video de YouTube

#### Opciones
- `--model`: Ruta al modelo de whisper (por defecto: /Users/cristophergutierrez/programming/models/ggml-large-v3.bin)
- `--output`: Directorio de salida (por defecto: output)

#### Ejemplo
```bash
python script.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 2. Extraer Segmento Específico

```bash
python extract_segment.py [URL] [TIEMPO_INICIO] [TIEMPO_FIN] [OPCIONES]
```

#### Argumentos
- `URL`: URL del video de YouTube
- `TIEMPO_INICIO`: Tiempo de inicio en formato MM:SS o HH:MM:SS
- `TIEMPO_FIN`: Tiempo de fin en formato MM:SS o HH:MM:SS

#### Opciones
- `--model`: Ruta al modelo de whisper (por defecto: /Users/cristophergutierrez/programming/models/ggml-large-v3.bin)
- `--output`: Directorio de salida (por defecto: output)

#### Ejemplos
```bash
# Extraer segmento de 1:30 a 2:45
python extract_segment.py "https://www.youtube.com/watch?v=VIDEO_ID" "1:30" "2:45"

# Extraer segmento de 1:30:00 a 1:35:00
python extract_segment.py "https://www.youtube.com/watch?v=VIDEO_ID" "1:30:00" "1:35:00"
```

## Estructura de Salida

### Procesador de Video Completo
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

### Extractor de Segmentos
```
output/
└── segment_[INICIO]-[FIN]/
    ├── metadata.json
    ├── [VIDEO_ID].mp3
    └── transcription.srt
```

## Notas

- Los tiempos pueden especificarse en formato MM:SS o HH:MM:SS
- Los subtítulos se generan con timestamps precisos para cada palabra
- Los archivos de audio se guardan en formato MP3 con calidad 192kbps
- Los archivos de etiquetas están en formato compatible con Audacity

## Licencia

MIT 