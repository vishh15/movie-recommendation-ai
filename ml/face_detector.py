"""
Face detection using MediaPipe with OpenCV Haar Cascade fallback.
"""

import cv2
import numpy as np

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("Warning: MediaPipe not available. Using OpenCV Haar Cascade fallback.")


class FaceDetector:
    """
    Face detector with MediaPipe primary and OpenCV Haar Cascade fallback.
    """
    
    def __init__(self, use_mediapipe=True):
        """
        Initialize face detector.
        
        Args:
            use_mediapipe: bool, whether to try MediaPipe first
        """
        self.use_mediapipe = use_mediapipe and MEDIAPIPE_AVAILABLE
        
        if self.use_mediapipe:
            self.mp_face_detection = mp.solutions.face_detection
            self.face_detection = self.mp_face_detection.FaceDetection(
                model_selection=0,
                min_detection_confidence=0.5
            )
        
        # Load OpenCV Haar Cascade as fallback
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
    
    def detect_faces_mediapipe(self, image):
        """
        Detect faces using MediaPipe.
        
        Args:
            image: numpy array (H, W, C) in RGB format
        
        Returns:
            List of face bounding boxes as dicts with 'x', 'y', 'width', 'height'
        """
        if not self.use_mediapipe:
            return []
        
        results = self.face_detection.process(image)
        
        if not results.detections:
            return []
        
        h, w = image.shape[:2]
        faces = []
        
        for detection in results.detections:
            bbox = detection.location_data.relative_bounding_box
            
            # Convert relative coordinates to absolute
            x = int(bbox.xmin * w)
            y = int(bbox.ymin * h)
            width = int(bbox.width * w)
            height = int(bbox.height * h)
            
            # Ensure coordinates are within image bounds
            x = max(0, x)
            y = max(0, y)
            width = min(width, w - x)
            height = min(height, h - y)
            
            faces.append({
                'x': x,
                'y': y,
                'width': width,
                'height': height,
                'confidence': detection.score[0]
            })
        
        return faces
    
    def detect_faces_opencv(self, image):
        """
        Detect faces using OpenCV Haar Cascade.
        
        Args:
            image: numpy array (H, W, C) in RGB or BGR format
        
        Returns:
            List of face bounding boxes as dicts
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Detect faces
        face_rects = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        faces = []
        for (x, y, w, h) in face_rects:
            faces.append({
                'x': int(x),
                'y': int(y),
                'width': int(w),
                'height': int(h),
                'confidence': 1.0  # Haar Cascade doesn't provide confidence
            })
        
        return faces
    
    def detect(self, image):
        """
        Detect faces using the best available method.
        
        Args:
            image: numpy array (H, W, C) in RGB format
        
        Returns:
            List of face bounding boxes as dicts, or empty list if no faces found
        """
        # Try MediaPipe first
        if self.use_mediapipe:
            try:
                faces = self.detect_faces_mediapipe(image)
                if faces:
                    return faces
            except Exception as e:
                print(f"MediaPipe detection failed: {e}. Falling back to OpenCV.")
        
        # Fallback to OpenCV
        return self.detect_faces_opencv(image)
    
    def get_largest_face(self, image):
        """
        Detect and return the largest face in the image.
        
        Args:
            image: numpy array (H, W, C)
        
        Returns:
            Dict with face bbox, or None if no face detected
        """
        faces = self.detect(image)
        
        if not faces:
            return None
        
        # Return the largest face (by area)
        largest_face = max(faces, key=lambda f: f['width'] * f['height'])
        return largest_face
    
    def __del__(self):
        """Clean up MediaPipe resources."""
        if hasattr(self, 'face_detection') and self.use_mediapipe:
            self.face_detection.close()


def detect_face_bbox(image):
    """
    Convenience function to detect the largest face bounding box.
    
    Args:
        image: numpy array or file path
    
    Returns:
        Dict with 'x', 'y', 'width', 'height' or None
    """
    # Load image if path provided
    if isinstance(image, str):
        image = cv2.imread(image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    detector = FaceDetector()
    face = detector.get_largest_face(image)
    
    return face
