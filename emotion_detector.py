import cv2
import numpy as np
from keras.models import load_model

# Load pre-trained model
model = load_model('model/emotion_model.h5')

# Emotion labels (should match your model output)
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# Load OpenCV's built-in face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def detect_emotion_from_webcam():
    """
    Captures a frame from the webcam, detects a face, and predicts the emotion using the CNN model.
    Returns the predicted emotion or an error message.
    """
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return {'error': 'Failed to access webcam'}

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    if len(faces) == 0:
        return {'error': 'No face detected'}

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        roi_gray = cv2.resize(roi_gray, (48, 48))
        roi = roi_gray.reshape(1, 48, 48, 1).astype('float32') / 255.0

        prediction = model.predict(roi)
        emotion_idx = int(np.argmax(prediction))
        emotion = emotion_labels[emotion_idx]
        return {'emotion': emotion}

    return {'error': 'Unable to process face'}

