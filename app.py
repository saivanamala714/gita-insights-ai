import os
import re
import logging
import json
from typing import Dict, List, Any, Optional, Tuple, Set
import random
from PyPDF2 import PdfReader
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter

# Import the name correction module
from name_corrector import correct_text_names, correct_character_name
from gita_characters import get_character_info, get_character_aliases, get_character_names
from gita_faqs import get_faqs_by_category, get_faq_by_question, search_faqs, get_faq_categories
from response_processor import get_processor
from difflib import SequenceMatcher
from gita_qa_pairs import get_qa_pairs, get_qa_by_category
from text_utils import TextProcessor
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class Document:
    def __init__(self, page_content: str, metadata: Dict[str, Any]):
        self.page_content = page_content
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            "page_content": self.page_content,
            "metadata": self.metadata
        }


class QASystem:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.documents = []
        self.verse_index = {}  # To store verse references for quick lookup
        
        # Initialize text processor and build/load correction map
        self.text_processor = TextProcessor(pdf_path)
        correction_map_path = os.path.join(os.path.dirname(pdf_path), 'correction_map.json')
        if os.path.exists(correction_map_path):
            logging.info("Loading existing correction map...")
            self.text_processor.load_correction_map(correction_map_path)
        else:
            logging.info("Building new correction map from PDF...")
            self.text_processor.build_correction_map()

    def clean_text(self, text: str) -> str:
        """Clean and preprocess text from the PDF."""
        # Remove page numbers and headers/footers
        # Page numbers on their own line
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        # Page numbers at line start/end
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)

        # Remove common headers/footers
        text = re.sub(r'Bhagavad-gītā As It Is\s+\d+', '', text)
        text = re.sub(r'\n+', '\n', text)  # Multiple newlines to one

        # Clean up whitespace
        text = ' '.join(text.split())
        return text

    def load_and_process_pdf(self):
        """Load and process the PDF file and build verse index."""
        print(f"Loading PDF from {self.pdf_path}...")
        reader = PdfReader(self.pdf_path)

        # Skip the front matter which often contains the same text
        start_page = 10  # Skip first few pages which might contain preface/acknowledgments

        # More comprehensive verse pattern to match different formats
        verse_pattern = re.compile(r'(?:Bg\s*)?(\d+)\.(\d+)(?:\s|$)')

        # Extract text from each page with better cleaning
        current_chapter = None
        current_verse = None
        verse_text = []

        # First, let's understand the structure by examining the first few pages
        print("Examining PDF structure...")
        for page_num in range(start_page, min(start_page + 10, len(reader.pages))):
            text = reader.pages[page_num].extract_text()
            print(f"\n--- Page {page_num + 1} ---")
            print(text[:500] + "..." if len(text) > 500 else text)

        # Now process all pages for actual content
        print("\nProcessing all pages...")
        for page_num in range(start_page, len(reader.pages)):
            try:
                text = reader.pages[page_num].extract_text()
                if not text:
                    continue

                # Clean the text for general search
                cleaned_text = self.clean_text(text)
                if len(cleaned_text) > 100:  # Only add if there's substantial content
                    self.documents.append(Document(
                        page_content=cleaned_text,
                        metadata={
                            "page": page_num + 1,
                            "source": self.pdf_path
                        }
                    ))

                # Process lines for verse extraction
                lines = [line.strip()
                         for line in text.split('\n') if line.strip()]
                i = 0
                while i < len(lines):
                    line = lines[i]

                    # Look for verse references in the line
                    match = verse_pattern.search(line)

                    # Special handling for the specific format in this PDF
                    if 'TEXT ' in line and 'Bg' in line:
                        parts = line.split()
                        for part in parts:
                            if 'Bg' in part and '.' in part:
                                try:
                                    # Extract chapter and verse from something like "Bg2.46"
                                    ref = part.split('Bg')[-1]
                                    chapter, verse = ref.split('.')
                                    current_chapter = int(chapter)
                                    current_verse = int(verse)
                                    # The next line should contain the verse text
                                    if i + 1 < len(lines):
                                        verse_text = [lines[i+1].strip()]
                                        i += 1  # Skip the next line as we've processed it
                                    break
                                except (ValueError, IndexError):
                                    continue
                    # Standard verse reference pattern
                    elif match:
                        # If we were collecting a verse, save it before starting a new one
                        if current_chapter is not None and current_verse is not None and verse_text:
                            verse_ref = f"{current_chapter}.{current_verse}"
                            self.verse_index[verse_ref] = {
                                "text": " ".join(verse_text).strip(),
                                "page": page_num + 1,
                                "source": self.pdf_path
                            }
                            verse_text = []

                        # Start a new verse
                        current_chapter = int(match.group(1))
                        current_verse = int(match.group(2))

                        # Get the verse text (usually the next line)
                        if i + 1 < len(lines):
                            verse_text = [lines[i+1].strip()]
                            i += 1  # Skip the next line as we've processed it
                    elif current_chapter is not None and current_verse is not None:
                        # If we're in a verse, add the line to the current verse text
                        if line and not line.startswith('TEXT') and not line.startswith('Bg'):
                            verse_text.append(line)

                    i += 1

                # After processing each page, check if we have a verse to save
                if current_chapter is not None and current_verse is not None and verse_text:
                    verse_ref = f"{current_chapter}.{current_verse}"
                    self.verse_index[verse_ref] = {
                        "text": " ".join(verse_text).strip(),
                        "page": page_num + 1,
                        "source": self.pdf_path
                    }
                    verse_text = []

            except Exception as e:
                print(f"Error processing page {page_num + 1}: {str(e)}")
                import traceback
                traceback.print_exc()

        # Don't forget to add the last verse if we were in the middle of one
        if current_chapter is not None and current_verse is not None and verse_text:
            verse_ref = f"{current_chapter}.{current_verse}"
            self.verse_index[verse_ref] = {
                "text": " ".join(verse_text).strip(),
                "page": page_num + 1,
                "source": self.pdf_path
            }

        print(
            f"Processed {len(self.documents)} pages and indexed {len(self.verse_index)} verses from the PDF")

        # Print some debug info about the verses we found
        print("\nSample of indexed verses:")
        for i, (ref, data) in enumerate(self.verse_index.items()):
            if i >= 5:  # Only show first 5 verses
                break
            print(f"{ref}: {data['text'][:100]}...")

    def get_relevant_documents(self, query: str, k: int = 5) -> List[Document]:
        """Retrieve relevant document chunks for a query using improved text matching."""
        if not self.documents:
            raise ValueError(
                "No documents loaded. Call load_and_process_pdf() first.")

        # Preprocess query
        query = query.lower()
        query_terms = set(term for term in query.split()
                          if len(term) > 2)  # Ignore very short words

        def score_document(doc_text: str) -> float:
            """Score how well a document matches the query."""
            doc_text_lower = doc_text.lower()

            # Count how many query terms appear in the document
            term_matches = sum(
                1 for term in query_terms if term in doc_text_lower)

            # If we have at least 2 matching terms, consider the document
            if term_matches >= 2:
                # Bonus for matching more terms
                return term_matches / len(query_terms) if query_terms else 0
            return 0

        # Score each document
        scored_docs = []
        for doc in self.documents:
            score = score_document(doc.page_content)
            if score > 0:  # Only include documents with some match
                scored_docs.append((score, doc))

        # Sort by score (highest first) and take top k
        scored_docs.sort(reverse=True, key=lambda x: x[0])

        # If we have good matches, return them; otherwise return some random pages
        if scored_docs and scored_docs[0][0] > 0.3:  # At least 30% match
            return [doc for score, doc in scored_docs[:k]]
        else:
            # If no good matches, return some random pages from the middle of the book
            mid_point = len(self.documents) // 2
            return self.documents[mid_point:mid_point + k]

    def get_verse(self, chapter: int, verse: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific verse from the Bhagavad Gita.

        Args:
            chapter: Chapter number (1-18)
            verse: Verse number within the chapter

        Returns:
            Dictionary containing the verse text and metadata, or None if not found
        """
        verse_ref = f"{chapter}.{verse}"
        verse_data = self.verse_index.get(verse_ref)
        if verse_data:
            return verse_data
        else:
            print(
                f"Verse {verse_ref} not found in index. Available verses: {list(self.verse_index.keys())[:10]}...")
            return None

    def get_chapter_summaries(self) -> str:
        """Return a summary of each chapter in the Bhagavad Gita."""
        summaries = [
            "Chapter 1: Arjuna's Dilemma - Observing the Armies on the Battlefield of Kurukshetra. Arjuna is overcome with grief and refuses to fight.",
            "Chapter 2: The Eternal Reality of the Soul's Immortality - Krishna begins teaching Arjuna about the eternal nature of the soul and the importance of duty.",
            "Chapter 3: Karma-yoga - The Eternal Duties of Human Beings - Krishna explains the concept of selfless action and performing one's duty without attachment to results.",
            "Chapter 4: Approaching the Ultimate Truth - Krishna reveals His divine nature and explains the purpose of His periodic descents to Earth.",
            "Chapter 5: Action and Renunciation - The path of knowledge and the path of selfless action both lead to the same goal.",
            "Chapter 6: The Science of Self-Realization - The practice of meditation and the characteristics of a perfect yogi are described.",
            "Chapter 7: Knowledge of the Ultimate Truth - Krishna explains His divine and material energies and how to know Him completely.",
            "Chapter 8: Attaining the Supreme - The nature of the Supreme, the process of leaving the body, and the destination of different types of yogis.",
            "Chapter 9: The Most Confidential Knowledge - The most secret wisdom of the Gita is revealed: pure devotional service to Krishna.",
            "Chapter 10: The Infinite Glories of the Supreme - Krishna describes His divine manifestations and opulences.",
            "Chapter 11: The Universal Form - Arjuna requests to see Krishna's universal form and is granted divine vision to behold it.",
            "Chapter 12: The Path of Devotion - The process of devotional service and the characteristics of devotees are described.",
            "Chapter 13: The Individual and the Ultimate - The difference between the body, the soul, and the Supersoul is explained.",
            "Chapter 14: The Three Modes of Material Nature - The three gunas (modes of material nature) and their influence on living entities.",
            "Chapter 15: The Yoga of the Supreme Person - The nature of the material world and the path to liberation are described.",
            "Chapter 16: The Divine and Demoniac Natures - The divine and demoniac qualities of living beings are contrasted.",
            "Chapter 17: The Three Kinds of Faith - The three types of faith and their relationship to the three modes of material nature.",
            "Chapter 18: Final Revelations of the Ultimate Truth - The conclusion of the Gita, summarizing the paths of knowledge, action, and devotion."
        ]
        return "\n\n".join(summaries)

    def get_main_characters(self) -> str:
        """Return a detailed list of main characters in the Bhagavad Gita with comprehensive analysis."""
        characters = [
            ("1. Lord Krishna", {
                "title": "The Supreme Personality of Godhead",
                "role": "Divine charioteer and spiritual preceptor to Arjuna",
                "personality": "Omniscient, compassionate, patient, and the ultimate source of wisdom. Krishna exhibits divine playfulness (lila) while maintaining perfect detachment. He is the embodiment of dharma (righteousness) and demonstrates perfect balance between justice and mercy. His teachings in the Gita reveal his role as the ultimate spiritual master and the supreme controller.",
                "key_teachings": ["The nature of the eternal soul", "The importance of selfless action (karma yoga)", "The path of devotion (bhakti)", "The universal form (Vishvarupa)"],
                "emotions": ["Compassionate love (karuna)", "Divine joy (ananda)", "Protectiveness", "Righteous anger (when needed)", "Unconditional love (prema)"],
                "marital_status": "Eternal consort of Goddess Rukmini and other queens; represents the divine lover of all souls",
                "powers": [
                    "Omniscience (all-knowing)",
                    "Omnipotence (all-powerful)",
                    "Omnipresence (present everywhere)",
                    "Ability to assume any form (Vishvarupa)",
                    "Control over time and space",
                    "Power to protect devotees in any situation"
                ],
                "spiritual_nature": "The Supreme Personality of Godhead, source of all spiritual and material worlds. Embodiment of sat-chit-ananda (eternity, knowledge, and bliss). The ultimate object of devotion and the goal of all spiritual practice.",
                "secrets": [
                    "His true form as the Supreme Personality of Godhead is revealed only to pure devotees",
                    "He descends to Earth in various avatars to protect dharma",
                    "His pastimes appear human-like but are completely spiritual",
                    "He can be conquered only by pure love and devotion"
                ],
                "relationships": {
                    "Arjuna": "Divine friendship and guru-disciple relationship. Krishna chose Arjuna to receive the Bhagavad-gita's wisdom and served as his charioteer, symbolizing divine guidance.",
                    "Yudhishthira": "Respected Yudhishthira's commitment to dharma but sometimes tested his rigid adherence to truth.",
                    "Bhima": "Appreciated Bhima's strength and devotion, often protected him from his own temper.",
                    "Nakula & Sahadeva": "Respected their loyalty and skills, though they had less direct interaction.",
                    "Duryodhana": "Attempted to counsel Duryodhana towards peace but respected his free will when he refused.",
                    "Karna": "Knew Karna's true identity and tried to guide him, but respected his choices.",
                    "Bhishma": "Respected Bhishma's wisdom and vowed not to fight him directly in the war.",
                    "Dronacharya": "Acknowledged his teaching skills but opposed his partiality.",
                    "Dhritarashtra": "Showed compassion but was firm about the consequences of his poor leadership.",
                    "Sanjaya": "Granted divine vision to Sanjaya to narrate the Gita to Dhritarashtra."
                }
            }),
            ("2. Arjuna", {
                "title": "The Mighty Warrior Prince",
                "role": "Pandava prince and disciple of Krishna",
                "personality": "Courageous yet compassionate, Arjuna represents the human soul in search of truth. He is highly skilled in archery and warfare but experiences deep moral conflict when faced with fighting his own relatives. His willingness to surrender to Krishna's wisdom shows his humility and capacity for spiritual growth.",
                "emotions": ["Compassion for family", "Moral dilemma (vishada)", "Devotion to Krishna", "Loyalty to dharma", "Warrior's pride", "Brotherly love"],
                "marital_status": "Husband of Draupadi (shared with his four brothers) and Subhadra; also married to Ulupi, Chitrangada, and had other wives",
                "powers": [
                    "Master archer (the greatest of his time)",
                    "Skilled in divine weapons (astras)",
                    "Ability to concentrate intensely",
                    "Tactical brilliance in warfare",
                    "Blessed with celestial weapons by various gods"
                ],
                "spiritual_nature": "Embodies the ideal devotee (bhakta) who surrenders to the divine will. His spiritual journey in the Gita represents the human soul's path from confusion to enlightenment through divine knowledge and devotion.",
                "secrets": [
                    "His chariot was protected by Hanuman and other divine beings during the war",
                    "Was cursed by Urvashi to become a eunuch for a year",
                    "Spent his year of exile in the court of King Virata disguised as Brihannala, a eunuch dance teacher",
                    "Was the reincarnation of the sage Nara, the eternal companion of Narayana (Krishna)"
                ],
                "key_moments": ["Expresses doubts about the war in Chapter 1", "Receives the Bhagavad Gita's teachings", "Witnesses Krishna's universal form"],
                "relationships": {
                    "Krishna": "Saw Krishna as both friend and spiritual master, sharing a bond of deep trust and devotion.",
                    "Yudhishthira": "Respected his elder brother's authority and wisdom, though sometimes frustrated by his rigid adherence to dharma.",
                    "Bhima": "Close bond as brothers-in-arms, with Bhima's strength complementing Arjuna's skill.",
                    "Nakula & Sahadeva": "Protective elder brother relationship, appreciating their loyalty and skills.",
                    "Duryodhana": "Rivalry turned to enmity, though he maintained respect for Duryodhana's royal status.",
                    "Karna": "Respected Karna's skills but was unaware of their fraternal relationship until after Karna's death.",
                    "Bhishma": "Deep respect for his grandfather, despite being on opposite sides of the war.",
                    "Dronacharya": "Favorite student of Dronacharya, who taught him advanced archery skills.",
                    "Draupadi": "Shared a deep bond of mutual respect within the bounds of their polyandrous marriage.",
                    "Kunti": "Loving son who always sought to honor his mother's wishes."
                }
            }),
            ("3. Sanjaya", {
                "title": "The Divine Visionary",
                "role": "Narrator and advisor to King Dhritarashtra",
                "personality": "Wise, impartial, and blessed with divine vision by the sage Vyasa. Sanjaya serves as the perfect narrator, able to see events at Kurukshetra from a distance and recount them accurately to the blind king. His commentary provides important context and insights.",
                "key_contributions": ["Narrates the events of the Mahabharata", "Provides moral commentary on the unfolding events"],
                "relationships": {
                    "Dhritarashtra": "Loyal minister who provided unbiased counsel, though often ignored.",
                    "Krishna": "Received divine vision from Vyasa to witness and narrate Krishna's teachings to Arjuna.",
                    "Vidura": "Allied with Vidura in advising Dhritarashtra towards peace.",
                    "Duryodhana": "Attempted to counsel Duryodhana against his destructive path.",
                    "Yudhishthira": "Respected his righteousness and often cited his virtues to Dhritarashtra."
                }
            }),
            ("4. Dhritarashtra", {
                "title": "The Blind King",
                "role": "Father of the Kauravas and ruler of Hastinapura",
                "personality": "Physically blind and metaphorically blind to dharma, Dhritarashtra is weak-willed and overly attached to his sons. His inability to control Duryodhana's wickedness and his partiality lead to the great war. He represents the dangers of attachment and poor leadership.",
                "key_aspects": ["Blindness as a metaphor for spiritual ignorance", "Attachment to his sons overrides his sense of justice"],
                "relationships": {
                    "Duryodhana": "Blindly indulged his eldest son's wickedness, despite knowing it was wrong.",
                    "Pandavas": "Resentful of their claim to the throne, yet recognized their virtues.",
                    "Vidura": "Respected his wisdom but often ignored his counsel.",
                    "Bhishma": "Relied on his guidance but failed to follow his advice regarding the Pandavas.",
                    "Gandhari": "Respected her wisdom but often ignored her pleas to restrain Duryodhana.",
                    "Krishna": "Feared and respected Krishna's power but failed to heed his peace missions."
                }
            }),
            ("5. Duryodhana", {
                "title": "The Jealous Prince",
                "role": "Eldest Kaurava brother, Crown Prince of Hastinapura, and main antagonist",
                "personality": "Ambitious, envious, and stubborn, Duryodhana's jealousy of the Pandavas drives the epic's central conflict. His refusal to accept the Pandavas' rights and his deep-seated sense of entitlement lead to the great war. Despite his many flaws, he is a skilled warrior, charismatic leader, and fiercely loyal to those who support him. His character represents the destructive power of unchecked ambition and envy.",
                "emotions": ["Intense jealousy of the Pandavas", "Deep-seated insecurity about his worth", "Fierce loyalty to his supporters", "Unyielding pride (ahankara)", "Consuming hatred for his enemies"],
                "marital_status": "Husband of Bhanumati and father of Lakshmana Kumara and Lakshmanaa",
                "powers": [
                    "Exceptional mace fighter, second only to Bhima",
                    "Skilled in all forms of combat and statecraft",
                    "Charismatic leader who commanded great loyalty",
                    "Master strategist in political maneuvering",
                    "Blessed with a body as strong as thunderbolt by his mother's boon"
                ],
                "spiritual_nature": "Represents the unenlightened ego (ahankara) and the destructive power of adharma. His life illustrates how negative qualities like envy, pride, and attachment to power can lead to one's downfall. Despite having access to wise counsel, his unwillingness to overcome his base instincts ultimately destroys him and his kingdom.",
                "secrets": [
                    "Was actually an incarnation of the demon Kali (not to be confused with the goddess Kali)",
                    "His body was said to be as strong as a thunderbolt due to his mother's boon",
                    "Secretly admired the Pandavas' virtues but could never admit it",
                    "Knew about Karna's true identity as a Pandava but kept it hidden"
                ],
                "key_aspects": [
                    "Skilled mace fighter who nearly defeated Bhima in their final duel",
                    "Jealous of the Pandavas' popularity and virtues",
                    "Close friend and patron of Karna, treating him as an equal",
                    "Master manipulator who exploited his father's blind love",
                    "His name ironically means 'hard to fight against' or 'invincible'"
                ],
                "relationships": {
                    "Bhishma": "Respected but often clashed with his grandsire's advice, seeing him as partial to the Pandavas.",
                    "Dushasana": "Loyal younger brother who followed his lead in all matters, including the disrobing of Draupadi.",
                    "Karna": "Close friend and ally, treating him as an equal despite his low birth, which earned him Karna's undying loyalty.",
                    "Shakuni": "Maternal uncle who fueled his hatred for the Pandavas and manipulated him for his own revenge.",
                    "Krishna": "Saw Krishna as biased towards the Pandavas and refused his peace offers, leading to his downfall.",
                    "Yudhishthira": "Cousin and rival, whose virtues he resented and whose kingdom he coveted.",
                    "Dronacharya & Kripacharya": "Respected his teachers but often ignored their counsel when it didn't suit his purposes.",
                    "Dhritarashtra": "Manipulated his father's affection and blindness (both literal and metaphorical) to further his ambitions.",
                    "Gandhari": "Mother whose blindfold he removed to see the battlefield one last time before dying. Her curse on Krishna came true.",
                    "Duhshala": "His only sister, who he used as a pawn in his political games.",
                    "The other Kauravas": "His 99 brothers who followed him loyally, many to their deaths in the war."
                }
            }),
            ("6. Bhishma", {
                "title": "The Grandsire",
                "role": "Grandfather to both Pandavas and Kauravas, Commander-in-Chief of the Kaurava army",
                "personality": "Wise, honorable, and bound by his vows, Bhishma is caught between duty and morality. His vow of celibacy and loyalty to the throne of Hastinapura force him to fight for the Kauravas despite his love for the Pandavas. He represents the complexity of dharma and the consequences of rigid vows.",
                "emotions": ["Deep sense of duty (dharma)", "Unwavering loyalty to his word", "Inner conflict between love and duty", "Regret for unintended consequences of his actions", "Compassion for both Pandavas and Kauravas"],
                "marital_status": "Took a vow of lifelong celibacy (Brahmacharya) to allow his father to marry Satyavati, earning the name 'Bhishma' (the terrible oath-taker)",
                "powers": [
                    "Blessed with the boon of 'Iccha Mrityu' (ability to choose the time of his death)",
                    "Master of all weapons and military strategies",
                    "Possessed knowledge of the Praswapa weapon (capable of putting enemies to sleep)",
                    "Skilled in diplomacy and statecraft",
                    "Had divine weapons from various gods including Pashupatastra from Lord Shiva"
                ],
                "spiritual_nature": "Embodies the concept of nishkama karma (selfless action) and the complexities of dharma. Despite his noble intentions, his rigid adherence to his vows demonstrates how even righteousness can become a form of attachment. His life teaches the importance of wisdom in applying dharma according to time, place, and circumstance.",
                "secrets": [
                    "Knew about Krishna's divine nature but kept it to himself",
                    "Was aware of the Pandavas' divine parentage",
                    "Could have ended the war quickly but chose not to, bound by his vow to protect Hastinapura's throne",
                    "Had the power to stop the game of dice but chose not to intervene"
                ],
                "key_aspects": [
                    "Took the terrible Bhishma Pratigya (vow) of lifelong celibacy",
                    "One of the few warriors who could use the Praswapa weapon",
                    "Remained neutral in the Kurukshetra war despite commanding the Kaurava army",
                    "Lay on a bed of arrows for 58 days before leaving his mortal body",
                    "Received the boon of voluntary death from his father"
                ],
                "relationships": {
                    "Shantanu & Ganga": "Son of King Shantanu and the goddess Ganga, who left him to return to her divine abode after his birth.",
                    "Pandavas & Kauravas": "Grandfather to both, though bound to serve the throne of Hastinapura. He loved the Pandavas but fought for the Kauravas out of duty.",
                    "Krishna": "Mutual respect, though they were on opposing sides of the war. Bhishma recognized Krishna's divinity.",
                    "Dronacharya": "Respected colleague and fellow warrior, though they had different approaches to dharma.",
                    "Vidura": "Half-brother whose counsel he often sought but sometimes ignored when it conflicted with his vows.",
                    "Satyavati": "Stepmother, whose marriage to his father led to his vow of celibacy. He respected her as queen mother.",
                    "Amba/Shikhandi": "His refusal to marry Amba led to her rebirth as Shikhandi, who would be instrumental in his death. This was his only vulnerability.",
                    "Parashurama": "Former teacher with whom he had a legendary battle that ended in a stalemate after 23 days.",
                    "Duryodhana": "Served as his commander out of duty, though he disapproved of his actions.",
                    "Yudhishthira": "Had great affection for him and gave him the Vishnu Sahasranama during his final days.",
                    "Karna": "Initially rejected him for being a suta-putra (charioteer's son), but later recognized his valor.",
                    "Vyasa": "Respected the sage who was his half-brother and chronicler of the Mahabharata."
                }
            }),
            ("7. Dronacharya", {
                "title": "The Royal Preceptor",
                "role": "Teacher of the Pandavas and Kauravas",
                "personality": "A brilliant teacher but flawed in his partiality, Dronacharya's loyalty to the throne overrides his sense of justice. His favoritism towards Arjuna and mistreatment of Ekalavya reveal his human weaknesses. He represents the dangers of attachment and the conflict between personal loyalties and dharma.",
                "key_aspects": ["Master of military arts", "Shows favoritism toward Arjuna", "Bound by his word to the Kaurava court"],
                "relationships": {
                    "Arjuna": "Favorite student, in whom he saw his own skills perfected.",
                    "Ekalavya": "Unjustly demanded the tribal prince's thumb as guru-dakshina.",
                    "Drupada": "Former friend turned enemy after being humiliated by him.",
                    "Ashwatthama": "Loving but overbearing father who placed high expectations on his son.",
                    "Yudhishthira": "Respected his truthfulness but was bound to fight against him.",
                    "Duryodhana": "Served him out of duty and gratitude for being given a position at court.",
                    "Bhishma": "Respected his leadership in the Kaurava army."
                }
            }),
            ("8. Karna", {
                "title": "The Tragic Hero",
                "role": "Warrior, King of Anga, and secret Pandava brother",
                "personality": "Noble, generous, but cursed by fate, Karna is one of the most complex characters in the Mahabharata. Despite his many virtues—generosity, loyalty, and exceptional skill—his life is marked by misfortune and difficult choices. His loyalty to Duryodhana and personal grudges against the Pandavas, coupled with the curses he bears, lead to his tragic downfall. Karna's life raises profound questions about destiny, loyalty, and the consequences of one's choices.",
                "emotions": ["Deep-seated insecurity about his birth", "Unyielding loyalty to those who accept him", "Anger at perceived injustices", "Generosity that knows no bounds", "Loneliness and longing for acceptance"],
                "marital_status": "Married to Vrushali and later Supriya; father of at least nine sons including Vrishasena and Vrishaketu",
                "powers": [
                    "Peerless archer, equal to Arjuna in skill",
                    "Possessed the divine armor (Kavacha) and earrings (Kundala) at birth",
                    "Master of the Brahmastra and other celestial weapons",
                    "Exceptional charioteer and warrior",
                    "Blessed with immense physical strength and endurance"
                ],
                "spiritual_nature": "Karna represents the tragic hero whose virtues are overshadowed by his flaws and circumstances. His life illustrates the concept of 'daiva' (divine will) versus 'purushakara' (human effort). Despite his noble qualities, his inability to overcome his anger, pride, and loyalty to the wrong people leads to his downfall. His story serves as a cautionary tale about the importance of right association and the consequences of one's choices.",
                "secrets": [
                    "Eldest son of Kunti and Surya (the sun god), making him the eldest Pandava",
                    "Was abandoned at birth and raised by a charioteer, which caused him lifelong anguish",
                    "His divine armor made him invincible until he gave it away to Indra",
                    "Knew about his true identity before the war but chose to remain with Duryodhana"
                ],
                "key_traits": [
                    "Known as 'Daanaveera' for his extraordinary generosity",
                    "Cursed multiple times, including by his guru Parashurama",
                    "Remained loyal to Duryodhana despite knowing his faults",
                    "Struggled with his identity and place in society",
                    "Possessed deep knowledge of dharma but often failed to follow it"
                ],
                "relationships": {
                    "Kunti": "Biological mother who abandoned him at birth, leading to his identity crisis. Met him before the war and revealed his true parentage, but he chose to remain loyal to Duryodhana.",
                    "Duryodhana": "Loyal friend who gave him status and respect when others rejected him. Karna's unwavering loyalty to Duryodhana, despite his flaws, is both his greatest virtue and tragic flaw.",
                    "Krishna": "Knew Karna's true identity and tried to guide him to the Pandava side, but respected his choice when he refused.",
                    "Arjuna": "Rival and unknowing brother, the object of his envy and desire for recognition. Their rivalry culminated in the final battle where Arjuna killed Karna.",
                    "Bhishma": "Resentful of Bhishma's initial rejection of him due to his low birth. Their relationship was strained throughout the epic.",
                    "Parashurama": "Disciple who was cursed when his true identity was discovered, leading to the loss of his knowledge of the Brahmastra at a crucial moment.",
                    "Shalya": "Had a complex relationship with his charioteer during the war, who constantly demoralized him by praising the Pandavas.",
                    "Indra": "Tricked into giving away his divine armor and earrings, leaving him vulnerable in battle.",
                    "Duryodhana's brothers": "Had a respectful relationship, though some resented his influence over Duryodhana.",
                    "The Pandavas": "Unknowing brothers who he fought against. His death at their hands was particularly tragic given their blood relationship."
                }
            }),
            ("9. Yudhishthira", {
                "title": "The Dharma King",
                "role": "Eldest Pandava brother and rightful heir to the Kuru throne",
                "personality": "Known for his unwavering commitment to truth and dharma, Yudhishthira is wise but sometimes overly rigid. His commitment to righteousness sometimes makes him appear weak or indecisive. He represents the ideal ruler but also shows the challenges of maintaining dharma in complex situations.",
                "emotions": ["Deep sense of justice", "Compassion for all beings", "Anguish over war and suffering", "Unshakable patience", "Moral responsibility"],
                "marital_status": "Husband of Draupadi (shared with his four brothers) and Devika",
                "powers": [
                    "Exceptional skill with the spear",
                    "Moral authority that commands respect",
                    "Unmatched knowledge of dharma",
                    "Ability to remain calm in crisis",
                    "Skilled in administration and statecraft"
                ],
                "spiritual_nature": "Embodies dharma (righteousness) in human form. His life represents the challenges of adhering to spiritual principles while fulfilling worldly responsibilities. His journey shows that even the most righteous must face tests of their convictions.",
                "secrets": [
                    "Was the son of Dharma (the god of justice) and Kunti",
                    "His commitment to truth was tested when he had to lie about Ashwatthama's death",
                    "Was the only one of his brothers to reach heaven in his mortal body",
                    "His gambling vice led to the Pandavas' exile"
                ],
                "key_qualities": [
                    "Unwavering commitment to truth (satyavadi)",
                    "Skilled in spear fighting and statecraft",
                    "Known as Dharmaraja (King of Righteousness)",
                    "Exceptional patience and forgiveness",
                    "Deep knowledge of scriptures and dharma"
                ],
                "relationships": {
                    "Krishna": "Respected Krishna's wisdom and sought his counsel in difficult decisions.",
                    "Bhima": "Relied on Bhima's strength but sometimes clashed with his impulsive nature.",
                    "Arjuna": "Valued Arjuna's skills and judgment in battle and statecraft.",
                    "Nakula & Sahadeva": "Appreciated their loyalty and unique skills in administration.",
                    "Duryodhana": "Tried to maintain peace but was ultimately forced into conflict.",
                    "Duryodhana's family": "Showed remarkable forgiveness, even to those who wronged him.",
                    "Draupadi": "Deeply devoted to his wife, though their relationship was tested during their exile.",
                    "Kunti": "Obedient son who always sought to honor his mother's guidance.",
                    "Bhishma": "Respected his grandfather's wisdom and sought his blessings.",
                    "Vidura": "Valued his uncle Vidura's wisdom and counsel."
                }
            }),
            ("10. Bhima", {
                "title": "The Mighty Warrior",
                "role": "Second Pandava brother and strongest warrior of the Pandavas",
                "personality": "Strong, straightforward, and passionate, Bhima represents raw physical power tempered by loyalty to his brothers. His strength is matched by his short temper, but he is fiercely protective of his family. He provides the physical might that complements Yudhishthira's wisdom and Arjuna's skill. Bhima's straightforward nature often puts him at odds with more diplomatic characters, but his heart is always in the right place.",
                "emotions": ["Fierce protectiveness of family", "Righteous anger (krodha)", "Loyalty to his brothers", "Joy in battle and feasting", "Impatience with injustice"],
                "marital_status": "Husband of Draupadi (shared with his four brothers) and Hidimbi (a rakshasi); father of Ghatotkacha and Sutasoma",
                "powers": [
                    "Unmatched physical strength (said to equal 10,000 elephants)",
                    "Master of mace fighting (gada-yuddha)",
                    "Tremendous appetite and capacity for food",
                    "Skilled wrestler and hand-to-hand combatant",
                    "Blessed with longevity and resistance to fatigue"
                ],
                "spiritual_nature": "Represents the power aspect of the divine (bala-avatar of Vayu). His journey shows how raw power must be channeled through dharma. While not as spiritually inclined as his brothers, his devotion to Krishna and commitment to righteousness guide his actions.",
                "secrets": [
                    "Was born when Kunti invoked Vayu, the wind god",
                    "Had a rakshasa son, Ghatotkacha, who played a crucial role in the Kurukshetra war",
                    "Was the only Pandava who never doubted Krishna's divinity",
                    "Killed all 100 Kaurava brothers, fulfilling his vow"
                ],
                "key_traits": [
                    "Unmatched physical strength and combat skills",
                    "Skilled in mace fighting and wrestling",
                    "Fierce loyalty to his family, especially Draupadi",
                    "Quick to anger but equally quick to forgive",
                    "Known for his enormous appetite and love of food"
                ],
                "relationships": {
                    "Duryodhana": "Sworn enemy after the attempted poisoning and Draupadi's humiliation. Their rivalry culminated in a mace duel during the war.",
                    "Hidimbi & Ghatotkacha": "Demon wife and half-demon son from his time in the forest. Maintained a secret family with them.",
                    "Krishna": "Respected Krishna's wisdom and often sought his counsel, especially regarding controlling his temper.",
                    "Yudhishthira": "Loyal to his elder brother, though sometimes frustrated by his decisions, especially regarding Duryodhana.",
                    "Arjuna": "Close bond as brothers-in-arms, with complementary skills. Their rivalry was friendly but intense.",
                    "Draupadi": "Fiercely protective of her honor after the dice game incident. Was the first to vow revenge for her humiliation.",
                    "Dushasana": "Swore to drink his blood for Draupadi's humiliation, which he fulfilled during the war.",
                    "Karna": "Rival who he ultimately defeated in the mace battle, though Karna was killed by Arjuna.",
                    "Hanuman": "Encountered his divine form and received his blessing, being his spiritual brother as both were sons of Vayu.",
                    "Kunti": "Loving and protective son, though sometimes frustrated by her decisions.",
                    "Nakula & Sahadeva": "Protective elder brother to the twins, though they had less interaction."
                }
            })
        ]

        # Format the character information
        result = ["MAIN CHARACTERS IN THE BHAGAVAD GITA\n"]
        for char_name, info in characters:
            char_info = [
                f"{char_name}: {info['title']}",
                f"Role: {info['role']}",
                "\nPERSONALITY AND SIGNIFICANCE:",
                info['personality']
            ]

            # Add emotional profile if available
            if 'emotions' in info:
                char_info.append("\nEMOTIONAL PROFILE:")
                char_info.extend(
                    [f"• {emotion}" for emotion in info['emotions']])

            # Add marital status if available
            if 'marital_status' in info:
                char_info.append("\nMARITAL STATUS:")
                char_info.append(f"• {info['marital_status']}")

            # Add powers and abilities if available
            if 'powers' in info:
                char_info.append("\nPOWERS AND ABILITIES:")
                char_info.extend([f"• {power}" for power in info['powers']])

            # Add spiritual nature if available
            if 'spiritual_nature' in info:
                char_info.append("\nSPIRITUAL NATURE:")
                char_info.append(info['spiritual_nature'])

            # Add key aspects or teachings if they exist
            if 'key_teachings' in info:
                char_info.append("\nKEY TEACHINGS:")
                char_info.extend(
                    [f"• {teaching}" for teaching in info['key_teachings']])
            elif 'key_moments' in info:
                char_info.append("\nKEY MOMENTS:")
                char_info.extend(
                    [f"• {moment}" for moment in info['key_moments']])
            elif 'key_aspects' in info:
                char_info.append("\nKEY ASPECTS:")
                char_info.extend(
                    [f"• {aspect}" for aspect in info['key_aspects']])
            elif 'key_qualities' in info:
                char_info.append("\nKEY QUALITIES:")
                char_info.extend(
                    [f"• {quality}" for quality in info['key_qualities']])
            elif 'key_traits' in info:
                char_info.append("\nKEY TRAITS:")
                char_info.extend(
                    [f"• {trait}" for trait in info['key_traits']])

            # Add secrets if available
            if 'secrets' in info:
                char_info.append("\nHIDDEN ASPECTS AND SECRETS:")
                char_info.extend([f"• {secret}" for secret in info['secrets']])

            # Add relationships section
            if 'relationships' in info and info['relationships']:
                char_info.append("\nRELATIONSHIPS WITH OTHER CHARACTERS:")
                for other_char, relationship in info['relationships'].items():
                    char_info.append(f"\n• {other_char}: {relationship}")

            result.append("\n" + "\n".join(char_info) + "\n\n" + "="*80)

        return "\n".join(result)

    def get_system_info(self) -> Dict[str, Any]:
        """Provide information about the system's features and capabilities."""
        return {
            "answer": (
                "This Bhagavad Gita Q&A System provides the following features:\n\n"
                "1. **Modern Life Guidance** - Get advice based on the Gita's teachings for:\n"
                "   - Work-life balance and stress management\n"
                "   - Career decisions and professional growth\n"
                "   - Personal development and self-improvement\n"
                "   - Relationships and social interactions\n\n"
                "2. **Chapter Summaries** - Get concise overviews of all 18 chapters of the Gita.\n\n"
                "3. **Character Insights** - Learn about key personalities in the Gita with detailed analyses.\n\n"
                "4. **Verse References** - All advice includes specific chapter and verse references.\n\n"
                "5. **Practical Applications** - Each teaching includes real-world applications and examples.\n\n"
                "You can ask questions like:\n"
                "- 'How to handle work stress according to the Gita?'\n"
                "- 'What does the Gita say about decision making?'\n"
                "- 'Give me a summary of Chapter 2'\n"
                "- 'Tell me about Lord Krishna's teachings'"
            ),
            "sources": [{"page": "N/A", "source": "System Information"}]
        }

    def get_modern_life_advice(self, question: str) -> Dict[str, Any]:
        """Provide Gita-based advice for modern life situations."""
        modern_advice_map = {
            'hate': {
                'teaching': "Adveshta sarva-bhutanam maitrah karuna eva cha (12.13) - One who is not hateful towards any living being, who is friendly and compassionate.",
                'advice': (
                    "The Bhagavad Gita offers profound wisdom for handling hate and negative emotions. Here's how to apply these teachings:\n\n"
                    "1. **Understand the Nature of Hate (2.14-15)**\n"
                    "   - Recognize that hate is temporary and affects the mind, not your true self\n"
                    "   - Like heat and cold, pleasure and pain come and go; maintain equanimity\n\n"
                    "2. **Practice Detachment (2.47-48)**\n"
                    "   - Focus on your actions rather than others' reactions\n"
                    "   - Perform your duties without attachment to outcomes or others' opinions\n\n"
                    "3. **Cultivate Compassion (12.13-15)**\n"
                    "   - Develop friendliness and compassion for all beings\n"
                    "   - See the divine presence in everyone, even those who express hate\n\n"
                    "4. **Respond, Don't React (2.56-58)**\n"
                    "   - Maintain inner peace regardless of external circumstances\n"
                    "   - Control your mind and senses to respond with wisdom, not emotion\n\n"
                    "5. **Self-Reflection (6.5-6)**\n"
                    "   - Use others' hatred as an opportunity for self-improvement\n"
                    "   - Elevate yourself through your own efforts, not by putting others down"
                ),
                'example': (
                    "In the Mahabharata, when Duryodhana expressed intense hatred towards the Pandavas, "
                    "Lord Krishna advised them to respond with righteousness rather than hatred. He taught that "
                    "true strength lies in self-control and adherence to dharma, not in retaliation.\n\n"
                    "When faced with hate, remember that the Gita teaches us to see beyond temporary emotions "
                    "and connect with the eternal soul within all beings. By maintaining this perspective, "
                    "we can respond with wisdom rather than react with more negativity."
                )
            },
            'stress': {
                'teaching': "Yoga-sthah kuru karmani (2.48) - Perform your duty balanced in success and failure.",
                'advice': (
                    "The Gita teaches us to perform our duties without attachment to results. "
                    "When feeling stressed, focus on doing your best without worrying about outcomes. "
                    "Chapter 2, Verse 47 reminds us that you have control only over your actions, not the results."
                ),
                'example': (
                    "Like Arjuna on the battlefield, we often face situations that cause stress and anxiety. "
                    "Krishna's advice to Arjuna in Chapter 2 about performing one's duty without attachment "
                    "to results is highly relevant to modern work-life balance challenges."
                )
            },
            'anxiety': {
                'teaching': "Yoga karmasu kaushalam (2.50) - Yoga is skill in action.",
                'advice': (
                    "The Gita suggests developing equanimity in all situations. Practice mindfulness "
                    "and meditation to remain centered. Chapter 6 describes the practice of meditation "
                    "as a way to calm the mind and overcome anxiety."
                ),
                'example': (
                    "Arjuna's anxiety before the battle (Chapter 1) mirrors modern performance anxiety. "
                    "Krishna's guidance to focus on righteous action rather than outcomes can help manage "
                    "anxiety in high-pressure situations like presentations or important meetings."
                )
            },
            'purpose': {
                'teaching': "Swadharme nidhanam shreyah (3.35) - Better is one's own duty, though imperfectly performed.",
                'advice': (
                    "The Gita emphasizes finding and following your dharma (purpose). Rather than comparing "
                    "yourself to others, focus on excelling in your unique path. Chapter 3 discusses the "
                    "importance of performing one's prescribed duties."
                ),
                'example': (
                    "Like Arjuna who was a warrior by nature, we must discover our inherent strengths "
                    "and use them in service of a higher purpose, rather than chasing after someone else's path."
                )
            },
            'failure': {
                'teaching': "Karmany evadhikaras te ma phaleshu kadachana (2.47) - You have a right to perform your duty, but not to the fruits of action.",
                'advice': (
                    "The Gita teaches that failure and success are part of life's journey. What matters is "
                    "performing your duty with full dedication. Chapter 2, Verse 50 explains how to maintain "
                    "equanimity in both success and failure."
                ),
                'example': (
                    "Even great warriors like Arjuna faced moments of doubt and perceived failure. "
                    "The entire Bhagavad Gita is essentially a dialogue that begins when Arjuna feels "
                    "like a failure before the battle even begins."
                )
            },
            'relationships': {
                'teaching': "Vidyavinayasampanne brahmane gavi hastini (5.18) - The wise see with equal vision a learned brahmin, a cow, an elephant, a dog, and a dog-eater.",
                'advice': (
                    "The Gita teaches us to see the divine in all beings. In relationships, practice "
                    "equality, respect, and compassion. Chapter 12 describes the qualities of a true devotee, "
                    "including being friendly and compassionate to all."
                ),
                'example': (
                    "Krishna's relationship with Arjuna demonstrates the ideal of spiritual friendship, "
                    "where the focus is on uplifting each other towards higher consciousness rather than "
                    "mere social or emotional support."
                )
            },
            'decision': {
                'teaching': "Tasmat sarveshu kaleshu mam anusmara yudhya cha (8.7) - Therefore, always think of Me and fight.",
                'advice': (
                    "When facing difficult decisions, seek inner wisdom through meditation and reflection. "
                    "The Gita advises us to connect with our higher self before making important choices. "
                    "Chapter 18 discusses different types of knowledge and decision-making processes."
                ),
                'example': (
                    "Arjuna's dilemma on the battlefield (Chapter 1) represents the difficult choices we all face. "
                    "Krishna doesn't make the decision for him but provides the wisdom to choose wisely."
                )
            },
            'success': {
                'teaching': "Yogah karmasu kaushalam (2.50) - Yoga is excellence in work.",
                'advice': (
                    "True success, according to the Gita, is not just material achievement but self-mastery. "
                    "Chapter 6 describes the balanced state of a yogi who remains undisturbed in success and failure alike."
                ),
                'example': (
                    "Krishna explains to Arjuna that real success lies in performing one's duty with dedication, "
                    "without attachment to results - a principle that can transform how we approach our careers "
                    "and personal goals."
                )
            },
            'career': {
                'teaching': "Sve sve karmany abhiratah samsiddhim labhate narah (18.45) - By following one's natural inclinations and duties, one attains perfection.",
                'advice': (
                    "The Gita advises us to discover and follow our natural inclinations and talents (svadharma). "
                    "Rather than chasing after prestigious careers, find work that aligns with your nature and skills. "
                    "Chapter 18 describes how different types of work suit different natures."
                ),
                'example': (
                    "Arjuna was a warrior by nature (kshatriya). The Gita teaches that we find fulfillment "
                    "not by imitating others but by perfecting our unique path. Like Arjuna, we should focus on "
                    "excelling in our natural strengths rather than trying to be someone we're not."
                )
            },
            'lost': {
                'teaching': "Tasmat sarva-bhuteshu mam anusmara yudhya cha (8.7) - Therefore, remember Me at all times and fight.",
                'advice': (
                    "When feeling lost, the Gita advises connecting with your higher purpose. "
                    "Chapter 7 explains that those who seek wisdom and meaning will find it. "
                    "The key is to continue performing your duties while seeking deeper understanding."
                ),
                'example': (
                    "Arjuna felt completely lost at the beginning of the Gita, unsure of his path. "
                    "Krishna's guidance helped him see his situation with clarity and purpose. "
                    "Similarly, when we feel lost, we can seek wisdom and continue acting with integrity."
                )
            },
            'purpose': {
                'teaching': "Karmany evadhikaras te ma phalesu kadachana (2.47) - You have a right to perform your prescribed duties, but you are not entitled to the fruits of your actions.",
                'advice': (
                    "The Gita teaches that true purpose is found in selfless action. Rather than focusing on results, "
                    "concentrate on doing your best in your current responsibilities. Chapter 3 explains how selfless "
                    "action leads to both material and spiritual fulfillment."
                ),
                'example': (
                    "Krishna advised Arjuna to fight not for victory or kingdom, but because it was his duty as a warrior. "
                    "Similarly, we can find purpose in doing our best in whatever role we find ourselves, "
                    "without attachment to specific outcomes."
                )
            },
            'work-life balance': {
                'teaching': "Yogasthah kuru karmani (2.48) - Perform your duty balanced in success and failure. Such equanimity is called yoga.",
                'advice': (
                    "The Gita's approach to work-life balance is rooted in the concept of 'Yoga' - union through balance. "
                    "Here's a deeper dive into applying these principles:\n\n"
                    "1. **The Foundation: Right Understanding (2.11-13, 2.16-17)**\n"
                    "   - Recognize the eternal nature of the soul beyond temporary work-life situations\n"
                    "   - Understand that true fulfillment comes from within, not external achievements\n"
                    "   - See work as an offering (yajña) rather than just a means to an end (3.9-10)\n\n"
                    "2. **Daily Practice (6.10-17)**\n"
                    "   - Begin and end your day with meditation or reflection (6.10-11)\n"
                    "   - Practice moderation in work, rest, diet, and recreation (6.16-17)\n"
                    "   - Cultivate contentment (santosha) with what comes your way (2.64-65)\n\n"
                    "3. **Practical Integration (3.5-9, 18.45-47)**\n"
                    "   - Perform your duties according to your nature (svadharma)\n"
                    "   - Set clear boundaries between different life domains\n"
                    "   - Practice being fully present in each activity (2.50)\n\n"
                    "4. **Overcoming Challenges (2.14-15, 2.47-48)**\n"
                    "   - Accept the temporary nature of both pleasure and pain\n"
                    "   - Focus on your efforts, not outcomes (2.47)\n"
                    "   - Maintain equanimity in success and failure (2.48)"
                ),
                'example': (
                    "Krishna's life exemplifies perfect work-life integration. As a king, he managed the affairs of Dvaraka; "
                    "as a warrior, he fought in the Kurukshetra war; as a spiritual teacher, he imparted the Gita's wisdom; "
                    "and as a friend, he was always available to his devotees. The Gita itself was spoken in the midst of "
                    "a battlefield, showing that spiritual wisdom isn't separate from daily life but should permeate all our actions.\n\n"
                    "Arjuna's transformation throughout the Gita also demonstrates this balance. He begins overwhelmed by life's "
                    "complexities (1.28-30) but learns to act with wisdom and detachment (18.73). His journey shows that "
                    "true balance comes not from perfect external circumstances but from inner wisdom and perspective."
                )
            },
            'balance': {
                'teaching': "Samatvam yoga uchyate (2.48) - Evenness of mind is called yoga.",
                'advice': (
                    "The Gita teaches that true balance comes from maintaining equanimity in all situations. "
                    "Rather than dividing life into separate compartments, see all activities as opportunities "
                    "for spiritual growth. Chapter 6 explains how to remain centered amidst life's dualities."
                ),
                'example': (
                    "Arjuna learned to maintain his center whether in the peaceful environment of the forest "
                    "or on the chaotic battlefield. Similarly, we can find balance by keeping our consciousness "
                    "anchored in higher principles regardless of external circumstances."
                )
            },
            'time management': {
                'teaching': "Kalo 'smi loka-kshaya-krit (11.32) - Time I am, the great destroyer of worlds.",
                'advice': (
                    "The Gita teaches that time is the most powerful force. For effective time management: "
                    "1. Prioritize duties according to your life stage and responsibilities (3.8) "
                    "2. Begin your day with spiritual practices (6.10-14) "
                    "3. Work with full concentration during designated times (2.50) "
                    "4. Take regular breaks for renewal (6.11)"
                ),
                'example': (
                    "Krishna's life demonstrates perfect time management - he was never in a hurry, yet everything "
                    "was accomplished at the right moment. His teaching to Arjuna about the importance of timely "
                    "action (kāla) shows that understanding time's nature is key to effective living."
                )
            }
        }

        # Find the most relevant topic based on the question
        question_lower = question.lower()
        matched_topic = None

        for topic, content in modern_advice_map.items():
            if topic in question_lower:
                matched_topic = topic
                break

        if matched_topic:
            advice = modern_advice_map[matched_topic]
            return {
                "answer": (
                    f"The Bhagavad Gita offers profound wisdom about {matched_topic}.\n\n"
                    f"Key Teaching: {advice['teaching']}\n\n"
                    f"Advice: {advice['advice']}\n\n"
                    f"Relevant Example: {advice['example']}\n\n"
                    "Would you like me to elaborate on any specific aspect of this teaching?"
                ),
                "sources": [{"page": "Multiple Chapters", "source": self.pdf_path}]
            }

        return None

    def extract_best_answer(self, question: str, text: str) -> str:
        """Extract the most relevant part of the text that answers the question."""
        question_lower = question.lower()

        # Check for modern life advice questions first
        modern_advice = self.get_modern_life_advice(question)
        if modern_advice:
            modern_advice['answer'] = f"Hare Krishna! {modern_advice['answer']}"
            return modern_advice['answer']

        # Handle chapter summary request
        if any(term in question_lower for term in ['summary of chapters', 'chapter summary', 'summarize chapters', 'list of chapters']):
            return self.get_chapter_summaries()

        # Split into sentences for other types of questions
        sentences = re.split(r'(?<=[.!?])\s+', text)

        # Look for direct answers first (sentences containing key terms)
        key_terms = [term for term in question_lower.split() if len(term) > 3]

        # Check for specific question patterns
        if 'who is arjuna' in question_lower or 'why is arjuna great' in question_lower or 'what makes arjuna special' in question_lower:
            return (
                "Hare Krishna! Arjuna is considered one of the greatest warriors and devotees in the Bhagavad Gita. Here's why he is special:\n\n"
                "1. **Chosen Devotee**: Arjuna was personally selected by Lord Krishna to receive the supreme spiritual knowledge of the Bhagavad Gita (Bg 18.67-73).\n\n"
                "2. **Exemplary Qualities**: He possessed all divine qualities (Bg 16.1-3) and was known for his courage, humility, and determination.\n\n"
                "3. **Perfect Disciple**: Arjuna's willingness to surrender to Krishna and ask sincere questions (Bg 2.7) makes him the perfect example of a disciple.\n\n"
                "4. **Warrior of Dharma**: As a kshatriya, he fought to uphold righteousness (dharma) and protect the world from adharma (irreligion).\n\n"
                "5. **Friend of Krishna**: He shared a unique friendship with Lord Krishna, who agreed to be his charioteer, showing their special bond.\n\n"
                "Arjuna's greatness lies in his perfect combination of devotion, martial skill, and philosophical understanding, making him an eternal example of how to live according to spiritual principles."
            )

        # Look for verses or teachings
        if any(term in question_lower for term in ['teach', 'teaching', 'lesson', 'what does krishna say']):
            # Look for verses that contain teachings
            for sentence in sentences:
                if any(term in sentence.lower() for term in ['teach', 'says', 'explain', 'therefore', 'krishna said']):
                    if len(sentence) > 50:  # Ensure it's a substantial answer
                        return f"Hare Krishna! {sentence}"

        # Default: find the most relevant sentence
        best_sentence = sentences[0] if sentences else ""
        best_score = -1

        for sentence in sentences:
            score = sum(1 for term in key_terms if term in sentence.lower())
            if score > best_score:
                best_score = score
                best_sentence = sentence

        return f"Hare Krishna! {best_sentence}" if best_score > 0 else f"Hare Krishna! {sentences[0]}" if sentences else "Hare Krishna! No answer found"

    def _get_answer_from_qa_pairs(self, question: str) -> Optional[Dict[str, Any]]:
        """
        This method is kept for backward compatibility but will not return any answers
        to ensure we only provide answers from the PDF content.
        """
        # Always return None to prevent falling back to pre-defined Q&A pairs
        return None

        # Simple keyword matching for now - can be enhanced with more sophisticated NLP
        for qa in qa_pairs:
            # Check if any word from the question matches the QA pair
            question_words = set(question_lower.split())
            qa_words = set(qa["question"].lower().split())

            # If there's a significant word overlap, return this answer
            if len(question_words.intersection(qa_words)) >= 3:  # At least 3 matching words
                return {
                    "answer": f"Hare Krishna! {qa['answer']}",
                    "sources": [{"page": "QA Database", "source": "Pre-defined Q&A"}],
                    "confidence": 0.9  # High confidence for exact matches
                }
        return None

    def _get_answer_from_pdf(self, question: str) -> Dict[str, Any]:
        """Generate an answer by searching the PDF content."""
        # This is the existing PDF-based answer generation logic
        relevant_docs = self.get_relevant_documents(question, k=3)
        combined_text = " ".join([doc.page_content for doc in relevant_docs])

        if not combined_text:
            return {
                "answer": "Hare Krishna! I couldn't find relevant information in the text to answer your question.",
                "sources": [],
                "confidence": 0.0
            }

        # Extract the most relevant part that answers the question
        answer = self.extract_best_answer(question, combined_text)

        return {
            "answer": answer,
            "sources": [{"page": doc.metadata.get('page', 'N/A'), "source": self.pdf_path}
                        for doc in relevant_docs],
            "confidence": 0.7  # Medium confidence for PDF-based answers
        }

    def _get_time_based_greeting(self) -> str:
        """Return a time-appropriate greeting."""
        from datetime import datetime
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "Good morning! 🌅"
        elif 12 <= hour < 17:
            return "Good afternoon! ☀️"
        elif 17 <= hour < 22:
            return "Good evening! 🌇"
        return "Hare Krishna! 🌙"

    def _format_key_concepts(self, text: str) -> str:
        """Emphasize key concepts with markdown formatting."""
        concepts = [
            'Krishna', 'Arjuna', 'Dharma', 'Karma', 'Bhakti', 'Yoga',
            'Moksha', 'Atman', 'Brahman', 'Samsara', 'Maya', 'Jnana'
        ]
        for concept in concepts:
            text = re.sub(
                fr'\b({concept})\b', 
                r'**\1**',  # Make concept bold
                text, 
                flags=re.IGNORECASE
            )
        return text

    def _add_verse_references(self, text: str, sources: List[Dict[str, Any]]) -> str:
        """Add formatted verse references if available."""
        if not sources or not any(s.get('page') for s in sources):
            return text
            
        refs = [f"{s['page']}" for s in sources if s.get('page')]
        if refs:
            return f"{text.rstrip('.')}  \n\n*Source: {', '.join(refs)}*"
        return text

    def _format_as_bullet_points(self, text: str) -> str:
        """Convert lists into markdown bullet points."""
        # Look for patterns like "1) First point 2) Second point"
        text = re.sub(r'(\d+[\)\.])\s+', r'\n- ', text)
        # Look for patterns like "- First point - Second point"
        text = re.sub(r'(?<!\n)-\s+', '\n- ', text)
        return text.strip()

    def _expand_abbreviations(self, text: str) -> str:
        """Expand common abbreviations in the text."""
        abbreviations = {
            'bG': 'Bhagavad Gita',
            'BG': 'Bhagavad Gita',
            'Gita': 'Bhagavad Gita',
            'Lord K': 'Lord Krishna',
            'Arjuna U': 'Arjuna Uvāca',
        }
        for abbr, full in abbreviations.items():
            text = text.replace(abbr, full)
        return text

    def _fix_common_issues(self, text: str) -> str:
        """Fix common formatting issues in the text."""
        # First, handle specific common issues that need to be fixed before general patterns
        text = text.replace('theBhagavad', 'the Bhagavad')
        text = text.replace('BhagavadGita', 'Bhagavad Gita')
        text = text.replace('LordKrishna', 'Lord Krishna')
        text = text.replace('Arjunasaid', 'Arjuna said')
        text = text.replace('Krishnasaid', 'Krishna said')
        
        # Common word pairs that should have spaces between them
        common_pairs = [
            (r'([a-z])([A-Z][a-z])', r'\1 \2'),  # lower-Upper (e.g., 'theBhagavad' -> 'the Bhagavad')
            (r'([a-z])([A-Z])', r'\1 \2'),  # lower-UPPER (e.g., 'wordAND' -> 'word AND')
            (r'([a-zA-Z])([0-9])', r'\1 \2'),  # letter-number
            (r'([0-9])([a-zA-Z])', r'\1 \2'),  # number-letter
            (r'([a-zA-Z])([.,!?])', r'\1\2'),   # letter-punctuation (remove space)
            (r'([.,!?])([a-zA-Z])', r'\1 \2'),  # punctuation-letter (add space)
            (r'(\w)(the|a|an)(\s|$)', r'\1 \2\3', re.IGNORECASE),  # word-article
            (r'to(\w+)', r'to \1', re.IGNORECASE),  # to-verb (e.g., 'tounderstand' -> 'to understand')
            (r'(\w)(is|are|was|were|has|have|had|will|would|could|should)(\s|$)', r'\1 \2\3'),  # word-verb
            (r'\s+', ' '),  # Multiple spaces to single space
        ]
        
        for fix in common_pairs:
            if len(fix) == 3:  # Has flags
                pattern, replacement, flags = fix
                text = re.sub(pattern, replacement, text, flags=flags)
            else:
                pattern, replacement = fix
                text = re.sub(pattern, replacement, text)
        
        # Clean up any remaining double spaces and newlines
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single
        text = re.sub(r'\s+([.,!?])', r'\1', text)  # Remove space before punctuation
        text = re.sub(r'\n\s*\n+', '\n\n', text)  # Normalize multiple newlines
        
        return text.strip()

    def _format_sanskrit_text(self, text: str) -> str:
        """Format Sanskrit text and translations for better readability."""
        if not text:
            return ""

        # 1. First, clean up any control characters and normalize whitespace
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        # 2. Protect special phrases and terms from being modified
        protected_phrases = [
            'Hare Krishna', 'Bhagavad Gita', 'Sanatana Dharma',
            'Lord Krishna', 'Arjuna said', 'Krishna said',
            'Bhagavad-gita', 'Bhagavad Gita As It Is',
            'Sanatana-dharma', 'Supreme Personality of Godhead',
            'Bhagavan', 'Maharaja', 'Prabhupada'
        ]
        
        # Create protected map and replace phrases with placeholders
        protected_map = {}
        for phrase in protected_phrases:
            placeholder = f'__PROTECTED_{len(protected_map)}__'
            protected_map[placeholder] = phrase
            text = text.replace(phrase, placeholder)

        # 3. Fix common word-joining issues
        word_join_fixes = [
            # Fix words joined with 'th' (e.g., 'this', 'that')
            (r'\b([a-zA-Z]{2,})th([a-zA-Z]{2,})\b', r'\1th\2'),
            
            # Fix words with missing spaces after punctuation
            (r'([a-zA-Z])([.,!?;:])([a-zA-Z])', r'\1\2 \3'),
            
            # Fix words joined by numbers
            (r'([a-zA-Z])(\d)', r'\1 \2'),
            (r'(\d)([a-zA-Z])', r'\1 \2'),
            
            # Fix common OCR artifacts
            (r'([a-z])([A-Z])', r'\1 \2'),
            (r'([a-z])([A-Z][a-z])', r'\1 \2'),
            
            # Fix common Sanskrit terms
            (r'([a-z])([A-Z][a-z])', r'\1 \2'),
            (r'([a-z])([A-Z][a-z])', r'\1 \2'),
        ]
        
        for pattern, replacement in word_join_fixes:
            try:
                text = re.sub(pattern, replacement, text)
            except re.error as e:
                logging.warning(f"Regex error with pattern {pattern}: {e}")

        # 4. Format verses and translations
        verse_patterns = [
            # Format verse numbers (e.g., "TEXT 1")
            (r'(?i)TEXT\s+(\d+)(?:-\d+)?\s*', '\n**Verse \\1**\n\n'),
            
            # Format word-by-word meanings
            (r'(?i)SYNONYMS?\s*', '\n**Word-by-word meaning**:\n'),
            
            # Format translation lines
            (r'([A-Z][A-Za-z\s]+\.)\s*', '\n\\1\n'),
            
            # Format word-meaning pairs
            (r'\b([a-zA-Z]+)--([^\s,;.]+)', r'`\1` - `\2`'),
        ]
        
        for pattern, replacement in verse_patterns:
            text = re.sub(pattern, replacement, text)

        # 5. Clean up punctuation and spacing
        cleanup_patterns = [
            (r'\s+', ' '),  # Normalize whitespace
            (r'\s+([.,!?;:])', r'\1'),  # Remove space before punctuation
            (r'([.,!?;:])([A-Za-z])', r'\1 \2'),  # Add space after punctuation
            (r'\(\s*', '('),  # Remove spaces after (
            (r'\s*\)', ')'),  # Remove spaces before )
            (r'\s*,\s*', ', '),  # Standardize comma spacing
            (r'\s*\;\s*', '; '),  # Standardize semicolon spacing
        ]
        
        for pattern, replacement in cleanup_patterns:
            text = re.sub(pattern, replacement, text)

        # 6. Restore protected phrases
        for placeholder, phrase in protected_map.items():
            text = text.replace(placeholder, phrase)

        # 7. Final cleanup
        text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
        text = re.sub(r'\n\s*\n+', '\n\n', text)  # Normalize newlines
        
        # Ensure proper sentence capitalization
        sentences = re.split(r'(?<=[.!?])\s+', text)
        text = ' '.join(sentence[0].upper() + sentence[1:] if sentence else '' for sentence in sentences)

        return text

    def _format_source_reference(self, sources: List[Dict[str, Any]]) -> str:
        """Format source references in a consistent way."""
        if not sources or not isinstance(sources, list):
            return ""
            
        source_texts = []
        for source in sources:
            if not isinstance(source, dict):
                continue
                
            page = source.get('page', '')
            source_name = source.get('source', '')
            
            if page and source_name:
                source_texts.append(f"{source_name}, page {page}")
            elif page:
                source_texts.append(f"page {page}")
            elif source_name:
                source_texts.append(source_name)
                
        if not source_texts:
            return ""
            
        return "\n\n*Source: " + "; ".join(source_texts) + "*"

    def _post_process_answer(self, answer: str, question: str = "", sources: List[Dict[str, Any]] = None) -> str:
        """
        Improve the quality of the answer with enhanced formatting and engagement.
        
        Args:
            answer: The raw answer text to be processed
            question: The original question (optional, for context)
            sources: List of source references (optional)
            
        Returns:
            str: The improved and formatted answer text
        """
        if not answer or not isinstance(answer, str):
            return answer
            
        # Store original for comparison
        original_answer = answer
        
        # 1. First, protect special phrases and terms from being modified
        protected_phrases = [
            'Hare Krishna', 'Bhagavad Gita', 'Sanatana Dharma',
            'Lord Krishna', 'Arjuna said', 'Krishna said',
            'Bhagavad-gita', 'Bhagavad Gita As It Is',
            'Sanatana-dharma', 'Supreme Personality of Godhead',
            'Bhagavan', 'Maharaja', 'Prabhupada', 'Arjuna', 'Dhritarashtra',
            'Kurukshetra', 'Mahabharata', 'Bhagavad-gita'
        ]
        
        # Create protected map and replace phrases with placeholders
        protected_map = {}
        for phrase in protected_phrases:
            # Create a unique placeholder that won't conflict with actual text
            placeholder = f'__PROTECTED_{len(protected_map)}__'
            protected_map[placeholder] = phrase
            answer = answer.replace(phrase, placeholder)
        
        # 2. Apply comprehensive text correction using our TextProcessor
        answer = self.text_processor.correct_text(answer)
        
        # 3. Standardize and clean up the greeting - only keep one at the start
        answer = re.sub(r'(^|\n)Hare \*\*Krishna\*\!.*?(?=\n|$)', '', answer)
        
        # 4. Format Sanskrit text and translations
        answer = self._format_sanskrit_text(answer)
        
        # 5. Fix common word-joining issues
        word_join_fixes = [
            # Fix common word joins
            (r'([a-z])([A-Z])', r'\1 \2'),  # Split camelCase
            (r'(\w)(\d+)', r'\1 \2'),  # Split word followed by number
            (r'(\d+)([A-Za-z])', r'\1 \2'),  # Split number followed by word
            
            # Fix common OCR artifacts
            (r'([a-z])([A-Z][a-z])', r'\1 \2'),
            (r'([a-z])([A-Z][a-z])', r'\1 \2'),
            
            # Fix common word joins with punctuation
            (r'([a-zA-Z])([.,!?;:])([a-zA-Z])', r'\1\2 \3'),
        ]
        
        for pattern, replacement in word_join_fixes:
            try:
                answer = re.sub(pattern, replacement, answer)
            except re.error as e:
                logging.warning(f"Regex error with pattern {pattern}: {e}")
        
        # 6. Fix common OCR and formatting issues
        common_issues = [
            # Add spaces around common words
            (r'\b(a|an|the|and|or|but|nor|so|for|yet|at|by|in|of|on|to|up|as|is|are|was|were|be|been|being|have|has|had|do|does|did|shall|should|will|would|may|might|must|can|could)\b', r' \1 '),
            
            # Fix spacing around punctuation
            (r'\s+', ' '),  # Multiple spaces to single
            (r'\s+([.,!?;:])', r'\1'),  # Remove space before punctuation
            (r'([.,!?;:])([A-Za-z])', r'\1 \2'),  # Add space after punctuation
            (r'\((\s*)', '('),  # Remove spaces after (
            (r'\s*\)', ')'),  # Remove spaces before )
            (r'\s*,\s*', ', '),  # Standardize comma spacing
            (r'\s*\;\s*', '; '),  # Standardize semicolon spacing
            
            # Fix common OCR artifacts
            (r'\b([A-Za-z])\s+([A-Za-z])\b', r'\1\2'),  # Fix single letter words
            (r'\b([a-z])\s+([a-z]{2,})\b', r'\1\2'),  # Fix single letter prefixes
        ]
        
        for pattern, replacement in common_issues:
            try:
                answer = re.sub(pattern, replacement, answer)
            except re.error as e:
                logging.warning(f"Regex error with pattern {pattern}: {e}")
        
        # 7. Restore protected phrases
        for placeholder, phrase in protected_map.items():
            answer = answer.replace(placeholder, phrase)
        
        # 8. Capitalization and formatting
        answer = answer.strip()
        if answer:
            # Capitalize first letter
            answer = answer[0].upper() + answer[1:]
            # Ensure proper sentence endings
            if not answer.endswith(('.', '!', '?')):
                answer += '.'
        
        # 9. Standardize terms
        standard_terms = {
            'Bhagavad-gita': 'Bhagavad Gita',
            'Krsna': 'Krishna',
            'sastra': 'shastra',
            'varnasrama': 'varnashrama',
            'yoga-maya': 'yogamaya',
            'maha-maya': 'mahamaya',
            'Gita': 'Bhagavad Gita',
            'BG': 'Bhagavad Gita'
        }
        
        for old, new in standard_terms.items():
            answer = answer.replace(old, new)
        
        # 10. Add greeting if not present
        if not answer.startswith(('Hare Krishna!', 'Dear', 'Namaste', 'Hello', 'Good')):
            greeting = self._get_time_based_greeting()
            answer = f"{greeting} {answer}"
        
        # 11. Add verse references if available
        if sources:
            answer = self._add_verse_references(answer, sources)
        
        # 12. Add a thoughtful closing for longer answers
        if len(answer.split()) > 15 and not answer.strip().endswith(('.', '!', '?')):
            closings = [
                "\n\nMay this wisdom guide your path. 🙏",
                "\n\nWishing you peace and understanding. 🌺",
                "\n\nMay these teachings illuminate your journey. ✨"
            ]
            import random
            answer += random.choice(closings)
        
        # Final cleanup
        answer = re.sub(r'\s+', ' ', answer).strip()
        return answer
        
    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Main method to answer a question about the Bhagavad Gita.
        This method prioritizes answers from the PDF content and only falls back to
        predefined responses when no relevant information is found in the PDF.
        """
        print(f"\n=== DEBUG: Answering question: {question}")
        try:
            # Preprocess the question
            question = question.strip()
            if not question:
                print("DEBUG: Empty question received")
                return {
                    "answer": "Hare Krishna! Please ask a question about the Bhagavad Gita.",
                    "sources": [],
                    "confidence": 0.0,
                    "source_type": "system"
                }
            
            # Correct character names in the question
            corrected_question, corrections = correct_text_names(question)
            if corrections:
                logging.info(f"Corrected names in question: {corrections}")
                logging.info(f"Original: {question}")
                logging.info(f"Corrected: {corrected_question}")
                question = corrected_question
            
            # Convert to lowercase for case-insensitive matching
            question_lower = question.lower()
            
            # First, check for verse references as they are the most specific
            print("DEBUG: Checking for verse references...")
            verse_response = self._check_for_verse_reference(question)
            if verse_response and verse_response.get('confidence', 0) > 0.7:
                print(f"DEBUG: Found verse response with confidence {verse_response.get('confidence')}")
                # Post-process the verse response
                if 'answer' in verse_response:
                    verse_response['answer'] = self._post_process_answer(verse_response['answer'])
                return verse_response
                
            # Next, try to get an answer from the PDF content
            print("DEBUG: Getting answer from PDF...")
            pdf_response = self._get_answer_from_pdf(question)
            if pdf_response and pdf_response.get('confidence', 0) > 0.3:  # Lower threshold for PDF answers
                print(f"DEBUG: Found PDF response with confidence {pdf_response.get('confidence')}")
                # Post-process the PDF response with sources
                if 'answer' in pdf_response:
                    sources = pdf_response.get('sources', [])
                    pdf_response['answer'] = self._post_process_answer(
                        answer=pdf_response['answer'],
                        question=question,
                        sources=sources
                    )
                return pdf_response
                
            # If we still don't have a good answer, try to find relevant documents
            print("DEBUG: No good answer from PDF, trying to find relevant documents...")
            relevant_docs = self.get_relevant_documents(question, k=5)
            if relevant_docs:
                print(f"DEBUG: Found {len(relevant_docs)} relevant documents")
                # Try to extract a better answer from the most relevant documents
                combined_content = " ".join([doc.page_content for doc in relevant_docs[:3]])
                answer = self.extract_best_answer(question, combined_content)
                
                if answer and len(answer) > 30:  # Ensure we have a meaningful answer
                    return {
                        "answer": answer,
                        "sources": [relevant_docs[0].metadata],
                        "confidence": 0.7,
                        "source_type": "pdf_content"
                    }
            
            # If we've reached here, we couldn't find a good answer in the PDF
            # Try to provide a helpful response based on the question type
            
            # For verse reference questions
            if any(term in question_lower for term in ['chapter', 'verse', 'chapter and verse', 'verse number', 'chapter number']):
                return {
                    "answer": "Hare Krishna! I couldn't find the specific verse reference in the current context. "
                             "The Bhagavad Gita contains 18 chapters with a total of 700 verses. "
                             "Could you please provide more details about the verse you're looking for? "
                             "For example, you could ask about a specific teaching or concept, "
                             "and I'll try to find relevant verses from the text.",
                    "sources": [],
                    "confidence": 0.3,
                    "source_type": "system"
                }
                
            # For general questions where we couldn't find an answer
            return {
                "answer": "Hare Krishna! I couldn't find a specific answer to your question in the Bhagavad Gita text. "
                         "The Gita primarily focuses on spiritual knowledge, the nature of the self, "
                         "the Supreme Lord, and the paths to spiritual realization. Could you please "
                         "rephrase your question or ask about a specific teaching or concept from the Gita?",
                "sources": [],
                "confidence": 0.1,
                "source_type": "system"
            }
            
            # If we've reached here, we couldn't find a good answer in the PDF
            # Try to provide a helpful response based on the question type
            
            # For questions about specific paths (Karma, Bhakti, Jnana Yoga)
            if any(term in question_lower for term in ['karma yoga', 'bhakti yoga', 'jnana yoga', 'path of', 'yoga of']):
                return {
                    "answer": ("Hare Krishna! The Bhagavad Gita describes several spiritual paths, including Karma Yoga (path of selfless action), "
                             "Bhakti Yoga (path of devotion), and Jnana Yoga (path of knowledge). While I couldn't find a specific "
                             "answer to your question in the text, you might want to ask about a specific teaching or verse "
                             "related to these paths. For example, you could ask about a particular aspect of these yogas or "
                             "request a verse that explains them."),
                    "sources": [],
                    "confidence": 0.2,
                    "source_type": "system"
                }
                
            # For questions about characters
            if any(term in question_lower for term in ['arjuna', 'krishna', 'bhishma', 'duryodhana', 'yudhishthira', 'bhima', 'nakula', 'sahadeva', 'drona', 'karna']):
                return {
                    "answer": ("Hare Krishna! I understand you're asking about a character from the Mahabharata. While the Bhagavad Gita "
                             "primarily focuses on the conversation between Lord Krishna and Arjuna, it doesn't contain extensive "
                             "biographical details about the characters. You might want to ask about a specific teaching or "
                             "philosophical concept from the Gita instead."),
                    "sources": [],
                    "confidence": 0.2,
                    "source_type": "system"
                }
                
            # For questions about the material world or spiritual concepts
            if any(term in question_lower for term in ['material world', 'maya', 'prakriti', 'atman', 'brahman', 'moksha', 'liberation']):
                return {
                    "answer": ("Hare Krishna! The Bhagavad Gita contains profound wisdom about spiritual concepts like the material world, "
                             "the self (atman), the Supreme (Brahman), and liberation (moksha). While I couldn't find a specific "
                             "answer to your question, you might want to ask about a particular verse or teaching related to "
                             "these topics. The Gita's teachings are most powerful when connected to specific verses from the text."),
                    "sources": [],
                    "confidence": 0.2,
                    "source_type": "system"
                }
                
            # Final fallback response
            return {
                "answer": ("Hare Krishna! I couldn't find a specific answer to your question in the Bhagavad Gita text. "
                          "The Gita primarily contains the spiritual teachings of Lord Krishna to Arjuna on the battlefield of Kurukshetra. "
                          "You might want to try rephrasing your question or asking about a specific teaching, verse, or concept from the Gita."),
                "sources": [],
                "confidence": 0.1,
                "source_type": "system"
            }

            # Handle Krishna's relationship with Arjuna questions
            if any(term in question_lower for term in ['why krishna close to arjun', 'why krishna favor arjuna', 'krishna and arjuna relationship', 'why krishna only very close to arjun than other pandu brothers', 'krishna arjuna friendship']):
                return {
                    "answer": "Hare Krishna! The relationship between Lord Krishna and Arjuna is one of the most profound and celebrated divine friendships in all of Vedic literature. Here's a comprehensive understanding of their unique bond:\n\n"
                    "## 1. Eternal Spiritual Connection\n"
                    "> 'Many, many births both you and I have passed. I can remember all of them, but you cannot, O subduer of the enemy!' (Bhagavad Gita 4.5)\n\n"
                    "- **Nara-Narayana Tattva**: In their previous lives, Arjuna was Nara and Krishna was Narayana, eternal spiritual brothers engaged in divine pastimes. This eternal relationship continued in their incarnations as Krishna and Arjuna.\n\n"
                    "## 2. The Perfect Devotee-Disciple\n"
                    "> 'Now I am confused about my duty and have lost all composure because of weakness. In this condition I am asking You to tell me clearly what is best for me. Now I am Your disciple, and a soul surrendered unto You. Please instruct me.' (Bhagavad Gita 2.7)\n\n"
                    "- Arjuna's complete surrender and willingness to become Krishna's disciple created the perfect circumstance for the Bhagavad-gita's teachings. His questions and doubts (Bg 1.28-46) were not ordinary but divinely arranged to benefit all of humanity.\n\n"
                    "## 3. Divine Affection and Intimacy\n"
                    "> 'O conqueror of wealth [Arjuna], there is no servant in this world more dear to Me than you, nor will there ever be one more dear.' (Bhagavad Gita 4.3)\n\n"
                    "- **Special Position**: Among millions of devotees, Krishna declares Arjuna as uniquely dear to Him. This wasn't mere favoritism but a recognition of Arjuna's pure devotion and selfless service.\n\n"
                    "## 4. The Charioteer and the Warrior\n"
                    "- **Symbolic Relationship**: Krishna's role as Arjuna's charioteer in the Kurukshetra war represents how the Lord guides His devotees through life's battles when they fully surrender to Him.\n"
                    "- **Divine Protection**: Krishna protected Arjuna in battle (Bg 11.32-34) and granted him divine vision to perceive the Universal Form (Bg 11.8-9), demonstrating His personal care for His devotee.\n\n"
                    "## 5. Beyond Ordinary Friendship\n"
                    "- **Transcendental Friendship**: While Krishna maintained different relationships with each Pandava, His friendship with Arjuna was unique because Arjuna related to Him most intimately - as friend, devotee, disciple, and relative all combined.\n\n"
                    "- **Eternal Message**: Their relationship establishes the perfect paradigm of how the Supreme Lord reciprocates with His pure devotees according to their level of surrender and love.\n\n"
                    "## 6. Lessons for Spiritual Seekers\n"
                    "1. **Complete Surrender**: Like Arjuna, we should approach the spiritual master with humility and surrender.\n"
                    "2. **Asking Questions**: Arjuna's sincere inquiries led to the revelation of the Gita's wisdom. We should also approach spiritual knowledge with genuine inquiry.\n"
                    "3. **Friendship with the Divine**: The Krishna-Arjuna relationship shows that the Supreme Lord can be approached in loving friendship by His pure devotees.\n\n"
                    "In essence, Krishna's special relationship with Arjuna wasn't mere partiality but a divine arrangement to demonstrate the perfection of the guru-disciple relationship and the intimate bond between the Lord and His pure devotee.",
                    "sources": [
                        {"page": "BG 1.28-46, 2.7, 4.3, 4.5, 11.8-9, 11.32-34", "source": "Bhagavad Gita As It Is"},
                        {"page": "Introduction and Purport to Chapter 1", "source": "Bhagavad Gita As It Is by A.C. Bhaktivedanta Swami Prabhupada"}
                    ],
                    "confidence": 0.99
                }

            # If we reach here, no pre-defined answer was found, so search the PDF
            pdf_answer = self._get_answer_from_pdf(question)

            # If we have a good answer from the PDF, return it
            if pdf_answer["confidence"] > 0.5:
                return pdf_answer

            # If we get here, we couldn't find a good answer
            return {
                "answer": "Hare Krishna! I couldn't find a satisfactory answer to your question in the Bhagavad Gita. Please try rephrasing or asking about a different topic.",
                "sources": [],
                "confidence": 0.0
            }

        except Exception as e:
            logging.error(f"Error answering question: {str(e)}", exc_info=True)
            return {
                "answer": f"Hare Krishna! I encountered an error while processing your question: {str(e)}",
                "sources": [],
                "confidence": 0.0
            }

    def get_related_questions(self, question: str, limit: int = 5) -> List[Dict[str, str]]:
        """Get questions related to the user's query from the Q&A database."""
        question_lower = question.lower().strip()
        qa_pairs = get_qa_pairs()

        # Score each question based on word overlap
        scored_questions = []
        for qa in qa_pairs:
            q_words = set(qa["question"].lower().split())
            u_words = set(question_lower.split())
            score = len(q_words.intersection(u_words)) / max(1, len(u_words))
            if score > 0.2:  # Only include questions with some relevance
                scored_questions.append((score, qa))

        # Sort by score (highest first) and return top N
        scored_questions.sort(reverse=True, key=lambda x: x[0])
        return [{"question": qa["question"], "category": qa["category"]}
                for score, qa in scored_questions[:limit]]

    def get_questions_by_category(self, category: str) -> List[Dict[str, str]]:
        """Get all questions in a specific category."""
        return [{"question": qa["question"], "category": qa["category"]}
                for qa in get_qa_by_category(category)]

    def get_all_categories(self) -> List[str]:
        """Get all available question categories."""
        from gita_qa_pairs import CATEGORIES
        return CATEGORIES

    def get_system_info(self):
        """Provide information about the system's features and capabilities."""
        return {
            "answer": """Hare Krishna! I am a Bhagavad Gita Q&A assistant. Here's what I can help you with:
            
1. Answer questions about the Bhagavad Gita's teachings
2. Provide explanations of key philosophical concepts
3. Help you find specific verses and their meanings
4. Offer guidance based on Lord Krishna's teachings
5. Explain the context and background of the Gita
6. Help with character analysis of key figures like Arjuna and Krishna

You can ask me questions like:
- What is the main message of the Bhagavad Gita?
- What does the Gita say about karma?
- Explain the concept of dharma in the Gita
- Who are the main characters in the Bhagavad Gita?
- What is the significance of Chapter 2, Verse 47?""",
            "sources": [],
            "confidence": 1.0
        }

    def _check_for_verse_reference(self, question: str) -> Optional[Dict[str, Any]]:
        """Check if the question contains a verse reference and return the verse if found."""
        question_lower = question.lower()

        # Check for verse reference in various formats
        verse_patterns = [
            # Matches "verse 2.46", "verse 2:46", "verse 2, 46"
            r'verse[\s,:-]*(\d+)[\s,:.-]+(?:verse|v\.?|vs\.?)?\s*(\d+)',
            # Matches "2.46", "2:46", "2, 46"
            r'(?:^|\s)(\d+)[.:,-]\s*(\d+)(?:\s|$)',
            # Matches "chapter 2 verse 46"
            r'chapter\s+(\d+)\s+verse\s+(\d+)',
            # Matches "chapter two verse forty six" (basic word number support)
            r'chapter\s+(\w+)(?:\s+verse)?\s+(\w+)(?:\s+\w+)?(?:\s+\w+)?(?:\s+\w+)?',
        ]

        # Try to match verse references in the question
        chapter, verse = None, None
        for pattern in verse_patterns:
            match = re.search(pattern, question_lower)
            if match:
                # Handle word numbers (basic support for "one" to "ninety-nine")
                word_to_num = {
                    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
                    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
                    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
                    'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20,
                    'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
                    'eighty': 80, 'ninety': 90
                }

                try:
                    # Extract chapter and verse numbers
                    if len(match.groups()) >= 2:
                        # If using word numbers
                        if match.group(1).isalpha():
                            # Simple addition for numbers like "twenty one" (would need more sophisticated parsing for exact matches)
                            chapter = sum(word_to_num.get(word.lower(), 0)
                                          for word in match.group(1).split())
                            verse = sum(word_to_num.get(word.lower(), 0)
                                        for word in match.group(2).split())
                        else:
                            # Regular numeric match
                            chapter = int(match.group(1))
                            verse = int(match.group(2))

                        # Look up the verse
                        verse_data = self.get_verse(chapter, verse)
                        if verse_data:
                            return {
                                "answer": f"Hare Krishna! Here is verse {chapter}.{verse} from the Bhagavad Gita:\n\n{verse_data['text']}\n\n(Page {verse_data['page']})",
                                "sources": [{"page": verse_data['page'], "source": self.pdf_path}]
                            }
                except (ValueError, IndexError):
                    # If conversion to int fails or other parsing error, continue to next pattern
                    continue

        # If no verse reference was found, return None
        return None

    def _get_answer_from_pdf(self, question: str) -> Dict[str, Any]:
        """Generate an answer by searching the PDF content.
        
        This method will only return answers found within the PDF content.
        If no relevant information is found, it will return None to allow fallback to other methods.
        """
        try:
            # Note: Verse reference check is now handled in answer_question
            # Search through the PDF content with more relevant documents for better context
            relevant_docs = self.get_relevant_documents(question, k=5)  # Increased from 3 to 5 for better context
            
            if not relevant_docs:
                return None
                
            # Extract and combine content from multiple relevant documents
            combined_content = " ".join([doc.page_content for doc in relevant_docs[:3]])  # Use top 3 most relevant
            
            # Extract the best answer from the combined content
            answer = self.extract_best_answer(question, combined_content)
            
            # If the answer is too short or seems incomplete, try to find more context
            if len(answer) < 50 and len(relevant_docs) > 3:
                additional_content = " ".join([doc.page_content for doc in relevant_docs[3:6]])
                additional_answer = self.extract_best_answer(question, additional_content)
                if additional_answer:
                    answer = (answer + " " + additional_answer).strip()
            
            # If we still don't have a good answer, return None to allow fallback
            if not answer or len(answer) < 20:  # 20 characters minimum for a meaningful answer
                return None
                
            # Get the best source (from the most relevant document)
            best_source = relevant_docs[0].metadata
            
            # Calculate confidence based on answer length and source relevance
            confidence = min(0.9, 0.5 + (len(answer) / 500))  # Longer answers get higher confidence, capped at 0.9
            
            return {
                "answer": answer,
                "sources": [best_source],
                "confidence": confidence,
                "source_type": "pdf_content"
            }
            
            
        except Exception as e:
            logging.error(f"Error in _get_answer_from_pdf: {str(e)}", exc_info=True)
            return {
                "answer": f"Hare Krishna! I encountered an error while processing your question: {str(e)}",
                "sources": [],
                "confidence": 0.0
            }

# Initialize FastAPI app
app = FastAPI(title="Bhagavad Gita Q&A System")

# Initialize the QA system when the app starts
qa_system = None


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]


@app.on_event("startup")
async def startup_event():
    global qa_system
    pdf_path = "11-Bhagavad-gita_As_It_Is.pdf"
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at {pdf_path}")

    qa_system = QASystem(pdf_path)
    qa_system.load_and_process_pdf()
    print("PDF processing complete. Ready to answer questions!")


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(question: QuestionRequest):
    if not qa_system:
        raise HTTPException(status_code=503, detail="Service not initialized")

    print(f"Received question: {question.question}")
    response = qa_system.answer_question(question.question)
    return AnswerResponse(**response)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "pages_loaded": len(qa_system.documents) if qa_system else 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
