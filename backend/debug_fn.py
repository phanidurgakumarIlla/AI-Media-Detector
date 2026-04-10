import asyncio
import os
from scraper import get_video_metadata
from ml_engine import analyze_media

async def main():
    url = "https://www.instagram.com/reel/DWdlp3qkUDW/"
    print(f"DEBUGGING AI False Negative: {url}")
    
    # 1. Scrape Metadata
    meta = await get_video_metadata(url)
    print(f"\n[META] Title: {meta.get('title')}")
    print(f"[META] Description: {meta.get('description')}")
    print(f"[META] Thumbnail: {meta.get('thumbnail')[:60]}...")
    
    # 2. Analyze Media
    source_text = f"{meta.get('title', '')} {meta.get('description', '')}"
    result = await analyze_media("url_source.mp4", source=source_text, thumbnail_url=metadata.get('thumbnail', ''))
    
    print("\n[RESULT] Verdict:", "AI" if result["isFake"] else "REAL")
    print(f"[RESULT] Probability: {result['aiProbability']:.4f}")
    print(f"[RESULT] Algorithm: {result['algorithmUsed']}")
    print(f"[RESULT] Details: {result['details']}")

if __name__ == "__main__":
    asyncio.run(main())
