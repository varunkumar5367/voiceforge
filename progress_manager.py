#!/usr/bin/env python3
"""
VoiceForge — progress_manager.py
Maintains global metrics and progress tracking statistics for synthesis jobs.
"""

import time

class ProgressTracker:
    def __init__(self):
        self.total_characters = 0
        self.total_chunks = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_generation_time = 0.0

    def record_generation(self, character_count, duration, is_cache_hit):
        """
        Records a single synthesis event.
        
        Args:
            character_count (int): Length of synthesized text chunk.
            duration (float): Seconds taken to generate (if cache miss).
            is_cache_hit (bool): Whether segment was served from cache.
        """
        self.total_characters += character_count
        self.total_chunks += 1
        if is_cache_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
            self.total_generation_time += duration

    def get_stats(self):
        """
        Returns a compiled dictionary of generation metrics.
        """
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = 0.0
        if total_requests > 0:
            hit_rate = (self.cache_hits / total_requests) * 100.0
            
        avg_time_per_char = 0.0
        if self.total_characters > 0 and self.total_generation_time > 0:
            avg_time_per_char = self.total_generation_time / self.total_characters
            
        return {
            "total_characters": self.total_characters,
            "total_chunks_processed": self.total_chunks,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate_pct": round(hit_rate, 2),
            "total_generation_time_sec": round(self.total_generation_time, 2),
            "avg_time_per_char_ms": round(avg_time_per_char * 1000, 4)
        }

# Global backend progress metrics instance
tracker = ProgressTracker()
