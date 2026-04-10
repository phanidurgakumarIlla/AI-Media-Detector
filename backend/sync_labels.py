import os
import pandas as pd

def sync():
    root = "data"
    fake_dir = os.path.join(root, "train", "fake")
    real_dir = os.path.join(root, "train", "real")
    
    data = []
    if os.path.exists(fake_dir):
        for f in os.listdir(fake_dir):
            if f.endswith((".jpg", ".png", ".webp", ".jpeg")):
                data.append({"filepath": os.path.join("data", "train", "fake", f), "label": "fake"})
                
    if os.path.exists(real_dir):
        for f in os.listdir(real_dir):
            if f.endswith((".jpg", ".png", ".webp", ".jpeg")):
                data.append({"filepath": os.path.join("data", "train", "real", f), "label": "real"})
    
    df = pd.DataFrame(data)
    csv_path = os.path.join(root, "labels.csv")
    df.to_csv(csv_path, index=False)
    print(f"Synchronized {len(df)} images to {csv_path}")

if __name__ == "__main__":
    sync()
