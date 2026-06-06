/* ═══════════════════════════════════════════════════
   VoiceForge — app.js
   Core orchestrator coordinating dynamic voice grids, PDF extraction,
   audio setting range-slider fills, and trigger actions.
   ═══════════════════════════════════════════════════ */

// Initialize PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc =
  'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

// ── State ─────────────────────────────────────────────
let currentMode     = 'text';
let extractedText   = '';
let selectedVoice   = 'en-gb-male';
let currentAudioURL = null;
let currentGender   = 'male';

// ── Voice data ────────────────────────────────────────
const VOICE_DATA = [
  { id:'en-gb-male',   name:'Ryan',   flag:'🇬🇧', accent:'British',    gender:'male',   best:true  },
  { id:'en-us-male',   name:'Guy',    flag:'🇺🇸', accent:'American',   gender:'male',   best:false },
  { id:'en-au-male',   name:'William',flag:'🇦🇺', accent:'Australian', gender:'male',   best:false },
  { id:'en-ca-male',   name:'Liam',   flag:'🇨🇦', accent:'Canadian',   gender:'male',   best:false },
  { id:'en-ie-male',   name:'Connor', flag:'🇮🇪', accent:'Irish',      gender:'male',   best:false },
  { id:'en-in-male',   name:'Prabhat',flag:'🇮🇳', accent:'Indian',     gender:'male',   best:false },
  { id:'en-gb-female', name:'Sonia',  flag:'🇬🇧', accent:'British',    gender:'female', best:false },
  { id:'en-us-female', name:'Jenny',  flag:'🇺🇸', accent:'American',   gender:'female', best:false },
  { id:'en-us-aria',   name:'Aria',   flag:'🇺🇸', accent:'American',   gender:'female', best:false },
  { id:'en-au-female', name:'Natasha',flag:'🇦🇺', accent:'Australian', gender:'female', best:false },
  { id:'en-ca-female', name:'Clara',  flag:'🇨🇦', accent:'Canadian',   gender:'female', best:false },
  { id:'en-in-female', name:'Neerja', flag:'🇮🇳', accent:'Indian',     gender:'female', best:false },
];

// ── Theme ─────────────────────────────────────────────
function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('vf-theme', theme);
}
function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'dark';
  applyTheme(current === 'dark' ? 'light' : 'dark');
}

// ── Voice grid ────────────────────────────────────────
function buildVoiceGrid() {
  const grid = document.getElementById('voice-grid');
  if (!grid) return;
  grid.innerHTML = '';

  VOICE_DATA.forEach(v => {
    const card = document.createElement('div');
    const isSelected = v.id === selectedVoice;
    const isCompared = compareVoices.includes(v.id);
    
    card.className = `voice-card ${v.gender}${isSelected ? ' selected' : ''}`;
    card.dataset.voice  = v.id;
    card.dataset.gender = v.gender;
    if (v.gender !== currentGender) card.style.display = 'none';

    card.innerHTML = `
      <div class="vc-check">✓</div>
      <label class="vc-compare-container" onclick="event.stopPropagation()">
        <input type="checkbox" class="vc-compare-chk" data-voice="${v.id}" ${isCompared ? 'checked' : ''} onchange="toggleCompareVoice('${v.id}', this.checked)"/>
        Compare
      </label>
      <div class="vc-flag">${v.flag}</div>
      <div class="vc-name">${v.name}</div>
      <div class="vc-accent">${v.accent}</div>
      <div style="display:flex;gap:4px;flex-wrap:wrap;justify-content:center;margin-top:2px;">
        ${v.best ? '<span class="vc-badge best">⭐ Best</span>' : ''}
        <span class="vc-badge ${v.gender}">${v.gender === 'male' ? '♂' : '♀'}</span>
      </div>
    `;
    card.addEventListener('click', () => selectVoice(v.id));
    grid.appendChild(card);
  });

  updateSelectedBanner();
}

function selectVoice(id) {
  selectedVoice = id;
  document.querySelectorAll('.voice-card').forEach(c => {
    c.classList.toggle('selected', c.dataset.voice === id);
  });
  updateSelectedBanner();
}

function showGender(gender) {
  currentGender = gender;
  document.getElementById('pill-male').classList.toggle('active', gender === 'male');
  document.getElementById('pill-female').classList.toggle('active', gender === 'female');
  document.querySelectorAll('.voice-card').forEach(c => {
    c.style.display = c.dataset.gender === gender ? '' : 'none';
  });
}

