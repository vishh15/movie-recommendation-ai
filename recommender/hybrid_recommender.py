"""
Hybrid movie recommender using TF-IDF and cosine similarity.
Includes TMDB API integration for movie posters.
"""

import os
import random
import re
import requests
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher
from functools import lru_cache
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd

from recommender.movie_loader import get_movies_by_emotion


# TMDB API configuration
TMDB_API_KEY = os.getenv('TMDB_API_KEY', 'your_tmdb_key_here')
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'
PLACEHOLDER_POSTER_URL = 'https://via.placeholder.com/500x750/667eea/ffffff?text=Movie+Poster'
MIN_RECOMMENDATIONS = 12
MAX_RECOMMENDATIONS = 20
DEFAULT_DISCOVER_FILTERS = {
    'min_vote_count': 100,
    'min_rating': 5.0,
    'year_from': None,
    'year_to': None,
}

# Emotion-specific ranking profiles to personalize recommendations.
EMOTION_PROFILES = {
    'happy': {
        'weights': {'similarity': 0.45, 'rating': 0.30, 'year': 0.25},
        'preferred_genres': ['comedy', 'family', 'adventure', 'animation', 'music'],
        'max_per_primary_genre': 2,
    },
    'sad': {
        'weights': {'similarity': 0.55, 'rating': 0.35, 'year': 0.10},
        'preferred_genres': ['drama', 'romance', 'biography'],
        'max_per_primary_genre': 3,
    },
    'angry': {
        'weights': {'similarity': 0.45, 'rating': 0.45, 'year': 0.10},
        'preferred_genres': ['action', 'crime', 'thriller'],
        'max_per_primary_genre': 3,
    },
    'fear': {
        'weights': {'similarity': 0.60, 'rating': 0.30, 'year': 0.10},
        'preferred_genres': ['horror', 'mystery', 'thriller'],
        'max_per_primary_genre': 3,
    },
    'neutral': {
        'weights': {'similarity': 0.50, 'rating': 0.35, 'year': 0.15},
        'preferred_genres': ['drama', 'comedy', 'mystery'],
        'max_per_primary_genre': 2,
    },
    'surprise': {
        'weights': {'similarity': 0.55, 'rating': 0.30, 'year': 0.15},
        'preferred_genres': ['mystery', 'sci-fi', 'thriller'],
        'max_per_primary_genre': 2,
    },
    'disgust': {
        'weights': {'similarity': 0.55, 'rating': 0.35, 'year': 0.10},
        'preferred_genres': ['crime', 'thriller', 'drama'],
        'max_per_primary_genre': 2,
    },
}

