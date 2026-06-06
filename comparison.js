/* ═══════════════════════════════════════════════════
   VoiceForge — comparison.js
   Handles voice comparison generation, caching, side-by-side rendering,
   playback controls, and voice selection bindings.
   ═══════════════════════════════════════════════════ */

let compareVoices = ['en-gb-male', 'en-us-male', 'en-au-male', 'en-ca-male'];
const comparisonCache = {}; // Cache key (voiceId_hash) -> blobUrl
const comparisonAudioUrls = {}; // Current active generated blob urls

let activeCompAudio = null;
let activeCompVoiceId = null;

/**
 * Initializes comparison hooks.
 */
function initComparison() {
  const btn = document.getElementById('btn-compare-action');
  if (btn) {
    btn.removeEventListener('click', runComparison);
    btn.addEventListener('click', runComparison);
  }
  updateCompareCount();
}

/**
 * Updates the compare button count badge.
 */
function updateCompareCount() {
  const el = document.getElementById('compare-count');
  if (el) el.textContent = compareVoices.length;
}

/**
 * Toggles a voice card in the comparison list.
 */
function toggleCompareVoice(voiceId, checked) {
  if (checked) {
    if (!compareVoices.includes(voiceId)) {
      compareVoices.push(voiceId);
    }
  } else {
    compareVoices = compareVoices.filter(id => id !== voiceId);
  }
  updateCompareCount();
}

/**
 * Closes the comparison panel and pauses active audio.
 */
function closeComparison() {
  const card = document.getElementById('card-comparison');
  if (card) card.classList.add('hidden');
  
  if (activeCompAudio) {
    activeCompAudio.pause();
    activeCompAudio = null;
    activeCompVoiceId = null;
  }
}

/**
 * Creates a unique hash key representation of comparison parameters.
 */
function getCompTextHash(text, params) {
  const cleanText = text.slice(0, 30).replace(/[^a-zA-Z0-9]/g, '');
  return `${text.length}_${cleanText}_${params.rate}_${params.pitch}_${params.volume}`;
}

/**
 * Generates and opens comparison previews side-by-side.
 */
