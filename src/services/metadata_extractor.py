"""Extract metadata from questions and answers (chapters, themes, characters)."""
import re
from typing import Dict, List, Any, Set
import logging

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Extract metadata from Bhagavad Gita Q&A interactions."""
    
    # Chapter keywords mapping
    CHAPTER_KEYWORDS = {
        1: ['arjuna', 'vishada', 'yoga', 'grief', 'despondency', 'battlefield'],
        2: ['sankhya', 'soul', 'atman', 'eternal', 'body', 'death', 'rebirth'],
        3: ['karma', 'action', 'duty', 'selfless', 'work'],
        4: ['jnana', 'knowledge', 'wisdom', 'sacrifice', 'yajna'],
        5: ['sannyasa', 'renunciation', 'karma yoga'],
        6: ['dhyana', 'meditation', 'yoga', 'mind control'],
        7: ['jnana', 'vijnana', 'knowledge', 'wisdom'],
        8: ['aksara', 'brahman', 'imperishable', 'om'],
        9: ['raja', 'vidya', 'royal', 'knowledge', 'secret'],
        10: ['vibhuti', 'opulence', 'manifestation', 'glory'],
        11: ['vishvarupa', 'universal form', 'cosmic form'],
        12: ['bhakti', 'devotion', 'love', 'worship'],
        13: ['kshetra', 'kshetrajna', 'field', 'knower'],
        14: ['guna', 'sattva', 'rajas', 'tamas', 'modes'],
        15: ['purushottama', 'supreme person', 'tree'],
        16: ['daiva', 'asura', 'divine', 'demonic', 'qualities'],
        17: ['shraddha', 'faith', 'threefold'],
        18: ['moksha', 'liberation', 'freedom', 'conclusion']
    }
    
    # Common themes in Bhagavad Gita
    THEMES = [
        'dharma', 'karma', 'yoga', 'bhakti', 'jnana', 'meditation',
        'duty', 'action', 'devotion', 'knowledge', 'wisdom', 'soul',
        'atman', 'brahman', 'liberation', 'moksha', 'detachment',
        'renunciation', 'sacrifice', 'selfless service', 'mind control',
        'faith', 'surrender', 'divine', 'supreme', 'eternal'
    ]
    
    # Main characters
    CHARACTERS = [
        'krishna', 'arjuna', 'sanjaya', 'dhritarashtra',
        'pandavas', 'kauravas', 'bhishma', 'drona', 'karna'
    ]
    
    def extract_metadata(self, question: str, answer: str) -> Dict[str, Any]:
        """
        Extract all metadata from a Q&A pair.
        
        Returns:
            Dict with chapter_references, verse_references, themes, characters_mentioned
        """
        combined_text = f"{question} {answer}".lower()
        
        return {
            'chapter_references': self.extract_chapters(combined_text),
            'verse_references': self.extract_verses(combined_text),
            'themes': self.extract_themes(combined_text),
            'characters_mentioned': self.extract_characters(combined_text)
        }
    
    def extract_chapters(self, text: str) -> List[int]:
        """Extract chapter references from text."""
        chapters = set()
        
        # Direct chapter mentions (e.g., "Chapter 2", "chapter 3")
        chapter_pattern = r'chapter\s+(\d+)'
        matches = re.findall(chapter_pattern, text, re.IGNORECASE)
        for match in matches:
            chapter_num = int(match)
            if 1 <= chapter_num <= 18:
                chapters.add(chapter_num)
        
        # Verse references (e.g., "2.47", "BG 3.27")
        verse_pattern = r'(?:bg\s*)?(\d+)[\.:](\d+)'
        matches = re.findall(verse_pattern, text, re.IGNORECASE)
        for match in matches:
            chapter_num = int(match[0])
            if 1 <= chapter_num <= 18:
                chapters.add(chapter_num)
        
        # Keyword-based chapter detection
        for chapter_num, keywords in self.CHAPTER_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    chapters.add(chapter_num)
                    break  # One match per chapter is enough
        
        return sorted(list(chapters))
    
    def extract_verses(self, text: str) -> List[str]:
        """Extract verse references from text."""
        verses = set()
        
        # Pattern: "2.47", "BG 3.27", "Gita 4:5"
        patterns = [
            r'(?:bg|gita)?\s*(\d+)[\.:](\d+)',
            r'verse\s+(\d+)[\.:](\d+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                chapter = int(match[0])
                verse = int(match[1])
                if 1 <= chapter <= 18:
                    verses.add(f"{chapter}.{verse}")
        
        return sorted(list(verses))
    
    def extract_themes(self, text: str) -> List[str]:
        """Extract themes from text."""
        found_themes = set()
        
        for theme in self.THEMES:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(theme.lower()) + r'\b'
            if re.search(pattern, text):
                found_themes.add(theme)
        
        return sorted(list(found_themes))
    
    def extract_characters(self, text: str) -> List[str]:
        """Extract character mentions from text."""
        found_characters = set()
        
        for character in self.CHARACTERS:
            pattern = r'\b' + re.escape(character.lower()) + r'\b'
            if re.search(pattern, text):
                # Capitalize first letter
                found_characters.add(character.capitalize())
        
        return sorted(list(found_characters))
    
    def get_conversation_summary(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of conversation metadata.
        
        Args:
            messages: List of message dictionaries with user_query and ai_response
        
        Returns:
            Aggregated metadata for the entire conversation
        """
        all_chapters = set()
        all_verses = set()
        all_themes = set()
        all_characters = set()
        
        for msg in messages:
            question = msg.get('user_query', '')
            answer = msg.get('ai_response', '')
            
            metadata = self.extract_metadata(question, answer)
            
            all_chapters.update(metadata['chapter_references'])
            all_verses.update(metadata['verse_references'])
            all_themes.update(metadata['themes'])
            all_characters.update(metadata['characters_mentioned'])
        
        return {
            'chapters_referenced': sorted(list(all_chapters)),
            'verse_references': sorted(list(all_verses)),
            'topics': sorted(list(all_themes)),
            'characters_mentioned': sorted(list(all_characters)),
            'total_messages': len(messages)
        }


# Global instance
metadata_extractor = MetadataExtractor()