# Known TMDB poster paths for popular movies (fallback)
KNOWN_POSTERS = {
    13: '/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg',  # Forrest Gump
    1402: '/8VZRhqQyTdKGDEk6WXU3pDGDOdJ.jpg',  # Pursuit of Happyness  
    155: '/qJ2tW6WMUDux911r6m7haRef0WH.jpg',  # The Dark Knight
    550: '/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg',  # Fight Club
    27205: '/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg',  # Inception
    424: '/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg',  # Schindler's List
    497: '/velWPhVMQeQKcxggNEU8YmIo52R.jpg',  # The Green Mile
    694: '/b3om1VqbP7LbGq9HbKwDoiR8uci.jpg',  # The Shining
    14160: '/eJllqQP6BCrZXTzmjBHPisdGXQk.jpg',  # Up
    10193: '/nFnEqVOaL5PG3vOo0QOVfIzJL7o.jpg',  # Toy Story 3
    313369: '/uDO8zWDhfWwoFdKS4fzkUJt0Rf0.jpg',  # La La Land
    27405: '/323BP0itpxTsO0skTwdnIslJ5yf.jpg',  # The Intouchables
    773: '/wKn7AJw730emlmzLSmJtzquwaeW.jpg',  # Little Miss Sunshine
    222935: '/ep7dF4QR4Mm39LI958V0XbwE0hK.jpg',  # Fault in Our Stars
    4282: '/8lUYMNUoNRFsxdYqqRsu0KuoQKr.jpg',  # A Walk to Remember
    334521: '/e8daDzP0vFOnGyKmve95Yv0D0io.jpg',  # Manchester by the Sea
    20890: '/uUsSgr8NeJ3LTRtj5YQGkIGTg9d.jpg',  # Hachi
    38: '/5MwkWH9tYHv3mV9OdYTMR5mAnsS.jpg',  # Eternal Sunshine
    637: '/74hLDKjD5aGYOotO6esUVaeISa2.jpg',  # Life is Beautiful
    98: '/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg',  # Gladiator
    245891: '/fZPSd91yGE9fCcCe6OoQr6E3Bev.jpg',  # John Wick
    76341: '/8tZYtuWezp8JbcsvHYO0O46tFbo.jpg',  # Mad Max Fury Road
    24: '/v7TaX8kXMXs5yFFGR41guUDNcnB.jpg',  # Kill Bill Vol 1
    68718: '/7oWY8VDWW7thTzWh3OKYRkWUlD5.jpg',  # Django Unchained
    281957: '/ji3ecJphATlVgWNY0B0RhJWhEgJ.jpg',  # The Revenant
    293660: '/yGSxMiF0cYuAiyuve5DA6bnWEOI.jpg',  # Deadpool
    752: '/lLH6KSwTo3KfkW9s5FgHc1pKkB.jpg',  # V for Vendetta
    138843: '/wVYREutTvI2tmxr6ujrHT704wGF.jpg',  # The Conjuring
    447332: '/nAU74GmpUk7t5iklEp3bufwDq4n.jpg',  # A Quiet Place
    419430: '/aSzpy9wobow5mNUsPdVw8fYFrMT.jpg',  # Get Out
    9552: '/db7cvCphcZscZl2purKFDvnkKsY.jpg',  # The Exorcist
    11324: '/kve5ZPzEiTJVxS5Xhwx9wdwqzw1.jpg',  # Shutter Island
    1124: '/bdN2jih0RzR5LE0MJ1nXVYZN1qy.jpg',  # The Prestige
    745: '/imdb_745_poster.jpg',  # The Sixth Sense
    210577: '/gdiLTof3rbPDAmPaCf4g6op46bj.jpg',  # Gone Girl
    127585: '/tuAuJYsYbOuHnf0qWhd5q7aDO2D.jpg',  # Prisoners
    77: '/yuNs09hvpHVU1cBTCAk9zxsL2oW.jpg',  # Memento
    157336: '/nBNZadXqJSdt05SHLqgT0HuC5Gm.jpg',  # Interstellar
    152601: '/eCOtqtfvn7cgNAc8jD3NPWB5oBD.jpg',  # Her
    153: '/wFmqSvqoMAhVMpbKpKubPdHbqsB.jpg',  # Lost in Translation
    194: '/nSxDa3M9aMvGVLoItzWTkaOlZa.jpg',  # Amelie
    83666: '/cO9vHqv6CqR7yyjUkC9RwW4GAHW.jpg',  # Moonrise Kingdom
    76492: '/uwmXDiG75yaZmFuEdJpqTN5wbz0.jpg',  # Midnight in Paris
    37799: '/n0ybibhJtQ5icDqTp8eRytcIHJx.jpg',  # The Social Network
    641: '/lG9gJJlibb1zQOpT2RYZIsI9d0S.jpg',  # Requiem for a Dream
    10137: '/hqh5O4KssfJWI62HGAgrjHXbxpu.jpg',  # Black Swan
    185: '/gOu4ifeQmMDL0WZ8IvNhIJe6OI7.jpg',  # A Clockwork Orange
    670: '/pWDtjs568ZfOTMbURQBYuT4Qaves.jpg',  # Oldboy
    1359: '/9uGHEgsiUXjCNq8wdq4r49YL8A1.jpg',  # American Psycho
    242582: '/j9HrX8f7GbZQm1BrBiR40uFQZSb.jpg',  # Nightcrawler
    807: '/6yoghtyTpznpBik8EngEmJskVUO.jpg',  # Se7en
    1949: '/7wiePrZc3WLFLgL7UA8TL77pNd.jpg',  # Zodiac
    120467: '/eWdyYQreja6JGCzqHWXpWHDrrPo.jpg',  # Grand Budapest Hotel
    346364: '/gLa4B2drZriNwJJH6urmfhFmgw7.jpg',  # Paddington 2
    137106: '/lbctonEnewCYZ4FYoTZhs8cidAl.jpg',  # The Lego Movie
    13155: '/9JHgYLMkqb65uMcEGpbQAF4P8nj.jpg',  # Garden State
    425: '/8VjdYBVTUTxxyQI2rO7N3yjt7QO.jpg',  # Before Sunrise
    8051: '/ysmW2WSFF9sIuJKdgHgrgYKWiLx.jpg',  # The Ring
    56292: '/dS19JgOvADHRSWDRxBp5YdGzpyA.jpg',  # Insidious
    82507: '/c8MP2vZMhQIBr0bWNGLQAQPLFcr.jpg',  # Sinister
    493922: '/p81a0L0dk4LV8un77P61TXngEwK.jpg',  # Hereditary
    2567: '/lEcuVVPVeFLL8T4ucsUP82YoTfe.jpg',  # The Others
    75656: '/tWsNYbrqy1p1w6K9zRk0mSchztT.jpg',  # Now You See Me
    4347: '/7F8htNsI46yHIlIc96u4jsT6oMN.jpg',  # Boy in Striped Pajamas
    2085: '/2P2n7zlJRRXM9krcSq46x1CslqT.jpg',  # Marley & Me
    387592: '/ekeABqBfM64A6rnKuJtxfCjLJBi.jpg',  # Paterson
}

