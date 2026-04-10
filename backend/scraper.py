import yt_dlp
import uuid
import os
import asyncio
import aiohttp
import diskcache

# Cache for URL metadata to speed up repeat scans (Phase 41)
_scraper_cache_dir = os.path.join(os.path.dirname(__file__), ".scraper_cache")
_metadata_cache = diskcache.Cache(_scraper_cache_dir)

class MyLogger(object):
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

async def _fast_thumbnail_download(thumb_url: str, timeout_sec: int = 5) -> str:
    """Download thumbnail to a temp file super fast with a hard timeout."""
    if not thumb_url:
        return ""
    try:
        timeout = aiohttp.ClientTimeout(total=timeout_sec)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(thumb_url) as resp:
                if resp.status == 200:
                    path = f"uploads/thumb_{uuid.uuid4().hex[:8]}.jpg"
                    if not os.path.exists("uploads"): os.makedirs("uploads")
                    with open(path, 'wb') as f:
                        f.write(await resp.read())
                    return path
    except Exception:
        pass
    return ""

async def get_video_metadata(url: str) -> dict:
    """
    Extracts metadata from a URL extremely quickly without downloading video.
    Optimized with socket timeout and flat extraction for Instagram speed.
    """
    if url in _metadata_cache:
        print(f"SCRAPER CACHE HIT [0ms]: Returning cached metadata for {url[:50]}...")
        return _metadata_cache[url]

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,
        'logger': MyLogger(),
        'skip_download': True,
        'format': 'best',
        'extract_flat': True,
        'lazy_playlist': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'max_downloads': 1,
        'no_color': True,
        'socket_timeout': 5,
        'retries': 1,
        'fragment_retries': 0,
        'extractor_retries': 1,
    }
    
    def _extract():
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception:
            return None
    
    # Hard 6-second timeout on the entire extraction (Flash Speed)
    try:
        info = await asyncio.wait_for(asyncio.to_thread(_extract), timeout=6.0)
    except asyncio.TimeoutError:
        print("Scraper: Timeout after 6s, using fallback metadata")
        info = None
    
    if not info:
        return {
            "title": "Social Media Video",
            "description": "Video extracted from url",
            "tags": [],
            "url": url,
            "thumbnail": ""
        }
        
    def _safe(text):
        if not text: return ""
        try:
            return str(text).encode('ascii', 'ignore').decode('ascii')
        except:
            return ""
            
    result = {
        "title": _safe(info.get('title', '')),
        "description": _safe(info.get('description', '')),
        "tags": [_safe(t) for t in info.get('tags', [])],
        "uploader": _safe(info.get('uploader', info.get('channel', ''))),
        "url": _safe(url),
        "thumbnail": _safe(info.get('thumbnail', ''))
    }
    
    _metadata_cache.set(url, result, expire=86400) # 24hr cache
    return result
