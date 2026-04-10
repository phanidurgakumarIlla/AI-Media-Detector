import sys
import os
import asyncio
import json

# Add backend to path
sys.path.append('f:/Exp  AI Dect/backend')
import ml_engine

async def debug_single_file(file_path):
    print(f"DEBUGGING FORENSICS FOR: {file_path}")
    result = await ml_engine.analyze_media(file_path, source=os.path.basename(file_path))
    print(f"\nFINAL RESULT: {json.dumps(result, indent=4)}")

if __name__ == "__main__":
    asyncio.run(debug_single_file('f:/Exp  AI Dect/Sample Data/AI/download.jfif'))
