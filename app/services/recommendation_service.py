"""
Movie recommendation service for Flask app.
"""

import random

from quiz.quiz_engine import get_emotion_from_answers
from recommender.hybrid_recommender import get_recommendations


class RecommendationService:
    """Service for movie recommendations."""
    
    def __init__(self, csv_path='data/movies_dataset.csv'):
        """
        Initialize recommendation service.
        
        Args:
            csv_path: str, path to movies CSV
        """
        self.csv_path = csv_path
        self.min_recommendations = 12
        self.max_recommendations = 20

    def _normalize_top_n(self, top_n):
        """Return clamped count or dynamic count if not provided."""
        if top_n is None:
            return random.randint(self.min_recommendations, self.max_recommendations)

        try:
            requested = int(top_n)
        except (TypeError, ValueError):
            return random.randint(self.min_recommendations, self.max_recommendations)

        return max(self.min_recommendations, min(self.max_recommendations, requested))
    
    def get_recommendations_from_emotion(
        self,
        emotion,
        top_n=None,
        include_debug=False,
        discover_filters=None,
    ):
        """
        Get movie recommendations based on emotion.
        
        Args:
            emotion: str, detected emotion
            top_n: int, number of recommendations
            include_debug: bool, include scoring breakdown per movie
            discover_filters: dict, TMDB discover filter overrides
        
        Returns:
            dict with 'success', 'emotion', 'movies', 'message'
        """
        try:
            top_n = self._normalize_top_n(top_n)

            movies = get_recommendations(
                emotion=emotion,
                top_n=top_n,
                csv_path=self.csv_path,
                include_debug=include_debug,
                discover_filters=discover_filters,
            )
            
            response = {
                'success': True,
                'emotion': emotion,
                'movies': movies,
                'count': len(movies),
                'message': f'Found {len(movies)} movies for {emotion} emotion'
            }

            if include_debug:
                response['debug'] = {
                    'include_debug': True,
                    'note': 'Each movie includes debug_scores for tuning.'
                }

            return response
        
        except Exception as e:
            return {
                'success': False,
                'emotion': emotion,
                'movies': [],
                'count': 0,
                'message': f'Error getting recommendations: {str(e)}'
            }
    
    def get_recommendations_from_quiz(self, answers, top_n=None, discover_filters=None):
        """
        Get movie recommendations based on quiz answers.
        
        Args:
            answers: dict, quiz answers (question_id -> option_id)
            top_n: int, number of recommendations
        
        Returns:
            dict with 'success', 'emotion', 'movies', 'message'
        """
        try:
            top_n = self._normalize_top_n(top_n)

            # Calculate emotion from quiz
            emotion_result = get_emotion_from_answers(answers)
            
            if not emotion_result['valid']:
                return {
                    'success': False,
                    'emotion': None,
                    'movies': [],
                    'count': 0,
                    'message': emotion_result.get('error', 'Invalid quiz answers')
                }
            
            emotion = emotion_result['emotion']
            
            # Get recommendations
            return self.get_recommendations_from_emotion(
                emotion,
                top_n,
                discover_filters=discover_filters,
            )
        
        except Exception as e:
            return {
                'success': False,
                'emotion': None,
                'movies': [],
                'count': 0,
                'message': f'Error processing quiz: {str(e)}'
            }


# Global instance (singleton)
_recommendation_service = None


def get_recommendation_service(csv_path='data/movies_dataset.csv'):
    """
    Get recommendation service singleton.
    
    Args:
        csv_path: str, movies dataset path
    
    Returns:
        RecommendationService instance
    """
    global _recommendation_service
    
    if _recommendation_service is None:
        _recommendation_service = RecommendationService(csv_path)
    
    return _recommendation_service
