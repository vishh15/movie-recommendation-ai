"""
Emotion detection service for Flask app.
"""

import base64
import io
import numpy as np
from PIL import Image

from ml.face_detector import FaceDetector
from ml.emotion_model import EmotionDetector
from ml.preprocess import preprocess_face


class EmotionService:
    """Service for emotion detection from images."""
    
    def __init__(self, model_path=None):
        """
        Initialize emotion service.
        
        Args:
            model_path: str, path to trained PyTorch model (optional)
        """
        self.face_detector = FaceDetector()
        self.emotion_detector = EmotionDetector(model_path)
    
    def detect_emotion_from_base64(self, base64_image):
        """
        Detect emotion from base64 encoded image.
        
        Args:
            base64_image: str, base64 encoded image
        
        Returns:
            dict with 'success', 'emotion', 'confidence', 'message'
        """
        try:
            # Decode base64 image
            image_data = base64.b64decode(base64_image.split(',')[1])
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to numpy array
            image_np = np.array(image)
            
            # Convert RGB to BGR for OpenCV
            if len(image_np.shape) == 3 and image_np.shape[2] == 3:
                image_np = image_np[:, :, ::-1].copy()
            
            return self.detect_emotion_from_array(image_np)
        
        except Exception as e:
            return {
                'success': False,
                'emotion': None,
                'confidence': 0.0,
                'message': f'Error decoding image: {str(e)}'
            }
    
    def detect_emotion_from_file(self, file_path):
        """
        Detect emotion from image file.
        
        Args:
            file_path: str, path to image file
        
        Returns:
            dict with 'success', 'emotion', 'confidence', 'message'
        """
        try:
            image = Image.open(file_path)
            image_np = np.array(image)
            
            # Convert RGB to BGR for OpenCV
            if len(image_np.shape) == 3 and image_np.shape[2] == 3:
                image_np = image_np[:, :, ::-1].copy()
            
            return self.detect_emotion_from_array(image_np)
        
        except Exception as e:
            return {
                'success': False,
                'emotion': None,
                'confidence': 0.0,
                'message': f'Error reading image: {str(e)}'
            }
    
    def detect_emotion_from_array(self, image_np):
        """
        Detect emotion from numpy array image.
        
        Args:
            image_np: numpy array, BGR image
        
        Returns:
            dict with 'success', 'emotion', 'confidence', 'message'
        """
        try:
            # Detect faces
            faces = self.face_detector.detect_faces_mediapipe(image_np)
            
            # Fallback to OpenCV if MediaPipe fails
            if len(faces) == 0:
                faces = self.face_detector.detect_faces_opencv(image_np)
            
            if len(faces) == 0:
                return {
                    'success': False,
                    'emotion': None,
                    'confidence': 0.0,
                    'message': 'No face detected in the image'
                }
            
            # Get largest face
            face_bbox = self.face_detector.get_largest_face(faces)
            
            # Crop and preprocess face
            x, y, w, h = face_bbox
            face_img = image_np[y:y+h, x:x+w]
            preprocessed_face = preprocess_face(face_img)
            
            # Detect emotion
            emotion, confidence = self.emotion_detector.predict_emotion(preprocessed_face)
            
            return {
                'success': True,
                'emotion': emotion,
                'confidence': float(confidence),
                'message': 'Emotion detected successfully'
            }
        
        except Exception as e:
            return {
                'success': False,
                'emotion': None,
                'confidence': 0.0,
                'message': f'Error detecting emotion: {str(e)}'
            }


# Global instance (singleton)
_emotion_service = None


def get_emotion_service(model_path=None):
    """
    Get emotion service singleton.
    
    Args:
        model_path: str, optional model path
    
    Returns:
        EmotionService instance
    """
    global _emotion_service
    
    if _emotion_service is None:
        _emotion_service = EmotionService(model_path)
    
    return _emotion_service
