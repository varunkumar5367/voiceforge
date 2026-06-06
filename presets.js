/* ═══════════════════════════════════════════════════
   VoiceForge — presets.js
   Manages speech speed, pitch, and volume configuration presets.
   ═══════════════════════════════════════════════════ */

const PRESETS = {
  narration: { name: 'Professional Narration', rate: 5, pitch: -1, volume: 3, icon: '🎙️' },
  conversational: { name: 'Conversational', rate: 8, pitch: 2, volume: 5, icon: '💬' },
  documentary: { name: 'Documentary', rate: 4, pitch: -2, volume: 2, icon: '🎞️' },
  audiobook: { name: 'Audiobook', rate: 0, pitch: -1, volume: 4, icon: '📖' },
  fast: { name: 'Fast Presentation', rate: 15, pitch: 1, volume: 5, icon: '⚡' }
};

/**
 * Renders the presets grid container dynamically.
 */
function buildPresetsGrid() {
  const grid = document.getElementById('presets-grid');
  if (!grid) return;
  grid.innerHTML = '';
  
  Object.keys(PRESETS).forEach(key => {
    const p = PRESETS[key];
    const btn = document.createElement('button');
    btn.className = 'preset-card';
    btn.id = `preset-${key}`;
    btn.innerHTML = `
      <span class="preset-icon">${p.icon}</span>
      <span class="preset-name">${p.name}</span>
    `;
    btn.addEventListener('click', () => selectPreset(key));
    grid.appendChild(btn);
  });
}

/**
 * Selects a preset and sets the sliders and their visual representations.
 */
function selectPreset(key) {
  const p = PRESETS[key];
  if (!p) return;
  
  const speedSlider = document.getElementById('speed-range');
  const pitchSlider = document.getElementById('pitch-range');
  const volumeSlider = document.getElementById('volume-range');
  
  if (speedSlider) speedSlider.value = p.rate;
  if (pitchSlider) pitchSlider.value = p.pitch;
  if (volumeSlider) volumeSlider.value = p.volume;
  
  // Call updateSlider from global app.js context to sync filled track & values
  if (typeof updateSlider === 'function') {
    updateSlider('speed');
    updateSlider('pitch');
    updateSlider('volume');
  }
  
  // Update UI selection classes
  document.querySelectorAll('.preset-card').forEach(c => c.classList.remove('active'));
  const activeCard = document.getElementById(`preset-${key}`);
  if (activeCard) activeCard.classList.add('active');
  
  // Sync to localStorage
  localStorage.setItem('vf-selected-preset', key);
}

/**
 * Removes active visual state from preset buttons.
 * Called when a user manually modifies any setting slider.
 */
function clearPresetSelection() {
  document.querySelectorAll('.preset-card').forEach(c => c.classList.remove('active'));
  localStorage.removeItem('vf-selected-preset');
}

/**
 * Automatically restores the last preset selected by the user.
 */
function restorePreset() {
  const saved = localStorage.getItem('vf-selected-preset');
  if (saved && PRESETS[saved]) {
    selectPreset(saved);
  }
}