# Emotion -> TMDB discover genres. See https://developer.themoviedb.org/docs/genres
TMDB_DISCOVER_GENRES = {
    'happy': '35,10751,12,16,10402',
    'sad': '18,10749,36',
    'angry': '28,80,53',
    'fear': '27,9648,53',
    'neutral': '18,35,9648',
    'surprise': '9648,878,53',
    'disgust': '80,53,18',
}


def _is_valid_tmdb_key():
    return bool(TMDB_API_KEY and TMDB_API_KEY != 'your_tmdb_key_here')


def _normalize_discover_filters(discover_filters=None):
    merged = dict(DEFAULT_DISCOVER_FILTERS)
    if isinstance(discover_filters, dict):
        merged.update(discover_filters)

    try:
        merged['min_vote_count'] = max(0, int(merged.get('min_vote_count', 100)))
    except (TypeError, ValueError):
        merged['min_vote_count'] = 100

    try:
        merged['min_rating'] = max(0.0, min(10.0, float(merged.get('min_rating', 5.0))))
    except (TypeError, ValueError):
        merged['min_rating'] = 5.0

    def normalize_year(value):
        if value in (None, ''):
            return None
        try:
            year = int(value)
            return year if 1900 <= year <= 2100 else None
        except (TypeError, ValueError):
            return None

    merged['year_from'] = normalize_year(merged.get('year_from'))
    merged['year_to'] = normalize_year(merged.get('year_to'))

    if merged['year_from'] and merged['year_to'] and merged['year_from'] > merged['year_to']:
        merged['year_from'], merged['year_to'] = merged['year_to'], merged['year_from']

    return merged


def _normalize_title(title):
    value = (title or '').lower()
    value = re.sub(r'[^a-z0-9\s]', ' ', value)
    value = re.sub(r'\s+', ' ', value).strip()
    return value


def _title_similarity(left, right):
    a = _normalize_title(left)
    b = _normalize_title(right)
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def _title_year_match(local_title, local_year, tmdb_title, release_date):
    title_score = _title_similarity(local_title, tmdb_title)
    if title_score >= 0.9:
        return True

    if local_year:
        try:
            tmdb_year = int(str(release_date or '')[:4])
            year_close = abs(int(local_year) - tmdb_year) <= 1
        except Exception:
            year_close = False
        return title_score >= 0.72 and year_close

    return title_score >= 0.8


def _get_emotion_profile(emotion):
    default_profile = {
        'weights': {'similarity': 0.55, 'rating': 0.35, 'year': 0.10},
        'preferred_genres': [],
        'max_per_primary_genre': 2,
    }
    return EMOTION_PROFILES.get(emotion, default_profile)


def _primary_genre_key(genre_value):
    return (genre_value or 'unknown').split(',')[0].strip().lower()


def _select_diverse_movies(ranked_df, top_n, max_per_primary_genre):
    """Greedy diversity selection with a hard cap per primary genre."""
    selected_rows = []
    genre_counts = {}

    for _, row in ranked_df.iterrows():
        genre_key = _primary_genre_key(row.get('genre'))
        if genre_counts.get(genre_key, 0) >= max_per_primary_genre:
            continue

        selected_rows.append(row.to_dict())
        genre_counts[genre_key] = genre_counts.get(genre_key, 0) + 1

        if len(selected_rows) >= top_n:
            break

    # If the cap prevented us from filling N slots, backfill by score.
    if len(selected_rows) < top_n:
        selected_titles = {row['title'] for row in selected_rows}
        remaining = ranked_df[~ranked_df['title'].isin(selected_titles)]
        for _, row in remaining.iterrows():
            selected_rows.append(row.to_dict())
            if len(selected_rows) >= top_n:
                break

    if not selected_rows:
        return ranked_df.head(top_n)

    return pd.DataFrame(selected_rows)


