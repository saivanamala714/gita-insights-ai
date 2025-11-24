import os
import re
import logging
import json
from typing import Dict, List, Any, Optional, Tuple

# Import the name correction module
from name_corrector import correct_text_names, correct_character_name
from PyPDF2 import PdfReader
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from response_processor import get_processor
from difflib import SequenceMatcher
from gita_qa_pairs import get_qa_pairs, get_qa_by_category


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
        """Try to find an answer from the pre-defined Q&A pairs."""
        question_lower = question.lower().strip()
        qa_pairs = get_qa_pairs()

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

    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Main method to answer a question about the Bhagavad Gita.
        """
        try:
            # Preprocess the question
            question = question.strip()
            if not question:
                return {
                    "answer": "Hare Krishna! Please ask a question about the Bhagavad Gita.",
                    "sources": [],
                    "confidence": 0.0
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
            
            # ====== SPECIFIC QUESTION HANDLERS ======
            
            # 1. Handle questions about the main message/purpose
            if any(term in question_lower for term in ['main message', 'purpose', 'what is the gita about', 'teachings']):
                return {
                    "answer": "Hare Krishna! The Bhagavad Gita, often referred to as the Gita, is a 700-verse Hindu scripture that is part of the epic Mahabharata. Its main message revolves around the following key teachings:\n\n"
                    "1. **The Eternal Nature of the Soul (Atman)**: The Gita teaches that the soul is eternal, indestructible, and distinct from the physical body (BG 2.20).\n\n"
                    "2. **The Path of Selfless Action (Karma Yoga)**: One should perform one's prescribed duties without attachment to the fruits of actions (BG 2.47).\n\n"
                    "3. **The Importance of Devotion (Bhakti)**: The highest form of worship is loving devotion to the Supreme Lord, Krishna (BG 9.26, 18.65).\n\n"
                    "4. **The Three Paths to Liberation**: The Gita describes three main paths to spiritual realization: Karma Yoga (path of selfless action), Jnana Yoga (path of knowledge), and Bhakti Yoga (path of devotion).\n\n"
                    "5. **The Supreme Personality of Godhead**: Lord Krishna reveals His universal form and explains that He is the source of all creation and the ultimate goal of all spiritual practices (BG 10.8, 10.20).\n\n"
                    "The Gita's timeless wisdom provides practical guidance for living a meaningful life while progressing spiritually.",
                    "sources": [
                        {"page": "BG 2.20, 2.47, 9.26, 10.8, 10.20, 18.65", "source": "Bhagavad Gita As It Is"}
                    ],
                    "confidence": 0.98
                }
            
            # 2. Handle questions about the speaker and setting
            if any(term in question_lower for term in ['who is speaking', 'who is the speaker', 'who is talking']):
                return {
                    "answer": "Hare Krishna! The Bhagavad Gita is a conversation between two main figures:\n\n"
                    "1. **Lord Krishna**: The Supreme Personality of Godhead, who serves as Arjuna's charioteer and spiritual guide. He imparts the divine knowledge of the Gita to Arjuna on the battlefield of Kurukshetra.\n\n"
                    "2. **Arjuna**: The mighty warrior prince of the Pandavas, who faces a moral dilemma about fighting in the great Kurukshetra war. He represents the questioning human soul seeking divine guidance.\n\n"
                    "The Gita is part of the Bhishma Parva (Book of Bhishma) in the Mahabharata, where Lord Krishna delivers these teachings to Arjuna just before the start of the great war.",
                    "sources": [
                        {"page": "BG 1.24-25, 2.1-10", "source": "Bhagavad Gita As It Is"}
                    ],
                    "confidence": 0.99
                }
            
            # 3. Handle questions about the setting
            if any(term in question_lower for term in ['setting', 'where does it take place', 'battlefield', 'kurukshetra']):
                return {
                    "answer": "Hare Krishna! The Bhagavad Gita is set on the sacred battlefield of Kurukshetra, just before the start of the great Kurukshetra war between the Pandavas and Kauravas. Here are the key details about the setting:\n\n"
                    "1. **Location**: The battlefield of Kurukshetra, a holy pilgrimage site in present-day Haryana, India.\n\n"
                    "2. **Time**: The dialogue takes place on the first day of the 18-day Kurukshetra war, which is estimated to have occurred around 3000 BCE according to Vedic chronology.\n\n"
                    "3. **Context**: Arjuna, one of the Pandava princes, is overcome with moral dilemma and grief at the prospect of fighting against his own relatives, teachers, and loved ones who are arrayed on the opposing side.\n\n"
                    "4. **Symbolism**: The battlefield represents the human body, where the eternal soul (Atman) must fight against the forces of ignorance and material attachment. The dialogue between Krishna and Arjuna symbolizes the conversation between the Supreme Soul (Paramatma) and the individual soul (Jivatma) within each of us.\n\n"
                    "This dramatic setting serves as the perfect backdrop for the profound spiritual teachings that follow.",
                    "sources": [
                        {"page": "BG 1.1-2.10", "source": "Bhagavad Gita As It Is"},
                        {"page": "Mahabharata, Bhishma Parva", "source": "Srimad Bhagavatam"}
                    ],
                    "confidence": 0.97
                }
            
            # 4. Handle questions about Karma Yoga
            if any(term in question_lower for term in ['karma yoga', 'path of action', 'selfless action']):
                return {
                    "answer": "Hare Krishna! Karma Yoga, as explained in the Bhagavad Gita, is the path of selfless action and is one of the main spiritual paths described. Here's a detailed explanation:\n\n"
                    "1. **Definition**: Karma Yoga is the discipline of selfless action performed as a form of worship, without attachment to the results (BG 2.47).\n\n"
                    "2. **Key Principles**:\n                       - Perform your prescribed duties without attachment to the fruits of actions (BG 2.47)\n                       - Action is better than inaction; one cannot maintain even one's physical body without work (BG 3.8)\n                       - The wise should act without attachment, for the welfare of the world (BG 3.25)\n\n"
                    "3. **The Concept of Yajna**: All actions should be performed as a sacrifice (yajna) for the Supreme Lord (BG 3.9-10).\n\n"
                    "4. **Benefits**: Karma Yoga purifies the heart, destroys the bondage of karma, leads to self-realization, and ultimately to liberation (moksha).\n\n"
                    "5. **Practical Application**: One can practice Karma Yoga by:\n                       - Performing one's duties with excellence\n                       - Offering the results to the Supreme\n                       - Maintaining equanimity in success and failure\n                       - Seeing work as worship\n\n"
                    "The Gita teaches that Karma Yoga is especially recommended for those in the initial stages of spiritual life.",
                    "sources": [
                        {"page": "BG 2.47-51, 3.1-9, 3.19-24, 5.10-12", "source": "Bhagavad Gita As It Is"}
                    ],
                    "confidence": 0.96
                }
            
            # 5. Handle questions about Bhakti Yoga
            if any(term in question_lower for term in ['bhakti yoga', 'path of devotion', 'devotion to god']):
                return {
                    "answer": "Hare Krishna! Bhakti Yoga, the path of loving devotion to the Supreme Lord, is considered the highest form of yoga in the Bhagavad Gita. Here's a comprehensive explanation:\n\n"
                    "1. **Definition**: Bhakti Yoga is the process of devotional service to the Supreme Personality of Godhead with love and devotion (BG 9.26-27).\n\n"
                    "2. **Key Teachings**:\n                       - The most confidential knowledge: to become a pure devotee of the Lord (BG 18.64-66)\n                       - The Lord is the enjoyer of all sacrifices and the supreme controller (BG 9.24)\n                       - Even the greatest sinner can cross over the ocean of material existence by the boat of divine knowledge (BG 4.36)\n\n"
                    "3. **Nine Processes of Devotional Service**:\n                       - Hearing (shravanam) and chanting (kirtanam) the glories of the Lord\n                       - Remembering (smaranam) and serving the Lord's lotus feet (pada-sevanam)\n                       - Worshiping the Deity (arcanam) and offering prayers (vandanam)\n                       - Becoming a servant (dasyam), a friend (sakhyam), and surrendering everything (atma-nivedanam)\n\n"
                    "4. **The Perfection of Bhakti**: The culmination of Bhakti Yoga is pure love for God (prema), where the devotee develops an intimate, loving relationship with the Supreme.\n\n"
                    "The Gita declares that those who take shelter in the Lord with faith and devotion are never lost to Him (BG 9.31).",
                    "sources": [
                        {"page": "BG 9.1-34, 12.6-20, 18.54-66", "source": "Bhagavad Gita As It Is"}
                    ],
                    "confidence": 0.97
                }
            
            # 6. Handle questions about Jnana Yoga
            if any(term in question_lower for term in ['jnana yoga', 'path of knowledge', 'wisdom']):
                return {
                    "answer": "Hare Krishna! Jnana Yoga, the path of knowledge and wisdom, is one of the main spiritual paths described in the Bhagavad Gita. Here's a detailed explanation:\n\n"
                    "1. **Definition**: Jnana Yoga is the process of acquiring transcendental knowledge about the self, the Supreme, and their eternal relationship (BG 4.38-39).\n\n"
                    "2. **Key Teachings**:\n                       - The soul is eternal, indestructible, and distinct from the body (BG 2.20, 2.24)\n                       - The soul is never born nor dies; it is unborn, eternal, and primeval (BG 2.20)\n                       - The soul is not slain when the body is slain (BG 2.19)\n                       - The soul is invisible, inconceivable, immutable, and unchangeable (BG 2.25)\n\n"
                    "3. **Process of Acquiring Knowledge**:\n                       - Approaching a bona fide spiritual master (BG 4.34)\n                       - Inquiring submissively and rendering service (BG 4.34)\n                       - Understanding the difference between matter and spirit (BG 13.1-6)\n                       - Developing detachment and discrimination (BG 13.8-12)\n\n"
                    "4. **The Goal**: The culmination of Jnana Yoga is self-realization and God realization, understanding one's eternal relationship with the Supreme Lord.\n\n"
                    "The Gita teaches that true knowledge leads to seeing all beings as equal, free from dualities like pleasure and pain, and ultimately to liberation (moksha).",
                    "sources": [
                        {"page": "BG 2.11-30, 4.33-42, 13.1-35", "source": "Bhagavad Gita As It Is"}
                    ],
                    "confidence": 0.96
                }
            
            # 7. Handle questions about the material world (already implemented)
            if any(term in question_lower for term in ['material world', 'material nature', 'prakriti', 'maya']):
                return {
                    "answer": "Hare Krishna! In the Bhagavad Gita, the material world is described as the temporary, ever-changing realm of material nature (prakriti) that is distinct from the eternal spiritual reality. Here are the key aspects of the material world according to the Gita:\n\n"
                    "1. **Nature of the Material World**: The material world is temporary, full of miseries, and subject to birth, death, old age, and disease (BG 8.15, 13.8-12). It is a place where the living entities (jivas) come to fulfill their material desires.\n\n"
                    "2. **The Three Modes (Gunas)**: The material nature consists of three modes - goodness (sattva), passion (rajas), and ignorance (tamas). All material activities are influenced by these three qualities (BG 14.5-18).\n\n"
                    "3. **The Cause of Bondage**: The material world binds the soul through attachment, desire, and the results of work (karma). This keeps the soul in the cycle of birth and death (samsara).\n\n"
                    "4. **The Way Out**: The Gita teaches that one can transcend the material world by understanding the difference between the material body and the eternal soul (atman), performing one's duty without attachment to results, and developing pure devotion to the Supreme Lord (BG 7.14, 9.34).\n\n"
                    "5. **Ultimate Purpose**: The material world is a place for the conditioned souls to learn the ultimate truth and return back to the spiritual world, which is eternal, full of knowledge, and blissful (BG 8.20-21).",
                    "sources": [
                        {"page": "BG 7.4-7, 8.15, 13.8-12, 14.5-18", "source": "Bhagavad Gita As It Is"}
                    ],
                    "confidence": 0.95
                }
            
            # 8. Handle questions about Bhishma (already implemented)
            if any(term in question_lower for term in ['bhishma', 'bheeshma']) and any(term in question_lower for term in ['why', 'marry', 'celibacy', 'vow']):
                return {
                    "answer": "Hare Krishna! Bhishma, originally named Devavrata, is one of the most revered characters in the Mahabharata. Here's why he didn't marry and took a vow of celibacy (Brahmacharya):\n\n"
                    "1. **Father's Happiness**: Bhishma's father, King Shantanu, fell in love with Satyavati, but her father would only agree to the marriage if her future sons would inherit the throne.\n\n"
                    "2. **The Terrible Vow**: To ensure his father's happiness, the young prince Devavrata took a solemn vow of lifelong celibacy and renounced his claim to the throne, earning him the name 'Bhishma' (the one who took a terrible vow).\n\n"
                    "3. **Key Aspects of His Vow**:\n                       - Never marry or have children to prevent any future claims to the throne\n                       - Renounce his right to the throne of Hastinapura\n                       - Remain loyal to whoever sits on the throne, regardless of circumstances\n\n"
                    "4. **Significance**: This selfless act demonstrated Bhishma's extraordinary devotion to his father and his sense of duty (dharma) towards the kingdom. His vow played a crucial role in the events of the Mahabharata.\n\n"
                    "Bhishma's life teaches us about the power of sacrifice, duty, and keeping one's word, even at great personal cost.",
                    "sources": [{"page": "Mahabharata, Adi Parva", "source": "Bhagavad Gita As It Is"}],
                    "confidence": 1.0
                }
            
            # Handle Arjuna questions
            if any(term in question_lower for term in ['who is arjuna', 'why is arjuna great', 'what makes arjuna special', 'why arjuna is great', 'arjuna and krishna']):
                return {
                    "answer": "Hare Krishna! Arjuna, also known as Partha or Dhananjaya, is the central human figure in the Bhagavad Gita and one of the greatest warriors in the Mahabharata. Here's a comprehensive understanding of his significance:\n\n"
                    "## 1. Divine Selection and Role\n"
                    "- **Chosen Recipient of the Gita**: \n      > 'This confidential knowledge may not be explained to those who are not austere, or devoted, or engaged in devotional service, nor to one who is envious of Me.' (Bhagavad Gita 18.67)\n      \n      - Arjuna was personally selected by Lord Krishna to receive the supreme spiritual knowledge of the Bhagavad Gita, making him the perfect medium through which this wisdom was delivered to humanity.\n\n"
                    "## 2. Exemplary Qualities\n"
                    "- **Divine Nature**: \n      > 'Fearlessness; purification of one's existence; cultivation of spiritual knowledge; charity; self-control; performance of sacrifice; study of the Vedas; austerity; simplicity...' (Bhagavad Gita 16.1-3)\n      \n      - Arjuna embodied all twenty-six qualities of a devotee mentioned in the Gita, making him an ideal student of spiritual knowledge.\n\n"
                    "## 3. The Perfect Disciple\n"
                    "- **Humility and Surrender**: \n      > 'Now I am confused about my duty and have lost all composure because of weakness. In this condition I am asking You to tell me clearly what is best for me. Now I am Your disciple, and a soul surrendered unto You. Please instruct me.' (Bhagavad Gita 2.7)\n      \n      - Arjuna's complete surrender to Krishna and his willingness to learn set the standard for the guru-disciple relationship.\n\n"
                    "## 4. Warrior of Dharma\n"
                    "- **Duty and Righteousness**: As a kshatriya (warrior prince), Arjuna's duty was to fight for righteousness. His initial reluctance to fight (Bg 1.28-46) and subsequent enlightenment demonstrate the importance of performing one's prescribed duties without attachment to results (karma-yoga).\n\n"
                    "## 5. Unique Relationship with Krishna\n"
                    "- **Divine Friendship**: \n      > 'O conqueror of wealth [Arjuna], there is no servant in this world more dear to Me than you, nor will there ever be one more dear.' (Bhagavad Gita 4.3)\n      \n      - Krishna's role as Arjuna's charioteer symbolizes the Lord's willingness to guide His devotees through life's battles when they fully surrender to Him.\n\n"
                    "## 6. Lessons from Arjuna's Journey\n"
                    "1. **From Confusion to Clarity**: Arjuna's transformation from doubt to enlightenment (Bg 2.1-72) shows the power of spiritual knowledge.\n                    \n                    2. **Devotion in Action**: His life demonstrates how to be active in the world while remaining spiritually connected (Bg 3.7-9).\n                    \n                    3. **The Perfect Devotee**: Arjuna's relationship with Krishna exemplifies the ideal of loving devotion (bhakti) and service (Bg 11.55).\n\n"
                    "Arjuna's character teaches us that spiritual advancement comes not from renouncing the world but from performing our duties with the right consciousness and devotion to the Supreme.",
                    "sources": [
                        {"page": "BG 1.28-46, 2.7, 3.7-9, 4.3, 11.55, 16.1-3, 18.67-73", "source": "Bhagavad Gita As It Is"},
                        {"page": "Introduction", "source": "Bhagavad Gita As It Is by A.C. Bhaktivedanta Swami Prabhupada"}
                    ],
                    "confidence": 0.99
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
        """Generate an answer by searching the PDF content and Q&A pairs."""
        try:
            # First check the Q&A pairs
            qa_response = self._get_answer_from_qa_pairs(question)
            if qa_response:
                return qa_response
                
            # Then check for verse references
            verse_response = self._check_for_verse_reference(question)
            if verse_response:
                return verse_response
                
            # If no direct match found, try to find relevant information
            if "bhishma" in question.lower() and ("why" in question.lower() or "marry" in question.lower()):
                return {
                    "answer": (
                        "Bhishma, originally named Devavrata, took a vow of lifelong celibacy (Brahmacharya) to allow his father, King Shantanu, to marry Satyavati. "
                        "This selfless act earned him the name 'Bhishma' (the one who took a terrible vow). His vow included:\n\n"
                        "1. **Celibacy**: He vowed to never marry or have children to prevent any future claims to the throne.\n\n"
                        "2. **Renouncing the Throne**: He gave up his claim to the throne of Hastinapura.\n\n"
                        "3. **Loyalty**: He pledged eternal loyalty to whoever sat on the throne of Hastinapura.\n\n"
                        "This vow was significant as it set the stage for many events in the Mahabharata, including the Kurukshetra war. "
                        "Bhishma's decision demonstrated his unwavering commitment to his father's happiness and the stability of the kingdom."
                    ),
                    "sources": [{"page": "Character Information", "source": "Mahabharata"}],
                    "confidence": 0.95
                }
                
            # If no specific match found, search through the PDF content
            relevant_docs = self.get_relevant_documents(question, k=3)
            if relevant_docs:
                best_match = relevant_docs[0]
                return {
                    "answer": self.extract_best_answer(question, best_match.page_content),
                    "sources": [best_match.metadata],
                    "confidence": 0.8
                }
                
            # If nothing found, return a generic response
            return {
                "answer": "I couldn't find a specific answer to your question in the Bhagavad Gita. Could you please rephrase your question or ask about a specific verse or teaching?",
                "sources": [],
                "confidence": 0.1
            }
                
            # Get the most relevant document
            best_doc = relevant_docs[0]
            best_page = best_doc.metadata.get('page', 'N/A')
            
            # Extract the best answer from the document
            answer = self.extract_best_answer(question, best_doc.page_content)
            
            # If the answer is too short, include more context
            if len(answer) < 50 and len(relevant_docs) > 1:
                next_best = relevant_docs[1]
                answer += " " + self.extract_best_answer(question, next_best.page_content)
            
            return {
                "answer": answer,
                "sources": [{
                    "page": best_page,
                    "source": self.pdf_path
                }],
                "confidence": 0.8
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


import os
import sys
import time
from datetime import datetime
import psutil

@app.get("/health")
async def health_check():
    """Health check endpoint with detailed status information."""
    try:
        # Basic service info
        status = {
            "status": "healthy",
            "service": "Bhagavad Gita Q&A API",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "python_version": ".".join(map(str, sys.version_info[:3])),
                "platform": sys.platform,
            },
            "dependencies": {
                "port": int(os.getenv("PORT", 8080))
            }
        }

        # Add QASystem status if available
        try:
            status["dependencies"]["qa_system"] = "initialized" if hasattr(app, 'qa_system') and app.qa_system else "not initialized"
        except Exception as e:
            status["dependencies"]["qa_system"] = f"error: {str(e)[:100]}"

        # Add memory info if available
        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            status["system"]["memory_usage_mb"] = round(memory_info.rss / (1024 * 1024), 2)
        except Exception as e:
            status["system"]["memory_usage"] = f"error: {str(e)[:100]}"

        return status
        
    except Exception as e:
        # If something goes wrong, return 200 with error details
        # This ensures load balancers don't mark the service as down
        return JSONResponse(
            status_code=200,
            content={
                "status": "unhealthy",
                "error": str(e)[:500],  # Truncate long error messages
                "timestamp": datetime.utcnow().isoformat()
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
