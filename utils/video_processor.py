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
    #
    # Tries multiple YouTube "player clients" in order. The android/ios
    # clients avoid the JS signature-challenge YouTube uses on the web
    # player, which is what was failing on Streamlit Cloud (no JS runtime
    # available there for yt-dlp's ejs/deno-based solver).

    cookies_path = os.environ.get("YT_COOKIES_PATH")
    print(f"[MeetMind] YT_COOKIES_PATH = {cookies_path}", flush=True)
    if cookies_path:
        exists = os.path.exists(cookies_path)
        print(f"[MeetMind] cookies file exists: {exists}", flush=True)
        if exists:
            with open(cookies_path, "r") as f:
                first_line = f.readline().strip()
            print(f"[MeetMind] cookies file first line: {first_line!r}", flush=True)

    output_path = os.path.join(
        DOWNLOAD_DIR,
        "%(title)s.%(ext)s"
    )

    base_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "cookiefile": cookies_path or None,
    }

    player_clients_to_try = ["android", "ios", "web"]
    last_error = None

    for client in player_clients_to_try:
        ydl_opts = {
            **base_opts,
            "extractor_args": {"youtube": {"player_client": [client]}},
        }
        try:
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
        except Exception as exc:
            print(f"[MeetMind] player_client={client} failed: {exc}")
            last_error = exc
            continue

    # All clients failed — surface the last error so the real cause
    # (403, cookies needed, etc.) still shows up in the logs.
    raise last_error

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