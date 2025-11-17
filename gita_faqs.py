"""
Bhagavad Gita Frequently Asked Questions

This module contains a comprehensive list of frequently asked questions about the Bhagavad Gita
along with their answers, organized by category for easy reference and integration
into the Q&A system.
"""
from typing import Dict, List, TypedDict

class FAQItem(TypedDict):
    """Structure for storing FAQ items with metadata."""
    question: str
    answer: str
    category: str
    keywords: List[str]
    verse_references: List[str]

# Categories for organizing the FAQs
CATEGORIES = [
    "Introduction",
    "Philosophy",
    "Karma Yoga",
    "Bhakti Yoga",
    "Jnana Yoga",
    "Meditation",
    "Dharma",
    "Characters",
    "Teachings",
    "Modern Application"
]

# Comprehensive list of frequently asked questions about the Bhagavad Gita
FAQ_LIST: List[FAQItem] = [
    {
        "question": "What is the Bhagavad Gita?",
        "answer": "The Bhagavad Gita, often referred to as the Gita, is a 700-verse Hindu scripture that is part of the epic Mahabharata. It is a conversation between Prince Arjuna and Lord Krishna, who serves as his charioteer. The Gita is set in a narrative framework of a dialogue between Pandava prince Arjuna and his guide and charioteer Krishna.",
        "category": "Introduction",
        "keywords": ["definition", "overview", "what is", "explain"],
        "verse_references": ["BG 1.1-46", "BG 2.1-72"]
    },
    {
        "question": "Who is the speaker of the Bhagavad Gita?",
        "answer": "The Bhagavad Gita is primarily a conversation between Lord Krishna and Arjuna. Lord Krishna, who is recognized as the Supreme Personality of Godhead, serves as the speaker of the Gita's divine wisdom, while Arjuna, the Pandava prince, is the recipient of this knowledge.",
        "category": "Introduction",
        "keywords": ["speaker", "who said", "who spoke", "Krishna"],
        "verse_references": ["BG 10.12-13", "BG 11.3-4"]
    },
    {
        "question": "What is the main message of the Bhagavad Gita?",
        "answer": "The main message of the Bhagavad Gita is the attainment of freedom or happiness through selfless action, devotion to God, and the cultivation of spiritual knowledge. It teaches the importance of doing one's duty (dharma) without attachment to the results, the nature of the self (atman), and the ultimate reality (Brahman).",
        "category": "Philosophy",
        "keywords": ["main message", "purpose", "core teaching", "essence"],
        "verse_references": ["BG 2.47-50", "BG 3.19-20", "BG 18.46"]
    },
    {
        "question": "What is Karma Yoga according to the Gita?",
        "answer": "Karma Yoga, as explained in the Bhagavad Gita, is the path of selfless action. It involves performing one's prescribed duties without attachment to the results, dedicating all actions to the Divine. Lord Krishna teaches that by working without selfish motives, one can attain liberation (moksha) while still fulfilling their worldly responsibilities.",
        "category": "Karma Yoga",
        "keywords": ["karma yoga", "selfless action", "duty", "action"],
        "verse_references": ["BG 2.47-48", "BG 3.4-9", "BG 5.10-12"]
    },
    {
        "question": "What is Bhakti Yoga in the Gita?",
        "answer": "Bhakti Yoga is the path of loving devotion to God. In the Gita, Lord Krishna explains that through unwavering devotion and complete surrender to the Divine, one can attain the highest spiritual realization. This path emphasizes developing a personal relationship with God through prayer, worship, and remembrance.",
        "category": "Bhakti Yoga",
        "keywords": ["bhakti", "devotion", "surrender", "love of God"],
        "verse_references": ["BG 9.22-34", "BG 12.6-20"]
    },
    {
        "question": "What is Jnana Yoga according to the Gita?",
        "answer": "Jnana Yoga is the path of knowledge and wisdom. The Gita teaches that through the cultivation of spiritual knowledge and discernment between the eternal and temporary, one can realize the true nature of the self and attain liberation. This involves studying sacred texts, self-inquiry, and meditation under proper guidance.",
        "category": "Jnana Yoga",
        "keywords": ["jnana", "knowledge", "wisdom", "self-realization"],
        "verse_references": ["BG 4.33-42", "BG 13.7-11"]
    },
    {
        "question": "What does the Gita say about meditation?",
        "answer": "The Bhagavad Gita describes meditation as the practice of focusing the mind on the Divine. In Chapter 6, Krishna explains the process of Dhyana Yoga (the yoga of meditation), which involves sitting in a clean place, holding the body steady, and focusing the mind on the Supreme. The goal is to achieve mental discipline and ultimately, self-realization.",
        "category": "Meditation",
        "keywords": ["meditation", "dhyana", "concentration", "mind control"],
        "verse_references": ["BG 6.10-15", "BG 6.25-28"]
    },
    {
        "question": "What is the concept of Dharma in the Gita?",
        "answer": "Dharma in the Bhagavad Gita refers to one's righteous duty or moral responsibility based on their nature and position in life. Krishna emphasizes that it is better to perform one's own dharma imperfectly than to perform another's dharma perfectly. The concept is central to the Gita's teachings on right action and social order.",
        "category": "Dharma",
        "keywords": ["dharma", "duty", "righteousness", "moral order"],
        "verse_references": ["BG 2.31-38", "BG 3.35", "BG 18.47"]
    },
    {
        "question": "Who was Arjuna in the Bhagavad Gita?",
        "answer": "Arjuna is the central human character in the Bhagavad Gita, a skilled archer and one of the five Pandava brothers. He serves as the student and devotee to whom Lord Krishna imparts the spiritual teachings of the Gita. Arjuna represents the human soul in search of divine guidance and wisdom.",
        "category": "Characters",
        "keywords": ["Arjuna", "Pandava", "warrior", "disciple"],
        "verse_references": ["BG 1.20-46", "BG 11.1-4"]
    },
    {
        "question": "What is the significance of the battlefield in the Gita?",
        "answer": "The battlefield of Kurukshetra, where the Bhagavad Gita is set, symbolizes the moral and ethical struggles of human life. It represents the inner conflict between right and wrong, duty and desire, and the eternal battle between the higher and lower aspects of human nature. The Gita teaches how to face life's battles with wisdom and equanimity.",
        "category": "Teachings",
        "keywords": ["battlefield", "Kurukshetra", "war", "struggle"],
        "verse_references": ["BG 1.1", "BG 2.1-10"]
    },
    {
        "question": "How can the Gita's teachings be applied in modern life?",
        "answer": "The Bhagavad Gita's teachings remain highly relevant in modern life. Its principles of selfless action, emotional equilibrium, mindfulness, and ethical living can help individuals navigate contemporary challenges. The Gita's wisdom on managing stress, making decisions, maintaining work-life balance, and finding purpose continues to inspire people worldwide.",
        "category": "Modern Application",
        "keywords": ["modern life", "today's world", "application", "relevance"],
        "verse_references": ["BG 2.47-50", "BG 3.19-20", "BG 6.5-6"]
    },
    {
        "question": "What is the concept of the Atman in the Gita?",
        "answer": "In the Bhagavad Gita, the Atman refers to the eternal, unchanging self or soul that exists within all living beings. Krishna teaches that the Atman is distinct from the physical body and mind, indestructible, and beyond birth and death. Realizing one's true nature as Atman leads to liberation from the cycle of birth and death.",
        "category": "Philosophy",
        "keywords": ["atman", "soul", "self", "eternal"],
        "verse_references": ["BG 2.12-30", "BG 13.1-2"]
    },
    {
        "question": "What is the role of the guru in the Gita?",
        "answer": "The Bhagavad Gita emphasizes the importance of a spiritual teacher (guru) in guiding the disciple on the path to self-realization. Krishna serves as the divine guru to Arjuna, imparting transcendental knowledge. The Gita teaches that one should approach a guru with humility, reverence, and a genuine desire to learn the truth.",
        "category": "Teachings",
        "keywords": ["guru", "teacher", "disciple", "spiritual guide"],
        "verse_references": ["BG 4.34-35", "BG 13.7-11"]
    },
    {
        "question": "What is the concept of Maya in the Gita?",
        "answer": "Maya in the Bhagavad Gita refers to the illusory energy that causes living beings to identify with the material world and forget their true spiritual nature. It is described as Krishna's divine energy that is difficult to overcome, but through devotion and spiritual knowledge, one can see beyond this illusion and realize the ultimate truth.",
        "category": "Philosophy",
        "keywords": ["maya", "illusion", "material world", "reality"],
        "verse_references": ["BG 7.14-15", "BG 7.25-26"]
    },
    {
        "question": "What is the significance of the three gunas in the Gita?",
        "answer": "The three gunas (qualities or modes of material nature) are fundamental concepts in the Bhagavad Gita. They are: Sattva (goodness, harmony), Rajas (passion, activity), and Tamas (ignorance, inertia). These gunas influence all aspects of life and consciousness. The Gita teaches that one should transcend these gunas to attain spiritual liberation.",
        "category": "Philosophy",
        "keywords": ["gunas", "sattva", "rajas", "tamas", "nature"],
        "verse_references": ["BG 14.5-18", "BG 17.1-22"]
    },
    {
        "question": "What is the ultimate goal of life according to the Gita?",
        "answer": "The ultimate goal of life according to the Bhagavad Gita is to attain moksha (liberation) from the cycle of birth and death and to achieve union with the Supreme (Brahman). This is accomplished through self-realization, performing one's dharma without attachment, and developing pure devotion to God.",
        "category": "Philosophy",
        "keywords": ["goal of life", "purpose", "liberation", "moksha"],
        "verse_references": ["BG 4.9", "BG 8.5-7", "BG 18.62-66"]
    }
]

