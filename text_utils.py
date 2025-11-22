import re
from collections import defaultdict
from typing import Dict, List, Set, Tuple
import json
import os
from tqdm import tqdm

class TextProcessor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.word_freq: Dict[str, int] = defaultdict(int)
        self.word_variants: Dict[str, Set[str]] = defaultdict(set)
        self.common_words = self._load_common_words()
        self.correction_map: Dict[str, str] = {}
        
    def _load_common_words(self) -> Set[str]:
        """Load a set of common English words and Bhagavad Gita specific terms."""
        import nltk
        from nltk.corpus import words, wordnet
        
        # Download required NLTK data
        try:
            nltk.data.find('corpora/words')
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('words')
            nltk.download('wordnet')
        
        # Get common English words
        common_words = set(words.words())
        
        # Add common Gita terms that might be useful for correction
        gita_terms = {
            'karma', 'dharma', 'bhakti', 'yoga', 'krishna', 'arjuna', 'bhagavad', 
            'gita', 'veda', 'upanishad', 'bhagavan', 'atman', 'brahman', 'moksha',
            'samsara', 'maya', 'prakriti', 'purusha', 'guna', 'jnana', 'karma',
            'bhakti', 'yogi', 'sankhya', 'yogin', 'ishvara', 'jiva', 'mahatma'
        }
        
        # Add common prefixes and suffixes for better word splitting
        prefixes = {'un', 're', 'in', 'im', 'dis', 'en', 'pre', 'pro', 'sub', 'trans'}
        suffixes = {'ing', 'ed', 'ly', 'ment', 'tion', 'sion', 'ness', 'less', 'ful', 'able'}
        
        return common_words.union(gita_terms, prefixes, suffixes)
    
    def _is_likely_error(self, word: str) -> bool:
        """Determine if a word is likely an OCR or formatting error."""
        if not word or len(word) < 2:
            return False
            
        # Skip common short words and numbers
        if len(word) <= 2 and word.lower() in {'a', 'i', 'an', 'at', 'be', 'by', 'do', 'go', 'he', 'hi', 'in', 'is', 'it', 'me', 'my', 'no', 'of', 'on', 'or', 'so', 'to', 'up', 'us', 'we'}:
            return False
            
        # Common Sanskrit and English words that should never be flagged as errors
        common_terms = {
            # Common Sanskrit terms
            'Krishna', 'Arjuna', 'Bhagavad', 'Gita', 'Veda', 'Upanishad', 'Bhagavan',
            'Atman', 'Brahman', 'Moksha', 'Samsara', 'Yoga', 'Yogi', 'Sankhya', 'Yogin', 'Jiva',
            'Mahatma', 'Bhishma', 'Duryodhana', 'Dronacharya', 'Karna', 'Vidura',
            'Vyasa', 'Dhritarashtra', 'Gandhari', 'Kunti', 'Draupadi', 'Subhadra',
            'Vasudeva', 'Devaki', 'Nanda', 'Yashoda', 'Balarama', 'Parikshit',
            'Janaka', 'Valmiki', 'Vishnu', 'Shiva', 'Brahma', 'Lakshmi', 'Saraswati',
            'Parvati', 'Durga', 'Kali', 'Hanuman', 'Garuda', 'Shesha', 'Indra', 'Agni',
            'Vayu', 'Varuna', 'Yama', 'Kubera', 'Vishvamitra', 'Vasishtha', 'Bharata',
            'Ramayana', 'Mahabharata', 'Pandava', 'Kaurava', 'Kuru', 'Panchala',
            'Gandhara', 'Kamboja', 'Sindhu', 'Sauvira', 'Madra', 'Kekaya', 'Kosala', 'Videha',
            
            # Common English words from the Bhagavad Gita context
            'soul', 'yoga', 'karma', 'dharma', 'bhakti', 'jnana', 'maya', 'prakriti', 
            'purusha', 'guna', 'ishvara', 'atma', 'bhagavad', 'gita', 'veda', 'upanishad',
            'bhagavan', 'yogi', 'sankhya', 'yogin', 'jiva', 'mahatma', 'bhishma',
            'duryodhana', 'dronacharya', 'karna', 'vidura', 'vyasa', 'dhritarashtra',
            'gandhari', 'kunti', 'draupadi', 'subhadra', 'vasudeva', 'devaki', 'nanda',
            'yashoda', 'balarama', 'parikshit', 'janaka', 'valmiki', 'vishnu', 'shiva',
            'brahma', 'lakshmi', 'saraswati', 'parvati', 'durga', 'kali', 'hanuman',
            'garuda', 'shesha', 'indra', 'agni', 'vayu', 'varuna', 'yama', 'kubera',
            'vishvamitra', 'vasishtha', 'bharata', 'ramayana', 'mahabharata', 'pandava',
            'kaurava', 'kuru', 'panchala', 'gandhara', 'kamboja', 'sindhu', 'sauvira',
            'madra', 'kekaya', 'kosala', 'videha'
        }
        
        # Check if it's in our common terms (case-insensitive)
        if word in common_terms or word.lower() in common_terms:
            return False
            
        # Check if it's a known error in our correction map
        if word in self.correction_map:
            return True
            
        # Check for common error patterns
        patterns = [
            r'[a-z][A-Z]',                 # camelCase or missing space
            r'[a-z]i[a-z]',                 # common OCR error (i in middle)
            r'[a-z]l[a-z]',                 # common OCR error (l vs I)
            r'[a-z]o[a-z]',                 # common OCR error (o vs 0)
            r'[a-z]s[a-z]',                 # common OCR error (s vs 5)
            r'[a-z]\\d',                   # letter followed by digit
            r'\\d[a-z]',                   # digit followed by letter
            r'[^\\w\\s]\\w',           # punctuation attached to word start
            r'\\w[^\\w\\s]',           # punctuation attached to word end
            r'[a-z]{2,}[A-Z][a-z]+',        # camelCase in middle of word
            r'[a-z]+[0-9]+',                # letters followed by numbers
            r'[0-9]+[a-z]+',                # numbers followed by letters
            r'([a-zA-Z])\\1{2,}',         # 3 or more repeated letters
            r'[^a-zA-Z0-9\\s]',           # any non-alphanumeric (except spaces)
            r'^[A-Z][a-z]+[A-Z]',           # mixed case words (e.g., 'TheBhagavad')
            r'[a-z][A-Z][a-z]',             # single capital in middle of word
            r'\\s'                         # contains spaces (multiple words)
        ]
        
        # Check if any pattern matches
        for pattern in patterns:
            if re.search(pattern, word):
                return True
                
        # Check if word is all uppercase (might be a heading or proper noun)
        if word.isupper() and len(word) > 1:
            return False
            
        # Check if word is in common words (case-insensitive)
        word_lower = word.lower()
        if word_lower in self.common_words or word_lower.capitalize() in self.common_words:
            return False
            
        # Check for common OCR error patterns in the word
        common_ocr_errors = [
            'rn', 'vv', 'cl', 'ij', 'in',  # Common OCR confusions
            '1', '0', '5', '8', '6', '9',  # Numbers that look like letters
            '|', '\\', '/', '`', '~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')',
            '_', '+', '=', '{', '}', '[', ']', '|', ';', ':', '"', '<', '>', '?', ',', '.',
            '“', '”', '‘', '’', '–', '—', '•', '·', '…'
        ]
        
        # If the word contains common OCR error patterns, it's likely an error
        for error in common_ocr_errors:
            if error in word:
                return True
                
        # Check if word is a common Sanskrit term (case-insensitive)
        sanskrit_terms = {
            'atma', 'brahman', 'dharma', 'karma', 'moksha', 'yoga', 'bhakti',
            'jnana', 'samsara', 'maya', 'prakriti', 'purusha', 'guna', 'ishvara',
            'krishna', 'arjuna', 'bhagavad', 'gita', 'veda', 'upanishad', 'bhagavan',
            'atman', 'brahman', 'moksha', 'samsara', 'yogi', 'sankhya', 'yogin', 'jiva',
            'mahatma', 'bhishma', 'duryodhana', 'dronacharya', 'karna', 'vidura',
            'vyasa', 'dhritarashtra', 'gandhari', 'kunti', 'draupadi', 'subhadra',
            'vasudeva', 'devaki', 'nanda', 'yashoda', 'balarama', 'subhadra', 'parikshit',
            'janaka', 'valmiki', 'vishnu', 'shiva', 'brahma', 'lakshmi', 'saraswati',
            'parvati', 'durga', 'kali', 'hanuman', 'garuda', 'shesha', 'indra', 'agni',
            'vayu', 'varuna', 'yama', 'kubera', 'vishvamitra', 'vasishtha', 'vishvamitra',
            'bharata', 'ramayana', 'mahabharata', 'pandava', 'kaurava', 'kuru', 'panchala',
            'gandhara', 'kamboja', 'sindhu', 'sauvira', 'madra', 'kekaya', 'kosala', 'videha'
        }
        
        if word_lower in sanskrit_terms or word_lower.capitalize() in sanskrit_terms:
            return False
            
        # If word is too long and not in common words, it might be a concatenation
        if len(word) > 15 and not any(c.isupper() for c in word[1:]) and word.isalpha():
            return True
            
        # Check for repeated words or characters that might indicate an error
        if re.search(r'(\w)\1{2,}', word):  # 3 or more repeated characters
            return True
            
        # Check for words with unusual character patterns
        if re.search(r'[aeiouAEIOU]{4,}', word):  # 4 or more vowels in a row
            return True
            
        if re.search(r'[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]{5,}', word):  # 5 or more consonants in a row
            return True
            
        # If we get here, it's probably not an error
        return False
    
    def _generate_correction(self, word: str) -> str:
        """Generate possible corrections for a word using multiple strategies."""
        if not word or len(word) < 2:
            return word
            
        original_word = word
        word = word.strip()
        
        # First check if we have a direct correction in our map
        if word in self.correction_map:
            return self.correction_map[word]
        
        # Common OCR error mappings - only include high-confidence replacements
        ocr_error_map = {
            # Common OCR confusions (only include very common and unambiguous ones)
            'rn': 'm', 'vv': 'w', 'cl': 'd', 'ij': 'n',
            # Don't include 'in' -> 'm' as it's too aggressive and breaks valid words like 'line'
            '1': 'l', '0': 'o', '5': 's', '8': 'b', '6': 'b', '9': 'g',
            '|': 'l', '\\': 'l', '/': 'l', '`': "'", '~': '~',
            '!': 'i', '@': 'a', '#': '', '$': 's', '%': '', '^': '',
            '&': 'and', '*': '', '(': '', ')': '', '_': ' ', '+': 't',
            '=': ' ', '{': '(', '}': ')', '[': '(', ']': ')', '|': 'l',
            ';': ':', ':': ':', '"': "'", '<': ',', '>': '.', '?': '',
            ',': ',', '.': '.', '“': '"', '”': '"', '‘': "'", '’': "'",
            '–': '-', '—': '-', '•': '-', '·': '.', '…': '...'
        }
        
        # Common word concatenations in Gita text
        common_concatenations = {
            # Basic concatenations
            'th is': 'this',
            'theBhagavad': 'the Bhagavad',
            'theGita': 'the Gita',
            'theLord': 'the Lord',
            'theSupreme': 'the Supreme',
            'acti ons': 'actions',
            'changeth is': 'change this',
            'perfecti on': 'perfection',
            'reacti ons': 'reactions',
            'preparati on': 'preparation',
            'servi ng': 'serving',
            'offeri ng': 'offering',
            'donot': 'do not',
            'tounderstand': 'to understand',
            'soulis': 'soul is',
            'karmais': 'karma is',
            'yogais': 'yoga is',
            'bhaktii': 'bhakti',
            'krishnasaid': 'Krishna said',
            'arjunasaid': 'Arjuna said',
            'lordkrishna': 'Lord Krishna',
            'bhagavadgita': 'Bhagavad Gita',
            'bhagavad-gita': 'Bhagavad-gita',
            'bhagavadgitaasitis': 'Bhagavad Gita As It Is',
            
            # More complex patterns
            'theSupremePersonalityofGodhead': 'the Supreme Personality of Godhead',
            'theSupremePersonalityofGod': 'the Supreme Personality of God',
            'theSupremePersonality': 'the Supreme Personality',
            'theSupremeLord': 'the Supreme Lord',
            'theBhagavadGita': 'the Bhagavad Gita',
            'theBhagavad-Gita': 'the Bhagavad-gita',
            'theBhagavadGitaAsItIs': 'the Bhagavad Gita As It Is',
            'theBhagavad-GitaAsItIs': 'the Bhagavad-gita As It Is',
        }
        
        # Check for common concatenations first (exact match)
        if word in common_concatenations:
            return common_concatenations[word]
            
        # Check for common concatenations (substring match)
        for concat, fixed in common_concatenations.items():
            if concat in word and len(concat) > 5:  # Only replace if the match is significant
                return word.replace(concat, fixed)
        
        # Check for common OCR errors - only apply to non-dictionary words
        # to avoid breaking valid words
        if word.lower() not in self.common_words and not word.isalpha():
            # Only apply OCR error correction to words that are likely to be errors
            # and not in our common words list
            for error, correction in ocr_error_map.items():
                if error in word:
                    # Create a test word with the replacement
                    test_word = word.replace(error, correction)
                    # Only apply if the replacement makes the word more like a known word
                    if (test_word.lower() in self.common_words or 
                        any(test_word.lower() in w for w in self.common_words)):
                        word = test_word
        
        # Handle camelCase or missing spaces (e.g., 'theBhagavad' -> 'the Bhagavad')
        if re.search(r'[a-z][A-Z]', word):
            # Insert space before capital letters preceded by lowercase
            word = re.sub(r'([a-z])([A-Z])', r'\1 \2', word)
            
            # If the first word is a common word, it's likely a good split
            parts = word.split(' ', 1)
            if len(parts) > 1:
                first_word = parts[0].lower()
                if (first_word in self.common_words or 
                    first_word in {'the', 'and', 'but', 'or', 'for', 'nor', 'so', 'yet', 
                                 'a', 'an', 'in', 'on', 'at', 'by', 'to', 'of', 'with', 
                                 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 
                                 'have', 'has', 'had', 'do', 'does', 'did', 'will', 
                                 'would', 'shall', 'should', 'may', 'might', 'must', 'can', 'could'}):
                    return word
        
        # Handle common OCR error: 'i' in the middle of words (e.g., 'acti ons' -> 'actions')
        if 'i ' in word or ' i' in word:
            # Try removing the space around 'i' and check if it forms a valid word
            test_word = word.replace('i ', 'i').replace(' i', 'i')
            if test_word.lower() in self.common_words or len(test_word) > len(word) - 1:
                return test_word
        
        # Handle common OCR error: missing space after punctuation
        word = re.sub(r'([.,;:!?])([A-Za-z])', r'\1 \2', word)
        
        # Handle common OCR error: extra spaces in the middle of words
        if ' ' in word:
            parts = word.split()
            
            # If combining parts makes a known word, return that
            combined = ''.join(parts)
            if (combined.lower() in self.common_words or 
                any(combined.lower() in w for w in self.common_words)):
                return combined
            
            # Try to find a reasonable split point
            for i in range(1, len(parts)):
                left = ' '.join(parts[:i])
                right = ' '.join(parts[i:])
                
                left_valid = (left.lower() in self.common_words or 
                             any(left.lower() in w for w in self.common_words))
                right_valid = (right.lower() in self.common_words or 
                              any(right.lower() in w for w in self.common_words))
                
                if left_valid and right_valid:
                    return f"{left} {right}"
                elif left_valid and len(right) > 2:
                    return f"{left} {right}"
                elif right_valid and len(left) > 2:
                    return f"{left} {right}"
        
        # Try to split long words that might be concatenations
        if (len(word) > 10 and word.isalpha() and 
            not any(c.isupper() for c in word[1:]) and
            ' ' not in word):
            
            # Try to find a split point where both parts are meaningful
            for i in range(3, min(len(word)-2, 10)):  # Limit lookahead for performance
                left, right = word[:i], word[i:]
                left_lower = left.lower()
                right_lower = right.lower()
                
                # Check if both parts are in common words or prefixes/suffixes
                left_valid = (left_lower in self.common_words or 
                            any(w.startswith(left_lower) for w in self.common_words) or
                            any(left_lower in w for w in self.common_words))
                            
                right_valid = (right_lower in self.common_words or 
                             any(w.endswith(right_lower) for w in self.common_words) or
                             any(right_lower in w for w in self.common_words))
                
                if left_valid and right_valid:
                    return f"{left} {right}"
                
                # Also check if combining with common prefixes/suffixes helps
                common_prefixes = {'un', 're', 'in', 'im', 'dis', 'en', 'pre', 'pro', 'sub', 'trans', 'non', 'mis', 'over', 'under', 'out', 'up', 'down', 'off', 'on', 'fore', 'with'}
                common_suffixes = {'ing', 'ed', 'ly', 'ment', 'tion', 'sion', 'ness', 'less', 'ful', 'able', 'ible', 'ant', 'ent', 'ism', 'ist', 'ity', 'ty', 'ive', 'ize', 'ise', 'ify', 'fy', 'en', 'er', 'or', 'al'}
                
                for prefix in common_prefixes:
                    if right_lower.startswith(prefix) and len(left) > 2:
                        return f"{left} {right}"
                
                for suffix in common_suffixes:
                    if left_lower.endswith(suffix) and len(right) > 2:
                        return f"{left} {right}"
        
        # If we've made changes, return the modified word
        if word != original_word:
            return word
        
        # If no better correction found, check if the word is in our common words
        if word.lower() in self.common_words:
            return word.lower()
            
        # If the word is all caps, try title case
        if word.isupper() and len(word) > 1:
            return word.title()
            
        # If the word is title case but not a proper noun, try lowercase
        if word.istitle() and word.lower() in self.common_words:
            return word.lower()
            
        # If no better correction found, return the original word
        return original_word
    
    def build_correction_map(self) -> Dict[str, str]:
        """Build a map of common errors to their corrections."""
        import PyPDF2
        from collections import Counter
        
        print("Building word frequency map from PDF...")
        word_freq = Counter()
        
        # First pass: Build word frequency map
        with open(self.pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in tqdm(pdf_reader.pages, desc="Processing PDF pages"):
                text = page.extract_text()
                if not text:
                    continue
                    
                # Basic text cleaning
                words = re.findall(r'\b[\w\'-]+\b', text.lower())
                word_freq.update(words)
        
        # Second pass: Identify likely errors and generate corrections
        print("Identifying potential errors and generating corrections...")
        correction_map = {}
        
        for word, count in tqdm(word_freq.most_common()):
            if self._is_likely_error(word):
                correction = self._generate_correction(word)
                if correction != word:
                    correction_map[word] = correction
        
        # Add common known errors
        common_errors = {
            'th is': 'this',
            'changeth is': 'change this',
            'perfecti on': 'perfection',
            'acti ons': 'actions',
            'reacti ons': 'reactions',
            'preparati on': 'preparation',
            'servi ng': 'serving',
            'offeri ng': 'offering',
            'theBhagavad': 'the Bhagavad',
            'donot': 'do not',
            'tounderstand': 'to understand',
            'theBhagavad': 'the Bhagavad',
            'theGita': 'the Gita',
            'theLord': 'the Lord',
            'theSupreme': 'the Supreme',
            'theSupremePersonality': 'the Supreme Personality',
            'theSupremeLord': 'the Supreme Lord',
            'theSupremePersonalityofGodhead': 'the Supreme Personality of Godhead',
            'theSupremePersonalityofGodhead,': 'the Supreme Personality of Godhead,',
            'theSupremePersonalityofGodhead.': 'the Supreme Personality of Godhead.'
        }
        
        correction_map.update(common_errors)
        self.correction_map = correction_map
        
        # Save the correction map for future use
        with open('correction_map.json', 'w') as f:
            json.dump(correction_map, f, indent=2)
            
        return correction_map
    
    def load_correction_map(self, map_path: str = 'correction_map.json') -> Dict[str, str]:
        """Load a pre-built correction map from file."""
        if os.path.exists(map_path):
            with open(map_path, 'r') as f:
                self.correction_map = json.load(f)
        return self.correction_map
    
    def correct_text(self, text: str) -> str:
        """Correct OCR and formatting errors in the given text."""
        if not text or not isinstance(text, str):
            return text
            
        # First check for exact matches in the correction map for the entire text
        text_stripped = text.strip()
        if text_stripped in self.correction_map:
            return self.correction_map[text_stripped]
            
        # Preserve the original text for comparison
        original_text = text
        
        # Check if the text contains newlines
        if '\n' in text:
            # Process each line separately to handle newlines correctly
            lines = text.splitlines(keepends=True)
            corrected_lines = []
            
            for i, line in enumerate(lines):
                # Skip empty lines but preserve them in the output
                if not line.strip():
                    corrected_lines.append('\n' if not line.endswith('\n') and i < len(lines) - 1 else line)
                    continue
                    
                # Process the line (without the trailing newline if present)
                line_content = line.rstrip('\n')
                if line_content:  # Only process non-empty lines
                    processed_line = self._process_single_line(line_content)
                    # Add back the newline if the original line had one
                    if line.endswith('\n'):
                        processed_line += '\n'
                    corrected_lines.append(processed_line)
                else:
                    corrected_lines.append(line)
            
            # Reconstruct the full text with all corrections and preserved newlines
            result = ''.join(corrected_lines)
        else:
            # No newlines, just process the entire text
            result = self._process_single_line(text)
        
        # If we've made the text worse (e.g., by changing 'line' to 'lme'), revert
        if len(original_text) > 10 and len(result) < len(original_text) * 0.8:
            return original_text
            
        return result
        
    def _process_single_line(self, line: str) -> str:
        """Process a single line of text for corrections."""
        # Split into words while preserving whitespace
        words = re.split(r'(\s+)', line)
        corrected_words = []
        
        for word in words:
            # Skip empty strings and pure whitespace
            if not word.strip():
                corrected_words.append(word)
                continue
                
            # Check if the word is in our correction map
            if word in self.correction_map:
                corrected_words.append(self.correction_map[word])
                continue
                
            # Check if the word needs correction
            if self._is_likely_error(word):
                corrected = self._generate_correction(word)
                corrected_words.append(corrected)
            else:
                corrected_words.append(word)
        
        # Reconstruct the line with corrections
        result = ''.join(corrected_words)
        
        # Apply multi-word corrections that are specific to this line
        for error, correction in sorted(self.correction_map.items(), key=lambda x: -len(x[0])):
            if ' ' in error and error in result:
                result = result.replace(error, correction)
        
        # Clean up any double spaces that might have been introduced
        result = re.sub(r'\s+', ' ', result).strip()
        
        # Fix common punctuation issues
        result = re.sub(r'\s+([.,!?;:])', r'\1', result)  # Remove space before punctuation
        result = re.sub(r'([(])\s+', r'\1', result)  # Remove space after (
        result = re.sub(r'\s+([)])', r'\1', result)  # Remove space before )
        
        return result