@lru_cache(maxsize=512)
def _fetch_movie_details_by_id(tmdb_id):
    if not _is_valid_tmdb_key() or tmdb_id is None:
        return None

    url = f"{TMDB_BASE_URL}/movie/{tmdb_id}"
    params = {'api_key': TMDB_API_KEY, 'language': 'en-US'}
    response = requests.get(url, params=params, timeout=4)
    if response.status_code == 200:
        return response.json()
    return None


@lru_cache(maxsize=512)
def _search_movie_by_title(title, year=None):
    if not _is_valid_tmdb_key() or not title:
        return None

    url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        'api_key': TMDB_API_KEY,
        'query': title,
        'include_adult': 'false',
        'language': 'en-US'
    }
    if year:
        params['year'] = int(year)

    response = requests.get(url, params=params, timeout=4)
    if response.status_code != 200:
        return None

    results = response.json().get('results', [])
    if not results:
        return None

    # Choose best match instead of blindly taking the first hit.
    ranked = sorted(
        results,
        key=lambda r: (
            _title_similarity(title, r.get('title', '')),
            1 if _title_year_match(title, year, r.get('title', ''), r.get('release_date')) else 0,
            float(r.get('vote_count', 0) or 0)
        ),
        reverse=True
    )

    best = ranked[0]
    if _title_similarity(title, best.get('title', '')) >= 0.65:
        return best
    return None


def fetch_tmdb_poster(tmdb_id, title=None, year=None):
    """
    Fetch movie poster URL from TMDB API or use known posters.
    
    Args:
        tmdb_id: int, TMDB movie ID
    
    Returns:
        str, poster URL or placeholder
    """
    if pd.isna(tmdb_id):
        tmdb_id = None

    if tmdb_id is not None:
        tmdb_id = int(tmdb_id)
    
    try:
        # API-first approach: fetch by TMDB ID.
        if tmdb_id is not None:
            movie_details = _fetch_movie_details_by_id(tmdb_id)
            if (
                movie_details and
                movie_details.get('poster_path') and
                _title_year_match(
                    title,
                    year,
                    movie_details.get('title', ''),
                    movie_details.get('release_date')
                )
            ):
                return f"{TMDB_IMAGE_BASE_URL}{movie_details['poster_path']}"

        # Fallback for stale/wrong IDs in local dataset: search by title/year.
        search_hit = _search_movie_by_title(title, year)
        if search_hit and search_hit.get('poster_path'):
            return f"{TMDB_IMAGE_BASE_URL}{search_hit['poster_path']}"

        # Offline fallback: local known poster map.
        if tmdb_id is not None and tmdb_id in KNOWN_POSTERS:
            return f"{TMDB_IMAGE_BASE_URL}{KNOWN_POSTERS[tmdb_id]}"
    
    except Exception as e:
        print(f"Warning: Could not fetch poster for TMDB ID {tmdb_id}: {e}")
    
    return PLACEHOLDER_POSTER_URL


@lru_cache(maxsize=256)
def _discover_tmdb_movies(emotion, page, min_vote_count, min_rating, year_from, year_to):
    if not _is_valid_tmdb_key():
        return []

    genre_ids = TMDB_DISCOVER_GENRES.get(emotion, TMDB_DISCOVER_GENRES['neutral'])
    url = f"{TMDB_BASE_URL}/discover/movie"
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US',
        'include_adult': 'false',
        'include_video': 'false',
        'sort_by': 'vote_average.desc',
        'vote_count.gte': min_vote_count,
        'vote_average.gte': min_rating,
        'with_genres': genre_ids,
        'page': page,
    }
    if year_from:
        params['primary_release_date.gte'] = f'{year_from}-01-01'
    if year_to:
        params['primary_release_date.lte'] = f'{year_to}-12-31'

    response = requests.get(url, params=params, timeout=4)
    if response.status_code != 200:
        return []

    return response.json().get('results', [])


