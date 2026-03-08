"""
Training script for emotion detection model on FER2013 dataset.
This is OPTIONAL - the app works without running this.
"""

import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
import numpy as np
from PIL import Image
import pandas as pd
from sklearn.model_selection import train_test_split

from emotion_model import EmotionClassifier, EMOTION_LABELS


class FER2013Dataset(Dataset):
    """
    Dataset class for FER2013 emotion recognition dataset.
    Download from: https://www.kaggle.com/datasets/msambare/fer2013
    """
    
    def __init__(self, images, labels, transform=None):
        self.images = images
        self.labels = labels
        self.transform = transform
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        image = self.images[idx]
        label = self.labels[idx]
        
        # Convert to PIL Image
        image = Image.fromarray(image)
        
        if self.transform:
            image = self.transform(image)
        
        return image, label


def load_fer2013_data(csv_path='data/fer2013.csv'):
    """
    Load FER2013 dataset from CSV.
    
    Args:
        csv_path: path to fer2013.csv
    
    Returns:
        X_train, X_val, y_train, y_val
    """
    print(f"Loading FER2013 dataset from {csv_path}...")
    
    df = pd.read_csv(csv_path)
    
    # Convert pixel strings to images
    images = []
    labels = []
    
    for idx, row in df.iterrows():
        pixels = np.array([int(p) for p in row['pixels'].split()], dtype=np.uint8)
        image = pixels.reshape(48, 48)
        
        # Convert to RGB
        image = np.stack([image] * 3, axis=2)
        
        images.append(image)
        labels.append(row['emotion'])
    
    images = np.array(images)
    labels = np.array(labels)
    
    # Split into train/val
    X_train, X_val, y_train, y_val = train_test_split(
        images, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    print(f"Train samples: {len(X_train)}, Val samples: {len(X_val)}")
    
    return X_train, X_val, y_train, y_val


def get_data_transforms():
    """
    Get data augmentation transforms.
    
    Returns:
        train_transform, val_transform
    """
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    return train_transform, val_transform


def train_model(
    model,
    train_loader,
    val_loader,
    num_epochs=50,
    learning_rate=0.001,
    device='cuda',
    save_path='models/emotion_model.pt'
):
    """
    Train the emotion detection model.
    
    Args:
        model: EmotionClassifier instance
        train_loader: training data loader
        val_loader: validation data loader
        num_epochs: number of training epochs
        learning_rate: initial learning rate
        device: 'cuda' or 'cpu'
        save_path: path to save best model
    """
    model = model.to(device)
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    # Learning rate scheduler
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=3, verbose=True
    )
    
    # Early stopping
    best_val_loss = float('inf')
    patience = 7
    patience_counter = 0
    
    print(f"\nTraining on {device}...")
    print(f"Epochs: {num_epochs}, Learning Rate: {learning_rate}")
    print("-" * 70)
    
    for epoch in range(num_epochs):
        # Training phase
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.to(device)
            
            # Forward pass
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            # Statistics
            train_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            train_total += labels.size(0)
            train_correct += (predicted == labels).sum().item()
        
        train_loss /= len(train_loader)
        train_acc = 100 * train_correct / train_total
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(device)
                labels = labels.to(device)
                
                outputs = model(images)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
        
        val_loss /= len(val_loader)
        val_acc = 100 * val_correct / val_total
        
        # Print progress
        print(f"Epoch [{epoch+1}/{num_epochs}] "
              f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}% | "
              f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
        
        # Learning rate scheduling
        scheduler.step(val_loss)
        
        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            
            # Save checkpoint
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': val_loss,
                'val_acc': val_acc
            }, save_path)
            print(f"  ✓ Saved best model (val_loss: {val_loss:.4f})")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"\nEarly stopping triggered after {epoch+1} epochs")
                break
    
    print(f"\nTraining complete! Best model saved to {save_path}")
    return model


def main():
    """Main training function."""
    # Configuration
    CSV_PATH = 'data/fer2013.csv'
    BATCH_SIZE = 64
    NUM_EPOCHS = 50
    LEARNING_RATE = 0.001
    DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
    SAVE_PATH = 'models/emotion_model.pt'
    
    print("=" * 70)
    print("Emotion Detection Model Training")
    print("=" * 70)
    
    # Check if dataset exists
    if not os.path.exists(CSV_PATH):
        print(f"\nError: FER2013 dataset not found at {CSV_PATH}")
        print("Please download from: https://www.kaggle.com/datasets/msambare/fer2013")
        print("Or the app will use rule-based fallback for emotion detection.")
        return
    
    # Load data
    X_train, X_val, y_train, y_val = load_fer2013_data(CSV_PATH)
    
    # Get transforms
    train_transform, val_transform = get_data_transforms()
    
    # Create datasets
    train_dataset = FER2013Dataset(X_train, y_train, transform=train_transform)
    val_dataset = FER2013Dataset(X_val, y_val, transform=val_transform)
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=4)
    
    # Create model
    model = EmotionClassifier(num_classes=len(EMOTION_LABELS), pretrained=True)
    print(f"\nModel created with {sum(p.numel() for p in model.parameters())} parameters")
    
    # Train model
    model = train_model(
        model,
        train_loader,
        val_loader,
        num_epochs=NUM_EPOCHS,
        learning_rate=LEARNING_RATE,
        device=DEVICE,
        save_path=SAVE_PATH
    )
    
    print("\n" + "=" * 70)
    print("Training finished successfully!")
    print("=" * 70)


if __name__ == '__main__':
    main()
