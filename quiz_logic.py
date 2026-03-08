# quiz_logic.py

def get_quiz_questions():
    """
    Returns a list of quiz questions with options.
    Each option contributes to a possible emotion outcome.
    """
    return [
        {
            "question": "How do you feel when you wake up in the morning?",
            "options": {
                "Excited": "Happy",
                "Sad or tired": "Sad",
                "Stressed or rushed": "Angry",
                "Anxious or worried": "Fear",
                "Calm or indifferent": "Neutral"
            }
        },
        {
            "question": "What kind of music do you feel like listening to right now?",
            "options": {
                "Upbeat and lively": "Happy",
                "Slow and emotional": "Sad",
                "Heavy or loud": "Angry",
                "None, I feel quiet": "Neutral",
                "Tense or eerie soundtracks": "Fear"
            }
        },
        {
            "question": "Which picture best matches your current mood?",
            "options": {
                "Smiling face": "Happy",
                "Crying face": "Sad",
                "Angry face": "Angry",
                "Scared face": "Fear",
                "Expressionless face": "Neutral"
            }
        },
        {
            "question": "How would you describe your current energy level?",
            "options": {
                "High and energetic": "Happy",
                "Low and drained": "Sad",
                "Frustrated and tense": "Angry",
                "Jumpy or nervous": "Fear",
                "Balanced and calm": "Neutral"
            }
        },
        {
            "question": "What kind of movie would you enjoy right now?",
            "options": {
                "Feel-good comedy": "Happy",
                "Heart-touching drama": "Sad",
                "Action-packed thriller": "Angry",
                "Horror or suspense": "Fear",
                "Chill slice-of-life": "Neutral"
            }
        }
    ]

def analyze_quiz_results(answers):
    """
    Takes a list of selected emotions from quiz answers and returns the most common one.
    :param answers: List of emotion strings
    :return: Detected emotion (str)
    """
    from collections import Counter

    if not answers:
        return "Neutral"

    emotion_count = Counter(answers)
    most_common_emotion = emotion_count.most_common(1)[0][0]

    return most_common_emotion