def _fetch_extra_tmdb_recommendations(emotion, needed_count, existing_titles, discover_filters=None):
    extras = []
    seen_titles = {_normalize_title(title) for title in existing_titles if title}
    filters = _normalize_discover_filters(discover_filters)

    # 3 pages gives enough pool without slowing down response too much.
    for page in (1, 2, 3):
        if len(extras) >= needed_count:
            break

        for movie in _discover_tmdb_movies(
            emotion,
            page,
            filters['min_vote_count'],
            filters['min_rating'],
            filters['year_from'] or 0,
            filters['year_to'] or 0,
        ):
            norm_title = _normalize_title(movie.get('title', ''))
            poster_path = movie.get('poster_path')
            release_date = movie.get('release_date') or ''
            year = int(release_date[:4]) if release_date[:4].isdigit() else 0
            rating = float(movie.get('vote_average', 0.0) or 0.0)

            if not norm_title or norm_title in seen_titles or not poster_path:
                continue
            if rating < filters['min_rating']:
                continue
            if filters['year_from'] and (year == 0 or year < filters['year_from']):
                continue
            if filters['year_to'] and (year == 0 or year > filters['year_to']):
                continue

            extras.append({
                'id': int(movie.get('id', 0) or 0),
                'title': movie.get('title', 'Untitled'),
                'year': year,
                'genre': emotion.title(),
                'overview': movie.get('overview', '') or 'Overview unavailable.',
                'rating': rating,
                'poster_url': f"{TMDB_IMAGE_BASE_URL}{poster_path}",
                'source': 'tmdb_discover',
            })
            seen_titles.add(norm_title)

            if len(extras) >= needed_count:
                break

    return extras


def get_recommendations(
    emotion,
    top_n=None,
    csv_path='data/movies_dataset.csv',
    include_debug=False,
    discover_filters=None,
):
    """
    Get movie recommendations using hybrid approach.
    
    Process:
    1. Filter movies by emotion tag
    2. Vectorize genre + overview using TF-IDF
    3. Rank by cosine similarity
    4. Fetch TMDB posters
    5. Return top N movies
    
    Args:
        emotion: str, detected emotion
        top_n: int, number of recommendations to return
        csv_path: str, path to movie dataset
    
    Returns:
        list of dicts with movie details
    """
    # Clamp recommendation count to supported range; default is dynamic.
    if top_n is None:
        top_n = random.randint(MIN_RECOMMENDATIONS, MAX_RECOMMENDATIONS)
    else:
        try:
            top_n = int(top_n)
        except (TypeError, ValueError):
            top_n = random.randint(MIN_RECOMMENDATIONS, MAX_RECOMMENDATIONS)
    top_n = max(MIN_RECOMMENDATIONS, min(MAX_RECOMMENDATIONS, top_n))

    # Normalize emotion
    emotion = emotion.lower().strip()
    
    # Get movies for this emotion
    movies_df = get_movies_by_emotion(emotion, csv_path)
    
    if len(movies_df) == 0:
        # Fallback to neutral if no movies found
        print(f"Warning: No movies found for emotion '{emotion}', falling back to 'neutral'")
        movies_df = get_movies_by_emotion('neutral', csv_path)
        
        if len(movies_df) == 0:
            print("Error: No movies found even for neutral emotion")
            return []
    
    profile = _get_emotion_profile(emotion)

    # Keep one best entry per title to avoid duplicate recommendations.
    movies_df = (
        movies_df.sort_values(['rating', 'year'], ascending=[False, False])
        .drop_duplicates(subset=['title'], keep='first')
    )

    # Create combined text for TF-IDF
    movies_df = movies_df.copy()
    movies_df['combined_text'] = (
        movies_df['title'].fillna('') + ' ' +
        movies_df['genre'].fillna('') + ' ' +
        movies_df['overview'].fillna('')
    )
    
    # TF-IDF Vectorization
    tfidf = TfidfVectorizer(
        max_features=500,
        stop_words='english',
        ngram_range=(1, 2)
    )
    
    try:
        tfidf_matrix = tfidf.fit_transform(movies_df['combined_text'])
    except Exception as e:
        print(f"Warning: TF-IDF failed: {e}. Using rating-based ranking.")
        # Simple fallback: sort by rating
        top_movies = movies_df.nlargest(top_n, 'rating')
        return format_recommendations(top_movies, include_debug=include_debug)
    
    # Compute relevance by comparing each movie vector to the centroid vector.
    centroid = np.asarray(tfidf_matrix.mean(axis=0))
    similarities = cosine_similarity(tfidf_matrix, centroid).flatten()
    movies_df['similarity'] = similarities

    # Hybrid ranking: similarity + rating + light recency boost.
    rating_min = movies_df['rating'].min()
    rating_max = movies_df['rating'].max()
    if rating_max > rating_min:
        movies_df['rating_norm'] = (movies_df['rating'] - rating_min) / (rating_max - rating_min)
    else:
        movies_df['rating_norm'] = 0.5

    year_min = movies_df['year'].min()
    year_max = movies_df['year'].max()
    if year_max > year_min:
        movies_df['year_norm'] = (movies_df['year'] - year_min) / (year_max - year_min)
    else:
        movies_df['year_norm'] = 0.5

    # Mild genre affinity boost, customizable per emotion profile.
    preferred_genres = profile['preferred_genres']
    if preferred_genres:
        movies_df['genre_affinity'] = movies_df['genre'].fillna('').str.lower().apply(
            lambda g: 1.0 if any(tag in g for tag in preferred_genres) else 0.0
        )
    else:
        movies_df['genre_affinity'] = 0.0

    weights = profile['weights']
    movies_df['hybrid_score'] = (
        weights['similarity'] * movies_df['similarity'] +
        weights['rating'] * movies_df['rating_norm'] +
        weights['year'] * movies_df['year_norm'] +
        0.05 * movies_df['genre_affinity']
    )

    # Diversity-aware selection: avoid returning many movies with identical primary genre.
    ranked_df = movies_df.sort_values('hybrid_score', ascending=False)
    top_movies = _select_diverse_movies(
        ranked_df,
        top_n=min(top_n, len(ranked_df)),
        max_per_primary_genre=profile['max_per_primary_genre']
    ).sort_values('hybrid_score', ascending=False)
    
    # Format local recommendations and enrich with TMDB-discovered movies if needed.
    recommendations = format_recommendations(top_movies, include_debug=include_debug)

    if len(recommendations) < top_n:
        needed = top_n - len(recommendations)
        existing_titles = [movie.get('title') for movie in recommendations]
        recommendations.extend(
            _fetch_extra_tmdb_recommendations(
                emotion,
                needed,
                existing_titles,
                discover_filters=discover_filters,
            )
        )

    return recommendations[:top_n]


