"""
Flask routes for movie recommender app.
"""

import random

from flask import Blueprint, current_app, render_template, request, jsonify, session

from app.services.emotion_service import get_emotion_service
from app.services.recommendation_service import get_recommendation_service
from quiz.questions import get_questions

# Create blueprint
bp = Blueprint('main', __name__)


def _pick_dynamic_top_n(min_n, max_n):
    """Pick a dynamic recommendation count and avoid repeating the previous one."""
    choices = list(range(min_n, max_n + 1))
    previous = session.get('last_top_n')

    if previous in choices and len(choices) > 1:
        choices.remove(previous)

    selected = random.choice(choices)
    session['last_top_n'] = selected
    return selected


def _build_discover_filters_from_request():
    """Build TMDB discover filters from request query params + app config."""
    min_vote_count = request.args.get(
        'min_vote_count',
        current_app.config.get('TMDB_MIN_VOTE_COUNT', 500),
        type=int,
    )
    min_rating = request.args.get(
        'min_rating',
        current_app.config.get('TMDB_MIN_RATING', 6.0),
        type=float,
    )
    year_from = request.args.get('year_from', current_app.config.get('TMDB_YEAR_FROM', ''), type=str)
    year_to = request.args.get('year_to', current_app.config.get('TMDB_YEAR_TO', ''), type=str)

    return {
        'min_vote_count': min_vote_count,
        'min_rating': min_rating,
        'year_from': year_from,
        'year_to': year_to,
    }


@bp.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@bp.route('/quiz')
def quiz():
    """Quiz page."""
    return render_template('quiz.html', questions=get_questions())


@bp.route('/camera')
def camera():
    """Camera page for emotion detection."""
    return render_template('camera.html')


@bp.route('/api/detect-emotion', methods=['POST'])
def detect_emotion():
    """
    API endpoint for emotion detection from image.
    
    Request JSON:
        {
            "image": "base64_encoded_image"
        }
    
    Response JSON:
        {
            "success": true/false,
            "emotion": "happy",
            "confidence": 0.95,
            "message": "..."
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({
                'success': False,
                'message': 'No image provided'
            }), 400
        
        # Get emotion service
        emotion_service = get_emotion_service()
        
        # Detect emotion
        result = emotion_service.detect_emotion_from_base64(data['image'])
        
        # Store emotion in session if successful
        if result['success']:
            session['emotion'] = result['emotion']
            session['confidence'] = result['confidence']
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@bp.route('/api/submit-quiz', methods=['POST'])
def submit_quiz():
    """
    API endpoint for quiz submission.
    
    Request JSON:
        {
            "answers": {
                "1": "a",
                "2": "c",
                ...
            }
        }
    
    Response JSON:
        {
            "success": true/false,
            "emotion": "happy",
            "message": "..."
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'answers' not in data:
            return jsonify({
                'success': False,
                'message': 'No answers provided'
            }), 400
        
        answers = data['answers']
        
        # Get recommendation service
        rec_service = get_recommendation_service()
        
        # Get emotion from quiz (just for validation)
        from quiz.quiz_engine import get_emotion_from_answers
        emotion_result = get_emotion_from_answers(answers)
        
        if not emotion_result['valid']:
            return jsonify({
                'success': False,
                'message': emotion_result.get('error', 'Invalid quiz answers')
            }), 400
        
        # Store emotion in session
        session['emotion'] = emotion_result['emotion']
        session['emotion_scores'] = emotion_result['scores']
        
        return jsonify({
            'success': True,
            'emotion': emotion_result['emotion'],
            'message': 'Quiz submitted successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@bp.route('/api/recommendations')
def get_recommendations_api():
    """
    API endpoint to get movie recommendations.
    
    Query params:
        emotion: str (optional, uses session if not provided)
        top_n: int (optional, default from config)
    
    Response JSON:
        {
            "success": true/false,
            "emotion": "happy",
            "movies": [...],
            "count": 12,
            "message": "..."
        }
    """
    try:
        # Get emotion from query param or session
        emotion = request.args.get('emotion')
        
        if not emotion:
            emotion = session.get('emotion')
        
        if not emotion:
            return jsonify({
                'success': False,
                'message': 'No emotion provided. Please complete quiz or camera detection first.'
            }), 400
        
        # If top_n is omitted, choose a dynamic count.
        min_n = current_app.config.get('MIN_RECOMMENDATIONS', 12)
        max_n = current_app.config.get('MAX_RECOMMENDATIONS', 20)
        top_n = request.args.get('top_n', type=int)
        if top_n is not None:
            top_n = max(min_n, min(max_n, top_n))
        else:
            top_n = _pick_dynamic_top_n(min_n, max_n)
        
        # Get recommendation service
        rec_service = get_recommendation_service()
        
        discover_filters = _build_discover_filters_from_request()

        # Get recommendations
        result = rec_service.get_recommendations_from_emotion(
            emotion,
            top_n,
            discover_filters=discover_filters,
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@bp.route('/api/recommendations/debug')
def get_recommendations_debug_api():
    """
    Debug API endpoint to get recommendations with score breakdown.

    Query params:
        emotion: str (optional, uses session if not provided)
        top_n: int (optional, default 10)
    """
    try:
        emotion = request.args.get('emotion')

        if not emotion:
            emotion = session.get('emotion')

        if not emotion:
            return jsonify({
                'success': False,
                'message': 'No emotion provided. Please complete quiz or camera detection first.'
            }), 400

        min_n = current_app.config.get('MIN_RECOMMENDATIONS', 12)
        max_n = current_app.config.get('MAX_RECOMMENDATIONS', 20)
        top_n = request.args.get('top_n', type=int)
        if top_n is not None:
            top_n = max(min_n, min(max_n, top_n))
        else:
            top_n = _pick_dynamic_top_n(min_n, max_n)

        discover_filters = _build_discover_filters_from_request()

        rec_service = get_recommendation_service()
        result = rec_service.get_recommendations_from_emotion(
            emotion,
            top_n,
            include_debug=True,
            discover_filters=discover_filters,
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@bp.route('/results')
def results():
    """
    Results page showing movie recommendations.
    Uses emotion from session.
    """
    emotion = session.get('emotion')
    confidence = session.get('confidence')
    
    if not emotion:
        return render_template('index.html', error='No emotion detected. Please try again.')
    
    # Get recommendations (dynamic count unless top_n query param is provided).
    rec_service = get_recommendation_service()
    min_n = current_app.config.get('MIN_RECOMMENDATIONS', 12)
    max_n = current_app.config.get('MAX_RECOMMENDATIONS', 20)
    top_n = request.args.get('top_n', type=int)
    if top_n is not None:
        top_n = max(min_n, min(max_n, top_n))
    else:
        top_n = _pick_dynamic_top_n(min_n, max_n)
    discover_filters = _build_discover_filters_from_request()
    result = rec_service.get_recommendations_from_emotion(
        emotion,
        top_n=top_n,
        discover_filters=discover_filters,
    )
    
    return render_template(
        'result.html',
        emotion=emotion,
        confidence=confidence,
        movies=result.get('movies', []),
        success=result['success'],
        message=result.get('message', '')
    )


@bp.route('/api/session-info')
def session_info():
    """API endpoint to get session information."""
    return jsonify({
        'emotion': session.get('emotion'),
        'confidence': session.get('confidence'),
        'has_emotion': 'emotion' in session
    })


@bp.route('/api/clear-session', methods=['POST'])
def clear_session():
    """API endpoint to clear session."""
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Session cleared'
    })
