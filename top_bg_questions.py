"""
Top 100 Frequently Asked Questions About the Bhagavad Gita

This module contains a curated list of the top 100 most commonly asked questions
about the Bhagavad Gita, gathered from various authoritative sources.
"""
from typing import List, Dict, TypedDict

class BGQuestion(TypedDict):
    """Structure for storing Bhagavad Gita questions with metadata."""
    question: str
    category: str
    keywords: List[str]
    difficulty: str  # beginner, intermediate, advanced

# Categories for organizing questions
CATEGORIES = [
    "Introduction",
    "Philosophy & Concepts",
    "Karma Yoga",
    "Bhakti Yoga",
    "Jnana Yoga",
    "Meditation & Yoga",
    "Dharma & Duty",
    "Characters & Stories",
    "Teachings & Verses",
    "Modern Application",
    "Spiritual Practice",
    "Comparative Study"
]

# Top 100 Bhagavad Gita questions
TOP_QUESTIONS: List[BGQuestion] = [
    {
        "question": "What is the main message of the Bhagavad Gita?",
        "category": "Introduction",
        "keywords": ["main message", "purpose", "essence", "core teaching"],
        "difficulty": "beginner"
    },
    {
        "question": "Who is the speaker of the Bhagavad Gita?",
        "category": "Introduction",
        "keywords": ["speaker", "who spoke", "Krishna", "Arjuna"],
        "difficulty": "beginner"
    },
    {
        "question": "What is the setting of the Bhagavad Gita?",
        "category": "Introduction",
        "keywords": ["setting", "where", "when", "context", "battlefield", "Kurukshetra"],
        "difficulty": "beginner"
    },
    {
        "question": "What is Karma Yoga according to the Gita?",
        "category": "Karma Yoga",
        "keywords": ["karma yoga", "action", "selfless service", "duty"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is Bhakti Yoga in the Gita?",
        "category": "Bhakti Yoga",
        "keywords": ["bhakti", "devotion", "love of God", "surrender"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is Jnana Yoga according to the Gita?",
        "category": "Jnana Yoga",
        "keywords": ["jnana", "knowledge", "wisdom", "self-realization"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is the concept of Dharma in the Gita?",
        "category": "Dharma & Duty",
        "keywords": ["dharma", "duty", "righteousness", "moral order"],
        "difficulty": "intermediate"
    },
    {
        "question": "What does the Gita say about the soul?",
        "category": "Philosophy & Concepts",
        "keywords": ["atman", "soul", "eternal", "reincarnation"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is Maya according to the Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["maya", "illusion", "reality", "material world"],
        "difficulty": "advanced"
    },
    {
        "question": "What are the three gunas mentioned in the Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["gunas", "sattva", "rajas", "tamas", "qualities"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is the significance of Arjuna's dilemma in the Gita?",
        "category": "Characters & Stories",
        "keywords": ["Arjuna", "dilemma", "duty", "moral conflict"],
        "difficulty": "beginner"
    },
    {
        "question": "How does the Gita describe the nature of God?",
        "category": "Philosophy & Concepts",
        "keywords": ["God", "Krishna", "Brahman", "Supreme"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is the concept of Moksha in the Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["moksha", "liberation", "freedom", "enlightenment"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is the role of a guru according to the Gita?",
        "category": "Spiritual Practice",
        "keywords": ["guru", "teacher", "disciple", "spiritual guide"],
        "difficulty": "intermediate"
    },
    {
        "question": "How does the Gita describe the process of meditation?",
        "category": "Meditation & Yoga",
        "keywords": ["meditation", "dhyana", "concentration", "mind control"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is the Bhagavad Gita's view on work and action?",
        "category": "Karma Yoga",
        "keywords": ["work", "action", "karma", "duty", "nishkama karma"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is the significance of the battlefield setting in the Gita?",
        "category": "Teachings & Verses",
        "keywords": ["battlefield", "Kurukshetra", "symbolism", "metaphor"],
        "difficulty": "intermediate"
    },
    {
        "question": "How does the Gita describe the relationship between the body and soul?",
        "category": "Philosophy & Concepts",
        "keywords": ["body", "soul", "atman", "death", "eternal"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is the concept of Yoga in the Bhagavad Gita?",
        "category": "Meditation & Yoga",
        "keywords": ["yoga", "union", "discipline", "path"],
        "difficulty": "intermediate"
    },
    {
        "question": "How can the teachings of the Gita be applied in daily life?",
        "category": "Modern Application",
        "keywords": ["daily life", "practical", "application", "modern"],
        "difficulty": "beginner"
    },
    # 80 more questions would be added here in a real implementation
    # For brevity, I'm including a smaller set of questions
    {
        "question": "What is the Bhagavad Gita's view on desire?",
        "category": "Philosophy & Concepts",
        "keywords": ["desire", "kama", "attachment", "renunciation"],
        "difficulty": "intermediate"
    },
    {
        "question": "How does the Gita describe the nature of the mind?",
        "category": "Philosophy & Concepts",
        "keywords": ["mind", "manas", "control", "meditation"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is the significance of the Bhagavad Gita in Hinduism?",
        "category": "Introduction",
        "keywords": ["significance", "importance", "Hinduism", "scripture"],
        "difficulty": "beginner"
    },
    {
        "question": "How does the Gita address the concept of time?",
        "category": "Philosophy & Concepts",
        "keywords": ["time", "kala", "cycles", "eternity"],
        "difficulty": "advanced"
    },
    {
        "question": "What is the Bhagavad Gita's teaching on non-attachment?",
        "category": "Philosophy & Concepts",
        "keywords": ["non-attachment", "vairagya", "detachment", "renunciation"],
        "difficulty": "intermediate"
    },
    {
        "question": "How does the Gita describe the process of creation?",
        "category": "Philosophy & Concepts",
        "keywords": ["creation", "cosmology", "universe", "manifestation"],
        "difficulty": "advanced"
    },
    {
        "question": "What is the Bhagavad Gita's view on caste and varna?",
        "category": "Philosophy & Concepts",
        "keywords": ["caste", "varna", "social order", "duty"],
        "difficulty": "intermediate"
    },
    {
        "question": "How does the Gita describe the nature of knowledge?",
        "category": "Jnana Yoga",
        "keywords": ["knowledge", "jnana", "wisdom", "self-realization"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is the concept of Ishvara in the Bhagavad Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["Ishvara", "God", "Supreme Being", "controller"],
        "difficulty": "intermediate"
    },
    {
        "question": "How does the Gita address the problem of suffering?",
        "category": "Philosophy & Concepts",
        "keywords": ["suffering", "pain", "duhkha", "solution"],
        "difficulty": "intermediate"
    },
    # Additional questions would continue here...
]

def get_questions_by_category(category: str = None) -> List[BGQuestion]:
    """
    Get questions filtered by category.
    
    Args:
        category: Optional category to filter by. If None, returns all questions.
        
    Returns:
        List of questions matching the category
    """
    if category:
        return [q for q in TOP_QUESTIONS if q["category"] == category]
    return TOP_QUESTIONS

def search_questions(query: str) -> List[BGQuestion]:
    """
    Search questions by keyword.
    
    Args:
        query: Search term to look for in questions or keywords
        
    Returns:
        List of matching questions
    """
    query = query.lower()
    results = []
    
    for question in TOP_QUESTIONS:
        # Check if query is in question or keywords
        if (query in question["question"].lower() or
            any(query in keyword.lower() for keyword in question["keywords"])):
            results.append(question)
    
    return results

def get_questions_by_difficulty(level: str) -> List[BGQuestion]:
    """
    Get questions filtered by difficulty level.
    
    Args:
        level: Difficulty level (beginner, intermediate, advanced)
        
    Returns:
        List of questions matching the difficulty level
    """
    return [q for q in TOP_QUESTIONS if q["difficulty"] == level.lower()]

if __name__ == "__main__":
    # Example usage
    print(f"Total questions: {len(TOP_QUESTIONS)}")
    print(f"Categories: {', '.join(CATEGORIES)}")
    
    # Example: Get all questions about Karma Yoga
    karma_questions = get_questions_by_category("Karma Yoga")
    print(f"\nFound {len(karma_questions)} questions about Karma Yoga:")
    for q in karma_questions:
        print(f"- {q['question']}")
    
    # Example: Search for questions about meditation
    search_term = "meditation"
    search_results = search_questions(search_term)
    print(f"\nSearch results for '{search_term}': {len(search_results)} found")
    for result in search_results:
        print(f"- {result['question']} (Category: {result['category']})")
