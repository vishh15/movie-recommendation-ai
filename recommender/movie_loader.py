"""
Movie data loader with caching.
Loads and caches movie dataset from CSV.
"""

import os
import pandas as pd


class MovieLoader:
    """
    Singleton movie data loader with in-memory caching.
    """
    
    _instance = None
    _movies_df = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MovieLoader, cls).__new__(cls)
        return cls._instance
    
    def load_movies(self, csv_path='data/movies_dataset.csv'):
        """
        Load movies from CSV file (with caching).
        
        Args:
            csv_path: path to movies CSV file
        
        Returns:
            pandas DataFrame with movie data
        """
        # Return cached data if available
        if self._movies_df is not None:
            return self._movies_df
        
        # Check if file exists
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Movie dataset not found at {csv_path}")
        
        # Load CSV
        try:
            self._movies_df = pd.read_csv(csv_path)
            print(f"✓ Loaded {len(self._movies_df)} movies from {csv_path}")
        except Exception as e:
            raise Exception(f"Error loading movie dataset: {e}")
        
        # Validate required columns
        required_columns = ['id', 'title', 'year', 'genre', 'overview', 'emotion_tags', 'rating']
        missing_columns = [col for col in required_columns if col not in self._movies_df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        return self._movies_df
    
    def get_movies_by_emotion(self, emotion, csv_path='data/movies_dataset.csv'):
        """
        Get all movies for a specific emotion.
        
        Args:
            emotion: str, emotion label
            csv_path: path to movies CSV
        
        Returns:
            pandas DataFrame filtered by emotion
        """
        df = self.load_movies(csv_path)
        
        # Normalize emotion (lowercase)
        emotion = emotion.lower().strip()
        
        # Filter by emotion tag
        filtered_df = df[df['emotion_tags'].str.lower() == emotion]
        
        return filtered_df
    
    def get_movie_by_id(self, movie_id, csv_path='data/movies_dataset.csv'):
        """
        Get a single movie by ID.
        
        Args:
            movie_id: int, movie ID
            csv_path: path to movies CSV
        
        Returns:
            pandas Series or None
        """
        df = self.load_movies(csv_path)
        
        result = df[df['id'] == movie_id]
        
        if len(result) == 0:
            return None
        
        return result.iloc[0]
    
    def reload(self):
        """Force reload of movie data (clear cache)."""
        self._movies_df = None
        print("Movie cache cleared")


def load_movies(csv_path='data/movies_dataset.csv'):
    """
    Convenience function to load movies.
    
    Args:
        csv_path: path to movies CSV
    
    Returns:
        pandas DataFrame
    """
    loader = MovieLoader()
    return loader.load_movies(csv_path)


def get_movies_by_emotion(emotion, csv_path='data/movies_dataset.csv'):
    """
    Convenience function to get movies by emotion.
    
    Args:
        emotion: str
        csv_path: path to CSV
    
    Returns:
        pandas DataFrame
    """
    loader = MovieLoader()
    return loader.get_movies_by_emotion(emotion, csv_path)
