"""Service for extracting transcripts from YouTube videos."""
import html
import os
import re
import tempfile
from pathlib import Path
from typing import List, Dict, Optional

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
    cookies = _get_youtube_cookies()

    try:
        transcript = _get_transcript_with_cookies(api, video_id, [language], cookies)
    except Exception:
        try:
            # Fallback: accept any available language
            transcript = _get_transcript_with_cookies(api, video_id, None, cookies)
        except Exception as e:
            try:
                transcript = _fetch_any_transcript(video_id, language, cookies)
            except Exception as fallback_error:
                try:
                    transcript = _fetch_transcript_with_ytdlp(video_url, language)
                except Exception as ytdlp_error:
                    raise ValueError(
                        f"Could not fetch transcript for video '{video_id}': {e}\n"
                        f"Fallback failed: {fallback_error}\n"
                        f"yt-dlp fallback failed: {ytdlp_error}\n"
                        "The video may have no captions, or captions may be disabled."
                    )

    return ' '.join(snippet['text'] for snippet in transcript)


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
    cookies = _get_youtube_cookies()

    try:
        transcript = _get_transcript_with_cookies(api, video_id, [language], cookies)
    except Exception:
        try:
            transcript = _get_transcript_with_cookies(api, video_id, None, cookies)
        except Exception as e:
            try:
                transcript = _fetch_any_transcript(video_id, language, cookies)
            except Exception as fallback_error:
                try:
                    transcript = _fetch_transcript_with_ytdlp(video_url, language)
                except Exception as ytdlp_error:
                    raise ValueError(
                        f"Could not fetch transcript for video '{video_id}': {e}\n"
                        f"Fallback failed: {fallback_error}\n"
                        f"yt-dlp fallback failed: {ytdlp_error}"
                    )

    return [
        {'text': snippet['text'], 'timestamp': snippet['start']}
        for snippet in transcript
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


def _get_youtube_cookies() -> Optional[object]:
    try:
        import browser_cookie3
    except Exception:
        return None

    for loader in (browser_cookie3.chrome, browser_cookie3.chromium, browser_cookie3.firefox):
        try:
            return loader(domain_name=".youtube.com")
        except Exception:
            continue

    return None


def _get_transcript_with_cookies(
    api: YouTubeTranscriptApi,
    video_id: str,
    languages: Optional[List[str]],
    cookies: Optional[object]
) -> List[Dict]:
    kwargs = {}
    if languages is not None:
        kwargs["languages"] = languages

    if cookies is not None:
        try:
            return _normalize_entries(_call_fetch(api, video_id, cookies=cookies, **kwargs))
        except TypeError:
            pass

    return _normalize_entries(_call_fetch(api, video_id, **kwargs))


def _list_transcripts_with_cookies(api: YouTubeTranscriptApi, video_id: str, cookies: Optional[object]):
    if cookies is not None:
        try:
            return _call_list(api, video_id, cookies=cookies)
        except TypeError:
            pass

    return _call_list(api, video_id)


def _fetch_any_transcript(
    video_id: str,
    language: str,
    cookies: Optional[object]
) -> List[Dict]:
    api = YouTubeTranscriptApi()
    transcript_list = _list_transcripts_with_cookies(api, video_id, cookies)

    try:
        transcript = transcript_list.find_manually_created_transcript([language])
    except Exception:
        try:
            transcript = transcript_list.find_generated_transcript([language])
        except Exception:
            transcript = next(iter(transcript_list))

    return _normalize_entries(transcript.fetch())


def _call_fetch(api: YouTubeTranscriptApi, video_id: str, **kwargs):
    if hasattr(api, "fetch"):
        return api.fetch(video_id, **kwargs)
    if hasattr(api, "get_transcript"):
        return api.get_transcript(video_id, **kwargs)
    return YouTubeTranscriptApi.get_transcript(video_id, **kwargs)


def _call_list(api: YouTubeTranscriptApi, video_id: str, **kwargs):
    if hasattr(api, "list"):
        return api.list(video_id, **kwargs)
    if hasattr(api, "list_transcripts"):
        return api.list_transcripts(video_id, **kwargs)
    return YouTubeTranscriptApi.list_transcripts(video_id, **kwargs)


def _normalize_entries(entries) -> List[Dict]:
    normalized = []
    for snippet in entries:
        if isinstance(snippet, dict):
            text = snippet.get("text", "")
            start = snippet.get("start")
            if start is None:
                start = snippet.get("timestamp", 0.0)
        else:
            text = getattr(snippet, "text", "")
            start = getattr(snippet, "start", 0.0)

        normalized.append({"text": text, "start": start})

    return normalized


def _fetch_transcript_with_ytdlp(video_url: str, language: str) -> List[Dict]:
    try:
        import yt_dlp
    except Exception as exc:
        raise ValueError(f"yt-dlp not available: {exc}")

    with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts = {
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [language, 'en'],
            'subtitlesformat': 'vtt',
            'outtmpl': os.path.join(tmpdir, '%(id)s.%(ext)s')
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        vtt_files = list(Path(tmpdir).glob('*.vtt'))
        if not vtt_files:
            raise ValueError("yt-dlp wrote no subtitle files")

        subtitle_text = vtt_files[0].read_text(encoding='utf-8')

    entries = _parse_vtt(subtitle_text)
    if not entries:
        raise ValueError("Subtitle parsing returned no text")

    return entries


def _parse_vtt(text: str) -> List[Dict]:
    entries = []
    current_start = None
    buffer = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            if current_start is not None and buffer:
                entries.append(_make_entry(current_start, buffer))
            buffer = []
            current_start = None
            continue

        if line.startswith('WEBVTT'):
            continue
        if '-->' in line:
            if current_start is not None and buffer:
                entries.append(_make_entry(current_start, buffer))
                buffer = []
            current_start = _parse_timestamp(line.split('-->')[0].strip())
            continue
        if line.isdigit():
            continue

        buffer.append(line)

    if current_start is not None and buffer:
        entries.append(_make_entry(current_start, buffer))

    return entries


def _parse_srv1(text: str) -> List[Dict]:
    entries = []

    for start, raw in re.findall(r'<text start="([^"]+)"[^>]*>(.*?)</text>', text):
        cleaned = _clean_subtitle_text(raw)
        if cleaned:
            entries.append({'text': cleaned, 'start': float(start)})

    if entries:
        return entries

    for start, raw in re.findall(r'<p begin="([^"]+)"[^>]*>(.*?)</p>', text):
        cleaned = _clean_subtitle_text(raw)
        if cleaned:
            entries.append({'text': cleaned, 'start': _parse_timestamp(start)})

    return entries


def _parse_json3(text: str) -> List[Dict]:
    try:
        import json
    except Exception:
        return []

    try:
        data = json.loads(text)
    except Exception:
        return []

    entries = []
    for event in data.get('events', []):
        start = event.get('tStartMs')
        segs = event.get('segs') or []
        if start is None or not segs:
            continue
        text_chunk = ''.join(seg.get('utf8', '') for seg in segs).strip()
        if text_chunk:
            entries.append({'text': text_chunk, 'start': float(start) / 1000.0})

    return entries


def _parse_timestamp(value: str) -> float:
    value = value.replace(',', '.')
    parts = value.split(':')
    if len(parts) == 3:
        hours, minutes, seconds = parts
    elif len(parts) == 2:
        hours = '0'
        minutes, seconds = parts
    else:
        return 0.0

    try:
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    except ValueError:
        return 0.0


def _make_entry(start: float, lines: List[str]) -> Dict:
    text = _clean_subtitle_text(' '.join(lines))
    return {'text': text, 'start': start}


def _clean_subtitle_text(text: str) -> str:
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    return ' '.join(text.split()).strip()


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