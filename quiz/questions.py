"""
Quiz questions with weighted emotion scores.
Each option maps to emotion probabilities.
"""

QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "How do you feel when you wake up in the morning?",
        "options": [
            {
                "text": "Excited and energized",
                "weights": {"happy": 0.8, "surprise": 0.1, "neutral": 0.1}
            },
            {
                "text": "Sad or tired",
                "weights": {"sad": 0.7, "neutral": 0.2, "disgust": 0.1}
            },
            {
                "text": "Stressed or rushed",
                "weights": {"angry": 0.6, "fear": 0.2, "sad": 0.2}
            },
            {
                "text": "Anxious or worried",
                "weights": {"fear": 0.7, "sad": 0.2, "neutral": 0.1}
            },
            {
                "text": "Calm and indifferent",
                "weights": {"neutral": 0.9, "happy": 0.1}
            }
        ]
    },
    {
        "id": 2,
        "question": "What kind of music are you in the mood for right now?",
        "options": [
            {
                "text": "Upbeat and lively music",
                "weights": {"happy": 0.8, "surprise": 0.1, "neutral": 0.1}
            },
            {
                "text": "Slow and emotional ballads",
                "weights": {"sad": 0.8, "neutral": 0.1, "happy": 0.1}
            },
            {
                "text": "Heavy metal or aggressive music",
                "weights": {"angry": 0.7, "disgust": 0.2, "fear": 0.1}
            },
            {
                "text": "Calm instrumental or ambient",
                "weights": {"neutral": 0.7, "happy": 0.2, "sad": 0.1}
            },
            {
                "text": "Tense or eerie soundtracks",
                "weights": {"fear": 0.6, "disgust": 0.2, "surprise": 0.2}
            }
        ]
    },
    {
        "id": 3,
        "question": "How would you describe your current energy level?",
        "options": [
            {
                "text": "High and energetic",
                "weights": {"happy": 0.6, "surprise": 0.2, "angry": 0.2}
            },
            {
                "text": "Low and drained",
                "weights": {"sad": 0.8, "fear": 0.1, "neutral": 0.1}
            },
            {
                "text": "Frustrated and tense",
                "weights": {"angry": 0.7, "disgust": 0.2, "fear": 0.1}
            },
            {
                "text": "Jumpy or nervous",
                "weights": {"fear": 0.7, "surprise": 0.2, "angry": 0.1}
            },
            {
                "text": "Balanced and calm",
                "weights": {"neutral": 0.8, "happy": 0.2}
            }
        ]
    },
    {
        "id": 4,
        "question": "What kind of movie would you enjoy right now?",
        "options": [
            {
                "text": "Feel-good comedy",
                "weights": {"happy": 0.9, "neutral": 0.1}
            },
            {
                "text": "Heart-touching drama",
                "weights": {"sad": 0.8, "neutral": 0.2}
            },
            {
                "text": "Action-packed thriller",
                "weights": {"angry": 0.5, "surprise": 0.3, "fear": 0.2}
            },
            {
                "text": "Horror or suspense",
                "weights": {"fear": 0.7, "disgust": 0.2, "surprise": 0.1}
            },
            {
                "text": "Chill slice-of-life",
                "weights": {"neutral": 0.7, "happy": 0.3}
            }
        ]
    },
    {
        "id": 5,
        "question": "How do you typically react to unexpected situations?",
        "options": [
            {
                "text": "I get excited and curious",
                "weights": {"surprise": 0.6, "happy": 0.3, "neutral": 0.1}
            },
            {
                "text": "I feel anxious and worried",
                "weights": {"fear": 0.7, "sad": 0.2, "angry": 0.1}
            },
            {
                "text": "I get annoyed or frustrated",
                "weights": {"angry": 0.7, "disgust": 0.2, "fear": 0.1}
            },
            {
                "text": "I stay calm and adapt",
                "weights": {"neutral": 0.8, "happy": 0.1, "surprise": 0.1}
            },
            {
                "text": "I feel overwhelmed",
                "weights": {"sad": 0.5, "fear": 0.3, "disgust": 0.2}
            }
        ]
    }
]


def get_questions():
    """
    Get all quiz questions.
    
    Returns:
        List of question dictionaries
    """
    return QUIZ_QUESTIONS


def get_question_by_id(question_id):
    """
    Get a specific question by ID.
    
    Args:
        question_id: int, question ID
    
    Returns:
        Question dict or None
    """
    for question in QUIZ_QUESTIONS:
        if question['id'] == question_id:
            return question
    return None
