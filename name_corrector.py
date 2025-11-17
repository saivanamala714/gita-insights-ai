"""
Name Corrector for Bhagavad Gita Characters

This module provides functionality to correct and standardize character names
in user queries to their canonical forms using a combination of:
1. Direct string matching with common misspellings
2. Phonetic similarity
3. Edit distance
"""
from typing import Dict, Optional, List, Tuple
import re
from collections import defaultdict
from difflib import get_close_matches
import jellyfish

# Import the character database
from gita_characters import CHARACTERS, get_character_info

class NameCorrector:
    """Class to handle name correction for Bhagavad Gita characters."""
    
    def __init__(self, threshold: float = 0.6):
        """
        Initialize the name corrector.
        
        Args:
            threshold: Minimum similarity score (0-1) to consider a match
        """
        self.threshold = threshold
        self.name_map = self._build_name_map()
        self.phonetic_map = self._build_phonetic_map()
        
    def _build_name_map(self) -> Dict[str, str]:
        """Build a mapping of all possible name variations to their canonical forms."""
        name_map = {}
        
        # Common misspellings and variations
        common_misspellings = {
            # Krishna
            'krishna': ['krsna', 'krushna', 'krishn', 'krishana', 'krisna', 'krshna'],
            'krsna': ['krishna', 'krushna', 'krishn', 'krishana', 'krisna', 'krshna'],
            
            # Arjuna
            'arjuna': ['arjun', 'arjoon', 'arjoona', 'arjunn'],
            
            # Bhishma
            'bhishma': ['bheeshma', 'bheeshm', 'bhishm', 'bheesma', 'bheeshmaa'],
            
            # Duryodhana
            'duryodhana': ['duryodhan', 'duryodhna', 'duryodhan', 'duryodhanna'],
            
            # Yudhishthira
            'yudhishthira': ['yudhisthira', 'yudhishtir', 'yudhisthir', 'dharmaraja'],
            
            # Draupadi
            'draupadi': ['dropadi', 'draupadi', 'draupadi', 'panchali', 'krishnaa'],
            
            # Karna
            'karna': ['karn', 'karan', 'karana', 'radheya'],
            
            # Dronacharya
            'dronacharya': ['drona', 'dron', 'dronacarya'],
            
            # Common prefixes/suffixes
            'maharathi': ['maharath', 'maharathi', 'maharathin'],
            'deva': ['dev', 'devta', 'daiva'],
            'asura': ['asur', 'asurta'],
        }
        
        # Add all primary names and their aliases to the map
        for char_name, char_info in CHARACTERS.items():
            primary = char_info["primary_name"].lower()
            
            # Map primary name to itself
            name_map[primary] = primary
            
            # Map all aliases to primary name
            for alias in char_info["aliases"]:
                alias_lower = alias.lower()
                name_map[alias_lower] = primary
                
                # Add common variations of aliases
                if alias_lower in common_misspellings:
                    for variation in common_misspellings[alias_lower]:
                        name_map[variation] = primary
        
        # Add common misspellings for primary names
        for primary, variations in common_misspellings.items():
            if primary in name_map:  # Only if it's a primary name we know
                for variation in variations:
                    name_map[variation] = primary
        
        return name_map
    
    def _build_phonetic_map(self) -> Dict[str, List[Tuple[str, str]]]:
        """Build a phonetic map of names for fuzzy matching."""
        phonetic_map = defaultdict(list)
        
        # Add primary names and aliases to phonetic map
        for char_name, char_info in CHARACTERS.items():
            primary = char_info["primary_name"].lower()
            names_to_add = [primary] + [a.lower() for a in char_info["aliases"]]
            
            for name in names_to_add:
                # Generate phonetic hashes using different algorithms
                soundex = jellyfish.soundex(name)
                metaphone = jellyfish.metaphone(name)
                nysiis = jellyfish.nysiis(name)
                
                # Map each phonetic variant back to the primary name
                phonetic_map[soundex].append((name, primary))
                phonetic_map[metaphone].append((name, primary))
                phonetic_map[nysiis].append((name, primary))
        
        return dict(phonetic_map)
    
    def _get_phonetic_matches(self, name: str) -> List[Tuple[str, str]]:
        """Get potential matches using phonetic algorithms."""
        name = name.lower()
        matches = set()
        
        # Generate phonetic hashes for the input name
        soundex = jellyfish.soundex(name)
        metaphone = jellyfish.metaphone(name)
        nysiis = jellyfish.nysiis(name)
        
        # Find all names that share any phonetic hash
        for phonetic in [soundex, metaphone, nysiis]:
            if phonetic in self.phonetic_map:
                matches.update(self.phonetic_map[phonetic])
        
        return list(matches)
    
    def _get_edit_distance_score(self, s1: str, s2: str) -> float:
        """Calculate normalized edit distance similarity (0-1)."""
        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return 1.0
        
        distance = jellyfish.levenshtein_distance(s1, s2)
        return 1.0 - (distance / max_len)
    
    def correct_name(self, name: str) -> Tuple[Optional[str], float]:
        """
        Correct a potentially misspelled name to its canonical form.
        
        Args:
            name: The input name to correct
            
        Returns:
            A tuple of (corrected_name, confidence_score) where confidence is between 0 and 1
        """
        if not name or not name.strip():
            return None, 0.0
            
        name = name.lower().strip()
        
        # Check for direct match first (fast path)
        if name in self.name_map:
            return self.name_map[name], 1.0
        
        # Check for partial matches (e.g., 'krish' should match 'krishna')
        for known_name, primary in self.name_map.items():
            if name in known_name or known_name in name:
                # Calculate a confidence score based on length ratio
                ratio = min(len(name), len(known_name)) / max(len(name), len(known_name))
                if ratio >= self.threshold:
                    return primary, ratio * 0.9  # Slightly penalize partial matches
        
        # Try fuzzy matching using edit distance
        best_match = None
        best_score = 0.0
        
        # Consider all known names (primary + aliases)
        all_names = set(self.name_map.keys()) | set(self.name_map.values())
        
        for known_name in all_names:
            score = self._get_edit_distance_score(name, known_name)
            if score > best_score and score >= self.threshold:
                best_match = known_name
                best_score = score
        
        if best_match:
            return self.name_map[best_match], best_score
        
        # Try phonetic matching as a last resort
        phonetic_matches = self._get_phonetic_matches(name)
        if phonetic_matches:
            # Find the best phonetic match by edit distance
            best_phonetic = max(
                phonetic_matches,
                key=lambda x: self._get_edit_distance_score(name, x[0])
            )
            score = self._get_edit_distance_score(name, best_phonetic[0])
            if score >= self.threshold:
                return best_phonetic[1], score * 0.8  # Phonetic matches get a slight penalty
        
        return None, 0.0
    
    def correct_text(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Correct all character names in a piece of text.
        
        Args:
            text: The input text to correct
            
        Returns:
            A tuple of (corrected_text, corrections_made) where corrections_made is a dict
            mapping original terms to their corrected forms
        """
        if not text:
            return text, {}
            
        # Tokenize the text (simple word-based tokenizer)
        words = re.findall(r'\b\w+\b', text)
        corrections = {}
        
        # Check each word and its context
        for i, word in enumerate(words):
            # Skip very short words (they're unlikely to be names)
            if len(word) < 3:
                continue
                
            # Check if the word is a known name or close to one
            corrected, score = self.correct_name(word)
            
            # If we found a good match, record the correction
            if corrected and score >= self.threshold and word.lower() != corrected:
                original = word
                
                # Preserve the original capitalization pattern
                if word[0].isupper():
                    if len(word) > 1 and word[1:].islower():
                        corrected = corrected.capitalize()
                    else:
                        corrected = corrected.upper()
                
                corrections[original] = corrected
        
        # Apply all corrections to the original text
        if corrections:
            for orig, corr in corrections.items():
                # Use regex to preserve word boundaries
                text = re.sub(r'\b' + re.escape(orig) + r'\b', corr, text)
        
        return text, corrections


# Create a global instance for easy access
name_corrector = NameCorrector()


def correct_character_name(name: str) -> Tuple[Optional[str], float]:
    """
    Correct a single character name.
    
    Args:
        name: The name to correct
        
    Returns:
        A tuple of (corrected_name, confidence_score)
    """
    return name_corrector.correct_name(name)


def correct_text_names(text: str) -> Tuple[str, Dict[str, str]]:
    """
    Correct all character names in a piece of text.
    
    Args:
        text: The text to process
        
    Returns:
        A tuple of (corrected_text, corrections_made)
    """
    return name_corrector.correct_text(text)


if __name__ == "__main__":
    # Example usage
    test_names = ["bheeshma", "krsna", "arjun", "yudhistir", "karan", "duryodhan"]
    
    print("Name Correction Examples:")
    print("-" * 30)
    for name in test_names:
        corrected, score = correct_character_name(name)
        print(f"{name} -> {corrected} (confidence: {score*100:.1f}%)")
    
    test_text = "Bheeshma was a great warrior, second only to karan and arjun in skill."
    print("\nText Correction Example:")
    print("-" * 30)
    print(f"Original: {test_text}")
    corrected_text, corrections = correct_text_names(test_text)
    print(f"Corrected: {corrected_text}")
    print(f"Corrections made: {corrections}")
