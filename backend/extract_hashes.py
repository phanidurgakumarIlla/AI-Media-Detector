import hashlib
import os
import json

def get_hashes(dir_path):
    results = {}
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        if os.path.isfile(file_path):
            with open(file_path, "rb") as f:
                # Hash only the first 512KB to match ml_engine.py!
                h = hashlib.sha256(f.read(524288)).hexdigest()
                results[h] = filename
    
    with open('backend/training_hashes.json', 'w') as f:
        json.dump(results, f, indent=4)
    print("Hashes saved to backend/training_hashes.json")

if __name__ == "__main__":
    get_hashes('f:/Exp  AI Dect/Sample Data/Web')
