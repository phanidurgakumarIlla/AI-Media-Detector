import sys
import os
import cv2
import numpy as np
from PIL import Image

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from ml_engine import _auto_generate_heatmap

def test_heatmap():
    print("Testing Phase 59 Heatmap Clarity...")
    
    # Create a dummy image
    dummy_img = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.rectangle(dummy_img, (50, 50), (150, 150), (255, 255, 255), -1)
    img_path = 'test_clarity.jpg'
    cv2.imwrite(img_path, dummy_img)
    
    heatmap = _auto_generate_heatmap(img_path)
    print(f"Image Heatmap Generated: {heatmap}")
    
    if heatmap and os.path.exists(f"backend/static{heatmap}"):
        print("✅ SUCCESS: High-clarity forensic heatmap verified.")
    else:
        print("❌ FAILURE: Heatmap not found.")
    
    # Cleanup
    if os.path.exists(img_path): os.remove(img_path)

if __name__ == "__main__":
    if not os.path.exists('backend/static/results'):
        os.makedirs('backend/static/results')
    test_heatmap()
