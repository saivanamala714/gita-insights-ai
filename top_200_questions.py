"""
Top 200 Frequently Asked Questions About the Bhagavad Gita

This module contains a curated list of the top 200 most commonly asked questions
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
    "Comparative Religion",
    "Mysteries & Symbolism",
    "Ethics & Morality",
    "Death & Afterlife",
    "Free Will & Destiny"
]

# Top 200 Bhagavad Gita questions
TOP_QUESTIONS: List[BGQuestion] = [
    # ===== Introduction (1-30) =====
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
        "question": "How many chapters and verses are in the Bhagavad Gita?",
        "category": "Introduction",
        "keywords": ["chapters", "verses", "count", "sections", "number of"],
        "difficulty": "beginner"
    },
    {
        "question": "What is the significance of the number 18 in the Bhagavad Gita?",
        "category": "Introduction",
        "keywords": ["number 18", "significance", "chapters", "symbolism"],
        "difficulty": "beginner"
    },
    {
        "question": "Is the Bhagavad Gita part of a larger text?",
        "category": "Introduction",
        "keywords": ["part of", "larger text", "Mahabharata", "where from"],
        "difficulty": "beginner"
    },
    {
        "question": "What language was the Bhagavad Gita originally written in?",
        "category": "Introduction",
        "keywords": ["language", "original", "Sanskrit", "written in"],
        "difficulty": "beginner"
    },
    {
        "question": "When was the Bhagavad Gita written?",
        "category": "Introduction",
        "keywords": ["when written", "time period", "historical context", "age"],
        "difficulty": "beginner"
    },
    {
        "question": "What is the relationship between the Bhagavad Gita and the Upanishads?",
        "category": "Introduction",
        "keywords": ["Upanishads", "Vedanta", "relation", "comparison"],
        "difficulty": "intermediate"
    },
    {
        "question": "Why is the Bhagavad Gita considered a spiritual classic?",
        "category": "Introduction",
        "keywords": ["spiritual classic", "importance", "significance", "value"],
        "difficulty": "beginner"
    },
    {
        "question": "What is the structure of the Bhagavad Gita?",
        "category": "Introduction",
        "keywords": ["structure", "organization", "sections", "chapters", "verses"],
        "difficulty": "beginner"
    },
    {
        "question": "How is the Bhagavad Gita relevant to modern life?",
        "category": "Introduction",
        "keywords": ["relevance", "modern life", "today's world", "applicability"],
        "difficulty": "beginner"
    },
    {
        "question": "What are the main themes of the Bhagavad Gita?",
        "category": "Introduction",
        "keywords": ["themes", "main ideas", "central concepts", "key teachings"],
        "difficulty": "beginner"
    },
    {
        "question": "Who was the original audience of the Bhagavad Gita?",
        "category": "Introduction",
        "keywords": ["audience", "intended for", "who is it for", "original listeners"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is the Bhagavad Gita's view on the purpose of human life?",
        "category": "Introduction",
        "keywords": ["purpose of life", "human existence", "meaning of life", "life's goal"],
        "difficulty": "intermediate"
    },
    
    # ===== Philosophy & Concepts (31-70) =====
    {
        "question": "What is the concept of Dharma in the Bhagavad Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["dharma", "duty", "righteousness", "moral order"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is the nature of the soul (Atman) according to the Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["soul", "atman", "self", "eternal", "nature of"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is Maya in the context of the Bhagavad Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["maya", "illusion", "reality", "perception"],
        "difficulty": "advanced"
    },
    {
        "question": "What is the concept of Karma in the Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["karma", "action", "cause and effect", "law of karma"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is the Bhagavad Gita's view on death and the afterlife?",
        "category": "Philosophy & Concepts",
        "keywords": ["death", "afterlife", "rebirth", "reincarnation"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is the concept of Moksha in the Bhagavad Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["moksha", "liberation", "freedom", "enlightenment"],
        "difficulty": "advanced"
    },
    {
        "question": "What is the relationship between the body, mind, and soul in the Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["body", "mind", "soul", "relationship", "connection"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is the concept of Gunas in the Bhagavad Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["gunas", "sattva", "rajas", "tamas", "qualities"],
        "difficulty": "advanced"
    },
    {
        "question": "What is the Bhagavad Gita's view on desire and attachment?",
        "category": "Philosophy & Concepts",
        "keywords": ["desire", "attachment", "craving", "clinging"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is the concept of Ishvara in the Bhagavad Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["ishvara", "God", "supreme being", "divine"],
        "difficulty": "advanced"
    },
    
    # ===== Karma Yoga (71-100) =====
    {
        "question": "What is Karma Yoga as described in the Bhagavad Gita?",
        "category": "Karma Yoga",
        "keywords": ["karma yoga", "path of action", "selfless service"],
        "difficulty": "intermediate"
    },
    {
        "question": "What does 'Nishkama Karma' mean in the Gita?",
        "category": "Karma Yoga",
        "keywords": ["nishkama karma", "selfless action", "without attachment to results"],
        "difficulty": "intermediate"
    },
    {
        "question": "How does the Gita define right action?",
        "category": "Karma Yoga",
        "keywords": ["right action", "proper conduct", "dharmic action"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is the role of intention in Karma Yoga?",
        "category": "Karma Yoga",
        "keywords": ["intention", "motive", "purpose behind action"],
        "difficulty": "intermediate"
    },
    {
        "question": "How can one practice Karma Yoga in daily life?",
        "category": "Karma Yoga",
        "keywords": ["practice", "daily life", "application", "practical"],
        "difficulty": "beginner"
    },
    {
        "question": "What is the difference between Sakama and Nishkama Karma?",
        "category": "Karma Yoga",
        "keywords": ["sakama karma", "nishkama karma", "comparison", "difference"],
        "difficulty": "intermediate"
    },
    
    # ===== Bhakti Yoga (101-130) =====
    {
        "question": "What is Bhakti Yoga according to the Gita?",
        "category": "Bhakti Yoga",
        "keywords": ["bhakti yoga", "devotion", "love of God"],
        "difficulty": "intermediate"
    },
    {
        "question": "What are the different types of Bhakti mentioned in the Gita?",
        "category": "Bhakti Yoga",
        "keywords": ["types of bhakti", "forms of devotion", "bhakti marga"],
        "difficulty": "advanced"
    },
    {
        "question": "How does the Gita describe the ideal devotee?",
        "category": "Bhakti Yoga",
        "keywords": ["ideal devotee", "characteristics", "qualities"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is the significance of surrender in Bhakti Yoga?",
        "category": "Bhakti Yoga",
        "keywords": ["surrender", "prapatti", "submission", "devotion"],
        "difficulty": "intermediate"
    },
    
    # ===== Jnana Yoga (131-160) =====
    {
        "question": "What is Jnana Yoga in the Bhagavad Gita?",
        "category": "Jnana Yoga",
        "keywords": ["jnana yoga", "path of knowledge", "wisdom"],
        "difficulty": "advanced"
    },
    {
        "question": "What is the difference between Jnana and Vijnana in the Gita?",
        "category": "Jnana Yoga",
        "keywords": ["jnana", "vijnana", "knowledge", "wisdom", "difference"],
        "difficulty": "advanced"
    },
    {
        "question": "What is the role of the Guru in Jnana Yoga?",
        "category": "Jnana Yoga",
        "keywords": ["guru", "teacher", "spiritual guide", "role"],
        "difficulty": "intermediate"
    },
    
    # ===== Meditation & Yoga (161-190) =====
    {
        "question": "What does the Gita say about meditation?",
        "category": "Meditation & Yoga",
        "keywords": ["meditation", "dhyana", "concentration"],
        "difficulty": "intermediate"
    },
    {
        "question": "What are the different types of yoga mentioned in the Gita?",
        "category": "Meditation & Yoga",
        "keywords": ["types of yoga", "yoga paths", "different yogas"],
        "difficulty": "intermediate"
    },
    
    # ===== Dharma & Duty (191-220) =====
    {
        "question": "What is Svadharma according to the Gita?",
        "category": "Dharma & Duty",
        "keywords": ["svadharma", "personal duty", "right action"],
        "difficulty": "intermediate"
    },
    
    # ===== Characters & Stories (221-250) =====
    {
        "question": "Who was Arjuna and why is he important in the Gita?",
        "category": "Characters & Stories",
        "keywords": ["Arjuna", "warrior", "disciple", "Pandava"],
        "difficulty": "beginner"
    },
    {
        "question": "Who are the main characters in the Bhagavad Gita?",
        "category": "Characters & Stories",
        "keywords": ["main characters", "who's who", "key figures"],
        "difficulty": "beginner"
    },
    
    # ===== Teachings & Verses (251-280) =====
    {
        "question": "What is the significance of Chapter 2, Verse 47 of the Bhagavad Gita?",
        "category": "Teachings & Verses",
        "keywords": ["2.47", "karmanye vadhikaraste", "right to action only"],
        "difficulty": "intermediate"
    },
    {
        "question": "What are some of the most famous verses from the Bhagavad Gita?",
        "category": "Teachings & Verses",
        "keywords": ["famous verses", "well-known shlokas", "popular quotes"],
        "difficulty": "beginner"
    },
    
    # ===== Modern Application (281-300) =====
    {
        "question": "How can the Gita's teachings be applied to modern life?",
        "category": "Modern Application",
        "keywords": ["modern life", "application", "practical"],
        "difficulty": "beginner"
    },
    {
        "question": "What can the Bhagavad Gita teach us about stress management?",
        "category": "Modern Application",
        "keywords": ["stress management", "anxiety", "coping", "mental health"],
        "difficulty": "beginner"
    },
    
    # ===== Comparative Religion (301-330) =====
    {
        "question": "How does the Gita compare to other religious texts?",
        "category": "Comparative Religion",
        "keywords": ["comparison", "other religions", "similarities"],
        "difficulty": "advanced"
    },
    
    # ===== Final questions =====
    {
        "question": "What is the Bhagavad Gita's view on the nature of the material world's temporary situations?",
        "category": "Philosophy & Concepts",
        "keywords": ["temporary situations", "circumstances", "conditions", "material world"],
        "difficulty": "intermediate"
    },
    {
        "question": "How does the Gita describe the process of achieving God consciousness?",
        "category": "Bhakti Yoga",
        "keywords": ["God consciousness", "Krishna consciousness", "divine awareness"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is the significance of the Bhagavad Gita's teachings on leadership?",
        "category": "Modern Application",
        "keywords": ["leadership", "management", "workplace", "application"],
        "difficulty": "intermediate"
    },
    {
        "question": "How does the Gita address the concept of free will?",
        "category": "Philosophy & Concepts",
        "keywords": ["free will", "destiny", "choice", "determinism"],
        "difficulty": "advanced"
    },
    
    # ===== Additional questions to reach 200 =====
    # Philosophy & Concepts
    {
        "question": "What is the concept of 'Stithaprajna' in the Bhagavad Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["stithaprajna", "steadfast wisdom", "enlightened being"],
        "difficulty": "advanced"
    },
    {
        "question": "How does the Gita describe the nature of the divine?",
        "category": "Philosophy & Concepts",
        "keywords": ["divine", "God", "supreme", "nature of God"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is the significance of the battlefield setting in the Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["battlefield", "Kurukshetra", "symbolism", "metaphor"],
        "difficulty": "intermediate"
    },
    {
        "question": "How does the Gita address the concept of time?",
        "category": "Philosophy & Concepts",
        "keywords": ["time", "kala", "eternity", "cyclical time"],
        "difficulty": "advanced"
    },
    {
        "question": "What is the role of detachment in the Gita's teachings?",
        "category": "Philosophy & Concepts",
        "keywords": ["detachment", "non-attachment", "vairagya"],
        "difficulty": "intermediate"
    },
    
    # Karma Yoga
    {
        "question": "What is the difference between Sakama and Nishkama Karma in the Gita?",
        "category": "Karma Yoga",
        "keywords": ["sakama karma", "nishkama karma", "selfish action", "selfless action"],
        "difficulty": "intermediate"
    },
    {
        "question": "How does the Gita describe the concept of 'Karma Phala Tyaga'?",
        "category": "Karma Yoga",
        "keywords": ["karma phala tyaga", "renunciation of fruits of action"],
        "difficulty": "intermediate"
    },
    
    # Bhakti Yoga
    {
        "question": "What are the nine forms of Bhakti mentioned in the Gita?",
        "category": "Bhakti Yoga",
        "keywords": ["nine forms of bhakti", "navavidha bhakti", "types of devotion"],
        "difficulty": "intermediate"
    },
    {
        "question": "How does the Gita describe the relationship between the devotee and the divine?",
        "category": "Bhakti Yoga",
        "keywords": ["devotee relationship", "bhakta bhagavan sambandha", "divine connection"],
        "difficulty": "intermediate"
    },
    
    # Jnana Yoga
    {
        "question": "What is the concept of 'Brahman' in the Bhagavad Gita?",
        "category": "Jnana Yoga",
        "keywords": ["brahman", "ultimate reality", "absolute truth"],
        "difficulty": "advanced"
    },
    {
        "question": "How does the Gita explain the concept of 'Akshara Brahma'?",
        "category": "Jnana Yoga",
        "keywords": ["akshara brahma", "imperishable absolute", "eternal truth"],
        "difficulty": "advanced"
    },
    
    # Meditation & Yoga
    {
        "question": "What are the different stages of meditation described in the Gita?",
        "category": "Meditation & Yoga",
        "keywords": ["stages of meditation", "dhyana avastha", "meditation process"],
        "difficulty": "intermediate"
    },
    {
        "question": "How does the Gita describe the ideal posture for meditation?",
        "category": "Meditation & Yoga",
        "keywords": ["meditation posture", "asana", "sitting position"],
        "difficulty": "beginner"
    },
    
    # Dharma & Duty
    {
        "question": "How does the Gita define one's 'Swadharma'?",
        "category": "Dharma & Duty",
        "keywords": ["swadharma", "personal duty", "individual responsibility"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is the concept of 'Varnashrama Dharma' in the Gita?",
        "category": "Dharma & Duty",
        "keywords": ["varnashrama dharma", "social order", "duty according to varna"],
        "difficulty": "intermediate"
    },
    
    # Characters & Stories
    {
        "question": "What is the significance of Lord Krishna's role in the Gita?",
        "category": "Characters & Stories",
        "keywords": ["Krishna's role", "charioteer", "divine teacher"],
        "difficulty": "beginner"
    },
    {
        "question": "Who are the other key figures mentioned in the Gita besides Arjuna and Krishna?",
        "category": "Characters & Stories",
        "keywords": ["other characters", "supporting figures", "mentioned personalities"],
        "difficulty": "beginner"
    },
    
    # Teachings & Verses
    {
        "question": "What is the significance of the 'Vishvarupa Darshana' in the Gita?",
        "category": "Teachings & Verses",
        "keywords": ["vishvarupa darshana", "cosmic form", "chapter 11"],
        "difficulty": "intermediate"
    },
    {
        "question": "What does the Gita say about the nature of the mind?",
        "category": "Teachings & Verses",
        "keywords": ["nature of mind", "manas", "controlling the mind"],
        "difficulty": "intermediate"
    },
    
    # Modern Application
    {
        "question": "How can the Gita's teachings help in managing work-life balance?",
        "category": "Modern Application",
        "keywords": ["work-life balance", "modern challenges", "practical application"],
        "difficulty": "beginner"
    },
    {
        "question": "What can the Gita teach us about dealing with failure?",
        "category": "Modern Application",
        "keywords": ["dealing with failure", "handling setbacks", "resilience"],
        "difficulty": "beginner"
    },
    
    # Comparative Religion
    {
        "question": "How does the Gita's concept of God compare with other religions?",
        "category": "Comparative Religion",
        "keywords": ["concept of God", "comparative theology", "religious comparison"],
        "difficulty": "advanced"
    },
    {
        "question": "What are the similarities between the Gita and Buddhist teachings?",
        "category": "Comparative Religion",
        "keywords": ["Buddhism", "similar teachings", "comparative study"],
        "difficulty": "advanced"
    },
    
    # Mysteries & Symbolism
    {
        "question": "What is the symbolic meaning of Arjuna's chariot in the Gita?",
        "category": "Mysteries & Symbolism",
        "keywords": ["chariot symbolism", "rath", "spiritual symbolism"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is the significance of the conch shells mentioned in the Gita?",
        "category": "Mysteries & Symbolism",
        "keywords": ["conch shells", "shankha", "symbolic meaning"],
        "difficulty": "intermediate"
    },
    
    # Ethics & Morality
    {
        "question": "What is the Gita's view on non-violence (Ahimsa)?",
        "category": "Ethics & Morality",
        "keywords": ["ahimsa", "non-violence", "ethical conduct"],
        "difficulty": "intermediate"
    },
    {
        "question": "How does the Gita address the concept of truth (Satya)?",
        "category": "Ethics & Morality",
        "keywords": ["truth", "satya", "honesty", "moral values"],
        "difficulty": "intermediate"
    },
    
    # Death & Afterlife
    {
        "question": "What happens to the soul after death according to the Gita?",
        "category": "Death & Afterlife",
        "keywords": ["after death", "soul's journey", "reincarnation"],
        "difficulty": "intermediate"
    },
    {
        "question": "What is the concept of 'Pitrloka' in the Gita?",
        "category": "Death & Afterlife",
        "keywords": ["pitrloka", "world of ancestors", "afterlife realms"],
        "difficulty": "advanced"
    },
    
    # Free Will & Destiny
    {
        "question": "How does the Gita reconcile free will with destiny?",
        "category": "Free Will & Destiny",
        "keywords": ["free will vs destiny", "predetermination", "karma theory"],
        "difficulty": "advanced"
    },
    {
        "question": "What is the role of divine grace in the Gita's teachings?",
        "category": "Free Will & Destiny",
        "keywords": ["divine grace", "kripa", "god's will"],
        "difficulty": "intermediate"
    },
    
    # Additional Questions (84-200)
    
    # Nature of Reality
    {
        "question": "How does the Gita describe the concept of 'Maya' (illusion)?",
        "category": "Philosophy & Concepts",
        "keywords": ["maya", "illusion", "reality", "perception"],
        "difficulty": "advanced"
    },
    {
        "question": "What is the Gita's perspective on the material world?",
        "category": "Philosophy & Concepts",
        "keywords": ["material world", "prakriti", "nature", "creation"],
        "difficulty": "intermediate"
    },
    
    # Yoga & Spiritual Practices
    {
        "question": "What are the different types of yoga mentioned in the Gita?",
        "category": "Meditation & Yoga",
        "keywords": ["types of yoga", "yoga paths", "spiritual practices"],
        "difficulty": "intermediate"
    },
    {
        "question": "How does the Gita describe the process of self-realization?",
        "category": "Meditation & Yoga",
        "keywords": ["self-realization", "atma jnana", "enlightenment"],
        "difficulty": "advanced"
    },
    
    # Social & Ethical Teachings
    {
        "question": "What is the Gita's view on social responsibility?",
        "category": "Ethics & Morality",
        "keywords": ["social responsibility", "duty to society", "loka sangraha"],
        "difficulty": "intermediate"
    },
    {
        "question": "How does the Gita address the concept of justice?",
        "category": "Ethics & Morality",
        "keywords": ["justice", "dharma", "righteousness", "moral order"],
        "difficulty": "intermediate"
    },
    
    # Psychology & Mind
    {
        "question": "What does the Gita teach about controlling the mind?",
        "category": "Teachings & Verses",
        "keywords": ["controlling mind", "manonigraha", "mental discipline"],
        "difficulty": "intermediate"
    },
    {
        "question": "How does the Gita describe the nature of desires?",
        "category": "Philosophy & Concepts",
        "keywords": ["desires", "kama", "attachment", "liberation"],
        "difficulty": "intermediate"
    },
    
    # Leadership & Management
    {
        "question": "What leadership lessons can be learned from the Gita?",
        "category": "Modern Application",
        "keywords": ["leadership", "management", "decision making"],
        "difficulty": "beginner"
    },
    {
        "question": "How can the Gita's teachings be applied in the workplace?",
        "category": "Modern Application",
        "keywords": ["workplace", "professional life", "career"],
        "difficulty": "beginner"
    },
    
    # Relationships & Family
    {
        "question": "What does the Gita say about family responsibilities?",
        "category": "Dharma & Duty",
        "keywords": ["family", "responsibilities", "householder life"],
        "difficulty": "beginner"
    },
    {
        "question": "How does the Gita view the role of a teacher?",
        "category": "Characters & Stories",
        "keywords": ["teacher", "guru", "disciple", "learning"],
        "difficulty": "intermediate"
    },
    
    # Science & Cosmology
    {
        "question": "What is the Gita's view on the origin of the universe?",
        "category": "Philosophy & Concepts",
        "keywords": ["origin of universe", "cosmology", "creation"],
        "difficulty": "advanced"
    },
    {
        "question": "How does the Gita describe the concept of time?",
        "category": "Philosophy & Concepts",
        "keywords": ["time", "kala", "cycles", "eternity"],
        "difficulty": "advanced"
    },
    
    # Women in the Gita
    {
        "question": "What is the Gita's perspective on women?",
        "category": "Philosophy & Concepts",
        "keywords": ["women", "gender", "feminine principle"],
        "difficulty": "intermediate"
    },
    
    # War & Peace
    {
        "question": "How does the Gita justify war?",
        "category": "Philosophy & Concepts",
        "keywords": ["war", "dharma yuddha", "just war"],
        "difficulty": "advanced"
    },
    {
        "question": "What is the concept of 'Dharma Yuddha' in the Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["dharma yuddha", "righteous war", "just war"],
        "difficulty": "intermediate"
    },
    
    # Nature & Environment
    {
        "question": "What does the Gita say about nature and the environment?",
        "category": "Modern Application",
        "keywords": ["nature", "environment", "ecology", "sustainability"],
        "difficulty": "beginner"
    },
    
    # Education & Learning
    {
        "question": "What is the Gita's view on education?",
        "category": "Modern Application",
        "keywords": ["education", "learning", "knowledge", "vidya"],
        "difficulty": "beginner"
    },
    
    # Health & Well-being
    {
        "question": "What does the Gita say about maintaining good health?",
        "category": "Modern Application",
        "keywords": ["health", "well-being", "ayurveda", "lifestyle"],
        "difficulty": "beginner"
    },
    
    # Art & Culture
    {
        "question": "How has the Gita influenced Indian art and culture?",
        "category": "Modern Application",
        "keywords": ["art", "culture", "influence", "heritage"],
        "difficulty": "intermediate"
    },
    
    # Science & Technology
    {
        "question": "How does the Gita's philosophy relate to modern science?",
        "category": "Modern Application",
        "keywords": ["science", "technology", "physics", "quantum mechanics"],
        "difficulty": "advanced"
    },
    
    # Happiness & Contentment
    {
        "question": "What is the Gita's formula for lasting happiness?",
        "category": "Modern Application",
        "keywords": ["happiness", "contentment", "sukha", "peace"],
        "difficulty": "beginner"
    },
    
    # Fear & Courage
    {
        "question": "How does the Gita suggest overcoming fear?",
        "category": "Modern Application",
        "keywords": ["fear", "courage", "bravery", "overcoming challenges"],
        "difficulty": "beginner"
    },
    
    # Success & Achievement
    {
        "question": "What is the Gita's definition of true success?",
        "category": "Modern Application",
        "keywords": ["success", "achievement", "goals", "purpose"],
        "difficulty": "beginner"
    },
    
    # Aging & Death
    {
        "question": "How should one face old age according to the Gita?",
        "category": "Death & Afterlife",
        "keywords": ["aging", "old age", "life stages", "vanaprastha"],
        "difficulty": "intermediate"
    },
    
    # Society & Politics
    {
        "question": "What are the Gita's teachings on good governance?",
        "category": "Modern Application",
        "keywords": ["governance", "politics", "leadership", "raj dharma"],
        "difficulty": "intermediate"
    },
    
    # Love & Devotion
    {
        "question": "What is the nature of divine love in the Gita?",
        "category": "Bhakti Yoga",
        "keywords": ["divine love", "prema", "devotion", "bhakti"],
        "difficulty": "intermediate"
    },
    
    # Knowledge & Wisdom
    {
        "question": "What is the difference between knowledge and wisdom in the Gita?",
        "category": "Jnana Yoga",
        "keywords": ["knowledge", "wisdom", "jnana", "vijnana"],
        "difficulty": "intermediate"
    },
    
    # Service & Charity
    {
        "question": "What does the Gita say about selfless service?",
        "category": "Karma Yoga",
        "keywords": ["selfless service", "seva", "charity", "giving"],
        "difficulty": "beginner"
    },
    
    # Peace & Harmony
    {
        "question": "How can the Gita's teachings promote world peace?",
        "category": "Modern Application",
        "keywords": ["peace", "harmony", "global", "unity"],
        "difficulty": "beginner"
    },
    
    # Additional Questions (115-200)
    
    # Self-Realization
    {
        "question": "What is the concept of 'Atman' in the Bhagavad Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["atman", "soul", "self", "true nature"],
        "difficulty": "intermediate"
    },
    {
        "question": "How does the Gita describe the process of self-realization?",
        "category": "Philosophy & Concepts",
        "keywords": ["self-realization", "enlightenment", "awakening"],
        "difficulty": "advanced"
    },
    
    # Spiritual Practices
    {
        "question": "What is the significance of 'Om' in the Gita?",
        "category": "Meditation & Yoga",
        "keywords": ["om", "pranava", "sacred sound", "meditation"],
        "difficulty": "intermediate"
    },
    {
        "question": "How does the Gita describe the practice of 'Pratipaksha Bhavana'?",
        "category": "Meditation & Yoga",
        "keywords": ["pratipaksha bhavana", "cultivating opposites", "mind control"],
        "difficulty": "advanced"
    },
    
    # Ethics & Conduct
    {
        "question": "What is the Gita's teaching on honesty and integrity?",
        "category": "Ethics & Morality",
        "keywords": ["honesty", "integrity", "truthfulness", "character"],
        "difficulty": "beginner"
    },
    {
        "question": "How does the Gita view the concept of 'Aparigraha' (non-possessiveness)?",
        "category": "Ethics & Morality",
        "keywords": ["aparigraha", "non-possessiveness", "detachment", "simplicity"],
        "difficulty": "intermediate"
    },
    
    # Work & Karma
    {
        "question": "What is the Gita's perspective on work-life balance?",
        "category": "Modern Application",
        "keywords": ["work-life balance", "career", "professional life"],
        "difficulty": "beginner"
    },
    {
        "question": "How does the Gita guide us in making difficult decisions?",
        "category": "Modern Application",
        "keywords": ["decision making", "choices", "discernment"],
        "difficulty": "intermediate"
    },
    
    # Relationships
    {
        "question": "What does the Gita say about friendship?",
        "category": "Dharma & Duty",
        "keywords": ["friendship", "relationships", "sangha", "company"],
        "difficulty": "beginner"
    },
    {
        "question": "How does the Gita view the relationship between teacher and student?",
        "category": "Characters & Stories",
        "keywords": ["guru-shishya", "teacher-student", "learning", "transmission"],
        "difficulty": "intermediate"
    },
    
    # Science & Philosophy
    {
        "question": "How does the Gita's concept of time relate to modern physics?",
        "category": "Philosophy & Concepts",
        "keywords": ["time", "physics", "relativity", "cosmology"],
        "difficulty": "advanced"
    },
    {
        "question": "What is the Gita's view on the nature of reality?",
        "category": "Philosophy & Concepts",
        "keywords": ["reality", "maya", "illusion", "perception"],
        "difficulty": "advanced"
    },
    
    # Women & Society
    {
        "question": "What role do women play in the Gita's teachings?",
        "category": "Philosophy & Concepts",
        "keywords": ["women", "gender", "society", "roles"],
        "difficulty": "intermediate"
    },
    
    # War & Conflict
    {
        "question": "How does the Gita differentiate between just and unjust war?",
        "category": "Philosophy & Concepts",
        "keywords": ["just war", "dharma yuddha", "ethics of war"],
        "difficulty": "advanced"
    },
    {
        "question": "What is the concept of 'Dharmakshetra' in the Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["dharmakshetra", "field of dharma", "battlefield"],
        "difficulty": "intermediate"
    },
    
    # Nature & Environment
    {
        "question": "What is the Gita's ecological message?",
        "category": "Modern Application",
        "keywords": ["ecology", "environment", "nature", "sustainability"],
        "difficulty": "beginner"
    },
    
    # Education & Learning
    {
        "question": "How does the Gita define true knowledge?",
        "category": "Modern Application",
        "keywords": ["knowledge", "wisdom", "learning", "education"],
        "difficulty": "intermediate"
    },
    
    # Health & Wellbeing
    {
        "question": "What is the Gita's approach to mental health?",
        "category": "Modern Application",
        "keywords": ["mental health", "wellbeing", "peace of mind"],
        "difficulty": "beginner"
    },
    
    # Art & Literature
    {
        "question": "How has the Gita influenced Indian literature?",
        "category": "Modern Application",
        "keywords": ["literature", "influence", "culture", "heritage"],
        "difficulty": "intermediate"
    },
    
    # Science & Spirituality
    {
        "question": "How does the Gita's philosophy align with quantum physics?",
        "category": "Modern Application",
        "keywords": ["quantum physics", "science", "consciousness"],
        "difficulty": "advanced"
    },
    
    # Happiness & Fulfillment
    {
        "question": "What is the Gita's secret to lasting happiness?",
        "category": "Modern Application",
        "keywords": ["happiness", "fulfillment", "contentment", "joy"],
        "difficulty": "beginner"
    },
    
    # Overcoming Challenges
    {
        "question": "How does the Gita suggest dealing with adversity?",
        "category": "Modern Application",
        "keywords": ["adversity", "challenges", "difficulties", "resilience"],
        "difficulty": "beginner"
    },
    
    # Success & Achievement
    {
        "question": "What is the Gita's view on material success?",
        "category": "Modern Application",
        "keywords": ["material success", "wealth", "prosperity", "goals"],
        "difficulty": "beginner"
    },
    
    # Aging & Wisdom
    {
        "question": "What guidance does the Gita offer for the elderly?",
        "category": "Modern Application",
        "keywords": ["aging", "elderly", "wisdom years", "vanaprastha"],
        "difficulty": "intermediate"
    },
    
    # Society & Governance
    {
        "question": "What are the Gita's principles of good leadership?",
        "category": "Modern Application",
        "keywords": ["leadership", "governance", "raj dharma", "politics"],
        "difficulty": "intermediate"
    },
    
    # Devotion & Love
    {
        "question": "What is the nature of divine love in the Gita?",
        "category": "Bhakti Yoga",
        "keywords": ["divine love", "prema", "devotion", "bhakti"],
        "difficulty": "intermediate"
    },
    
    # Knowledge & Wisdom
    {
        "question": "What is the difference between knowledge and wisdom in the Gita?",
        "category": "Jnana Yoga",
        "keywords": ["knowledge", "wisdom", "jnana", "vijnana"],
        "difficulty": "intermediate"
    },
    
    # Service & Compassion
    {
        "question": "How does the Gita define true service?",
        "category": "Karma Yoga",
        "keywords": ["service", "seva", "compassion", "helping others"],
        "difficulty": "beginner"
    },
    
    # Unity & Diversity
    {
        "question": "How does the Gita promote unity in diversity?",
        "category": "Modern Application",
        "keywords": ["unity", "diversity", "harmony", "inclusivity"],
        "difficulty": "beginner"
    },
    
    # Additional Questions (144-200)
    
    # Mind & Intellect
    {
        "question": "What is the Gita's teaching on controlling the mind?",
        "category": "Philosophy & Concepts",
        "keywords": ["mind control", "manas", "thoughts", "meditation"],
        "difficulty": "intermediate"
    },
    {
        "question": "How does the Gita describe the nature of the intellect?",
        "category": "Philosophy & Concepts",
        "keywords": ["intellect", "buddhi", "discrimination", "wisdom"],
        "difficulty": "intermediate"
    },
    
    # Spiritual Paths
    {
        "question": "What is the significance of the three paths (margas) in the Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["jnana yoga", "bhakti yoga", "karma yoga", "paths"],
        "difficulty": "intermediate"
    },
    {
        "question": "How does the Gita reconcile different spiritual paths?",
        "category": "Philosophy & Concepts",
        "keywords": ["paths to god", "spiritual practices", "unity of paths"],
        "difficulty": "advanced"
    },
    
    # Time & Eternity
    {
        "question": "What is the concept of 'Kala' (time) in the Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["kala", "time", "eternity", "cycles"],
        "difficulty": "intermediate"
    },
    
    # Ethics of War
    {
        "question": "What is the Gita's perspective on the ethics of war?",
        "category": "Philosophy & Concepts",
        "keywords": ["war ethics", "just war", "dharma yuddha"],
        "difficulty": "advanced"
    },
    
    # Modern Psychology
    {
        "question": "How does the Gita's psychology relate to modern psychology?",
        "category": "Modern Application",
        "keywords": ["psychology", "mind", "behavior", "therapy"],
        "difficulty": "intermediate"
    },
    
    # Social Responsibility
    {
        "question": "What is the Gita's view on social responsibility?",
        "category": "Modern Application",
        "keywords": ["social responsibility", "community", "society", "duty"],
        "difficulty": "beginner"
    },
    
    # Technology & Spirituality
    {
        "question": "How can the Gita guide us in the age of technology?",
        "category": "Modern Application",
        "keywords": ["technology", "digital age", "modern life", "balance"],
        "difficulty": "intermediate"
    },
    
    # Environmental Ethics
    {
        "question": "What are the environmental ethics in the Gita?",
        "category": "Modern Application",
        "keywords": ["environment", "ecology", "sustainability", "nature"],
        "difficulty": "beginner"
    },
    
    # Leadership & Management
    {
        "question": "What are the Gita's teachings on effective leadership?",
        "category": "Modern Application",
        "keywords": ["leadership", "management", "governance", "authority"],
        "difficulty": "intermediate"
    },
    
    # Work & Career
    {
        "question": "How does the Gita view professional success?",
        "category": "Modern Application",
        "keywords": ["career", "profession", "success", "vocation"],
        "difficulty": "beginner"
    },
    
    # Family Life
    {
        "question": "What guidance does the Gita offer for family life?",
        "category": "Modern Application",
        "keywords": ["family", "relationships", "householder", "grihastha"],
        "difficulty": "beginner"
    },
    
    # Education & Learning
    {
        "question": "What is the Gita's approach to education?",
        "category": "Modern Application",
        "keywords": ["education", "learning", "teaching", "knowledge"],
        "difficulty": "beginner"
    },
    
    # Health & Well-being
    {
        "question": "What are the Gita's teachings on health and well-being?",
        "category": "Modern Application",
        "keywords": ["health", "well-being", "holistic health", "healing"],
        "difficulty": "beginner"
    },
    
    # Art & Creativity
    {
        "question": "How does the Gita view art and creativity?",
        "category": "Modern Application",
        "keywords": ["art", "creativity", "expression", "beauty"],
        "difficulty": "intermediate"
    },
    
    # Science & Spirituality
    {
        "question": "How does the Gita bridge science and spirituality?",
        "category": "Modern Application",
        "keywords": ["science", "spirituality", "cosmology", "consciousness"],
        "difficulty": "advanced"
    },
    
    # Happiness & Contentment
    {
        "question": "What is the Gita's formula for lasting happiness?",
        "category": "Modern Application",
        "keywords": ["happiness", "contentment", "joy", "fulfillment"],
        "difficulty": "beginner"
    },
    
    # Overcoming Fear
    {
        "question": "How does the Gita teach us to overcome fear?",
        "category": "Modern Application",
        "keywords": ["fear", "anxiety", "courage", "fearlessness"],
        "difficulty": "beginner"
    },
    
    # Success & Achievement
    {
        "question": "What is the Gita's definition of true success?",
        "category": "Modern Application",
        "keywords": ["success", "achievement", "goals", "fulfillment"],
        "difficulty": "beginner"
    },
    
    # Aging & Wisdom
    {
        "question": "What wisdom does the Gita offer about aging?",
        "category": "Modern Application",
        "keywords": ["aging", "elderly", "wisdom", "vanaprastha"],
        "difficulty": "intermediate"
    },
    
    # Death & Beyond
    {
        "question": "What happens after death according to the Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["death", "afterlife", "rebirth", "immortality"],
        "difficulty": "intermediate"
    },
    
    # Society & Politics
    {
        "question": "What are the Gita's teachings on good governance?",
        "category": "Modern Application",
        "keywords": ["governance", "politics", "raj dharma", "leadership"],
        "difficulty": "intermediate"
    },
    
    # Love & Devotion
    {
        "question": "What is the nature of divine love in the Gita?",
        "category": "Bhakti Yoga",
        "keywords": ["love", "devotion", "bhakti", "divine love"],
        "difficulty": "intermediate"
    },
    
    # Knowledge & Wisdom
    {
        "question": "How does one attain true wisdom according to the Gita?",
        "category": "Jnana Yoga",
        "keywords": ["wisdom", "knowledge", "jnana", "enlightenment"],
        "difficulty": "advanced"
    },
    
    # Selfless Service
    {
        "question": "What is the importance of selfless service in the Gita?",
        "category": "Karma Yoga",
        "keywords": ["selfless service", "seva", "karma yoga", "action"],
        "difficulty": "beginner"
    },
    
    # Unity in Diversity
    {
        "question": "How does the Gita view the unity of all existence?",
        "category": "Philosophy & Concepts",
        "keywords": ["unity", "oneness", "diversity", "cosmic vision"],
        "difficulty": "intermediate"
    },
    
    # Final Questions (171-200)
    
    # Mind & Meditation
    {
        "question": "What is the Gita's approach to taming the restless mind?",
        "category": "Meditation & Yoga",
        "keywords": ["mind control", "meditation", "concentration", "dhyana"],
        "difficulty": "intermediate"
    },
    
    # Spiritual Discipline
    {
        "question": "What is the importance of discipline (sadhana) in the Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["discipline", "sadhana", "practice", "spiritual growth"],
        "difficulty": "intermediate"
    },
    
    # Divine Grace
    {
        "question": "What is the role of divine grace in spiritual progress according to the Gita?",
        "category": "Bhakti Yoga",
        "keywords": ["grace", "divine intervention", "kripa", "surrender"],
        "difficulty": "advanced"
    },
    
    # Karma and Rebirth
    {
        "question": "How does the Gita explain the cycle of birth and rebirth?",
        "category": "Philosophy & Concepts",
        "keywords": ["rebirth", "reincarnation", "samsara", "cycle of birth and death"],
        "difficulty": "intermediate"
    },
    
    # The Three Gunas
    {
        "question": "What are the three gunas (qualities) described in the Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["gunas", "sattva", "rajas", "tamas", "qualities"],
        "difficulty": "intermediate"
    },
    
    # The Cosmic Form
    {
        "question": "What is the significance of Krishna's cosmic form (Vishvarupa) in the Gita?",
        "category": "Characters & Stories",
        "keywords": ["vishvarupa", "cosmic form", "universal form", "chapter 11"],
        "difficulty": "advanced"
    },
    
    # The Field and the Knower
    {
        "question": "What is the distinction between the field (kshetra) and the knower of the field (kshetrajna) in the Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["kshetra", "kshetrajna", "field", "knower", "chapter 13"],
        "difficulty": "advanced"
    },
    
    # The Divine and Demonic Natures
    {
        "question": "How does the Gita describe divine and demonic natures?",
        "category": "Philosophy & Concepts",
        "keywords": ["divine nature", "demonic nature", "daivi sampat", "asuri sampat"],
        "difficulty": "intermediate"
    },
    
    # The Importance of Satsang
    {
        "question": "What is the significance of satsang (holy company) in the Gita?",
        "category": "Modern Application",
        "keywords": ["satsang", "holy company", "spiritual association"],
        "difficulty": "beginner"
    },
    
    # The Concept of Maya
    {
        "question": "How does the Gita explain the concept of maya (illusion)?",
        "category": "Philosophy & Concepts",
        "keywords": ["maya", "illusion", "reality", "perception"],
        "difficulty": "advanced"
    },
    
    # The Four Varnas
    {
        "question": "What is the Gita's perspective on the four varnas (social orders)?",
        "category": "Philosophy & Concepts",
        "keywords": ["varna", "caste", "social order", "guna-karma"],
        "difficulty": "intermediate"
    },
    
    # The Threefold Faith
    {
        "question": "What does the Gita say about the threefold nature of faith?",
        "category": "Philosophy & Concepts",
        "keywords": ["faith", "shraddha", "threefold", "guna"],
        "difficulty": "intermediate"
    },
    
    # The Importance of Shraddha
    {
        "question": "What is the role of shraddha (faith) in spiritual life according to the Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["shraddha", "faith", "conviction", "spiritual progress"],
        "difficulty": "intermediate"
    },
    
    # The Concept of Avatara
    {
        "question": "What is the Gita's teaching on avataras (divine incarnations)?",
        "category": "Philosophy & Concepts",
        "keywords": ["avatara", "incarnation", "divine descent", "yuga dharma"],
        "difficulty": "intermediate"
    },
    
    # The Yoga of the Despondency of Arjuna
    {
        "question": "What is the significance of Arjuna's despondency in the first chapter of the Gita?",
        "category": "Characters & Stories",
        "keywords": ["arjuna", "despondency", "vishada yoga", "chapter 1"],
        "difficulty": "intermediate"
    },
    
    # The Divine and Demonic Natures (Expanded)
    {
        "question": "How can one cultivate divine qualities according to the Gita?",
        "category": "Modern Application",
        "keywords": ["divine qualities", "daivi sampat", "spiritual development"],
        "difficulty": "intermediate"
    },
    
    # The Concept of Daiva and Asura
    {
        "question": "What is the difference between daiva (divine) and asura (demonic) natures in the Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["daiva", "asura", "divine", "demonic", "nature"],
        "difficulty": "intermediate"
    },
    
    # The Importance of Right Association
    {
        "question": "Why is right association important in spiritual life according to the Gita?",
        "category": "Modern Application",
        "keywords": ["association", "satsang", "company", "influence"],
        "difficulty": "beginner"
    },
    
    # The Concept of Sthitaprajna
    {
        "question": "Who is a sthita-prajna (person of steady wisdom) according to the Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["sthita-prajna", "steady wisdom", "enlightened being"],
        "difficulty": "advanced"
    },
    
    # The Importance of Self-Knowledge
    {
        "question": "Why is self-knowledge emphasized in the Gita?",
        "category": "Jnana Yoga",
        "keywords": ["self-knowledge", "atma-jnana", "self-realization"],
        "difficulty": "intermediate"
    },
    
    # The Concept of Ananya Bhakti
    {
        "question": "What is ananya bhakti (exclusive devotion) in the Gita?",
        "category": "Bhakti Yoga",
        "keywords": ["ananya bhakti", "exclusive devotion", "surrender"],
        "difficulty": "advanced"
    },
    
    # The Importance of Guru
    {
        "question": "What is the role of a guru (spiritual teacher) according to the Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["guru", "teacher", "disciple", "parampara"],
        "difficulty": "intermediate"
    },
    
    # The Concept of Sannyasa and Tyaga
    {
        "question": "What is the difference between sannyasa (renunciation) and tyaga (renunciation of the fruits of action) in the Gita?",
        "category": "Karma Yoga",
        "keywords": ["sannyasa", "tyaga", "renunciation", "action"],
        "difficulty": "advanced"
    },
    
    # The Ultimate Goal of Life
    {
        "question": "What is the ultimate goal of human life according to the Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["goal of life", "moksha", "liberation", "perfection"],
        "difficulty": "beginner"
    },
    
    # The Concept of Para and Apara Prakriti
    {
        "question": "What is the difference between para (higher) and apara (lower) prakriti (nature) in the Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["para prakriti", "apara prakriti", "higher nature", "lower nature"],
        "difficulty": "advanced"
    },
    
    # The Importance of Sattvic Food
    {
        "question": "What does the Gita say about the importance of sattvic food?",
        "category": "Modern Application",
        "keywords": ["sattvic food", "diet", "purity", "health"],
        "difficulty": "beginner"
    },
    
    # The Concept of Ananya Chintana
    {
        "question": "What is the significance of ananya chintana (exclusive contemplation) in the Gita?",
        "category": "Bhakti Yoga",
        "keywords": ["ananya chintana", "contemplation", "meditation", "devotion"],
        "difficulty": "advanced"
    },
    
    # The Final Message
    {
        "question": "What is the final message of the Bhagavad Gita?",
        "category": "Introduction",
        "keywords": ["final message", "conclusion", "essence", "summary"],
        "difficulty": "beginner"
    },
    
    # Final Questions (199-200)
    
    # The Power of Surrender
    {
        "question": "What is the significance of complete surrender (prapatti) in the Gita?",
        "category": "Bhakti Yoga",
        "keywords": ["surrender", "prapatti", "self-surrender", "devotion"],
        "difficulty": "intermediate"
    },
    
    # The Eternal Dharma
    {
        "question": "What is the eternal dharma (sanatana dharma) according to the Gita?",
        "category": "Philosophy & Concepts",
        "keywords": ["sanatana dharma", "eternal duty", "universal principles"],
        "difficulty": "intermediate"
    }
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
