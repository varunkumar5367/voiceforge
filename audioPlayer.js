/* ═══════════════════════════════════════════════════
   VoiceForge — audioPlayer.js
   Manages generation metrics calculation and displays them in a beautiful collapsible UI.
   ═══════════════════════════════════════════════════ */

/**
 * Renders generation performance stats in a details element.
 */
function displayGenerationStats(metrics, voiceId) {
  const v = VOICE_DATA.find(x => x.id === voiceId);
  const voiceLabel = v ? `${v.flag} ${v.name} (${v.accent})` : voiceId;
  
  let statsContainer = document.getElementById('generation-stats-container');
  if (!statsContainer) {
    statsContainer = document.createElement('div');
    statsContainer.id = 'generation-stats-container';
    statsContainer.className = 'stats-accordion';
    
    const audioReady = document.getElementById('audio-ready');
    const actionsRow = audioReady.querySelector('.player-actions');
    audioReady.insertBefore(statsContainer, actionsRow);
  }
  
  statsContainer.innerHTML = `
    <details class="stats-details">
      <summary class="stats-summary">
        <span>📊 Generation Statistics</span>
        <span class="stats-summary-arrow">▼</span>
      </summary>
      <div class="stats-content">
        <table class="stats-table">
          <tr>
            <td>Text Size</td>
            <td><strong>${metrics.characterCount.toLocaleString()} characters</strong></td>
          </tr>
          <tr>
            <td>Audio Chunks</td>
            <td><strong>${metrics.chunkCount} chunk${metrics.chunkCount !== 1 ? 's' : ''}</strong></td>
          </tr>
          <tr>
            <td>Generation Time</td>
            <td><strong>${metrics.generationDuration.toFixed(2)} seconds</strong></td>
          </tr>
          <tr>
            <td>Average Chunk Synthesis Time</td>
            <td><strong>${metrics.avgProcessingTime.toFixed(2)} seconds</strong></td>
          </tr>
          <tr>
            <td>Selected Narrator</td>
            <td><strong>${voiceLabel}</strong></td>
          </tr>
          <tr>
            <td>Estimated Audio Length</td>
            <td><strong>${formatAudioDuration(metrics.audioDurationEstimate)}</strong></td>
          </tr>
        </table>
      </div>
    </details>
  `;
}

/**
 * Formats duration seconds into readable time (m:ss).
 */
function formatAudioDuration(seconds) {
  if (isNaN(seconds) || seconds < 0) return '0:00';
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}
