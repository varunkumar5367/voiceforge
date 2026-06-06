#!/usr/bin/env python3
"""
VoiceForge — chunker.py
Intelligently splits long text/scripts into manageable chunks under a specified character limit.
Prioritizes natural boundaries:
1. Paragraph breaks (\n\n, \n)
2. Sentence endings (.!? followed by whitespace)
3. Punctuation breaks (,;: - followed by whitespace)
4. Spaces / word boundaries
5. Character limits (hard slice as a fallback)
"""

import re

def split_text_into_chunks(text, max_chars=2500):
    """
    Intelligently splits a long text document into smaller text chunks, each with a
    maximum character length of `max_chars`.
    
    Returns:
        List of text chunks (strings).
    """
    text = (text or "").strip()
    if not text:
        return []
        
    if len(text) <= max_chars:
        return [text]
        
    chunks = []
    remaining = text
    
    while remaining:
        remaining = remaining.strip()
        if not remaining:
            break
            
        if len(remaining) <= max_chars:
            chunks.append(remaining)
            break
            
        # Get the slice we have to split within
        candidate = remaining[:max_chars]
        
        # 1. Try Paragraph Breaks (from right to left)
        split_idx = -1
        for p_break in ['\n\n', '\r\n\r\n', '\n']:
            idx = candidate.rfind(p_break)
            if idx != -1:
                # Split right after the paragraph break
                split_idx = max(split_idx, idx + len(p_break))
                
        if split_idx > 0:
            chunks.append(remaining[:split_idx].strip())
            remaining = remaining[split_idx:]
            continue
            
        # 2. Try Sentence Endings: . ! ? followed by space or end of string
        sentence_endings = list(re.finditer(r'[.!?](\s+|$)', candidate))
        if sentence_endings:
            split_idx = sentence_endings[-1].end()
            chunks.append(remaining[:split_idx].strip())
            remaining = remaining[split_idx:]
            continue
            
        # 3. Try Punctuation: , ; : - followed by space or end of string
        punctuation_breaks = list(re.finditer(r'[,;:-](\s+|$)', candidate))
        if punctuation_breaks:
            split_idx = punctuation_breaks[-1].end()
            chunks.append(remaining[:split_idx].strip())
            remaining = remaining[split_idx:]
            continue
            
        # 4. Try Word Boundaries: spaces
        space_breaks = list(re.finditer(r'\s+', candidate))
        if space_breaks:
            split_idx = space_breaks[-1].end()
            chunks.append(remaining[:split_idx].strip())
            remaining = remaining[split_idx:]
            continue
            
        # 5. Last Resort: Force slice at max_chars
        split_idx = max_chars
        chunks.append(remaining[:split_idx].strip())
        remaining = remaining[split_idx:]
        
    return [c for c in chunks if c]