function updateSelectedBanner() {
  const v = VOICE_DATA.find(x => x.id === selectedVoice);
  if (v) {
    document.getElementById('selected-voice-name').textContent =
      `${v.flag} ${v.name} — ${v.accent} ${v.gender === 'male' ? '♂ Male' : '♀ Female'}`;
  }
}

// ── Tab switch ────────────────────────────────────────
function switchTab(mode) {
  currentMode = mode;
  document.getElementById('pill-text').classList.toggle('active', mode === 'text');
  document.getElementById('pill-pdf').classList.toggle('active', mode === 'pdf');
  document.getElementById('panel-text').classList.toggle('hidden', mode !== 'text');
  document.getElementById('panel-pdf').classList.toggle('hidden', mode !== 'pdf');
}

// ── Text input ────────────────────────────────────────
const textInput = document.getElementById('text-input');
const charCount = document.getElementById('char-count');

if (textInput) {
  textInput.addEventListener('input', () => {
    const n = textInput.value.length;
    charCount.textContent = n.toLocaleString() + (n === 1 ? ' character' : ' characters');
    charCount.className = 'char-count' + (n > 5000 ? ' long' : n > 2000 ? ' warn' : '');
  });
}

function clearText() {
  textInput.value = '';
  charCount.textContent = '0 characters';
  charCount.className = 'char-count';
  textInput.focus();
}

async function pasteText() {
  try {
    const text = await navigator.clipboard.readText();
    textInput.value = text;
    textInput.dispatchEvent(new Event('input'));
  } catch {
    alert('Clipboard access denied. Paste manually (Ctrl+V).');
  }
}

// ── PDF handling ──────────────────────────────────────
function handleDragOver(e) { e.preventDefault(); document.getElementById('dropzone').classList.add('drag-over'); }
function handleDragLeave() { document.getElementById('dropzone').classList.remove('drag-over'); }
function handleDrop(e) {
  e.preventDefault();
  document.getElementById('dropzone').classList.remove('drag-over');
  const f = e.dataTransfer.files[0];
  if (f?.type === 'application/pdf') processPDF(f);
  else alert('Please drop a PDF file.');
}
function handleFileSelect(e) { if (e.target.files[0]) processPDF(e.target.files[0]); }

function removePDF() {
  extractedText = '';
  document.getElementById('dropzone').classList.remove('hidden');
  document.getElementById('pdf-info').classList.add('hidden');
  document.getElementById('pdf-file').value = '';
}

async function processPDF(file) {
  document.getElementById('dropzone').classList.add('hidden');
  const info = document.getElementById('pdf-info');
  info.classList.remove('hidden');
  document.getElementById('pdf-name').textContent = file.name;
  document.getElementById('pdf-pages').textContent = 'Reading…';

  const progress = document.getElementById('pdf-progress');
  const fill     = document.getElementById('pdf-fill');
  progress.classList.remove('hidden');
  fill.style.width = '0%';

  try {
    const buf = await file.arrayBuffer();
    const pdf = await pdfjsLib.getDocument({ data: buf }).promise;
    const total = pdf.numPages;
    document.getElementById('pdf-pages').textContent = `${total} page${total !== 1 ? 's' : ''}`;

    let full = '';
    for (let i = 1; i <= total; i++) {
      const page = await pdf.getPage(i);
      const content = await page.getTextContent();
      full += content.items.map(it => it.str).join(' ') + '\n\n';
      fill.style.width = Math.round((i / total) * 100) + '%';
    }

    extractedText = full.trim();
    progress.classList.add('hidden');
    const prev = document.getElementById('pdf-preview');
    document.getElementById('pdf-preview').classList.remove('hidden');
    document.getElementById('preview-text').textContent =
      extractedText.slice(0, 500) + (extractedText.length > 500 ? '…' : '');
  } catch (err) {
    console.error(err);
    document.getElementById('pdf-pages').textContent = '⚠️ Error reading PDF';
    progress.classList.add('hidden');
    alert('Could not extract text. Make sure it is a text-based PDF, not a scanned image.');
  }
}

