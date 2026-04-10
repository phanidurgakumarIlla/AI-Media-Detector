import os
import torch
import pandas as pd
from PIL import Image
from transformers import ViTForImageClassification, ViTImageProcessor
from torch.utils.data import DataLoader, Dataset, random_split
from torch.optim import AdamW
from torch.optim.lr_scheduler import StepLR
import torchvision.transforms as T
from tqdm import tqdm
import torch.nn as nn

# ------------------------------------------------------------------
# Config
# ------------------------------------------------------------------
DATA_ROOT = os.path.join(os.path.dirname(__file__), "data")
LABELS_CSV = os.path.join(DATA_ROOT, "labels.csv")
MODEL_SAVE_PATH = os.path.join(os.path.dirname(__file__), "model", "fine_tuned")
MODEL_NAME = "google/vit-base-patch16-224"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BATCH_SIZE = 4 # Increased for stability
EPOCHS = 20
LR = 3e-5 # Slightly lower for specialized fine-tuning
LABEL_SMOOTHING = 0.1

# ------------------------------------------------------------------
# Dataset
# ------------------------------------------------------------------
class ForensicDataset(Dataset):
    def __init__(self, df, processor, augment=False):
        self.df = df
        self.processor = processor
        self.augment = augment
        self.transforms = T.Compose([
            T.RandomHorizontalFlip(p=0.5),
            T.RandomRotation(degrees=10),
            T.ColorJitter(brightness=0.1, contrast=0.1),
            T.Resize((224, 224))
        ])
    
    def __len__(self):
        return len(self.df)
    
    def __getitem__(self, idx):
        path = self.df.iloc[idx]["filepath"]
        if not os.path.isabs(path):
            path = os.path.join(DATA_ROOT, "..", path)
        
        label_str = self.df.iloc[idx]["label"]
        label = 1 if label_str == "fake" else 0
        
        try:
            image = Image.open(path).convert("RGB")
            if self.augment:
                image = self.transforms(image)
            inputs = self.processor(images=image, return_tensors="pt")
            return inputs["pixel_values"].squeeze(0), torch.tensor(label)
        except Exception as e:
            # Return a dummy if image is broken, though labels.csv should be clean
            return torch.zeros((3, 224, 224)), torch.tensor(0)

def train():
    os.makedirs(MODEL_SAVE_PATH, exist_ok=True)
    df = pd.read_csv(LABELS_CSV)
    processor = ViTImageProcessor.from_pretrained(MODEL_NAME)
    
    # Split
    train_size = int(0.85 * len(df))
    val_size = len(df) - train_size
    train_df = df.sample(frac=1, random_state=42).iloc[:train_size]
    val_df = df.sample(frac=1, random_state=42).iloc[train_size:]
    
    train_ds = ForensicDataset(train_df, processor, augment=True)
    val_ds = ForensicDataset(val_df, processor, augment=False)
    
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE)
    
    model = ViTForImageClassification.from_pretrained(
        MODEL_NAME, 
        num_labels=2,
        ignore_mismatched_sizes=True
    ).to(DEVICE)

    optimizer = AdamW(model.parameters(), lr=LR)
    scheduler = StepLR(optimizer, step_size=5, gamma=0.5)
    criterion = nn.CrossEntropyLoss(label_smoothing=LABEL_SMOOTHING)

    best_val_loss = float('inf')
    
    print(f"[INFO] High-Intensity Training: {len(df)} images, {EPOCHS} epochs, {DEVICE}")
    
    for epoch in range(EPOCHS):
        model.train()
        train_loss = 0
        for batch in tqdm(train_loader, desc=f"Epoch {epoch+1} [TRAIN]"):
            pixel_values, labels = [b.to(DEVICE) for b in batch]
            outputs = model(pixel_values=pixel_values)
            loss = criterion(outputs.logits, labels)
            
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            train_loss += loss.item()
        
        # Validation
        model.eval()
        val_loss = 0
        correct = 0
        total = 0
        with torch.no_grad():
            for batch in val_loader:
                pixel_values, labels = [b.to(DEVICE) for b in batch]
                outputs = model(pixel_values=pixel_values)
                loss = criterion(outputs.logits, labels)
                val_loss += loss.item()
                
                preds = torch.argmax(outputs.logits, dim=1)
                correct += (preds == labels).sum().item()
                total += labels.size(0)
        
        avg_val_loss = val_loss/len(val_loader)
        accuracy = correct/total
        print(f"Epoch {epoch+1}: Train Loss: {train_loss/len(train_loader):.4f} | Val Loss: {avg_val_loss:.4f} | Val Acc: {accuracy:.2%}")
        
        scheduler.step()
        
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            model.save_pretrained(MODEL_SAVE_PATH)
            processor.save_pretrained(MODEL_SAVE_PATH)
            print(f"[*] New Best Model Saved (Val Loss: {avg_val_loss:.4f})")

    print("[SUCCESS] Production-Grade Fine-tuning complete!")

if __name__ == "__main__":
    train()
