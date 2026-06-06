# 🎙️ VoiceForge — Professional Neural Text-to-Speech (TTS) Studio

🔗 **Live Link:** [https://voiceforge-pzxd.onrender.com](https://voiceforge-pzxd.onrender.com)

VoiceForge is a modern, high-fidelity neural text-to-speech studio that turns scripts and PDF documents into natural, studio-quality narration. Powered by Microsoft Edge's Neural TTS engine, it offers regional English voices, customizable pitch/speed settings, voice comparison, and automatic audio segment chunking.

---

## ✨ Features

- **🎨 Premium Interface**: Beautiful glassmorphic design system with dynamic light/dark modes.
- **🎙️ Microsoft Neural Voices**: Access to 12 top-tier male & female natural narrators across global accents (British, American, Australian, Canadian, Irish, Indian).
- **🎛️ Audio Settings**: Fine-tune Speed, Pitch, and Volume modifiers to craft the perfect tone.
- **⚡ Voice Presets**: Fast-apply presets like *Professional Narration*, *Conversational*, *Documentary*, *Audiobook*, or *Fast Presentation*.
- **📊 AI Script Chunking**: Supports processing of long texts and PDF scripts by splitting segments intelligently at paragraph and sentence boundaries.
- **🔄 Retry & Recovery**: Automatically handles connection drops or chunk failures by retrying failed clips once, avoiding restarting from scratch.
- **⚡ Voice Comparison Mode**: Test up to 4+ voices side-by-side using a 250-character sample of your script.
- **💾 Disk & Memory Caching**: Backend SHA-256 caching saves audio segments to avoid duplicate network queries and make replays instant.
- **📈 Generation Metrics**: Displays text size, chunk count, processing duration, and estimated audio length in a collapsible panel.

---

## 🛠️ Tech Stack

- **Frontend**: Vanilla HTML5, CSS3 Variables, JavaScript (ES6 Modules)
- **Backend**: Python 3.7+ (`http.server` with thread-safe `ThreadingHTTPServer`)
- **APIs & Tools**: Microsoft `edge-tts`, PDF.js (by Mozilla)

---

## 🚀 Running Locally

1. **Clone this repository**:
   ```bash
   git clone https://github.com/your-username/voiceforge.git
   cd voiceforge
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the server**:
   ```bash
   python server.py
   ```

4. **Open in browser**:
   Visit [http://localhost:8080](http://localhost:8080) in your web browser.

---

## 🌐 Deploying Online (Live Link)

VoiceForge is fully deployed and running live on Render:
- **Live URL:** [https://voiceforge-pzxd.onrender.com](https://voiceforge-pzxd.onrender.com)

To host your own version:
1. Push code to your own GitHub repository.
2. Create a new **Web Service** on Render pointing to your repository.
3. Render automatically detects `requirements.txt`. Set the start command to `python server.py`.

