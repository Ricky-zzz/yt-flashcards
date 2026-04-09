"""
Service for extracting transcripts from YouTube videos.
"""
import re
from typing import List, Dict

from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> str:
    """
    Extract video ID from various YouTube URL formats.

    Supports:
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://www.youtube.com/shorts/VIDEO_ID
    - Raw VIDEO_ID (11 chars)
    """
    url = url.strip()

    # Already a bare ID
    if re.fullmatch(r'[a-zA-Z0-9_-]{11}', url):
        return url

    for pattern in [
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'v=([a-zA-Z0-9_-]{11})',
        r'shorts/([a-zA-Z0-9_-]{11})',
    ]:
        m = re.search(pattern, url)
        if m:
            return m.group(1)

    raise ValueError(f"Could not extract video ID from: {url}")


def get_transcript(video_url: str, language: str = 'en') -> str:
    """
    Fetch full transcript from a YouTube video as a plain string.

    Args:
        video_url: YouTube URL or video ID
        language: Preferred language code (default: 'en')

    Returns:
        Full transcript as a single concatenated string

    Raises:
        ValueError: If transcript cannot be fetched
    """
    video_id = extract_video_id(video_url)
    api = YouTubeTranscriptApi()

    try:
        transcript = api.fetch(video_id, languages=[language])
    except Exception:
        try:
            # Fallback: accept any available language
            transcript = api.fetch(video_id)
        except Exception as e:
            raise ValueError(
                f"Could not fetch transcript for video '{video_id}': {e}\n"
                "The video may have no captions, or captions may be disabled."
            )

    return ' '.join(snippet.text for snippet in transcript.snippets)


def get_transcript_with_timestamps(video_url: str, language: str = 'en') -> List[Dict]:
    """
    Fetch transcript with per-snippet timestamps.

    Args:
        video_url: YouTube URL or video ID
        language: Preferred language code (default: 'en')

    Returns:
        List of {'text': str, 'timestamp': float} dicts
    """
    video_id = extract_video_id(video_url)
    api = YouTubeTranscriptApi()

    try:
        transcript = api.fetch(video_id, languages=[language])
    except Exception:
        try:
            transcript = api.fetch(video_id)
        except Exception as e:
            raise ValueError(
                f"Could not fetch transcript for video '{video_id}': {e}"
            )

    return [
        {'text': snippet.text, 'timestamp': snippet.start}
        for snippet in transcript.snippets
    ]


# Alias for consistency
def extract_transcript(url: str, language: str = 'en') -> str:
    """
    Alias for get_transcript for consistency with pipeline.
    
    Args:
        url: YouTube URL or video ID
        language: Preferred language code (default: 'en')
        
    Returns:
        Full transcript as a single concatenated string
    """
    return get_transcript(url, language)


def get_video_title(video_url: str) -> str:
    """
    Extract video title from YouTube video.
    
    Try to use yt-dlp if available, otherwise return a generic title.
    
    Args:
        video_url: YouTube URL or video ID
        
    Returns:
        Video title or default string if extraction fails
    """
    try:
        import yt_dlp
        
        with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return info.get('title', 'Untitled Video')
    except Exception:
        # Fallback: try to extract from BeautifulSoup if available
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # Extract video ID
            video_id = extract_video_id(video_url)
            
            # Use youtube.com embed metadata
            embed_url = f"https://www.youtube.com/watch?v={video_id}"
            response = requests.get(embed_url, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title_tag = soup.find('meta', {'name': 'title'})
            if title_tag:
                return title_tag.get('content', 'Untitled Video')
        except Exception:
            pass
        
        # Final fallback
        return 'Untitled Video'