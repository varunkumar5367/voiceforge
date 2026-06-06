#!/usr/bin/env python3
"""
VoiceForge — cache_manager.py
Implements disk-based caching of generated audio segments.
Uses SHA-256 hash of text + voice settings as unique identifiers.
"""

import hashlib
from pathlib import Path

# Local cache directory
CACHE_DIR = Path(__file__).parent / ".cache"
CACHE_DIR.mkdir(exist_ok=True)

def get_cache_key(text, voice, rate, pitch, volume):
    """
    Generates a unique SHA-256 hash for the given parameter string.
    """
    key_str = f"{voice}_{rate}_{pitch}_{volume}_{text}"
    return hashlib.sha256(key_str.encode("utf-8")).hexdigest()

def get_cached_audio(text, voice, rate, pitch, volume):
    """
    Reads cached audio from disk if available.
    
    Returns:
        bytes or None: The audio data or None if cache miss.
    """
    key = get_cache_key(text, voice, rate, pitch, volume)
    file_path = CACHE_DIR / f"{key}.mp3"
    
    if file_path.exists() and file_path.is_file():
        try:
            return file_path.read_bytes()
        except IOError as e:
            print(f"⚠️ Cache read error for {key}: {e}")
            return None
    return None

def save_to_cache(text, voice, rate, pitch, volume, audio_bytes):
    """
    Saves generated audio bytes to disk.
    """
    key = get_cache_key(text, voice, rate, pitch, volume)
    file_path = CACHE_DIR / f"{key}.mp3"
    
    try:
        file_path.write_bytes(audio_bytes)
        return True
    except IOError as e:
        print(f"⚠️ Cache write error for {key}: {e}")
        return False

def clear_cache():
    """
    Clears all cached MP3 files.
    """
    for file in CACHE_DIR.glob("*.mp3"):
        try:
            file.unlink()
        except OSError as e:
            print(f"⚠️ Failed to delete cache file {file.name}: {e}")
