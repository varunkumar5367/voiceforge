#!/usr/bin/env python3
"""
VoiceForge TTS Server — FastAPI Implementation
Provides TTS generation, chunking, caching, stats, and StoryForge API integration.

Run:   python server.py
Open:  http://localhost:8080
"""

import os
import sys
import time
from pathlib import Path

from fastapi import FastAPI, Form, Response, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Import modular helper services
from chunker import split_text_into_chunks
from tts_service import generate_audio_stream
import cache_manager
from progress_manager import tracker

# Handle console encoding on Windows to prevent UnicodeEncodeError
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

ROOT = Path(__file__).parent
PORT = int(os.environ.get("PORT", 8080))

MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".ico": "image/x-icon",
    ".png": "image/png",
    ".mp3": "audio/mpeg"
}

VOICES = {
    "en-gb-male"  : "en-GB-RyanNeural",
    "en-us-male"  : "en-US-GuyNeural",
    "en-au-male"  : "en-AU-WilliamNeural",
    "en-ca-male"  : "en-CA-LiamNeural",
    "en-ie-male"  : "en-IE-ConnorNeural",
    "en-in-male"  : "en-IN-PrabhatNeural",
    "en-gb-female": "en-GB-SoniaNeural",
    "en-us-female": "en-US-JennyNeural",
    "en-us-aria"  : "en-US-AriaNeural",
    "en-au-female": "en-AU-NatashaNeural",
    "en-ca-female": "en-CA-ClaraNeural",
    "en-in-female": "en-IN-NeerjaNeural",
}

app = FastAPI(title="VoiceForge API")

# ── Update 2: CORS Middleware ───────────────────────────
# StoryForge backend (on Render) needs to call VoiceForge (on Render)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict to your StoryForge URL later
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

async def _tts_core(text: str, voice_id: str, rate: str, pitch: str, volume: str):
    # Retrieve voice name, default to Ryan Neural if not found or if already a full name
    voice = VOICES.get(voice_id, voice_id)
    if voice not in VOICES.values() and voice_id not in VOICES:
        voice = "en-GB-RyanNeural"
        
    # 1. Check disk cache
    cached_data = cache_manager.get_cached_audio(text, voice, rate, pitch, volume)
    if cached_data is not None:
        tracker.record_generation(len(text), 0.0, is_cache_hit=True)
        print(f"  ⚡  Cache Hit: {len(cached_data)//1024}KB [{voice}]")
        return cached_data

    # 2. Cache Miss - Generate dynamically via edge-tts
    start_time = time.time()
    try:
        data = await generate_audio_stream(text, voice, rate, pitch, volume)
        if not data or len(data) < 50:
            raise ValueError("Empty or invalid audio generated.")

        duration = time.time() - start_time
        
        # Save to cache
        cache_manager.save_to_cache(text, voice, rate, pitch, volume, data)
        tracker.record_generation(len(text), duration, is_cache_hit=False)
        print(f"  🎙   Generated: {len(data)//1024}KB [{voice}] rate={rate} pitch={pitch} ({duration:.2f}s)")
        return data
    except Exception as e:
        print(f"  ❌ Generation Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ── API Endpoints ───────────────────────────────────────

# ── Update 4: Health check ──────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "ok"}

# ── Update 3: Voice List ────────────────────────────────
@app.get("/api/voices")
def get_voices():
    return {
        "voices": [
            {"id": "en-GB-RyanNeural", "name": "Ryan", "gender": "male"},
            {"id": "en-US-GuyNeural", "name": "Guy", "gender": "male"},
            {"id": "en-AU-WilliamNeural", "name": "William", "gender": "male"},
            {"id": "en-CA-LiamNeural", "name": "Liam", "gender": "male"},
            {"id": "en-IE-ConnorNeural", "name": "Connor", "gender": "male"},
            {"id": "en-IN-PrabhatNeural", "name": "Prabhat", "gender": "male"},
            {"id": "en-GB-SoniaNeural", "name": "Sonia", "gender": "female"},
            {"id": "en-US-JennyNeural", "name": "Jenny", "gender": "female"},
            {"id": "en-US-AriaNeural", "name": "Aria", "gender": "female"},
            {"id": "en-AU-NatashaNeural", "name": "Natasha", "gender": "female"},
            {"id": "en-CA-ClaraNeural", "name": "Clara", "gender": "female"},
            {"id": "en-IN-NeerjaNeural", "name": "Neerja", "gender": "female"}
        ]
    }

# ── Update 1: Form-based TTS API ────────────────────────
@app.post("/api/tts")
async def tts_api(
    text: str = Form(...),
    voice: str = Form(default="en-GB-RyanNeural"),
    speed: float = Form(default=1.0),
    pitch: int = Form(default=0)
):
    # Map speed multiplier to relative percentage format (e.g. 1.05 -> "+5%", 0.85 -> "-15%")
    pct = int(round((speed - 1.0) * 100))
    rate_str = f"{pct:+}%"
    
    # Map pitch to signed Hz format (e.g. 2 -> "+2Hz", 0 -> "+0Hz")
    pitch_str = f"{pitch:+}Hz"
    
    audio_bytes = await _tts_core(text, voice, rate_str, pitch_str, "+0%")
    return Response(content=audio_bytes, media_type="audio/mpeg")

# ── Legacy Endpoints (For VoiceForge UI) ────────────────

@app.get("/voices")
def get_legacy_voices():
    return VOICES

class ChunkRequest(BaseModel):
    text: str
    max_len: int = 2500

@app.post("/chunk")
def post_chunk(req: ChunkRequest):
    chunks = split_text_into_chunks(req.text, req.max_len)
    return {"chunks": chunks}

@app.get("/tts")
async def get_legacy_tts(
    text: str = Query(...),
    voice: str = Query("en-gb-male"),
    rate: str = Query("+0%"),
    pitch: str = Query("+0Hz"),
    volume: str = Query("+0%")
):
    data = await _tts_core(text, voice, rate, pitch, volume)
    return Response(content=data, media_type="audio/mpeg")

class TTSRequest(BaseModel):
    text: str
    voice: str = "en-gb-male"
    rate: str = "+0%"
    pitch: str = "+0Hz"
    volume: str = "+0%"

@app.post("/tts")
async def post_legacy_tts(req: TTSRequest):
    data = await _tts_core(req.text, req.voice, req.rate, req.pitch, req.volume)
    return Response(content=data, media_type="audio/mpeg")

@app.get("/stats")
def get_stats():
    return tracker.get_stats()

# Serve static web UI files at root last
app.mount("/", StaticFiles(directory=str(ROOT), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print(f"\n╔══════════════════════════════════╗\n║  🎙  VoiceForge (FastAPI)        ║\n║  http://localhost:{PORT}            ║\n╚══════════════════════════════════╝\n")
    uvicorn.run("server:app", host="0.0.0.0", port=PORT, reload=False)
