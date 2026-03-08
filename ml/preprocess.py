"""
Face preprocessing for emotion detection.
Handles face cropping, resizing, and normalization for EfficientNet.
"""

import cv2
import numpy as np
from PIL import Image


def preprocess_face(face_img, target_size=(224, 224)):
    """
    Preprocess face image for EfficientNet model.
    
    Args:
        face_img: numpy array or PIL Image
        target_size: tuple (width, height) for resizing
    
    Returns:
        Preprocessed image tensor ready for model input
    """
    # Convert to PIL Image if numpy array
    if isinstance(face_img, np.ndarray):
        if len(face_img.shape) == 2:  # Grayscale
            face_img = cv2.cvtColor(face_img, cv2.COLOR_GRAY2RGB)
        elif face_img.shape[2] == 4:  # RGBA
            face_img = cv2.cvtColor(face_img, cv2.COLOR_RGBA2RGB)
        face_img = Image.fromarray(face_img)
    
    # Resize to target size
    face_img = face_img.resize(target_size, Image.Resampling.LANCZOS)
    
    # Convert to numpy array
    img_array = np.array(face_img, dtype=np.float32)
    
    # Normalize to [0, 1]
    img_array = img_array / 255.0
    
    # Normalize using ImageNet stats (EfficientNet was trained on ImageNet)
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    img_array = (img_array - mean) / std
    
    # Transpose to channel-first format (C, H, W)
    img_array = img_array.transpose(2, 0, 1)
    
    # Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)
    
    return img_array


def crop_face(image, bbox, padding=0.2):
    """
    Crop face from image using bounding box with optional padding.
    
    Args:
        image: numpy array (H, W, C)
        bbox: tuple (x, y, w, h) or dict with 'x', 'y', 'width', 'height'
        padding: float, percentage of bbox size to add as padding
    
    Returns:
        Cropped face image
    """
    h, w = image.shape[:2]
    
    # Extract bbox coordinates
    if isinstance(bbox, dict):
        x, y, bw, bh = bbox['x'], bbox['y'], bbox['width'], bbox['height']
    else:
        x, y, bw, bh = bbox
    
    # Add padding
    pad_w = int(bw * padding)
    pad_h = int(bh * padding)
    
    x1 = max(0, x - pad_w)
    y1 = max(0, y - pad_h)
    x2 = min(w, x + bw + pad_w)
    y2 = min(h, y + bh + pad_h)
    
    # Crop face
    face = image[y1:y2, x1:x2]
    
    return face


def enhance_contrast(image):
    """
    Enhance image contrast using CLAHE.
    
    Args:
        image: numpy array
    
    Returns:
        Contrast-enhanced image
    """
    if len(image.shape) == 3:
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge channels
        lab = cv2.merge([l, a, b])
        
        # Convert back to RGB
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    else:
        # Grayscale
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
    
    return enhanced
