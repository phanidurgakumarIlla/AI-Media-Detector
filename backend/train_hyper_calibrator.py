import sys
import os
import cv2
import numpy as np
import sys
import io

# Fix encoding for Windows console (Phase 6 Unicode Patch)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend to path for importing forensic modules
sys.path.append('f:/Exp  AI Dect/backend')
import ml_engine

def analyze_dataset(dir_path):
    print(f"ANALYZING DATASET: {dir_path}")
    results = {}
    
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        ext = os.path.splitext(filename)[1].lower()
        
        try:
            if ext in ['.jpg', '.jpeg', '.png', '.jfif', '.webp', '.avif']:
                img = cv2.imread(file_path)
                if img is not None:
                    lattice = ml_engine._analyze_diffusion_lattice(img)
                    fidelity = ml_engine._analyze_noise_fidelity(img)
                    results[filename] = {"type": "image", "lattice": lattice, "fidelity": fidelity}
            
            elif ext in ['.mp3', '.wav']:
                gap = ml_engine._analyze_audio_gaps(file_path)
                results[filename] = {"type": "audio", "gap": gap}
                
            elif ext in ['.mp4', '.avi']:
                cap = cv2.VideoCapture(file_path)
                frames = []
                for _ in range(10):
                    ret, frame = cap.read()
                    if ret: frames.append(frame)
                cap.release()
                jitter = ml_engine._analyze_static_jitter(frames)
                results[filename] = {"type": "video", "jitter": jitter}
        except Exception as e:
            results[filename] = {"error": str(e)}

    import json
    with open('backend/signatures.json', 'w') as f:
        json.dump(results, f, indent=4)
    print("Signatures saved to backend/signatures.json")

if __name__ == "__main__":
    analyze_dataset('f:/Exp  AI Dect/Sample Data/Web')
