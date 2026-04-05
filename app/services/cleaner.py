"""
Service for cleaning and preprocessing YouTube transcript text.
YouTube auto-captions are lowercase, unpunctuated, and noisy.
This cleaner handles those specific artifacts.
"""
import re


def clean_text(text: str) -> str:
    """
    Clean raw YouTube transcript text.

    YouTube auto-captions:
    - Are fully lowercase with no punctuation
    - Contain [Music], [Applause] tags
    - Have filler words (um, uh, like)
    - Have broken words across lines

    Args:
        text: Raw transcript text

    Returns:
        Cleaned text
    """
    # Remove bracketed annotations [Music], [Applause], etc.
    text = re.sub(r'\[.*?\]', '', text)

    # Remove filler words (common in auto-captions)
    fillers = r'\b(um+|uh+|hmm+|like i said|you know|i mean|sort of|kind of|basically)\b'
    text = re.sub(fillers, '', text, flags=re.IGNORECASE)

    # Collapse multiple spaces/newlines into single space
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def preprocess_for_chunking(text: str) -> str:
    """
    Main preprocessing pipeline for YouTube transcripts.
    Keeps text mostly raw — Gemini handles understanding,
    we just remove noise.

    Args:
        text: Raw transcript text

    Returns:
        Cleaned text ready for chunking
    """
    return clean_text(text)