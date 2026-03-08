"""
Quiz engine for calculating emotions from weighted quiz answers.
"""

from collections import defaultdict
from quiz.questions import get_questions


def _normalize_answers_to_indices(answers):
    """Convert incoming quiz answers to an ordered list of option indices."""
    questions = get_questions()

    if isinstance(answers, list):
        return answers

    if isinstance(answers, dict):
        ordered = []
        for question in questions:
            qid = question['id']
            if qid not in answers and str(qid) not in answers:
                raise ValueError(f"Missing answer for question {qid}")

            raw_value = answers.get(qid, answers.get(str(qid)))
            if isinstance(raw_value, str):
                if not raw_value.isdigit():
                    raise ValueError(f"Answer for question {qid} must be an integer index")
                raw_value = int(raw_value)

            if not isinstance(raw_value, int):
                raise ValueError(f"Answer for question {qid} must be an integer index")

            ordered.append(raw_value)

        return ordered

    raise ValueError("Answers must be a list or dict")


def calculate_emotion(answers):
    """
    Calculate emotion from quiz answers using weighted scoring.
    
    Args:
        answers: List of selected option indices (0-based) for each question
                 Example: [0, 1, 2, 0, 1] means option 0 for Q1, option 1 for Q2, etc.
    
    Returns:
        dict with 'emotion' (str), 'confidence' (float), 'scores' (dict)
    """
    if not answers or len(answers) == 0:
        return {
            'emotion': 'neutral',
            'confidence': 0.5,
            'scores': {}
        }
    
    questions = get_questions()
    
    # Validate answers length
    if len(answers) != len(questions):
        # Pad or truncate if needed
        while len(answers) < len(questions):
            answers.append(0)  # Default to first option
        answers = answers[:len(questions)]
    
    # Aggregate emotion scores
    emotion_scores = defaultdict(float)
    total_weight = 0
    
    for question_idx, answer_idx in enumerate(answers):
        if question_idx >= len(questions):
            break
        
        question = questions[question_idx]
        options = question['options']
        
        # Validate answer index
        if answer_idx < 0 or answer_idx >= len(options):
            answer_idx = 0  # Default to first option
        
        selected_option = options[answer_idx]
        weights = selected_option['weights']
        
        # Add weighted scores
        for emotion, weight in weights.items():
            emotion_scores[emotion] += weight
            total_weight += weight
    
    # Normalize scores
    if total_weight > 0:
        for emotion in emotion_scores:
            emotion_scores[emotion] /= total_weight
    
    # Find dominant emotion
    if not emotion_scores:
        return {
            'emotion': 'neutral',
            'confidence': 0.5,
            'scores': {}
        }
    
    dominant_emotion = max(emotion_scores, key=emotion_scores.get)
    confidence = emotion_scores[dominant_emotion]
    
    return {
        'emotion': dominant_emotion,
        'confidence': confidence,
        'scores': dict(emotion_scores)
    }


def validate_answers(answers):
    """
    Validate quiz answers format.
    
    Args:
        answers: Answer data to validate
    
    Returns:
        tuple (is_valid, error_message)
    """
    questions = get_questions()

    try:
        answer_list = _normalize_answers_to_indices(answers)
    except ValueError as exc:
        return False, str(exc)

    if len(answer_list) == 0:
        return False, "No answers provided"

    if len(answer_list) != len(questions):
        return False, f"Expected {len(questions)} answers, got {len(answer_list)}"

    for idx, answer in enumerate(answer_list):
        if not isinstance(answer, int):
            return False, f"Answer {idx+1} must be an integer"

        if idx < len(questions):
            question = questions[idx]
            num_options = len(question['options'])
            if answer < 0 or answer >= num_options:
                return False, f"Answer {idx+1} out of range (0-{num_options-1})"
    
    return True, None


def get_emotion_from_answers(answers):
    """
    Convenience function to get emotion directly from answers.
    
    Args:
        answers: List of answer indices
    
    Returns:
        str, emotion label
    """
    is_valid, error = validate_answers(answers)
    if not is_valid:
        return {
            'valid': False,
            'error': error,
            'emotion': None,
            'confidence': 0.0,
            'scores': {}
        }

    answer_list = _normalize_answers_to_indices(answers)
    result = calculate_emotion(answer_list)

    return {
        'valid': True,
        'error': None,
        'emotion': result['emotion'],
        'confidence': result['confidence'],
        'scores': result['scores']
    }
