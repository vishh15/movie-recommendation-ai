"""
Flask app configuration.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration."""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'
    
    # Server
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Session
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    
    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_EXTENSIONS = ['.jpg', '.jpeg', '.png']
    
    # ML Model paths
    MODEL_PATH = os.path.join('models', 'emotion_model.pth')
    HAARCASCADE_PATH = os.path.join('models', 'haarcascade_frontalface_default.xml')
    
    # Data paths
    MOVIES_CSV_PATH = os.path.join('data', 'movies_dataset.csv')
    
    # TMDB API
    TMDB_API_KEY = os.getenv('TMDB_API_KEY', 'your_tmdb_key_here')
    TMDB_MIN_VOTE_COUNT = int(os.getenv('TMDB_MIN_VOTE_COUNT', 100))
    TMDB_MIN_RATING = float(os.getenv('TMDB_MIN_RATING', 5.0))
    TMDB_YEAR_FROM = os.getenv('TMDB_YEAR_FROM', '')
    TMDB_YEAR_TO = os.getenv('TMDB_YEAR_TO', '')
    
    # Emotion settings
    EMOTIONS = ['happy', 'sad', 'angry', 'fear', 'neutral', 'surprise', 'disgust']
    
    # Recommendation settings
    MIN_RECOMMENDATIONS = 12
    MAX_RECOMMENDATIONS = 20
    TOP_N_RECOMMENDATIONS = 16


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


# Config dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Get configuration object."""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
