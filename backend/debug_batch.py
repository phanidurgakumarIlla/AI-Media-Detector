import asyncio
from scraper import get_video_metadata
from ml_engine import analyze_media

async def debug_batch():
    urls = [
        "https://www.instagram.com/reel/DWF_pBaD2Sp/",
        "https://www.instagram.com/reel/DVkRjrEieUK/" # AI Influencer
    ]
    for url in urls:
        print(f"\n--- DEBUGGING URL: {url} ---")
        meta = await get_video_metadata(url)
        print(f"Title: {meta.get('title')}")
        print(f"Desc: {meta.get('description')[:100]}...")
        
        source_text = f"{meta.get('title', '')} {meta.get('description', '')}"
        result = await analyze_media("url_source.mp4", source=source_text, thumbnail_url=meta.get('thumbnail', ''))
        
        print(f"RESULT: {'AI' if result['isFake'] else 'REAL'} (Score: {result['aiProbability']:.4f})")
        print(f"ALGO: {result['algorithmUsed']}")
        print(f"HINTS: {'divyanshii' in source_text.lower()}, {'influencer' in source_text.lower()}")

if __name__ == "__main__":
    asyncio.run(debug_batch())
