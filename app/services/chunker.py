"""
Service for chunking YouTube transcript text into segments for Q&A generation.

KEY INSIGHT: YouTube auto-captions have NO punctuation, so sentence-based
chunking never splits. We use word-count chunking with overlap instead.
Gemini handles semantic understanding — we just need reasonably sized windows.
"""
from typing import List


# Tuned for Gemini Flash context window and flashcard quality.
# ~600 words ≈ ~2-3 minutes of speech — enough context per chunk.
DEFAULT_CHUNK_SIZE = 600
DEFAULT_OVERLAP = 75       # ~12% overlap keeps context across boundaries
MIN_CHUNK_WORDS = 80       # Drop tiny trailing chunks (not enough to make cards from)


def chunk_by_word_count(text: str,
                        chunk_size: int = DEFAULT_CHUNK_SIZE,
                        overlap: int = DEFAULT_OVERLAP) -> List[str]:
    """
    Split text into overlapping word-count windows.

    Args:
        text: Cleaned transcript text
        chunk_size: Target words per chunk
        overlap: Words shared between consecutive chunks

    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []
    step = chunk_size - overlap

    for i in range(0, len(words), step):
        chunk_words = words[i: i + chunk_size]
        chunks.append(' '.join(chunk_words))

    return chunks


def validate_chunks(chunks: List[str],
                    min_word_count: int = MIN_CHUNK_WORDS) -> List[str]:
    """Drop chunks too small to generate meaningful flashcards from."""
    return [c for c in chunks if len(c.split()) >= min_word_count]


def smart_chunk(text: str,
                chunk_size: int = DEFAULT_CHUNK_SIZE,
                overlap: int = DEFAULT_OVERLAP,
                min_chunk_words: int = MIN_CHUNK_WORDS) -> List[str]:
    """
    Main chunking entry point.

    Args:
        text: Cleaned transcript text
        chunk_size: Target words per chunk
        overlap: Word overlap between chunks
        min_chunk_words: Minimum words to keep a chunk

    Returns:
        List of validated text chunks
    """
    chunks = chunk_by_word_count(text, chunk_size=chunk_size, overlap=overlap)
    chunks = validate_chunks(chunks, min_word_count=min_chunk_words)
    return chunks