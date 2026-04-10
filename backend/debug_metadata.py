import sys
import os
import asyncio
from scraper import get_video_metadata

async def debug_metadata():
    url = "https://www.instagram.com/reel/DVgRUJFGK2Z/"
    metadata = await get_video_metadata(url)
    print("METADATA EXTRACTED:")
    print(metadata)

if __name__ == "__main__":
    asyncio.run(debug_metadata())
