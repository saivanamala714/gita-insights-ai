import unittest
import os
import re
from text_utils import TextProcessor

class TestTextProcessor(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a sample PDF path (the actual file doesn't need to exist for most tests)
        self.sample_pdf = os.path.join(os.path.dirname(__file__), 'sample.pdf')
        self.processor = TextProcessor(self.sample_pdf)
        
        # Add some test data to the processor
        self.processor.common_words.update({
            'the', 'and', 'bhagavad', 'gita', 'krishna', 'arjuna',
            'yoga', 'karma', 'dharma', 'bhakti', 'soul', 'lord', 'supreme'
        })
        
        # Add some test corrections
        self.processor.correction_map = {
            'th is': 'this',
            'changeth is': 'change this',
            'perfecti on': 'perfection',
            'acti ons': 'actions',
            'theBhagavad': 'the Bhagavad',
            'theGita': 'the Gita',
            'theLord': 'the Lord'
        }
    
    def test_is_likely_error(self):
        """Test the _is_likely_error method."""
        # Test cases for likely errors
        self.assertTrue(self.processor._is_likely_error('th is'))
        self.assertTrue(self.processor._is_likely_error('theBhagavad'))
        self.assertTrue(self.processor._is_likely_error('acti ons'))
        self.assertTrue(self.processor._is_likely_error('verylongwordwithoutspaces'))
        
        # Test cases for non-errors - these should be in the common words or sanskrit terms
        self.assertFalse(self.processor._is_likely_error('bhagavad'))
        self.assertFalse(self.processor._is_likely_error('Krishna'))
        self.assertFalse(self.processor._is_likely_error('yoga'))
        self.assertFalse(self.processor._is_likely_error('a'))
        self.assertFalse(self.processor._is_likely_error('I'))
        self.assertFalse(self.processor._is_likely_error(''))
    
    def test_generate_correction(self):
        """Test the _generate_correction method."""
        # Test simple corrections - these should be in the common_concatenations
        self.assertEqual(self.processor._generate_correction('th is'), 'this')
        self.assertEqual(self.processor._generate_correction('acti ons'), 'actions')
        
        # Test camelCase splitting - these should be handled by the regex
        self.assertEqual(self.processor._generate_correction('theBhagavad'), 'the Bhagavad')
        self.assertEqual(self.processor._generate_correction('theGita'), 'the Gita')
        
        # Test common concatenations - these should be in the common_concatenations
        self.assertEqual(self.processor._generate_correction('theBhagavadGita'), 'the Bhagavad Gita')
        
        # Test words that shouldn't be changed - these should be in common words or sanskrit terms
        self.assertEqual(self.processor._generate_correction('bhagavad'), 'bhagavad')
        # Note: Our implementation converts to lowercase for common words
        self.assertEqual(self.processor._generate_correction('Krishna').lower(), 'krishna')
    
    def test_correct_text(self):
        """Test the correct_text method."""
        # Add test cases to the correction map first
        self.processor.correction_map.update({
            'th is': 'this',
            'acti ons': 'actions',
            'theBhagavad': 'the Bhagavad'
        })
        
        # Test simple correction
        self.assertEqual(
            self.processor.correct_text('th is is a test'),
            'this is a test'
        )
        
        # Test multiple corrections in a sentence
        self.assertEqual(
            self.processor.correct_text('th is is theBhagavad gita'),
            'this is the Bhagavad gita'
        )
        
        # Test with punctuation
        self.assertEqual(
            self.processor.correct_text('acti ons speak louder than words.'),
            'actions speak louder than words.'
        )
        
        # Test with newlines
        self.assertEqual(
            self.processor.correct_text('line one\nline two with acti ons'),
            'line one\nline two with actions'
        )
    
    def test_build_correction_map(self):
        """Test building a correction map from a sample text."""
        # This test would normally require a real PDF, so we'll test the structure
        # by mocking the PDF reading part in a real test environment
        pass
    
    def test_load_correction_map(self):
        """Test loading a correction map from a file."""
        import tempfile
        import json
        
        # Create a temporary file with test corrections
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
            json.dump({
                'th is': 'this',
                'theBhagavad': 'the Bhagavad'
            }, f)
            temp_path = f.name
        
        try:
            # Load the corrections
            self.processor.load_correction_map(temp_path)
            
            # Verify the corrections were loaded
            self.assertEqual(self.processor.correction_map['th is'], 'this')
            self.assertEqual(self.processor.correction_map['theBhagavad'], 'the Bhagavad')
            
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

if __name__ == '__main__':
    unittest.main()
