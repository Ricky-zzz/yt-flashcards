"""
Service for chunking text into optimal segments for Q&A generation.
Balances chunk size with semantic coherence.
"""
from typing import List
import re


def chunk_by_word_count(text: str, 
                        chunk_size: int = 300, 
                        overlap: int = 50) -> List[str]:
    """
    Split text into chunks of approximately chunk_size words.
    Uses overlap to maintain context between chunks.
    
    Args:
        text: Input text to chunk
        chunk_size: Target number of words per chunk (default: 300)
        overlap: Number of words to overlap between chunks (default: 50)
    
    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []
    
    i = 0
    while i < len(words):
        # Take chunk_size words, or remaining words if at end
        chunk_end = min(i + chunk_size, len(words))
        chunk_words = words[i:chunk_end]
        chunk = ' '.join(chunk_words)
        
        chunks.append(chunk)
        
        # Move forward by (chunk_size - overlap) to create overlap
        i += chunk_size - overlap
    
    return chunks


def chunk_by_sentences(text: str,
                       target_chunk_size: int = 300,
                       min_chunk_size: int = 100) -> List[str]:
    """
    Split text into chunks by sentences, trying to reach target_chunk_size words.
    Better for preserving sentence structure.
    
    Args:
        text: Input text to chunk
        target_chunk_size: Aim for approximately this many words per chunk
        min_chunk_size: Minimum words before creating a new chunk
    
    Returns:
        List of text chunks
    """
    # Split by sentence boundaries (., !, ?)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for sentence in sentences:
        sentence_word_count = len(sentence.split())
        
        # If adding this sentence exceeds target, start new chunk
        if (current_word_count + sentence_word_count > target_chunk_size and 
            current_word_count > min_chunk_size):
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_word_count = sentence_word_count
        else:
            current_chunk.append(sentence)
            current_word_count += sentence_word_count
    
    # Add remaining chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks


def chunk_with_metadata(text: str,
                        chunk_size: int = 300,
                        overlap: int = 50) -> List[dict]:
    """
    Chunk text and return with metadata (start position, word count).
    
    Args:
        text: Input text to chunk
        chunk_size: Target words per chunk
        overlap: Word overlap between chunks
    
    Returns:
        List of dicts with 'text', 'word_count', and 'start_position' keys
    """
    words = text.split()
    chunks = []
    
    i = 0
    position = 0
    
    while i < len(words):
        chunk_end = min(i + chunk_size, len(words))
        chunk_words = words[i:chunk_end]
        chunk_text = ' '.join(chunk_words)
        
        chunks.append({
            'text': chunk_text,
            'word_count': len(chunk_words),
            'start_position': position,
            'chunk_index': len(chunks)
        })
        
        position += len(chunk_words)
        i += chunk_size - overlap
    
    return chunks


def validate_chunks(chunks: List[str], 
                    min_word_count: int = 50) -> List[str]:
    """
    Filter out chunks that are too small (likely noise).
    
    Args:
        chunks: List of text chunks
        min_word_count: Minimum words to keep a chunk
    
    Returns:
        Filtered list of chunks
    """
    return [chunk for chunk in chunks if len(chunk.split()) >= min_word_count]


def smart_chunk(text: str, 
                chunk_size: int = 300,
                overlap: int = 50,
                min_chunk_words: int = 50) -> List[str]:
    """
    Main chunking pipeline. Combines sentence-aware and word-count strategies.
    
    Args:
        text: Input text
        chunk_size: Target words per chunk
        overlap: Word overlap between chunks
        min_chunk_words: Minimum words to keep a chunk
    
    Returns:
        List of validated chunks
    """
    # Use sentence-aware chunking for better structure
    chunks = chunk_by_sentences(text, target_chunk_size=chunk_size)
    
    # Validate and filter small chunks
    chunks = validate_chunks(chunks, min_word_count=min_chunk_words)
    
    return chunks
