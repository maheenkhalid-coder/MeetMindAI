# Handles audio input:
# downloads YouTube audio, converts local files to 16 kHz mono WAV,
# checks the 15-minute limit, and splits the audio into smaller chunks.


import os
import subprocess

import yt_dlp
from pydub import AudioSegment


DOWNLOAD_DIR = "downloads"
MAX_DURATION = 15 * 60  # Maximum allowed duration: 15 minutes


# Creates the download folder if it does not already exist.
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:
    # Downloads the best available YouTube audio, converts it to WAV,
    # and returns the path of the downloaded file.

    output_path = os.path.join(
        DOWNLOAD_DIR,
        "%(title)s.%(ext)s"
    )

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,

        # Use yt-dlp's EJS challenge solver.
        "remote_components": ["ejs:github"],

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],

        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    filename = (
        filename
        .replace(".webm", ".wav")
        .replace(".m4a", ".wav")
        .replace(".mp4", ".wav")
    )

    return filename


def convert_to_wav(input_path: str) -> str:
    # Converts an audio/video file to mono 16 kHz WAV format
    # and returns the new file path.
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"

    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)

    audio.export(output_path, format="wav")

    return output_path


def get_duration(file_path: str) -> float:
    # Gets the duration of the audio/video file in seconds.
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            file_path,
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    return float(result.stdout.strip())


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    # Splits the WAV file into smaller chunks and returns their file paths.
    audio = AudioSegment.from_wav(wav_path)

    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start:start + chunk_ms]

        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")

        chunks.append(chunk_path)

    return chunks


def process_input(source: str) -> list:
    # Detects YouTube or local input, converts to WAV,
    # checks the 15-minute limit, splits the audio, and returns the chunks.

    if source.startswith(("http://", "https://")):
        print("Detected YouTube URL. Downloading audio...")
        raw_path = download_youtube_audio(source)
        wav_path = convert_to_wav(raw_path)

    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    # Check the duration before creating chunks.
    duration = get_duration(wav_path)

    print(f"Video duration: {duration / 60:.1f} minutes")

    if duration > MAX_DURATION:
        raise ValueError(
            "Video is too long. Please provide a video that is 15 minutes or less."
        )

    print("Chunking audio...")

    chunks = chunk_audio(wav_path)

    print(f"Audio ready — {len(chunks)} chunk(s) created.")

    return chunks