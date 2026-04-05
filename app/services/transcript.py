"""
Service for extracting transcripts from YouTube videos.
"""
from youtube_transcript_api import YouTubeTranscriptApi
from typing import List, Dict
import re


def extract_video_id(url: str) -> str:
    """
    Extract video ID from various YouTube URL formats.
    
    Supports:
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/watch?v=VIDEO_ID
    - Just VIDEO_ID
    """
    # If it's already just an ID
    if len(url) == 11 and url.isalnum():
        return url
    
    # Match youtu.be format
    youtu_match = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', url)
    if youtu_match:
        return youtu_match.group(1)
    
    # Match youtube.com format
    yt_match = re.search(r'v=([a-zA-Z0-9_-]{11})', url)
    if yt_match:
        return yt_match.group(1)
    
    raise ValueError(f"Could not extract video ID from URL: {url}")


def get_transcript(video_url: str, language: str = 'en') -> str:
    """
    Fetch transcript from YouTube video.
    
    Args:
        video_url: YouTube URL or video ID
        language: Language code (default: 'en' for English)
    
    Returns:
        Full transcript as concatenated string
    
    Raises:
        ValueError: If video ID cannot be extracted or transcript unavailable
    """
    video_id = extract_video_id(video_url)
    
    try:
        # Create API instance and fetch transcript
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, languages=[language])
    except Exception as e:
        # Fallback to available transcript if specific language unavailable
        try:
            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id)
        except Exception as fallback_e:
            raise ValueError(f"Could not fetch transcript for video {video_id}: {str(fallback_e)}")
    
    # Concatenate all text from transcript snippets
    full_text = ' '.join([snippet.text for snippet in transcript.snippets])
    
    return full_text


def get_transcript_with_timestamps(video_url: str, language: str = 'en') -> List[Dict]:
    """
    Fetch transcript with timestamps preserved.
    
    Args:
        video_url: YouTube URL or video ID
        language: Language code (default: 'en' for English)
    
    Returns:
        List of dicts with 'text' and 'timestamp' keys
    """
    video_id = extract_video_id(video_url)
    
    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, languages=[language])
    except Exception as e:
        try:
            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id)
        except Exception as fallback_e:
            raise ValueError(f"Could not fetch transcript for video {video_id}: {str(fallback_e)}")
    
    return [
        {
            'text': snippet.text,
            'timestamp': snippet.start
        }
        for snippet in transcript.snippets
    ]
