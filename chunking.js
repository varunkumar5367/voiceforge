/* ═══════════════════════════════════════════════════
   VoiceForge — chunking.js
   Manages chunk tasks and handles sequential generation, progress reporting,
   failed-chunk retries, and compilation metrics.
   ═══════════════════════════════════════════════════ */

class ChunkTask {
  constructor(id, text) {
    this.id = id;
    this.text = text;
    this.status = 'Pending'; // Pending | Processing | Completed | Failed
    this.attempts = 0;
    this.audioBlob = null;
    this.duration = 0.0; // In seconds
  }
}

class ChunkProcessor {
  constructor(chunks, voiceId, params, onProgress) {
    this.tasks = chunks.map((text, idx) => new ChunkTask(idx, text));
    this.voiceId = voiceId;
    this.params = params;
    this.onProgress = onProgress;
    this.isAborted = false;
    
    // Performance Metrics
    this.metrics = {
      characterCount: chunks.reduce((sum, text) => sum + text.length, 0),
      chunkCount: chunks.length,
      generationDuration: 0.0,
      avgProcessingTime: 0.0,
      audioDurationEstimate: 0.0,
      startTime: null,
      endTime: null
    };
  }

  abort() {
    this.isAborted = true;
  }

  async process() {
    this.metrics.startTime = performance.now();
    
    for (let i = 0; i < this.tasks.length; i++) {
      if (this.isAborted) {
        throw new Error('Generation cancelled by user.');
      }
      
      const task = this.tasks[i];
      task.status = 'Processing';
      task.attempts++;
      this.onProgress(this.getProgressStats(), task);
      
      const startChunkTime = performance.now();
      let success = false;
      let blob = null;
      
      // Build GET TTS URL with current chunk parameters
      const url = `/tts?voice=${encodeURIComponent(this.voiceId)}` +
                  `&text=${encodeURIComponent(task.text)}` +
                  `&rate=${encodeURIComponent(this.params.rate)}` +
                  `&pitch=${encodeURIComponent(this.params.pitch)}` +
                  `&volume=${encodeURIComponent(this.params.volume)}`;

      // First Attempt
      try {
        blob = await this.fetchAudioChunk(url);
        success = true;
      } catch (err) {
        console.warn(`[ChunkProcessor] Chunk ${task.id + 1} first attempt failed:`, err);
        
        // Retry Once
        if (task.attempts < 2) {
          task.status = 'Retrying';
          task.attempts++;
          this.onProgress(this.getProgressStats(), task);
          
          // Small delay before retry
          await new Promise(resolve => setTimeout(resolve, 1200));
          
          try {
            blob = await this.fetchAudioChunk(url);
            success = true;
            console.log(`[ChunkProcessor] Chunk ${task.id + 1} retry succeeded.`);
          } catch (retryErr) {
            console.error(`[ChunkProcessor] Chunk ${task.id + 1} retry failed:`, retryErr);
          }
        }
      }

      task.duration = (performance.now() - startChunkTime) / 1000.0;
      
      if (success && blob) {
        task.status = 'Completed';
        task.audioBlob = blob;
      } else {
        task.status = 'Failed';
        this.onProgress(this.getProgressStats(), task);
        throw new Error(`Failed to generate audio for chunk ${task.id + 1} after retry.`);
      }
      
      this.onProgress(this.getProgressStats(), task);
    }
    
    this.metrics.endTime = performance.now();
    this.calculateMetrics();
    return this.stitchAudio();
  }

  async fetchAudioChunk(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP Error ${res.status}`);
    const blob = await res.blob();
    if (blob.size < 50) throw new Error('Returned empty audio blob');
    return blob;
  }

  getProgressStats() {
    const completed = this.tasks.filter(t => t.status === 'Completed').length;
    const failed = this.tasks.filter(t => t.status === 'Failed').length;
    const pct = Math.round((completed / this.tasks.length) * 100);
    
    return {
      completed,
      failed,
      total: this.tasks.length,
      pct
    };
  }

  calculateMetrics() {
    const durationMs = this.metrics.endTime - this.metrics.startTime;
    this.metrics.generationDuration = durationMs / 1000.0;
    
    const completedTasks = this.tasks.filter(t => t.status === 'Completed');
    if (completedTasks.length > 0) {
      const sumDurations = completedTasks.reduce((sum, t) => sum + t.duration, 0);
      this.metrics.avgProcessingTime = sumDurations / completedTasks.length;
    }
    
    // Estimate audio length: average speech is ~150 words/min (roughly 1000 characters).
    // This gives 0.04s per character. Speed rate increases or decreases this duration.
    let speedPct = parseFloat(this.params.rate.replace('%', '')) || 0.0;
    let speedMultiplier = 1.0 + (speedPct / 100.0);
    if (speedMultiplier <= 0) speedMultiplier = 0.1; // Guard against division/multiplication by 0
    
    this.metrics.audioDurationEstimate = (this.metrics.characterCount * 0.045) / speedMultiplier;
  }

  stitchAudio() {
    // Collect blobs in correct sequence
    const blobs = this.tasks
      .filter(t => t.status === 'Completed')
      .map(t => t.audioBlob);
    return new Blob(blobs, { type: 'audio/mpeg' });
  }
}
