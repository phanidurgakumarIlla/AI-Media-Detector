import asyncio
import time
from scraper import get_video_metadata
import yt_dlp

async def test_reel(url):
    print(f"Testing Reel: {url}")
    start = time.time()
    try:
        # Test standard scraper
        metadata = await get_video_metadata(url)
        print(f"Metadata Success: {metadata['title'][:50]}")
    except Exception as e:
        print(f"Scraper Failed: {e}")
    
    print(f"Time Taken: {time.time() - start:.2f}s")

if __name__ == "__main__":
    asyncio.run(test_reel("https://www.instagram.com/reel/DWdlp3qkU/"))
