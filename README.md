# YouTube Segment Extractor

Este script permite extraer y transcribir segmentos específicos de videos de YouTube, generando subtítulos a nivel de palabra perfectos para practicar.

## Características

- Extrae segmentos específicos de videos de YouTube
- Descarga solo la parte del audio que necesitas
- Transcribe el audio usando whisper.cpp
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
git clone [URL_DEL_REPOSITORIO]
cd youtube-segment-extractor
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

```bash
python extract_segment.py [URL] [TIEMPO_INICIO] [TIEMPO_FIN] [OPCIONES]
```

### Argumentos

- `URL`: URL del video de YouTube
- `TIEMPO_INICIO`: Tiempo de inicio en formato MM:SS o HH:MM:SS
- `TIEMPO_FIN`: Tiempo de fin en formato MM:SS o HH:MM:SS

### Opciones

- `--model`: Ruta al modelo de whisper (por defecto: /Users/cristophergutierrez/programming/models/ggml-large-v3.bin)
- `--output`: Directorio de salida (por defecto: output)

### Ejemplos

```bash
# Extraer segmento de 1:30 a 2:45
python extract_segment.py "https://www.youtube.com/watch?v=VIDEO_ID" "1:30" "2:45"

# Extraer segmento de 1:30:00 a 1:35:00
python extract_segment.py "https://www.youtube.com/watch?v=VIDEO_ID" "1:30:00" "1:35:00"

# Especificar modelo y directorio de salida
python extract_segment.py "https://www.youtube.com/watch?v=VIDEO_ID" "1:30" "2:45" --model "/ruta/al/modelo.bin" --output "mis_segmentos"
```

## Estructura de Salida

```
output/
└── segment_[INICIO]-[FIN]/
    ├── metadata.json
    ├── [VIDEO_ID].mp3
    └── transcription.srt
```

## Notas

- Los tiempos pueden especificarse en formato MM:SS o HH:MM:SS
- El script validará que los tiempos estén dentro de la duración del video
- Los subtítulos se generan con timestamps precisos para cada palabra
- Los archivos de audio se guardan en formato MP3 con calidad 192kbps

## Licencia

MIT 