import json
import random
import os
import requests

# TMDB API Configuration
TMDB_API_KEY = '59b6724b967a22b087188902d1162018'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/w500'

def get_movie_poster(title, year):
    """
    Fetch movie poster URL from TMDB API.
    Returns poster URL or a placeholder if not found.
    """
    try:
        # Search for movie
        search_url = f"{TMDB_BASE_URL}/search/movie"
        params = {
            'api_key': TMDB_API_KEY,
            'query': title,
            'year': year
        }
        
        response = requests.get(search_url, params=params, timeout=3)
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            if results:
                poster_path = results[0].get('poster_path')
                if poster_path:
                    return f"{TMDB_IMAGE_BASE}{poster_path}"
        
        # Fallback to placeholder
        return f"https://via.placeholder.com/500x750/8b5cf6/ffffff?text={title.replace(' ', '+')}"
    
    except Exception as e:
        # Return placeholder on any error
        return f"https://via.placeholder.com/500x750/8b5cf6/ffffff?text={title.replace(' ', '+')}"

def load_movie_data(path='movies.json'):
    """
    Loads emotion-wise movie data from a JSON file.
    Returns a dictionary mapping emotion to movie list.
    """
    if not os.path.exists(path):
        print(f"Error: {path} not found.")
        return {}

    try:
        with open(path, 'r') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in movies.json.")
        return {}

# Emotion mapping for synonyms and fallbacks
EMOTION_MAPPING = {
    'surprised': 'surprise',  # Normalize to 'surprise'
}

def get_recommendations(emotion, count=15):
    """
    Returns a list of movies based on the given emotion.
    Returns 7-15 movies by default for a richer selection.
    If the emotion is not found, returns a fallback message.
    """
    movies_data = load_movie_data()

    if not movies_data:
        return [{"title": "Movie data is unavailable", "year": "N/A", "genre": "N/A", "rating": 0, "poster_url": "https://via.placeholder.com/500x750/8b5cf6/ffffff?text=No+Data"}]

    # Normalize input: lowercase and strip whitespace
    emotion = emotion.lower().strip()
    
    # Map to alternative emotion if not found
    if emotion not in movies_data:
        emotion = EMOTION_MAPPING.get(emotion, 'happy')  # Default to happy
    
    if emotion not in movies_data:
        # Final fallback
        return [{"title": "The Shawshank Redemption", "year": 1994, "genre": "Drama", "rating": 9.3, "poster_url": get_movie_poster("The Shawshank Redemption", 1994)}]

    movie_list = movies_data[emotion]
    random.shuffle(movie_list)
    selected_movies = movie_list[:count]
    
    # Add poster URLs and overview to each movie
    for movie in selected_movies:
        movie['poster_url'] = get_movie_poster(movie['title'], movie['year'])
        # Add a simple overview if not present
        if 'overview' not in movie:
            movie['overview'] = f"A {movie['genre']} film from {movie['year']}. Rating: {movie['rating']}/10"
    
    return selected_movies
