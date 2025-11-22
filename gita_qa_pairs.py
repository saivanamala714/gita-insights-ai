"""
Bhagavad Gita Q&A Pairs

This module contains a comprehensive list of questions and answers about the Bhagavad Gita,
including both general knowledge and specific verse-based questions.
"""
from typing import Dict, List, Tuple

# Categories for organizing questions
CATEGORIES = [
    "Basic Information",
    "Philosophical Concepts",
    "Key Teachings",
    "Characters",
    "Key Verses",
    "Practical Applications",
    "Spiritual Practices",
    "Comparative Studies",
    "Deeper Philosophy",
    "Modern Relevance"
]

# Comprehensive list of questions and answers
QA_PAIRS: List[Dict[str, any]] = [
    # Basic Information
    {
        "question": "What is the Bhagavad Gita?",
        "answer": "The Bhagavad Gita, often referred to as the Gita, is a 700-verse Hindu scripture that is part of the epic Mahabharata. It is a conversation between Prince Arjuna and Lord Krishna, who serves as his charioteer. The Gita addresses the moral and philosophical dilemmas faced by Arjuna on the battlefield of Kurukshetra and presents a synthesis of Hindu ideas about dharma, theistic bhakti, and the yogic ideals of moksha.",
        "category": "Basic Information",
        "verse_references": ["Introduction"],
        "keywords": ["introduction", "overview", "what is", "basics"]
    },
    {
        "question": "Who wrote the Bhagavad Gita?",
        "answer": "The Bhagavad Gita is part of the Mahabharata, which was written by the sage Vyasa. According to tradition, Vyasa dictated the entire Mahabharata, including the Gita, to the god Ganesha, who served as his scribe. The text itself is a dialogue between Lord Krishna and Arjuna, with Sanjaya narrating the conversation to King Dhritarashtra.",
        "category": "Basic Information",
        "verse_references": ["1.1"],
        "keywords": ["author", "written by", "composed by", "origin"]
    },
    {
        "question": "How many chapters are in the Bhagavad Gita?",
        "answer": "The Bhagavad Gita consists of 18 chapters, with a total of 700 verses. These chapters cover various aspects of life, philosophy, and spirituality, with each chapter focusing on a particular theme or teaching.",
        "category": "Basic Information",
        "verse_references": ["18.78"],
        "keywords": ["chapters", "verses", "length", "structure"]
    },
    
    # Philosophical Concepts
    {
        "question": "What is Karma Yoga according to the Gita?",
        "answer": "Karma Yoga, as explained in the Bhagavad Gita, is the path of selfless action. It involves performing one's prescribed duties without attachment to the results, offering all actions to God. Lord Krishna teaches that by working in this consciousness, one can attain liberation (moksha) while still fulfilling one's worldly responsibilities. Key aspects include performing actions as a form of worship, maintaining equanimity in success and failure, and seeing all work as service to the divine.",
        "category": "Philosophical Concepts",
        "verse_references": ["2.47-48", "3.19-20", "5.10", "18.6-9"],
        "keywords": ["karma", "action", "duty", "selfless service"]
    },
    {
        "question": "What is Bhakti Yoga in the Gita?",
        "answer": "Bhakti Yoga is the path of loving devotion to the Supreme Lord, Krishna. The Gita describes it as the highest and most direct path to spiritual realization. Key aspects include: developing pure love for God, constant remembrance of the divine, seeing God in all beings, and surrendering all actions and their results to the Lord. The 12th chapter of the Gita is particularly dedicated to the practice of Bhakti Yoga.",
        "category": "Philosophical Concepts",
        "verse_references": ["9.34", "12.1-20", "18.54-55"],
        "keywords": ["devotion", "bhakti", "love of God", "surrender"]
    },
    {
        "question": "What is Jnana Yoga in the Gita?",
        "answer": "Jnana Yoga is the path of knowledge and wisdom. It involves discerning the eternal from the temporary, understanding the true nature of the self (atman) as distinct from the body and mind, and realizing the ultimate truth of Brahman (the Absolute Truth). The Gita emphasizes that true knowledge leads to seeing the unity of all existence in the Supreme. However, it also warns that mere intellectual knowledge without devotion and self-discipline is insufficient for liberation.",
        "category": "Philosophical Concepts",
        "verse_references": ["4.38-39", "13.7-11", "18.20-22"],
        "keywords": ["knowledge", "wisdom", "jnana", "self-realization"]
    },
    
    # Key Teachings
    {
        "question": "What is the main message of the Bhagavad Gita?",
        "answer": "The central message of the Bhagavad Gita is the attainment of spiritual freedom (moksha) through selfless action (karma yoga), devotion (bhakti yoga), and knowledge (jnana yoga). Key teachings include: 1) Perform your duty without attachment to results (2.47), 2) The soul is eternal and indestructible (2.20), 3) Surrender completely to God (18.66), 4) Equanimity in success and failure (2.48), and 5) The importance of selfless service and devotion. The Gita ultimately teaches that the purpose of life is to reawaken our divine relationship with the Supreme Lord, Krishna.",
        "category": "Key Teachings",
        "verse_references": ["2.47", "18.66", "2.20", "9.27", "12.6-7"],
        "keywords": ["main message", "central teaching", "purpose", "essence"]
    },
    {
        "question": "What does the Gita say about the soul?",
        "answer": "The Bhagavad Gita provides profound insights about the soul (atman): 1) The soul is eternal, indestructible, immutable (2.17-25), 2) It is distinct from the body and mind, 3) The soul is never born nor does it ever die (2.20), 4) It is not affected by the changes of the body, just as the sky is not affected by clouds, 5) The soul is a tiny, indestructible part of the Supreme Lord (15.7), 6) It is the source of consciousness throughout the body, and 7) The ultimate goal is to realize one's eternal spiritual identity and relationship with the Supreme Soul (Paramatma).",
        "category": "Key Teachings",
        "verse_references": ["2.12-30", "15.7-10", "13.1-6", "18.54-55"],
        "keywords": ["soul", "atman", "self", "consciousness", "rebirth"]
    },
    
    # Characters
    {
        "question": "Who is Arjuna in the Bhagavad Gita?",
        "answer": "Arjuna is the central human figure in the Bhagavad Gita, a mighty warrior prince of the Pandava dynasty. He is the third of the five Pandava brothers and is considered the best archer of his time. In the Gita, he serves as the student and devotee of Lord Krishna. His moral dilemma on the battlefield of Kurukshetra, where he is reluctant to fight against his own relatives, forms the backdrop for Krishna's teachings. Arjuna represents the ideal disciple, showing the human struggle with duty, morality, and spiritual understanding. His questions and doubts provide the opportunity for Lord Krishna to deliver the profound wisdom of the Gita.",
        "category": "Characters",
        "verse_references": ["1.20-47", "2.1-10", "11.31-34"],
        "keywords": ["Arjuna", "Pandava", "warrior", "disciple", "student"]
    },
    {
        "question": "Who is Lord Krishna in the Bhagavad Gita?",
        "answer": "In the Bhagavad Gita, Lord Krishna is the Supreme Personality of Godhead who serves as Arjuna's charioteer and spiritual master. He reveals His universal form (Vishvarupa) to Arjuna in Chapter 11, demonstrating His divine nature as the source of all existence. Krishna teaches the paths of karma yoga, jnana yoga, and bhakti yoga, ultimately revealing that pure devotional service is the highest spiritual practice. He declares Himself as the ultimate goal of all spiritual paths and the source of all incarnations of God. The Gita presents Krishna not just as a historical figure but as the Supreme Absolute Truth itself.",
        "category": "Characters",
        "verse_references": ["4.6-8", "7.7", "10.8-11", "11.1-55", "18.64-66"],
        "keywords": ["Krishna", "God", "Supreme", "charioteer", "teacher"]
    },
    
    # Practical Applications
    {
        "question": "How can I apply the Gita's teachings in daily life?",
        "answer": "The Bhagavad Gita offers numerous practical applications for daily life: 1) Perform your duties with dedication but without attachment to results (2.47), 2) Maintain equanimity in success and failure (2.48), 3) Cultivate self-control over the mind and senses (6.5-6), 4) Practice seeing the divine in all beings (6.30-32), 5) Develop a regular spiritual practice (6.10-17), 6) Control anger and desire (2.62-63), 7) Be content with what comes without undue anxiety (2.14), 8) Treat everyone equally, without discrimination (5.18-19), 9) Focus on the present moment (2.14), and 10) Cultivate devotion and surrender to the divine (18.66). These principles can help create peace, purpose, and spiritual growth in everyday life.",
        "category": "Practical Applications",
        "verse_references": ["2.47-50", "6.5-6", "12.13-20", "18.65-66"],
        "keywords": ["daily life", "practical", "application", "modern life"]
    },
    
    # Modern Relevance
    {
        "question": "How is the Bhagavad Gita relevant today?",
        "answer": "The Bhagavad Gita remains profoundly relevant in the modern world because it addresses universal human concerns that transcend time and culture: 1) It provides guidance for dealing with stress, anxiety, and depression through its teachings on the eternal nature of the soul and the importance of duty (2.11-30), 2) It offers a framework for ethical decision-making and leadership (3.20-21), 3) Its teachings on non-attachment are valuable in our materialistic world (2.47), 4) It promotes universal values of compassion, self-discipline, and spiritual growth, 5) It provides a scientific approach to understanding consciousness and the self, 6) Its teachings on work as worship (karma yoga) can transform our approach to careers and service, and 7) It offers a path to inner peace in an increasingly chaotic world. The Gita's timeless wisdom continues to inspire millions seeking meaning and purpose in life.",
        "category": "Modern Relevance",
        "verse_references": ["2.11-30", "3.19-21", "6.5-6", "18.45-48"],
        "keywords": ["modern life", "relevance today", "21st century", "contemporary"]
    },
    
    # Deeper Philosophy
    {
        "question": "What is the concept of Dharma in the Gita?",
        "answer": "Dharma is a central concept in the Bhagavad Gita, often translated as 'duty,' 'righteousness,' or 'religion.' Key aspects include: 1) Svadharma - one's personal duty based on their nature and position in life (3.35, 18.47), 2) Sanatana-dharma - the eternal religion of all living beings, which is to serve the Supreme, 3) Varnashrama-dharma - the system of social and spiritual organization, 4) The importance of following one's own dharma rather than imitating others' paths (3.35), 5) Dharma as the foundation of universal order and individual well-being. The Gita teaches that following one's dharma with devotion to God leads to both material prosperity and spiritual liberation.",
        "category": "Deeper Philosophy",
        "verse_references": ["2.31-38", "3.35", "18.41-48", "18.66"],
        "keywords": ["dharma", "duty", "righteousness", "moral order"]
    },
    
    # Spiritual Practices
    {
        "question": "What is meditation according to the Gita?",
        "answer": "The Bhagavad Gita describes meditation (dhyana yoga) as a systematic process for controlling the mind and realizing the self. Key aspects include: 1) Sitting in a clean, sacred place with a straight back (6.11-12), 2) Focusing the mind on the Supreme (6.14-15), 3) Practicing moderation in eating, sleeping, work, and recreation (6.16-17), 4) Withdrawing the senses from sense objects (2.58), 5) Achieving a state of complete absorption in the divine (6.18-23), 6) The ultimate goal is to fix the mind constantly on Krishna (6.47). The Gita also explains that true meditation is not just a mechanical practice but requires proper understanding, detachment, and devotion. The highest form of meditation is to always think of the Supreme with love and devotion (8.8, 12.8).",
        "category": "Spiritual Practices",
        "verse_references": ["6.10-28", "12.6-12", "8.7-10"],
        "keywords": ["meditation", "dhyana", "contemplation", "mind control"]
    },
    
    # Comparative Studies
    {
        "question": "How does the Gita compare with other spiritual texts?",
        "answer": "The Bhagavad Gita holds a unique position among the world's spiritual texts: 1) Unlike many scriptures that present philosophical teachings in abstract terms, the Gita presents its wisdom in the context of a dialogue between friends on a battlefield, making it highly practical and applicable. 2) It synthesizes and harmonizes different spiritual paths (karma, jnana, bhakti, dhyana), while other texts often focus on just one approach. 3) The Gita is part of the larger Mahabharata, giving its teachings a narrative and historical context that many philosophical texts lack. 4) It presents a personal, loving God (Krishna) who is also the impersonal Brahman, bridging personal and impersonal conceptions of the divine. 5) The Gita's emphasis on performing one's duty in the world while maintaining spiritual consciousness distinguishes it from world-renouncing traditions. 6) It has been widely studied and commented upon by scholars from various traditions, both Eastern and Western, making it a bridge between different spiritual paths.",
        "category": "Comparative Studies",
        "verse_references": ["4.1-15", "9.1-4", "15.15-20"],
        "keywords": ["comparison", "other texts", "Upanishads", "Bible", "Buddhism"]
    }
]

