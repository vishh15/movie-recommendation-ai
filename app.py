from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from keras.models import load_model
from recommendation_engine import get_recommendations
from quiz_logic import analyze_quiz_results, get_quiz_questions
from emotion_detector import detect_emotion_from_webcam

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a strong secret key!

# Disable caching for development
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# Load pre-trained emotion detection model
model = load_model('model/emotion_model.h5')

# Emotion labels (same order as the model's output)
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/quiz')
def quiz():
    # Get quiz questions and transform to template format
    raw_questions = get_quiz_questions()
    questions = []
    for idx, q in enumerate(raw_questions):
        questions.append({
            'id': idx,
            'question': q['question'],
            'options': [{'text': option_text, 'emotion': emotion} for option_text, emotion in q['options'].items()]
        })
    return render_template('quiz.html', questions=questions)

@app.route('/camera')
def camera():
    return render_template('camera.html')


@app.route('/api/submit-quiz', methods=['POST'])
def submit_quiz():
    """Handle quiz submission from the new premium UI"""
    try:
        answers_dict = request.json.get('answers', {})
        
        if not answers_dict:
            return jsonify({'success': False, 'message': 'No answers provided'}), 400
        
        # Get quiz questions to map answers to emotions
        raw_questions = get_quiz_questions()
        emotions = []
        
        for idx, q in enumerate(raw_questions):
            answer_idx = answers_dict.get(str(idx))
            if answer_idx is not None:
                option_list = list(q['options'].items())
                if int(answer_idx) < len(option_list):
                    _, emotion = option_list[int(answer_idx)]
                    emotions.append(emotion)
        
        if not emotions:
            return jsonify({'success': False, 'message': 'Invalid answers'}), 400
        
        # Analyze emotions and persist only lightweight result metadata in session
        detected_emotion = analyze_quiz_results(emotions)
        
        session['quiz_result'] = {
            'emotion': detected_emotion,
            'success': True
        }
        
        return jsonify({'success': True, 'emotion': detected_emotion})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/quiz-result', methods=['POST'])
def quiz_result():
    """Traditional form POST endpoint - works without JavaScript"""
    # Handle both form data and JSON
    if request.is_json:
        answers = request.json.get('answers', [])
    else:
        # Traditional form submission
        answers = {}
        raw_questions = get_quiz_questions()
        for idx, q in enumerate(raw_questions):
            form_key = f'q{idx}'
            if form_key in request.form:
                option_list = list(q['options'].items())
                answer_idx = int(request.form[form_key])
                if answer_idx < len(option_list):
                    _, emotion = option_list[answer_idx]
                    if idx not in answers:
                        answers[idx] = []
                    answers[idx].append(emotion)
        
        # Flatten the emotions list
        all_emotions = []
        for emotion_list in answers.values():
            all_emotions.extend(emotion_list)
        
        if not all_emotions:
            return redirect(url_for('quiz'))
        
        detected_emotion = analyze_quiz_results(all_emotions)
        
        # Save in session
        session['quiz_result'] = {
            'emotion': detected_emotion,
            'success': True
        }
        
        # Redirect to results page
        return redirect(url_for('results'))
    
    # JSON handling for backward compatibility
    if not answers or not isinstance(answers, list):
        return jsonify({'success': False, 'error': 'Invalid answers format'}), 400
    
    emotion = analyze_quiz_results(answers)

    session['quiz_result'] = {
        'emotion': emotion,
        'success': True
    }

    return jsonify({'success': True})

@app.route('/result')
def result():
    result_data = session.get('quiz_result')
    if not result_data:
        # Redirect to quiz if no result in session
        return redirect(url_for('quiz'))
    
    emotion = result_data.get('emotion', 'Unknown')
    success = result_data.get('success', True)
    confidence = result_data.get('confidence')
    
    # Recompute movies from emotion to avoid oversized session payload issues.
    movies = get_recommendations(emotion)
    if not isinstance(movies, list):
        movies = []

    unique_genres = set()
    for movie in movies:
        if isinstance(movie, dict):
            genre_text = movie.get('genre', '')
            for part in str(genre_text).split(','):
                cleaned = part.strip()
                if cleaned:
                    unique_genres.add(cleaned)
    genre_count = len(unique_genres)

    return render_template(
        'result.html',
        emotion=emotion,
        movies=movies,
        success=success,
        confidence=confidence,
        genre_count=genre_count
    )

@app.route('/results')
def results():
    """Alias route for /result to match frontend links"""
    return result()

@app.route('/api/detect-emotion', methods=['POST'])
def api_detect_emotion():
    """Handle camera emotion detection from premium UI"""
    try:
        image_data = request.json.get('image')
        if not image_data:
            return jsonify({'success': False, 'message': 'No image provided'}), 400
        
        # Here you would process the base64 image
        # For now, simulating with the webcam detector
        result = detect_emotion_from_webcam()
        
        if 'error' in result:
            return jsonify({'success': False, 'message': result['error']}), 400
        
        emotion = result.get('emotion', 'Neutral')
        confidence = result.get('confidence', 0.0)
        
        # Save lightweight data only; recommendations are generated in /result.
        session['quiz_result'] = {
            'emotion': emotion,
            'confidence': confidence,
            'success': True
        }
        
        return jsonify({
            'success': True,
            'emotion': emotion,
            'confidence': confidence
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/detect-emotion', methods=['POST'])
def detect_emotion():
    try:
        result = detect_emotion_from_webcam()
        if 'error' in result:
            return jsonify(result), 400

        emotion = result.get('emotion', 'Neutral')
        movies = get_recommendations(emotion)
        
        # Save lightweight data only; recommendations are generated in /result.
        session['quiz_result'] = {
            'emotion': emotion,
            'success': True
        }
        
        return jsonify({'emotion': emotion, 'movies': movies})
    except Exception as e:
        return jsonify({'error': f'Failed to detect emotion: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
