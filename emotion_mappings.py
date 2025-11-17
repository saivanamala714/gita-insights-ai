"""
Emotion Mappings for Bhagavad Gita Teachings

This module maps human emotions to relevant teachings from the Bhagavad Gita.
Each emotion includes a teaching, practical advice, and relevant verses.
"""
from typing import Dict, List, Any

# Comprehensive list of human emotions based on Plutchik's Wheel of Emotions
EMOTIONS = [
    # Primary Emotions
    'joy', 'trust', 'fear', 'surprise', 'sadness', 'disgust', 'anger', 'anticipation',
    
    # Secondary Emotions (combinations of primary emotions)
    'love', 'submission', 'awe', 'disapproval', 'remorse', 'contempt', 'aggressiveness', 'optimism',
    
    # Tertiary Emotions
    'serenity', 'acceptance', 'apprehension', 'distraction', 'pensiveness', 'boredom', 'annoyance', 'interest',
    'ecstasy', 'admiration', 'terror', 'amazement', 'grief', 'loathing', 'rage', 'vigilance',
    'joyful', 'trusting', 'fearful', 'surprised', 'sad', 'disgusted', 'angry', 'hopeful',
    
    # Additional Common Emotions
    'anxiety', 'contentment', 'gratitude', 'guilt', 'jealousy', 'pride', 'shame', 'hope',
    'frustration', 'loneliness', 'excitement', 'awe', 'envy', 'pity', 'despair', 'relief',
    'embarrassment', 'disappointment', 'affection', 'compassion', 'satisfaction', 'wonder',
    'confusion', 'regret', 'resentment', 'humiliation', 'happiness', 'misery', 'elation',
    'devastation', 'fulfillment', 'insecurity', 'isolation', 'overwhelm', 'peace', 'vulnerability',
    'bitterness', 'desperation', 'disillusionment', 'empowerment', 'freedom', 'gloom', 'helplessness',
    'inspiration', 'longing', 'melancholy', 'nostalgia', 'panic', 'passion', 'pessimism', 'rage',
    'remorse', 'skepticism', 'tenderness', 'uneasiness', 'worry', 'zeal', 'admiration', 'agitation',
    'amazement', 'amusement', 'anger', 'anguish', 'annoyance', 'anticipation', 'anxiety', 'apathy',
    'apprehension', 'arrogance', 'awe', 'boredom', 'confidence', 'confusion', 'contempt', 'contentment',
    'courage', 'curiosity', 'defeat', 'defensiveness', 'delight', 'depression', 'desire', 'despair',
    'disappointment', 'disapproval', 'disgust', 'dismay', 'displeasure', 'distress', 'doubt', 'dread',
    'eagerness', 'ecstasy', 'elation', 'embarrassment', 'empathy', 'enchantment', 'enjoyment', 'envy',
    'euphoria', 'excitement', 'fear', 'frustration', 'gratitude', 'grief', 'guilt', 'happiness',
    'hate', 'helplessness', 'homesickness', 'hope', 'hopelessness', 'horror', 'hostility', 'humiliation',
    'hurt', 'hysteria', 'indifference', 'insecurity', 'insult', 'interest', 'irritation', 'isolation',
    'jealousy', 'joy', 'loneliness', 'longing', 'love', 'lust', 'misery', 'neglect', 'optimism',
    'outrage', 'panic', 'passion', 'pessimism', 'pity', 'pleasure', 'pride', 'rage', 'regret',
    'rejection', 'relaxation', 'relief', 'reluctance', 'remorse', 'resentment', 'sadness', 'satisfaction',
    'scorn', 'self-pity', 'shame', 'shock', 'sorrow', 'suffering', 'surprise', 'suspicion', 'sympathy',
    'tenderness', 'tension', 'terror', 'thankfulness', 'thrill', 'triumph', 'uncertainty', 'uneasiness',
    'unhappiness', 'vulnerability', 'warmth', 'wonder', 'worry', 'wrath', 'zeal'
]

# Initialize the emotion mappings with empty lists
EMOTION_MAPPINGS = {emotion: [] for emotion in EMOTIONS}

def add_emotion_mapping(emotion: str, teaching: str, advice: str, verses: List[str],
                       example: str = None, related_emotions: List[str] = None) -> None:
    """
    Add a new mapping between an emotion and Gita teaching.
    
    Args:
        emotion: The emotion to map (must be in EMOTIONS list)
        teaching: The core teaching from the Gita
        advice: Practical advice based on the teaching
        verses: List of relevant verse references
        example: Optional example or story from the Gita
        related_emotions: Other related emotions this applies to
    """
    if emotion not in EMOTION_MAPPINGS:
        raise ValueError(f"Emotion '{emotion}' not in recognized emotions list")
    
    mapping = {
        'teaching': teaching,
        'advice': advice,
        'verses': verses,
        'example': example or ""
    }
    
    # Add to the primary emotion
    EMOTION_MAPPINGS[emotion].append(mapping)
    
    # Add to related emotions if specified
    if related_emotions:
        for related in related_emotions:
            if related in EMOTION_MAPPINGS:
                EMOTION_MAPPINGS[related].append(mapping)

def get_emotion_teachings(emotion: str) -> List[Dict[str, Any]]:
    """
    Get all teachings related to a specific emotion.
    
    Args:
        emotion: The emotion to get teachings for
        
    Returns:
        List of teaching dictionaries, or empty list if no teachings found
    """
    return EMOTION_MAPPINGS.get(emotion.lower(), [])

def search_teachings(query: str) -> List[Dict[str, Any]]:
    """
    Search for teachings related to a query string.
    
    Args:
        query: Search term to look for in teachings
        
    Returns:
        List of matching teaching dictionaries
    """
    query = query.lower()
    results = []
    
    for emotion, teachings in EMOTION_MAPPINGS.items():
        for teaching in teachings:
            # Search in teaching text and advice
            if (query in emotion.lower() or
                query in teaching['teaching'].lower() or
                query in teaching['advice'].lower() or
                any(query in verse.lower() for verse in teaching['verses'])):
                results.append({
                    'emotion': emotion,
                    **teaching
                })
    
    return results