def get_qa_pairs() -> List[Dict[str, any]]:
    """Return an empty list to ensure we don't use pre-defined Q&A pairs.
    This ensures all answers come from the PDF content only."""
    return []

def get_qa_by_category(category: str) -> List[Dict[str, any]]:
    """Return Q&A pairs filtered by category.
    
    Args:
        category: The category to filter by (must match exactly)
        
    Returns:
        List of Q&A dictionaries in the specified category
    """
    return [qa for qa in QA_PAIRS if qa["category"] == category]

def get_random_qa_pairs(count: int = 5) -> List[Dict[str, any]]:
    """Return a random selection of Q&A pairs.
    
    Args:
        count: Number of random Q&A pairs to return (default: 5)
        
    Returns:
        List of randomly selected Q&A dictionaries
    """
    import random
    return random.sample(QA_PAIRS, min(count, len(QA_PAIRS)))

def search_qa(query: str, threshold: float = 0.3) -> List[Dict[str, any]]:
    """Search for Q&A pairs relevant to the query.
    
    Args:
        query: The search query string
        threshold: Minimum similarity score (0-1) to include a result
        
    Returns:
        List of relevant Q&A dictionaries, sorted by relevance
    """
    from difflib import SequenceMatcher
    
    query = query.lower().strip()
    query_terms = set(query.split())
    results = []
    
    for qa in QA_PAIRS:
        # Check keywords first
        if 'keywords' in qa and any(keyword in query for keyword in qa['keywords']):
            results.append((1.0, qa))  # High confidence for keyword match
            continue
            
        # Check question similarity
        question = qa['question'].lower()
        question_terms = set(question.split())
        
        # Calculate Jaccard similarity
        intersection = len(query_terms.intersection(question_terms))
        union = len(query_terms.union(question_terms))
        jaccard_sim = intersection / union if union > 0 else 0
        
        # Calculate sequence similarity
        seq_sim = max(
            SequenceMatcher(None, query, question).ratio(),
            SequenceMatcher(None, query, qa['answer'][:100].lower()).ratio()
        )
        
        # Combined score (weighted average)
        score = (jaccard_sim * 0.6) + (seq_sim * 0.4)
        
        if score >= threshold:
            results.append((score, qa))
    
    # Sort by score (highest first) and return
    results.sort(reverse=True, key=lambda x: x[0])
    return [qa for score, qa in results]

if __name__ == "__main__":
    # Example usage
    print(f"Total Q&A pairs: {len(QA_PAIRS)}")
    print("\nCategories:")
    for category in CATEGORIES:
        count = len(get_qa_by_category(category))
        print(f"- {category}: {count} questions")