// ── Sliders ───────────────────────────────────────────
function updateSlider(type) {
  const el  = document.getElementById(`${type}-range`);
  const val = document.getElementById(`${type}-val`);
  if (!el || !val) return;
  
  const n = parseFloat(el.value);

  // Sync filled slider track width
  const fill = document.getElementById(`${type}-fill`);
  if (fill) {
    const min = parseFloat(el.min) || 0;
    const max = parseFloat(el.max) || 100;
    const pct = ((n - min) / (max - min)) * 100;
    fill.style.width = pct + '%';
  }

  // Display textual value mapping
  if (type === 'speed') {
    const spd = 1 + n / 100;
    val.textContent = spd.toFixed(2) + '×';
  } else if (type === 'pitch') {
    val.textContent = (n >= 0 ? '+' : '') + n + ' Hz';
  } else if (type === 'volume') {
    val.textContent = (n >= 0 ? '+' : '') + n + '%';
  } else if (type === 'chunk-size') {
    val.textContent = n + ' chars';
  }
}

function resetSettings() {
  ['speed','pitch','volume'].forEach(t => {
    document.getElementById(`${t}-range`).value = 0;
    updateSlider(t);
  });
  document.getElementById('chunk-size-range').value = 2500;
  updateSlider('chunk-size');
  
  // Clear any active preset selection
  clearPresetSelection();
}

function getEdgeTTSParams() {
  const speed  = parseFloat(document.getElementById('speed-range').value) || 0;
  const pitch  = parseFloat(document.getElementById('pitch-range').value) || 0;
  const volume = parseFloat(document.getElementById('volume-range').value) || 0;
  return {
    rate  : (speed  >= 0 ? '+' : '') + speed  + '%',
    pitch : (pitch  >= 0 ? '+' : '') + pitch  + 'Hz',
    volume: (volume >= 0 ? '+' : '') + volume + '%',
  };
}

// ── Client-Side Chunking Fallback ─────────────────────
function chunkTextFallback(text, maxChars = 2500) {
  const sentences = text.match(/[^.!?\n]+[.!?\n]+\s*/g) || [text];
  const chunks = [];
  let current = '';
  for (const s of sentences) {
    if (s.length > maxChars) {
      if (current) { chunks.push(current.trim()); current = ''; }
      const sub = s.match(new RegExp(`.{1,${maxChars}}(?:[,;]\\s*|\\s|$)`, 'g')) || [s];
      sub.forEach(x => { if (x.trim()) chunks.push(x.trim()); });
    } else if ((current + s).length > maxChars) {
      if (current.trim()) chunks.push(current.trim());
      current = s;
    } else {
      current += s;
    }
  }
  if (current.trim()) chunks.push(current.trim());
  return chunks.filter(c => c.length > 0);
}

// ── Server status ─────────────────────────────────────
async function checkServer() {
  const badge  = document.getElementById('server-badge');
  const dot    = document.getElementById('badge-dot');
  const label  = document.getElementById('badge-label');
  if (!badge) return;
  
  try {
    const r = await fetch('/voices', { signal: AbortSignal.timeout(2000) });
    if (r.ok) {
      badge.className = 'server-badge online';
      label.textContent = 'Server Online';
    } else throw new Error();
  } catch {
    badge.className = 'server-badge offline';
    label.textContent = 'Server Offline';
  }
}

// ── Audio Generation ──────────────────────────────────
let activeProcessor = null;

