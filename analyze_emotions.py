"""
Bhagavad Gita Emotion Analysis

This script analyzes the Bhagavad Gita text to extract teachings related to different emotions.
It processes the PDF and populates the emotion mappings with relevant verses and teachings.
"""
import os
import re
from typing import List, Dict, Any
from PyPDF2 import PdfReader
from emotion_mappings import add_emotion_mapping, EMOTIONS, EMOTION_MAPPINGS

class GitaEmotionAnalyzer:
    def __init__(self, pdf_path: str):
        """Initialize the analyzer with the path to the Bhagavad Gita PDF."""
        self.pdf_path = pdf_path
        self.text = ""
        self.chapters = {}
        
    def load_and_process_pdf(self) -> None:
        """Load and process the PDF file."""
        print(f"Loading PDF from {self.pdf_path}...")
        reader = PdfReader(self.pdf_path)
        self.text = ""
        
        # Extract text from all pages
        for page in reader.pages:
            self.text += page.extract_text() + "\n"
        
        # Split into chapters
        self._split_into_chapters()
        
    def _split_into_chapters(self) -> None:
        """Split the text into chapters based on chapter markers."""
        # This pattern looks for chapter numbers and titles
        chapter_pattern = r'Chapter\s+(\d+)[\s\n]+([^\n]+)'
        
        # Find all chapter starts
        chapters = list(re.finditer(chapter_pattern, self.text, re.IGNORECASE))
        
        # Extract chapter content
        for i in range(len(chapters)):
            chapter_num = chapters[i].group(1)
            chapter_title = chapters[i].group(2).strip()
            start_pos = chapters[i].end()
            
            # End position is either the start of the next chapter or the end of text
            end_pos = chapters[i+1].start() if i+1 < len(chapters) else len(self.text)
            
            chapter_text = self.text[start_pos:end_pos].strip()
            self.chapters[chapter_num] = {
                'title': chapter_title,
                'text': chapter_text,
                'verses': self._split_into_verses(chapter_text)
            }
    
    def _split_into_verses(self, chapter_text: str) -> Dict[str, str]:
        """Split chapter text into individual verses."""
        verses = {}
        # This pattern looks for verse numbers like "Bg 1.1" or "1.1"
        verse_pattern = r'(?:Bg\s*)?(\d+\.\d+)[\s\n]+(.+?)(?=(?:\n\s*Bg\s*\d+\.\d+|$))'
        
        for match in re.finditer(verse_pattern, chapter_text, re.DOTALL):
            verse_num = match.group(1)
            verse_text = match.group(2).strip()
            verses[verse_num] = verse_text
            
        return verses
    
    def analyze_emotions(self) -> None:
        """Analyze the text for teachings related to different emotions."""
        print("Analyzing emotions in the Bhagavad Gita...")
        
        # Define emotion-related keywords and their associated emotions
        emotion_keywords = {
            'fear': ['fear', 'afraid', 'dread', 'terror', 'apprehension'],
            'anger': ['anger', 'rage', 'wrath', 'fury', 'irritation'],
            'joy': ['joy', 'happiness', 'bliss', 'delight', 'ecstasy'],
            'sadness': ['sadness', 'sorrow', 'grief', 'misery', 'despair'],
            'love': ['love', 'devotion', 'affection', 'compassion', 'kindness'],
            'hate': ['hate', 'hatred', 'aversion', 'loathing', 'disgust'],
            'peace': ['peace', 'tranquility', 'serenity', 'calm', 'equanimity'],
            'anxiety': ['anxiety', 'worry', 'unease', 'nervousness', 'apprehension'],
            'envy': ['envy', 'jealousy', 'covetousness', 'resentment'],
            'gratitude': ['gratitude', 'thankfulness', 'appreciation'],
            'shame': ['shame', 'guilt', 'remorse', 'regret', 'humiliation'],
            'pride': ['pride', 'arrogance', 'conceit', 'egotism', 'vanity'],
            'hope': ['hope', 'optimism', 'expectation', 'aspiration'],
            'desire': ['desire', 'craving', 'longing', 'lust', 'attachment'],
            'contentment': ['contentment', 'satisfaction', 'fulfillment', 'ease']
        }
        
        # Search for each emotion's keywords in the text
        for emotion, keywords in emotion_keywords.items():
            print(f"Analyzing teachings related to: {emotion}")
            self._analyze_emotion(emotion, keywords)
    
    def _analyze_emotion(self, emotion: str, keywords: List[str]) -> None:
        """Analyze the text for a specific emotion."""
        relevant_verses = []
        
        # Search through all chapters and verses
        for chapter_num, chapter_data in self.chapters.items():
            for verse_num, verse_text in chapter_data['verses'].items():
                # Check if any keyword is in the verse (case-insensitive)
                if any(re.search(r'\b' + re.escape(keyword) + r'\b', 
                               verse_text, re.IGNORECASE) 
                      for keyword in keywords):
                    relevant_verses.append({
                        'chapter': chapter_num,
                        'verse': verse_num,
                        'text': verse_text
                    })
        
        # If we found relevant verses, add them to our mappings
        if relevant_verses:
            # Extract key teachings (simplified for this example)
            teachings = self._extract_teachings(emotion, relevant_verses)
            
            # Add to our emotion mappings
            for teaching in teachings:
                add_emotion_mapping(
                    emotion=emotion,
                    teaching=teaching['teaching'],
                    advice=teaching['advice'],
                    verses=teaching['verses'],
                    example=teaching.get('example', '')
                )
    
    def _extract_teachings(self, emotion: str, verses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract structured teachings from relevant verses."""
        teachings = []
        
        # This is a simplified version - in a real implementation, you would use
        # more sophisticated NLP techniques to extract and summarize teachings
        
        # Group verses by chapter
        verses_by_chapter = {}
        for verse in verses:
            if verse['chapter'] not in verses_by_chapter:
                verses_by_chapter[verse['chapter']] = []
            verses_by_chapter[verse['chapter']].append(verse)
        
        # Create teachings for each chapter with relevant verses
        for chapter_num, chapter_verses in verses_by_chapter.items():
            # Get the first few verses as examples
            example_verses = [f"{v['chapter']}.{v['verse']}" for v in chapter_verses[:3]]
            verse_texts = [v['text'] for v in chapter_verses[:3]]
            
            # Create a teaching based on the emotion and verses
            teaching = {
                'teaching': f"The Gita's perspective on {emotion} (Chapter {chapter_num})",
                'advice': (
                    f"In Chapter {chapter_num}, the Gita addresses {emotion} through several verses. "
                    f"Key teachings include the importance of maintaining balance and understanding "
                    f"the temporary nature of emotions."
                ),
                'verses': example_verses,
                'example': '\n\n'.join(verse_texts)
            }
            
            # Add emotion-specific advice
            if emotion == 'fear':
                teaching['advice'] = (
                    "The Gita teaches that fear arises from attachment and ignorance of the eternal soul. "
                    "By cultivating knowledge and devotion, one can transcend fear and find inner peace."
                )
            elif emotion == 'anger':
                teaching['advice'] = (
                    "Anger leads to clouded judgment and spiritual downfall. The Gita advises practicing "
                    "forgiveness, tolerance, and seeing the divine in all beings to overcome anger."
                )
            # Add more emotion-specific advice as needed
            
            teachings.append(teaching)
        
        return teachings

def main():
    # Initialize the analyzer with the path to the Gita PDF
    analyzer = GitaEmotionAnalyzer("11-Bhagavad-gita_As_It_Is.pdf")
    
    # Load and process the PDF
    analyzer.load_and_process_pdf()
    
    # Analyze emotions in the text
    analyzer.analyze_emotions()
    
    # Print summary of findings
    print("\nEmotion Analysis Complete!")
    print(f"Analyzed {len(analyzer.chapters)} chapters")
    
    # Count teachings per emotion
    print("\nTeachings found per emotion:")
    for emotion in sorted(EMOTIONS):
        count = len(EMOTION_MAPPINGS[emotion])
        if count > 0:
            print(f"- {emotion.capitalize()}: {count} teachings")
    
    # Save the emotion mappings to a file for later use
    import json
    with open("gita_emotion_mappings.json", "w") as f:
        # Filter out emotions with no teachings
        filtered_mappings = {k: v for k, v in EMOTION_MAPPINGS.items() if v}
        json.dump(filtered_mappings, f, indent=2)
    
    print("\nSaved emotion mappings to gita_emotion_mappings.json")

if __name__ == "__main__":
    main()
