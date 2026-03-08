"""
Emotion detection model using EfficientNet-B0 with PyTorch.
Includes rule-based fallback for running without a trained model.
"""

import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from efficientnet_pytorch import EfficientNet
import cv2


# Emotion labels (7 basic emotions)
EMOTION_LABELS = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']


class EmotionClassifier(nn.Module):
    """
    EfficientNet-B0 based emotion classifier.
    """
    
    def __init__(self, num_classes=7, pretrained=True):
        super(EmotionClassifier, self).__init__()
        
        # Load EfficientNet-B0
        if pretrained:
            self.efficientnet = EfficientNet.from_pretrained('efficientnet-b0')
        else:
            self.efficientnet = EfficientNet.from_name('efficientnet-b0')
        
        # Get the number of features from the last layer
        num_features = self.efficientnet._fc.in_features
        
        # Replace the final fully connected layer
        self.efficientnet._fc = nn.Identity()
        
        # Custom classification head
        self.classifier = nn.Sequential(
            nn.Linear(num_features, 256),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        # Extract features
        features = self.efficientnet(x)
        
        # Classify
        output = self.classifier(features)
        
        return output


class EmotionDetector:
    """
    Emotion detector with model loading and prediction.
    """
    
    def __init__(self, model_path='models/emotion_model.pt', use_gpu=False):
        """
        Initialize emotion detector.
        
        Args:
            model_path: path to trained model weights
            use_gpu: whether to use GPU if available
        """
        self.model_path = model_path
        self.device = torch.device('cuda' if use_gpu and torch.cuda.is_available() else 'cpu')
        self.model = None
        self.model_available = False
        
        # Try to load model
        if os.path.exists(model_path):
            try:
                self.load_model()
                self.model_available = True
                print(f"✓ Loaded trained emotion model from {model_path}")
            except Exception as e:
                print(f"Warning: Could not load model: {e}")
                print("Using rule-based fallback for emotion detection.")
        else:
            print(f"Note: No trained model found at {model_path}")
            print("Using rule-based fallback for emotion detection.")
    
    def load_model(self):
        """Load the trained model weights."""
        self.model = EmotionClassifier(num_classes=len(EMOTION_LABELS), pretrained=False)
        
        # Load state dict
        checkpoint = torch.load(self.model_path, map_location=self.device)
        
        if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
            self.model.load_state_dict(checkpoint['model_state_dict'])
        else:
            self.model.load_state_dict(checkpoint)
        
        self.model.to(self.device)
        self.model.eval()
    
    def predict_with_model(self, face_tensor):
        """
        Predict emotion using trained model.
        
        Args:
            face_tensor: preprocessed face image tensor (1, 3, 224, 224)
        
        Returns:
            dict with 'emotion', 'confidence', 'probabilities'
        """
        with torch.no_grad():
            # Convert to torch tensor if numpy
            if isinstance(face_tensor, np.ndarray):
                face_tensor = torch.from_numpy(face_tensor).float()
            
            face_tensor = face_tensor.to(self.device)
            
            # Forward pass
            outputs = self.model(face_tensor)
            probabilities = F.softmax(outputs, dim=1)
            
            # Get prediction
            confidence, predicted_idx = torch.max(probabilities, 1)
            
            emotion = EMOTION_LABELS[predicted_idx.item()]
            confidence = confidence.item()
            probs_dict = {
                label: prob.item()
                for label, prob in zip(EMOTION_LABELS, probabilities[0])
            }
        
        return {
            'emotion': emotion,
            'confidence': confidence,
            'probabilities': probs_dict
        }
    
    def predict_rule_based(self, face_image):
        """
        Rule-based emotion prediction using image features.
        Fallback method when no trained model is available.
        
        Args:
            face_image: numpy array (H, W, 3) RGB image
        
        Returns:
            dict with 'emotion', 'confidence', 'probabilities'
        """
        # Convert to grayscale for analysis
        if len(face_image.shape) == 3:
            gray = cv2.cvtColor(face_image, cv2.COLOR_RGB2GRAY)
        else:
            gray = face_image
        
        # Calculate image statistics
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        # Calculate color distribution in RGB
        if len(face_image.shape) == 3:
            r_mean = np.mean(face_image[:, :, 0])
            g_mean = np.mean(face_image[:, :, 1])
            b_mean = np.mean(face_image[:, :, 2])
        else:
            r_mean = g_mean = b_mean = brightness
        
        # Simple rule-based classification
        # These are heuristics and not accurate - just for fallback
        scores = np.zeros(len(EMOTION_LABELS))
        
        # Happiness: brighter, warmer colors
        happy_idx = EMOTION_LABELS.index('happy')
        scores[happy_idx] = (brightness / 255.0) * 0.5 + (r_mean / 255.0) * 0.3
        
        # Sadness: darker, cooler colors
        sad_idx = EMOTION_LABELS.index('sad')
        scores[sad_idx] = (1 - brightness / 255.0) * 0.4 + (b_mean / 255.0) * 0.2
        
        # Neutral: balanced
        neutral_idx = EMOTION_LABELS.index('neutral')
        scores[neutral_idx] = 1 - abs(brightness - 128) / 128
        
        # Angry: higher contrast, redder
        angry_idx = EMOTION_LABELS.index('angry')
        scores[angry_idx] = (contrast / 100.0) * 0.3 + (r_mean - g_mean) / 255.0 * 0.3
        
        # Fear & Surprise: higher contrast
        fear_idx = EMOTION_LABELS.index('fear')
        surprise_idx = EMOTION_LABELS.index('surprise')
        scores[fear_idx] = (contrast / 100.0) * 0.4
        scores[surprise_idx] = (contrast / 100.0) * 0.35
        
        # Disgust: similar to angry
        disgust_idx = EMOTION_LABELS.index('disgust')
        scores[disgust_idx] = (contrast / 100.0) * 0.25
        
        # Add some randomness to make it more realistic
        scores += np.random.rand(len(EMOTION_LABELS)) * 0.1
        
        # Normalize to probabilities
        probabilities = np.exp(scores) / np.sum(np.exp(scores))
        
        predicted_idx = np.argmax(probabilities)
        emotion = EMOTION_LABELS[predicted_idx]
        confidence = probabilities[predicted_idx]
        
        probs_dict = {
            label: float(prob)
            for label, prob in zip(EMOTION_LABELS, probabilities)
        }
        
        return {
            'emotion': emotion,
            'confidence': float(confidence),
            'probabilities': probs_dict,
            'method': 'rule_based'
        }
    
    def predict_emotion(self, face_tensor_or_image):
        """
        Predict emotion from face image.
        
        Args:
            face_tensor_or_image: Preprocessed tensor (1, 3, 224, 224) or numpy array
        
        Returns:
            dict with 'emotion', 'confidence', 'probabilities'
        """
        if self.model_available and self.model is not None:
            return self.predict_with_model(face_tensor_or_image)
        else:
            # Use rule-based fallback
            # If tensor, convert back to image
            if torch.is_tensor(face_tensor_or_image):
                face_image = face_tensor_or_image.cpu().numpy()[0].transpose(1, 2, 0)
                # Denormalize
                mean = np.array([0.485, 0.456, 0.406])
                std = np.array([0.229, 0.224, 0.225])
                face_image = (face_image * std + mean) * 255
                face_image = face_image.astype(np.uint8)
            elif isinstance(face_tensor_or_image, np.ndarray):
                if len(face_tensor_or_image.shape) == 4:
                    # Batch tensor
                    face_image = face_tensor_or_image[0].transpose(1, 2, 0)
                    mean = np.array([0.485, 0.456, 0.406])
                    std = np.array([0.229, 0.224, 0.225])
                    face_image = (face_image * std + mean) * 255
                    face_image = face_image.astype(np.uint8)
                else:
                    face_image = face_tensor_or_image
            else:
                face_image = face_tensor_or_image
            
            return self.predict_rule_based(face_image)


def load_model(model_path='models/emotion_model.pt'):
    """
    Convenience function to load emotion detector.
    
    Args:
        model_path: path to model weights
    
    Returns:
        EmotionDetector instance
    """
    return EmotionDetector(model_path=model_path)


def predict_emotion(face_tensor):
    """
    Convenience function to predict emotion.
    
    Args:
        face_tensor: preprocessed face tensor
    
    Returns:
        dict with emotion prediction
    """
    detector = EmotionDetector()
    return detector.predict_emotion(face_tensor)
