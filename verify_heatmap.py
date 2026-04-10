import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from ml_engine import analyze_media

async def test():
    file_path = r"f:\Exp  AI Dect\backend\data\train\real\real_gsm_9.jpg"
    print(f"Testing Heatmap Generation on: {file_path}")
    result = await analyze_media(file_path)
    print(f"Analysis Result: {result}")
    
    if "heatmap_path" in result:
        print(f"Heatmap saved at: {result['heatmap_path']}")
    else:
        print("Heatmap generation failed or not returned.")

if __name__ == "__main__":
    asyncio.run(test())
