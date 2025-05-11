#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import yt_dlp
import srt
import json
import re
from datetime import datetime, timedelta

# 👇 Add this if moviepy was installed in user path (just in case)
sys.path.append(os.path.expanduser('~/Library/Python/3.9/lib/python/site-packages'))
import moviepy.editor as mp

# --- Check ffmpeg ---
if not shutil.which("ffmpeg"):
    print("❌ Error: FFmpeg is not installed or not in PATH.")
    print("🔧 Solution: Run 'brew install ffmpeg'")
    sys.exit(1)

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
YOUTUBE_URL = 'https://www.youtube.com/watch?v=PZNg3TA6Osw'
MODEL_PATH = '/Users/cristophergutierrez/programming/models/ggml-large-v3.bin'
BASE_OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'output')

# --- Functions ---
def download_audio(youtube_url, output_path):
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

def save_metadata(info, video_dir):
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
        'youtube_url': YOUTUBE_URL
    }
    
    metadata_path = os.path.join(video_dir, 'metadata.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    return metadata_path

def transcribe_whisper_cpp(audio_path, model_path, output_path):
    os.makedirs(output_path, exist_ok=True)
    subprocess.run([
        './whisper-cli',
        '-m', model_path,
        '-f', audio_path,
        '-osrt',
        '-owts',  # Enable word-level timestamps
        '-of', os.path.join(output_path, 'transcription')
    ], check=True)

def parse_word_timestamps(srt_file):
    """Parse SRT file and extract word-level timestamps."""
    with open(srt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into segments
    segments = []
    current_segment = None
    
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a timestamp line
        if '-->' in line:
            start, end = line.split(' --> ')
            current_segment = {
                'start': start,
                'end': end,
                'words': []
            }
            segments.append(current_segment)
        elif current_segment is not None:
            # This is a text line, split into words
            words = line.split()
            for word in words:
                # Clean the word but preserve punctuation
                word = re.sub(r'[^\w\s.,!?-]', '', word)
                if word:
                    current_segment['words'].append(word)
    
    return segments

def create_word_level_srt(segment, output_file, segment_start):
    """Create an SRT file with word-level timestamps for a sentence."""
    subtitles = []
    start_time = datetime.strptime(segment['start'], '%H:%M:%S,%f')
    end_time = datetime.strptime(segment['end'], '%H:%M:%S,%f')
    
    # Convert to seconds relative to the start of the segment
    start_seconds = (start_time - datetime(1900, 1, 1)).total_seconds() - segment_start
    end_seconds = (end_time - datetime(1900, 1, 1)).total_seconds() - segment_start
    duration = end_seconds - start_seconds
    
    if segment['words']:
        time_per_word = duration / len(segment['words'])
        
        # Create a subtitle for each word
        for word_idx, word in enumerate(segment['words']):
            word_start = start_seconds + (time_per_word * word_idx)
            word_end = word_start + time_per_word
            
            subtitle = srt.Subtitle(
                index=word_idx + 1,
                start=timedelta(seconds=word_start),
                end=timedelta(seconds=word_end),
                content=word
            )
            subtitles.append(subtitle)
    
    # Write the SRT file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(srt.compose(subtitles))

def slice_audio(audio_file, segments, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    audio = mp.AudioFileClip(audio_file)
    sentence_meta = []
    
    for idx, segment in enumerate(segments):
        start = datetime.strptime(segment['start'], '%H:%M:%S,%f')
        end = datetime.strptime(segment['end'], '%H:%M:%S,%f')
        start_seconds = (start - datetime(1900, 1, 1)).total_seconds()
        end_seconds = (end - datetime(1900, 1, 1)).total_seconds()
        
        # Process all segments between 2 and 10 seconds
        if 2.0 < (end_seconds - start_seconds) < 10.0:
            wav = f"sentence_{idx+1:03}.wav"
            srt_file = f"sentence_{idx+1:03}.srt"
            
            # Extract audio clip
            clip = audio.subclip(start_seconds, end_seconds)
            clip.write_audiofile(os.path.join(output_folder, wav), codec='pcm_s16le')
            
            # Create word-level SRT for this sentence with relative timestamps
            create_word_level_srt(segment, os.path.join(output_folder, srt_file), start_seconds)
            
            sentence_meta.append((start_seconds, end_seconds, ' '.join(segment['words'])))
    
    return sentence_meta

def generate_label_file(sentences, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for start, end, text in sentences:
            f.write(f"{start:.2f}\t{end:.2f}\t{text}\n")

# --- Main ---
def main():
    # Create video-specific directory
    info, audio = download_audio(YOUTUBE_URL, BASE_OUTPUT_DIR)
    video_id = info['id']
    video_dir = os.path.join(BASE_OUTPUT_DIR, video_id)
    os.makedirs(video_dir, exist_ok=True)
    
    # Save metadata
    metadata_path = save_metadata(info, video_dir)
    
    # Move audio file to video directory
    shutil.move(audio, os.path.join(video_dir, f"{video_id}.mp3"))
    audio = os.path.join(video_dir, f"{video_id}.mp3")

    print("🧠 Transcribing with whisper.cpp...")
    transcribe_whisper_cpp(audio, MODEL_PATH, video_dir)

    srt_path = os.path.join(video_dir, 'transcription.srt')
    print("📖 Parsing word-level timestamps...")
    segments = parse_word_timestamps(srt_path)

    print("✂️ Slicing audio...")
    sd = os.path.join(video_dir, 'sentences')
    meta = slice_audio(audio, segments, sd)

    print("🏷️ Generating label file for Audacity...")
    labels = os.path.join(sd, 'labels.txt')
    generate_label_file(meta, labels)

    print(f"\n✅ Done! Output in: {video_dir}")
    print(f"📋 Metadata: {metadata_path}")
    print(f"🎧 Sentences in: {sd}")
    print(f"📄 Labels: {labels}")
    print(f"📝 Subtitles: {srt_path}")

if __name__ == '__main__':
    main()