def get_faqs_by_category(category: str = None) -> List[FAQItem]:
    """
    Get FAQs filtered by category.
    
    Args:
        category: Optional category to filter by. If None, returns all FAQs.
        
    Returns:
        List of FAQ items matching the category
    """
    if category:
        return [faq for faq in FAQ_LIST if faq["category"].lower() == category.lower()]
    return FAQ_LIST

def search_faqs(query: str) -> List[FAQItem]:
    """
    Search FAQs by question, answer, or keywords.
    
    Args:
        query: Search term to look for in questions, answers, or keywords
        
    Returns:
        List of matching FAQ items
    """
    query = query.lower()
    results = []
    
    for faq in FAQ_LIST:
        # Check if query is in question, answer, or keywords
        if (query in faq["question"].lower() or
            query in faq["answer"].lower() or
            any(query in keyword.lower() for keyword in faq["keywords"])):
            results.append(faq)
    
    return results

def get_faq_by_question(question: str) -> Optional[FAQItem]:
    """
    Get an FAQ by its exact question.
    
    Args:
        question: The exact question to look up
        
    Returns:
        The FAQ item if found, None otherwise
    """
    for faq in FAQ_LIST:
        if faq["question"].lower() == question.lower():
            return faq
    return None

if __name__ == "__main__":
    # Example usage
    print(f"Total FAQs: {len(FAQ_LIST)}")
    print(f"Categories: {', '.join(CATEGORIES)}")
    
    # Example: Get all FAQs about Karma Yoga
    karma_faqs = get_faqs_by_category("Karma Yoga")
    print(f"\nFound {len(karma_faqs)} FAQs about Karma Yoga:")
    for faq in karma_faqs:
        print(f"- {faq['question']}")
    
    # Example: Search for FAQs about meditation
    search_term = "meditation"
    search_results = search_faqs(search_term)
    print(f"\nSearch results for '{search_term}': {len(search_results)} found")
    for result in search_results:
        print(f"- {result['question']} (Category: {result['category']})")