async function runComparison() {
  const textInput = document.getElementById('text-input');
  const rawText = currentMode === 'text' ? textInput.value.trim() : extractedText.trim();
  
  if (!rawText) {
    alert('Please enter some text or upload a PDF first.');
    return;
  }
  
  if (compareVoices.length < 2) {
    alert('Please select at least 2 voices to compare (use the checkboxes at the bottom of the voice cards).');
    return;
  }
  
  // Show comparison container
  const card = document.getElementById('card-comparison');
  if (card) {
    card.classList.remove('hidden');
    card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
  
  const grid = document.getElementById('comparison-grid');
  if (!grid) return;
  grid.innerHTML = '';
  
  // Take first 200-300 characters for quick comparison
  const compText = rawText.slice(0, 300);
  const params = getEdgeTTSParams();
  const hash = getCompTextHash(compText, params);
  
  // Render loading skeleton for selected comparison cards
  compareVoices.forEach(voiceId => {
    const v = VOICE_DATA.find(x => x.id === voiceId);
    if (!v) return;
    
    const cardEl = document.createElement('div');
    cardEl.className = 'comp-card';
    cardEl.id = `comp-card-${voiceId}`;
    cardEl.innerHTML = `
      <div class="comp-header">
        <span class="comp-flag">${v.flag}</span>
        <div class="comp-meta">
          <div class="comp-name">${v.name}</div>
          <div class="comp-accent">${v.accent} · ${v.gender === 'male' ? 'Male' : 'Female'}</div>
        </div>
      </div>
      
      <div class="comp-loading" id="comp-loading-${voiceId}">
        <div class="spinner"></div>
        <span>Generating…</span>
      </div>
      
      <div class="comp-controls hidden" id="comp-controls-${voiceId}">
        <div class="comp-audio-row">
          <button class="comp-play-btn" id="comp-play-${voiceId}" onclick="playComparisonAudio('${voiceId}')">
            <svg viewBox="0 0 20 20" fill="currentColor" width="14"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"/></svg>
            Play
          </button>
          <button class="comp-download-btn" onclick="downloadComparisonAudio('${voiceId}')" title="Download Preview">
            <svg viewBox="0 0 20 20" fill="currentColor" width="14"><path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
          </button>
        </div>
        <button class="comp-use-btn" onclick="useComparisonVoice('${voiceId}')">Use This Voice</button>
      </div>
      
      <div class="comp-error-msg hidden" id="comp-error-${voiceId}">
        ⚠️ Generation failed
      </div>
    `;
    grid.appendChild(cardEl);
  });
  
  // Fire off API requests concurrently
  compareVoices.forEach(voiceId => {
    fetchComparisonPreview(voiceId, compText, params, hash);
  });
}

/**
 * Fetches the comparison audio, checking cache first to feel instantaneous.
 */
async function fetchComparisonPreview(voiceId, text, params, hash) {
  const cacheKey = `${voiceId}_${hash}`;
  const loadingEl = document.getElementById(`comp-loading-${voiceId}`);
  const controlsEl = document.getElementById(`comp-controls-${voiceId}`);
  const errorEl = document.getElementById(`comp-error-${voiceId}`);
  
  // Check client-side memory cache
  if (comparisonCache[cacheKey]) {
    comparisonAudioUrls[voiceId] = comparisonCache[cacheKey];
    if (loadingEl) loadingEl.classList.add('hidden');
    if (controlsEl) controlsEl.classList.remove('hidden');
    return;
  }
  
  const url = `/tts?voice=${encodeURIComponent(voiceId)}` +
              `&text=${encodeURIComponent(text)}` +
              `&rate=${encodeURIComponent(params.rate)}` +
              `&pitch=${encodeURIComponent(params.pitch)}` +
              `&volume=${encodeURIComponent(params.volume)}`;
              
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP Error ${res.status}`);
    const blob = await res.blob();
    if (blob.size < 50) throw new Error('Empty blob response');
    
    const blobUrl = URL.createObjectURL(blob);
    // Cache the preview url for quick replays
    comparisonCache[cacheKey] = blobUrl;
    comparisonAudioUrls[voiceId] = blobUrl;
    
    if (loadingEl) loadingEl.classList.add('hidden');
    if (controlsEl) controlsEl.classList.remove('hidden');
  } catch (err) {
    console.error(`[Comparison] error generating ${voiceId}:`, err);
    if (loadingEl) loadingEl.classList.add('hidden');
    if (errorEl) errorEl.classList.remove('hidden');
  }
}

/**
 * Handles playing and pausing of compared audio items.
 */
function playComparisonAudio(voiceId) {
  const url = comparisonAudioUrls[voiceId];
  if (!url) return;
  
  const playBtn = document.getElementById(`comp-play-${voiceId}`);
  const playIcon = `<svg viewBox="0 0 20 20" fill="currentColor" width="14"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"/></svg> Play`;
  const pauseIcon = `<svg viewBox="0 0 20 20" fill="currentColor" width="14"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd"/></svg> Pause`;
  
  if (activeCompVoiceId === voiceId && activeCompAudio) {
    if (activeCompAudio.paused) {
      activeCompAudio.play();
      playBtn.innerHTML = pauseIcon;
    } else {
      activeCompAudio.pause();
      playBtn.innerHTML = playIcon;
    }
    return;
  }
  
  // Stop previously playing audio
  if (activeCompAudio) {
    activeCompAudio.pause();
    const prevBtn = document.getElementById(`comp-play-${activeCompVoiceId}`);
    if (prevBtn) prevBtn.innerHTML = playIcon;
  }
  
  activeCompVoiceId = voiceId;
  activeCompAudio = new Audio(url);
  activeCompAudio.play();
  playBtn.innerHTML = pauseIcon;
  
  activeCompAudio.onended = () => {
    if (playBtn) playBtn.innerHTML = playIcon;
    activeCompAudio = null;
    activeCompVoiceId = null;
  };
}

/**
 * Downloads the comparison MP3 file.
 */
function downloadComparisonAudio(voiceId) {
  const url = comparisonAudioUrls[voiceId];
  if (!url) return;
  const v = VOICE_DATA.find(x => x.id === voiceId);
  const name = v ? `${v.name}_${v.accent}` : voiceId;
  const filename = `voiceforge_compare_${name.replace(/\s+/g,'_').toLowerCase()}.mp3`;
  
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

/**
 * Selects the comparison voice as the primary voice.
 */
function useComparisonVoice(voiceId) {
  if (typeof selectVoice === 'function') {
    selectVoice(voiceId);
  }
  
  // Ensure the correct gender filter tab is selected
  const v = VOICE_DATA.find(x => x.id === voiceId);
  if (v && v.gender !== currentGender) {
    if (typeof showGender === 'function') {
      showGender(v.gender);
    }
  }
  
  closeComparison();
}
