#!/usr/bin/env python3
"""
VoiceForge TTS Server — Thread-safe HTTP Server
Integrates modular chunking, caching, stats, and tts_service.

Run:   python server.py
Open:  http://localhost:8080
"""

import io
import os
import sys
import json
import time
import asyncio
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

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

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        code = args[1] if len(args) > 1 else "?"
        icon = "✅" if str(code).startswith("2") else "⚠️"
        print(f"  {icon} {getattr(self, 'command', '?')} {self.path} → {code}")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        p = urlparse(self.path)
        q = parse_qs(p.query)

        if p.path == "/tts":
            self._handle_tts_get(q)
            return

        if p.path == "/voices":
            d = json.dumps(VOICES).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(d)))
            self._cors()
            self.end_headers()
            self.wfile.write(d)
            return

        if p.path == "/stats":
            d = json.dumps(tracker.get_stats()).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(d)))
            self._cors()
            self.end_headers()
            self.wfile.write(d)
            return

        self._file(p.path if p.path != "/" else "/index.html")

    def do_POST(self):
        p = urlparse(self.path)
        l = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(l)

        if p.path == "/chunk":
            self._handle_chunk_post(body)
            return

        if p.path == "/tts":
            self._handle_tts_post(body)
            return

        self._raw(404, b"Not found")

    def _handle_chunk_post(self, body):
        try:
            d = json.loads(body)
        except Exception:
            d = {}
        
        text = d.get("text", "").strip()
        max_len = int(d.get("max_len", 2500))

        # Perform intelligent text split
        chunks = split_text_into_chunks(text, max_len)
        res_data = json.dumps({"chunks": chunks}).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(res_data)))
        self._cors()
        self.end_headers()
        self.wfile.write(res_data)

    def _handle_tts_get(self, q):
        text = q.get("text", [""])[0].strip()
        voice_id = q.get("voice", ["en-gb-male"])[0]
        rate = q.get("rate", ["+0%"])[0]
        pitch = q.get("pitch", ["+0Hz"])[0]
        volume = q.get("volume", ["+0%"])[0]
        self._tts(text, voice_id, rate, pitch, volume)

    def _handle_tts_post(self, body):
        try:
            d = json.loads(body)
        except Exception:
            d = {}
        
        text = d.get("text", "").strip()
        voice_id = d.get("voice", "en-gb-male")
        rate = d.get("rate", "+0%")
        pitch = d.get("pitch", "+0Hz")
        volume = d.get("volume", "+0%")
        self._tts(text, voice_id, rate, pitch, volume)

    def _tts(self, text, voice_id, rate, pitch, volume):
        if not text:
            self._raw(400, b"No text provided")
            return

        v = VOICES.get(voice_id, "en-GB-RyanNeural")
        
        # 1. Check disk cache
        cached_data = cache_manager.get_cached_audio(text, v, rate, pitch, volume)
        if cached_data is not None:
            # Record metrics as a cache hit
            tracker.record_generation(len(text), 0.0, is_cache_hit=True)
            
            self.send_response(200)
            self.send_header("Content-Type", "audio/mpeg")
            self.send_header("Content-Length", str(len(cached_data)))
            self._cors()
            self.end_headers()
            self.wfile.write(cached_data)
            print(f"  ⚡  Cache Hit: {len(cached_data)//1024}KB [{v}]")
            return

        # 2. Cache Miss - Generate dynamically via edge-tts
        start_time = time.time()
        try:
            # Run the coroutine in a synchronous loop context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                data = loop.run_until_complete(
                    generate_audio_stream(text, v, rate, pitch, volume)
                )
            finally:
                loop.close()

            if not data or len(data) < 50:
                raise ValueError("Empty or invalid audio generated.")

            duration = time.time() - start_time
            
            # Save to cache
            cache_manager.save_to_cache(text, v, rate, pitch, volume, data)
            
            # Record statistics
            tracker.record_generation(len(text), duration, is_cache_hit=False)

            self.send_response(200)
            self.send_header("Content-Type", "audio/mpeg")
            self.send_header("Content-Length", str(len(data)))
            self._cors()
            self.end_headers()
            self.wfile.write(data)
            print(f"  🎙   Generated: {len(data)//1024}KB [{v}] rate={rate} pitch={pitch} ({duration:.2f}s)")
            
        except Exception as e:
            print(f"  ❌ Generation Error: {e}")
            self._raw(500, str(e).encode())

    def _file(self, path):
        try:
            # Resolve the absolute path to prevent path traversal (../)
            fp = (ROOT / path.lstrip("/")).resolve()
            # Ensure the resolved file path starts with the ROOT path
            if ROOT.resolve() in fp.parents and fp.is_file():
                d = fp.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", MIME.get(fp.suffix.lower(), "application/octet-stream"))
                self.send_header("Content-Length", str(len(d)))
                self._cors()
                self.end_headers()
                self.wfile.write(d)
                return
        except Exception as e:
            print(f"  ⚠️ File read error: {e}")
            
        self._raw(404, b"Not found")

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _raw(self, code, body):
        self.send_response(code)
        self._cors()
        self.end_headers()
        self.wfile.write(body)

if __name__ == "__main__":
    # Use ThreadingHTTPServer to handle requests concurrently
    server = ThreadingHTTPServer(("", PORT), Handler)
    print(f"\n╔══════════════════════════════════╗\n║  🎙  VoiceForge · Neural TTS     ║\n║  http://localhost:{PORT}            ║\n╚══════════════════════════════════╝\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  ⏹  Stopped.\n")
