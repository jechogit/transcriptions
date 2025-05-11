#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import yt_dlp
import srt
import json
from datetime import datetime, timedelta
import argparse

# 👇 Add this if moviepy was installed in user path (just in case)
sys.path.append(os.path.expanduser('~/Library/Python/3.9/lib/python/site-packages'))
import moviepy.editor as mp

# --- Check ffmpeg ---
if not shutil.which("ffmpeg"):
    print("❌ Error: FFmpeg is not installed or not in PATH.")
    print("🔧 Solution: Run 'brew install ffmpeg'")
    sys.exit(1)

def parse_time(time_str):
    """Parse time string in format MM:SS or HH:MM:SS to seconds."""
    parts = time_str.split(':')
    if len(parts) == 2:
        minutes, seconds = map(int, parts)
        return minutes * 60 + seconds
    elif len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
        return hours * 3600 + minutes * 60 + seconds
    else:
        raise ValueError("Time must be in format MM:SS or HH:MM:SS")

def download_audio(youtube_url, output_path, start_time, end_time):
    """Download audio segment from YouTube video."""
    os.makedirs(output_path, exist_ok=True)
    
    # Get video info first
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        video_id = info['id']
        duration = info['duration']
        
        # Validate time range
        if start_time >= duration:
            raise ValueError(f"Start time ({start_time}s) is beyond video duration ({duration}s)")
        if end_time > duration:
            print(f"⚠️ Warning: End time ({end_time}s) is beyond video duration ({duration}s). Adjusting to {duration}s")
            end_time = duration
        if end_time <= start_time:
            raise ValueError("End time must be greater than start time")
    
    # Download the segment
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, f"{video_id}.%(ext)s"),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'download_ranges': lambda info: [[start_time, end_time]],
        'force_keyframes_at_cuts': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
        return info, os.path.join(output_path, f"{video_id}.mp3")

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

def save_metadata(info, output_dir, start_time, end_time):
    """Save metadata about the extracted segment."""
    metadata = {
        'video_id': info['id'],
        'title': info['title'],
        'uploader': info['uploader'],
        'upload_date': info['upload_date'],
        'segment_start': start_time,
        'segment_end': end_time,
        'segment_duration': end_time - start_time,
        'processed_date': datetime.now().isoformat(),
        'model_used': os.path.basename(MODEL_PATH),
        'youtube_url': YOUTUBE_URL
    }
    
    metadata_path = os.path.join(output_dir, 'metadata.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    return metadata_path

def main():
    parser = argparse.ArgumentParser(description='Extract and transcribe a segment from a YouTube video')
    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument('start_time', help='Start time (MM:SS or HH:MM:SS)')
    parser.add_argument('end_time', help='End time (MM:SS or HH:MM:SS)')
    parser.add_argument('--model', default='/Users/cristophergutierrez/programming/models/ggml-large-v3.bin',
                      help='Path to whisper model (default: /Users/cristophergutierrez/programming/models/ggml-large-v3.bin)')
    parser.add_argument('--output', default='output',
                      help='Output directory (default: output)')
    
    args = parser.parse_args()
    
    try:
        start_seconds = parse_time(args.start_time)
        end_seconds = parse_time(args.end_time)
        
        # Create output directory
        output_dir = os.path.join(args.output, f"segment_{start_seconds}-{end_seconds}")
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"🎥 Downloading segment from {args.url}")
        print(f"⏱️ Time range: {args.start_time} - {args.end_time}")
        
        # Download audio segment
        info, audio_path = download_audio(args.url, output_dir, start_seconds, end_seconds)
        
        # Save metadata
        metadata_path = save_metadata(info, output_dir, start_seconds, end_seconds)
        
        print("🧠 Transcribing with whisper.cpp...")
        transcribe_whisper_cpp(audio_path, args.model, output_dir)
        
        print(f"\n✅ Done! Output in: {output_dir}")
        print(f"📋 Metadata: {metadata_path}")
        print(f"🎧 Audio: {audio_path}")
        print(f"📝 Subtitles: {os.path.join(output_dir, 'transcription.srt')}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 