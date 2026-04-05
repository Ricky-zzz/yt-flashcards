"""
Service for cleaning and preprocessing transcript text.
Removes noise, normalizes spacing, and prepares text for chunking.
"""
import re
from typing import List


def clean_text(text: str) -> str:
    """
    Clean transcript text by removing common YouTube caption artifacts.
    
    Operations:
    - Remove [Music], [Applause], [Laughter] and similar tags
    - Remove multiple consecutive spaces/newlines
    - Strip leading/trailing whitespace
    - Normalize punctuation spacing
    
    Args:
        text: Raw transcript text
    
    Returns:
        Cleaned text
    """
    # Remove bracketed annotations (music, applause, etc)
    text = re.sub(r'\[.*?\]', '', text)
    
    # Remove multiple consecutive spaces
    text = re.sub(r' +', ' ', text)
    
    # Remove multiple consecutive newlines
    text = re.sub(r'\n+', ' ', text)
    
    # Normalize space before punctuation
    text = re.sub(r' +([.!?,;:])', r'\1', text)
    
    # Add space after punctuation if missing (except for ellipsis)
    text = re.sub(r'([.!?,;:])([A-Z])', r'\1 \2', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def remove_duplicates(text: str, threshold: float = 0.8) -> str:
    """
    Remove or reduce heavily repeated sentences/phrases.
    Useful for auto-generated captions with repetition.
    
    Args:
        text: Input text
        threshold: Similarity threshold (0-1) for removing duplicates (0.8 = 80% similar)
    
    Returns:
        Text with reduced repetition
    """
    sentences = text.split('. ')
    unique_sentences = []
    
    for sentence in sentences:
        # Simple check: if sentence is very similar to previous one, skip it
        if unique_sentences:
            # Calculate basic similarity (same length, starts same way)
            if (len(sentence) > 20 and 
                sentence[:10].lower() == unique_sentences[-1][:10].lower()):
                continue
        
        unique_sentences.append(sentence)
    
    return '. '.join(unique_sentences)


def normalize_whitespace(text: str) -> str:
    """
    Normalize all types of whitespace (tabs, multiple spaces, etc).
    
    Args:
        text: Input text
    
    Returns:
        Text with normalized whitespace
    """
    # Replace tabs with spaces
    text = text.replace('\t', ' ')
    
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    
    return text.strip()


def preprocess_for_chunking(text: str) -> str:
    """
    Main preprocessing pipeline. Combines all cleaning steps.
    
    Args:
        text: Raw transcript text
    
    Returns:
        Cleaned, normalized text ready for chunking
    """
    text = clean_text(text)
    text = normalize_whitespace(text)
    text = remove_duplicates(text)
    text = normalize_whitespace(text)  # Final pass
    
    return text
