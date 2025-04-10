# emotions.py
EMOTION_THRESHOLDS = {
    "depressed": (0, 6),
    "neutral": (7, 12),
    "positive": (13, 18)
}

def calculate_emotion(answers: list[int]) -> dict:
    total_score = sum(answers)
    
    for emotion, (min_score, max_score) in EMOTION_THRESHOLDS.items():
        if min_score <= total_score <= max_score:
            return {
                "score": total_score,
                "label": emotion,
                "description": get_emotion_description(emotion)
            }

def get_emotion_description(label: str) -> str:
    descriptions = {
        "depressed": "Ваше состояние требует внимания. Рекомендуем обратиться к специалисту.",
        "neutral": "Ваше состояние стабильно. Не забывайте заботиться о себе.",
        "positive": "Отличные показатели! Продолжайте в том же духе!"
    }
    return descriptions.get(label, "Не удалось определить состояние")