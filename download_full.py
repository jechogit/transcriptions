#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import yt_dlp
import json
from datetime import datetime
import argparse

# --- Check ffmpeg ---
if not shutil.which("ffmpeg"):
    print("❌ Error: FFmpeg is not installed or not in PATH.")
    print("🔧 Solution: Run 'brew install ffmpeg'")
    sys.exit(1)

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = '/Users/cristophergutierrez/programming/models/ggml-large-v3.bin'
BASE_OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'output')

def download_audio(youtube_url, output_path):
    """Download full audio from YouTube video."""
    os.makedirs(output_path, exist_ok=True)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        return info, os.path.join(output_path, f"{info['id']}.mp3")

def transcribe_whisper_cpp(audio_path, model_path, output_path):
    """Transcribe audio using whisper.cpp."""
    os.makedirs(output_path, exist_ok=True)
    subprocess.run([
        './whisper-cli',
        '-m', model_path,
        '-f', audio_path,
        '-osrt',
        '-owts',  # Enable word-level timestamps
        '-of', os.path.join(output_path, 'transcription')
    ], check=True)

def save_metadata(info, output_dir):
    """Save metadata about the video."""
    metadata = {
        'video_id': info['id'],
        'title': info['title'],
        'uploader': info['uploader'],
        'upload_date': info['upload_date'],
        'duration': info['duration'],
        'view_count': info['view_count'],
        'like_count': info.get('like_count', 0),
        'description': info['description'],
        'processed_date': datetime.now().isoformat(),
        'model_used': os.path.basename(MODEL_PATH),
        'youtube_url': args.url
    }
    
    metadata_path = os.path.join(output_dir, 'metadata.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    return metadata_path

def main():
    parser = argparse.ArgumentParser(description='Download full audio and generate subtitles from YouTube video')
    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument('--model', default=MODEL_PATH,
                      help=f'Path to whisper model (default: {MODEL_PATH})')
    parser.add_argument('--output', default=BASE_OUTPUT_DIR,
                      help=f'Output directory (default: {BASE_OUTPUT_DIR})')
    
    global args
    args = parser.parse_args()
    
    try:
        # Create video-specific directory
        info, audio = download_audio(args.url, args.output)
        video_id = info['id']
        video_dir = os.path.join(args.output, video_id)
        os.makedirs(video_dir, exist_ok=True)
        
        # Save metadata
        metadata_path = save_metadata(info, video_dir)
        
        # Move audio file to video directory
        shutil.move(audio, os.path.join(video_dir, f"{video_id}.mp3"))
        audio = os.path.join(video_dir, f"{video_id}.mp3")

        print("🧠 Transcribing with whisper.cpp...")
        transcribe_whisper_cpp(audio, args.model, video_dir)

        print(f"\n✅ Done! Output in: {video_dir}")
        print(f"📋 Metadata: {metadata_path}")
        print(f"🎧 Audio: {audio}")
        print(f"📝 Subtitles: {os.path.join(video_dir, 'transcription.srt')}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 