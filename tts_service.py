#!/usr/bin/env python3
"""
VoiceForge — tts_service.py
Wraps edge-tts API calls to generate MP3 audio streams.
"""

import asyncio
import edge_tts

async def generate_audio_stream(text, voice, rate="+0%", pitch="+0Hz", volume="+0%"):
    """
    Interfaces with edge_tts.Communicate to generate audio bytes.
    
    Args:
        text: Script to synthesize.
        voice: Full Microsoft voice identifier (e.g. 'en-GB-RyanNeural').
        rate: Speed modifier string (e.g. '+10%').
        pitch: Pitch modifier string (e.g. '-2Hz').
        volume: Volume modifier string (e.g. '+5%').
        
    Returns:
        bytes: Raw MP3 stream bytes.
    """
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, volume=volume)
    audio_chunks = []
    
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_chunks.append(chunk["data"])
            
    return b"".join(audio_chunks)