async function generateAudio() {
  const text = currentMode === 'text' ? textInput.value.trim() : extractedText.trim();
  if (!text) { alert('Please enter some text or upload a PDF first.'); return; }

  // Check server connectivity
  try {
    const probe = await fetch('/voices', { signal: AbortSignal.timeout(2000) });
    if (!probe.ok) throw new Error();
  } catch {
    alert('⚠️  VoiceForge server is not running!\n\nIn PowerShell, run:\n\n    python server.py\n\nThen refresh and try again.');
    return;
  }

  const params  = getEdgeTTSParams();
  const maxChars = parseInt(document.getElementById('chunk-size-range').value) || 2500;
  
  const genBtn  = document.getElementById('btn-generate');
  const cardPl  = document.getElementById('card-player');
  const genProg = document.getElementById('gen-progress');
  const audioRd = document.getElementById('audio-ready');
  const genLbl  = document.getElementById('gen-label');
  const genFill = document.getElementById('gen-fill');
  const genPct  = document.getElementById('gen-pct');
  const descEl  = document.getElementById('player-desc');

  // Trigger UI loading state
  cardPl.classList.remove('hidden');
  genProg.classList.remove('hidden');
  audioRd.classList.add('hidden');
  descEl.textContent = 'Preparing generation…';
  genBtn.disabled = true;
  genLbl.textContent = 'Analyzing text chunks…';
  genFill.style.width = '0%';
  genPct.textContent  = '0%';
  cardPl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

  // Get chunks from backend splitting service
  let chunks = [];
  try {
    const chunkRes = await fetch('/chunk', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, max_len: maxChars })
    });
    if (!chunkRes.ok) throw new Error();
    const data = await chunkRes.json();
    chunks = data.chunks || [];
  } catch (err) {
    console.warn('Backend chunking endpoint failed, falling back to client-side chunker:', err);
    chunks = chunkTextFallback(text, maxChars);
  }

  if (!chunks || chunks.length === 0) {
    genLbl.textContent = '⚠️ Error segmenting text chunks.';
    genBtn.disabled = false;
    return;
  }

  // Create processor using the Chunk Processing Service
  activeProcessor = new ChunkProcessor(chunks, selectedVoice, params, (stats, task) => {
    // Progress hook
    let labelText = `Chunk ${task.id + 1} of ${stats.total}`;
    if (task.status === 'Retrying') labelText += ' (Retrying once…)';
    
    genLbl.textContent = labelText;
    genFill.style.width = stats.pct + '%';
    genPct.textContent  = stats.pct + '%';
    descEl.textContent = `${stats.pct}% Completed`;
  });

  try {
    const finalBlob = await activeProcessor.process();
    
    // Complete generation progress UI
    genFill.style.width = '100%';
    genPct.textContent  = '100%';
    genBtn.disabled = false;

    if (currentAudioURL) URL.revokeObjectURL(currentAudioURL);
    currentAudioURL = URL.createObjectURL(finalBlob);

    // Swap loading state with ready audio player
    genProg.classList.add('hidden');
    audioRd.classList.remove('hidden');

    const v = VOICE_DATA.find(x => x.id === selectedVoice);
    document.getElementById('player-voice-tag').innerHTML =
      `<svg viewBox="0 0 20 20" fill="currentColor" width="12"><path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z"/></svg> ${v ? v.flag+' '+v.name+' · '+v.accent : selectedVoice}`;

    const player = document.getElementById('audio-player');
    player.src   = currentAudioURL;
    
    // Render the collapsible statistics section
    displayGenerationStats(activeProcessor.metrics, selectedVoice);

    player.play().catch(() => {});
    descEl.textContent = `Ready — ${(finalBlob.size / 1024).toFixed(0)} KB`;
  } catch (err) {
    console.error('[VoiceForge] Generation failed:', err);
    genLbl.textContent = `⚠️ Error: ${err.message}`;
    descEl.textContent = 'Generation stopped.';
    genBtn.disabled = false;
  }
}

// ── Save MP3 ──────────────────────────────────────────
function saveCurrentAudio() {
  if (!currentAudioURL) { alert('Generate audio first!'); return; }
  const v        = VOICE_DATA.find(x => x.id === selectedVoice);
  const name     = v ? `${v.name}_${v.accent}` : selectedVoice;
  const filename = `voiceforge_${name.replace(/\s+/g,'_').toLowerCase()}_${Date.now()}.mp3`;
  const a = document.createElement('a');
  a.href = currentAudioURL; a.download = filename;
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
}

// ── Init ──────────────────────────────────────────────
window.addEventListener('load', () => {
  // Apply saved theme
  const saved = localStorage.getItem('vf-theme') || 'dark';
  applyTheme(saved);

  // Build primary voice selection grid
  buildVoiceGrid();

  // Initialize sliders
  updateSlider('speed');
  updateSlider('pitch');
  updateSlider('volume');
  updateSlider('chunk-size');

  // Add listeners to reset preset highlighting on manual modification
  ['speed', 'pitch', 'volume'].forEach(type => {
    const el = document.getElementById(`${type}-range`);
    if (el) {
      el.addEventListener('input', () => {
        clearPresetSelection();
      });
    }
  });

  // Render presets list and restore state
  buildPresetsGrid();
  restorePreset();

  // Initialize Voice Comparison
  initComparison();

  // Perform server pinging
  checkServer();
  setInterval(checkServer, 10000);
});
