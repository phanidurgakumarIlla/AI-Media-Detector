import sys
import os
import asyncio
import json

# Add backend to path
sys.path.append('f:/Exp  AI Dect/backend')
import ml_engine

async def verify_100_percent(dir_path):
    print(f"VERIFYING 100% ACCURACY ON: {dir_path}")
    failed = []
    passed = 0
    
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        
        # Analyze using the LIVE engine
        result = await ml_engine.analyze_media(file_path, source=filename)
        
        if result["isFake"]:
            print(f"  [PASS] {filename[:30]}... -> AI (Score: {result['aiProbability']:.2f})")
            passed += 1
        else:
            print(f"  [FAIL] {filename[:30]}... -> REAL! (Accuracy Breach)")
            failed.append(filename)
            
    print(f"\nFINAL STATUS: {passed}/{passed+len(failed)} AI SPECIMENS CORRECTLY DETECTED")
    if not failed:
        print("🏆 100% ACCURACY ACHIEVED ON USER DATASET")
    else:
        print(f"❌ ACCURACY BREACH ON: {failed}")

if __name__ == "__main__":
    asyncio.run(verify_100_percent('f:/Exp  AI Dect/Sample Data/AI'))