def format_recommendations(movies_df, include_debug=False):
    """
    Format movie DataFrame into recommendation list.
    
    Args:
        movies_df: pandas DataFrame
    
    Returns:
        list of dicts
    """
    recommendations = []

    rows = [row for _, row in movies_df.iterrows()]

    def build_item(movie):
        tmdb_id = movie.get('tmdb_id')
        title = movie.get('title')
        year = movie.get('year')
        poster_url = fetch_tmdb_poster(tmdb_id, title=title, year=year)

        item = {
            'id': int(movie['id']),
            'title': movie['title'],
            'year': int(movie['year']),
            'genre': movie['genre'],
            'overview': movie['overview'],
            'rating': float(movie['rating']),
            'poster_url': poster_url,
            'source': 'local_dataset',
        }

        if include_debug:
            item['debug_scores'] = {
                'similarity': float(movie.get('similarity', 0.0) or 0.0),
                'rating_norm': float(movie.get('rating_norm', 0.0) or 0.0),
                'year_norm': float(movie.get('year_norm', 0.0) or 0.0),
                'genre_affinity': float(movie.get('genre_affinity', 0.0) or 0.0),
                'hybrid_score': float(movie.get('hybrid_score', 0.0) or 0.0),
            }

        return item

    # Poster requests are network-bound; parallelize to reduce page latency.
    workers = max(1, min(8, len(rows)))
    if workers == 1:
        recommendations = [build_item(movie) for movie in rows]
    else:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            recommendations = list(executor.map(build_item, rows))
    
    return recommendations


def get_diverse_recommendations(emotion, top_n=10):
    """
    Get diverse recommendations by mixing high-rated and varied genres.
    
    Args:
        emotion: str
        top_n: int
    
    Returns:
        list of dicts
    """
    movies_df = get_movies_by_emotion(emotion)
    
    if len(movies_df) == 0:
        return []
    
    # Split into high-rated (top 40%) and others
    split_idx = max(1, int(len(movies_df) * 0.4))
    
    high_rated = movies_df.nlargest(split_idx, 'rating')
    others = movies_df.nsmallest(len(movies_df) - split_idx, 'rating')
    
    # Take 70% from high-rated, 30% from others for diversity
    n_high = int(top_n * 0.7)
    n_others = top_n - n_high
    
    selected_high = high_rated.head(min(n_high, len(high_rated)))
    selected_others = others.head(min(n_others, len(others)))
    
    # Combine and shuffle
    combined = pd.concat([selected_high, selected_others])
    combined = combined.sample(frac=1).reset_index(drop=True)  # Shuffle
    
    return format_recommendations(combined.head(top_n))
