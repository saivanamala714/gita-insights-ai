"""
Bhagavad Gita Character Database

This module contains a comprehensive list of characters from the Bhagavad Gita
along with their alternative names and aliases to help with character recognition.
"""
from typing import Dict, List, TypedDict


class CharacterInfo(TypedDict):
    """Structure to hold character information."""
    primary_name: str
    aliases: List[str]
    description: str
    role: str


# Main dictionary of characters with their information
CHARACTERS: Dict[str, CharacterInfo] = {
    # Divine Personalities
    "krishna": {
        "primary_name": "Krishna",
        "aliases": ["Krsna", "Govinda", "Madhava", "Hari", "Vasudeva", "Keshava", "Mukunda"],
        "description": "The Supreme Personality of Godhead, speaker of the Bhagavad Gita",
        "role": "Divine Charioteer and Spiritual Guide"
    },
    "arjuna": {
        "primary_name": "Arjuna",
        "aliases": ["Partha", "Dhananjaya", "Gudakesha", "Kaunteya", "Parantapa", "Bharata"],
        "description": "The mighty warrior prince and devotee of Lord Krishna",
        "role": "Main Disciple and Prince of Kuru Dynasty"
    },
    
    # Kuru Dynasty (Pandavas)
    "yudhishthira": {
        "primary_name": "Yudhishthira",
        "aliases": ["Dharmaraja", "Ajatashatru", "Bharata", "Pandava"],
        "description": "Eldest of the Pandava brothers, known for his righteousness",
        "role": "Righteous King and Pandava Prince"
    },
    "bhima": {
        "primary_name": "Bhima",
        "aliases": ["Vrikodara", "Bhimasena", "Jarasandha-jit"],
        "description": "Second Pandava brother, known for his immense strength",
        "role": "Mighty Warrior of the Pandavas"
    },
    "nakula": {
        "primary_name": "Nakula",
        "aliases": ["Madri-nandana"],
        "description": "One of the twin Pandava brothers, skilled in swordsmanship",
        "role": "Pandava Prince and Warrior"
    },
    "sahadeva": {
        "primary_name": "Sahadeva",
        "aliases": ["Madri-suta"],
        "description": "Youngest Pandava brother, known for his wisdom and knowledge",
        "role": "Pandava Prince and Strategist"
    },
    
    # Kuru Dynasty (Kauravas)
    "duryodhana": {
        "primary_name": "Duryodhana",
        "aliases": ["Suyodhana", "Kaurava"],
        "description": "Eldest Kaurava brother and main antagonist of the Mahabharata",
        "role": "Kaurava Prince and Rival to the Pandavas"
    },
    "dushasana": {
        "primary_name": "Dushasana",
        "aliases": [],
        "description": "Second Kaurava brother, known for dragging Draupadi",
        "role": "Kaurava Prince"
    },
    
    # Teachers and Sages
    "drona": {
        "primary_name": "Dronacharya",
        "aliases": ["Drona", "Dronacarya"],
        "description": "Teacher of both Pandavas and Kauravas in military arts",
        "role": "Royal Guru and Military Trainer"
    },
    "kripacharya": {
        "primary_name": "Kripacharya",
        "aliases": ["Kripa"],
        "description": "Teacher of the Kuru princes and a great warrior",
        "role": "Royal Priest and Teacher"
    },
    
    # Other Key Characters
    "bhishma": {
        "primary_name": "Bhishma",
        "aliases": ["Devavrata", "Gangeya", "Shantanu-nandana"],
        "description": "Grandsire of the Kuru dynasty, took a vow of celibacy",
        "role": "Elder Statesman and Commander of Kaurava Army"
    },
    "dhritharashtra": {
        "primary_name": "Dhritarashtra",
        "aliases": [],
        "description": "Blind king and father of the Kauravas",
        "role": "King of Hastinapura"
    },
    "vidura": {
        "primary_name": "Vidura",
        "aliases": ["Kshatri"],
        "description": "Half-brother to Dhritarashtra, known for his wisdom",
        "role": "Prime Minister and Advisor"
    },
    "sanjaya": {
        "primary_name": "Sanjaya",
        "aliases": [],
        "description": "Dhritarashtra's charioteer and minister, narrator of the Bhagavad Gita",
        "role": "Narrator and Advisor"
    },
    "karna": {
        "primary_name": "Karna",
        "aliases": ["Radheya", "Vaikartana", "Sutaputra"],
        "description": "Eldest son of Kunti, raised by a charioteer, ally of Duryodhana",
        "role": "Mighty Warrior and Kaurava Ally"
    },
    "drupada": {
        "primary_name": "Drupada",
        "aliases": ["Yajnasena"],
        "description": "King of Panchala, father of Draupadi and Dhrishtadyumna",
        "role": "Ally of the Pandavas"
    },
    "draupadi": {
        "primary_name": "Draupadi",
        "aliases": ["Krishnaa", "Panchali", "Yajnaseni"],
        "description": "Wife of the Pandavas, daughter of King Drupada",
        "role": "Queen of the Pandavas"
    },
    "shakuni": {
        "primary_name": "Shakuni",
        "aliases": ["Saubala"],
        "description": "Maternal uncle of Duryodhana, mastermind behind the dice game",
        "role": "Kaurava Advisor and Strategist"
    },
    
    # Divine Beings
    "indra": {
        "primary_name": "Indra",
        "aliases": ["Sakra", "Devaraja", "Purandara"],
        "description": "King of the Devas and father of Arjuna",
        "role": "Vedic Deity"
    },
    "surya": {
        "primary_name": "Surya",
        "aliases": ["Vivasvan", "Aditya"],
        "description": "Sun god and father of Karna",
        "role": "Solar Deity"
    },
    "yama": {
        "primary_name": "Yama",
        "aliases": ["Dharmaraja", "Mrityu"],
        "description": "God of death and justice, father of Yudhishthira",
        "role": "Deity of Death and Dharma"
    },
    "vayu": {
        "primary_name": "Vayu",
        "aliases": ["Pavana", "Matali"],
        "description": "God of wind and father of Bhima",
        "role": "Vedic Deity"
    },
    
    # Sages and Rishis
    "vyasa": {
        "primary_name": "Vyasa",
        "aliases": ["Vedavyasa", "Krishna Dvaipayana"],
        "description": "Compiler of the Vedas and author of the Mahabharata",
        "role": "Sage and Author"
    },
    "parashurama": {
        "primary_name": "Parashurama",
        "aliases": ["Bhargava", "Jamadagnya"],
        "description": "Sixth avatar of Vishnu, teacher of Bhishma, Drona, and Karna",
        "role": "Warrior Sage"
    },
    
    # Other Important Characters
    "abhimanyu": {
        "primary_name": "Abhimanyu",
        "aliases": ["Arjuni", "Subhadra-nandana"],
        "description": "Son of Arjuna and Subhadra, married to Uttara",
        "role": "Pandava Prince and Warrior"
    },
    "gandhari": {
        "primary_name": "Gandhari",
        "aliases": [],
        "description": "Wife of Dhritarashtra and mother of the Kauravas",
        "role": "Queen Mother of the Kauravas"
    },
    "kunti": {
        "primary_name": "Kunti",
        "aliases": ["Pritha"],
        "description": "Mother of the Pandavas (except Sahadeva and Nakula)",
        "role": "Mother of the Pandavas"
    },
    "madri": {
        "primary_name": "Madri",
        "aliases": [],
        "description": "Second wife of Pandu, mother of Nakula and Sahadeva",
        "role": "Mother of the Pandava Twins"
    }
}

def get_character_info(name: str) -> CharacterInfo:
    """
    Get information about a character by any of their names or aliases.
    
    Args:
        name: The name or alias of the character (case-insensitive)
        
    Returns:
        CharacterInfo if found, None otherwise
    """
    name_lower = name.lower()
    
    # Check primary names first
    for char_name, char_info in CHARACTERS.items():
        if char_name.lower() == name_lower or char_info["primary_name"].lower() == name_lower:
            return char_info
    
    # Check aliases
    for char_info in CHARACTERS.values():
        if any(alias.lower() == name_lower for alias in char_info["aliases"]):
            return char_info
    
    return None

def get_character_names() -> List[str]:
    """Get a list of all primary character names and aliases."""
    names = []
    for char_info in CHARACTERS.values():
        names.append(char_info["primary_name"])
        names.extend(char_info["aliases"])
    return names

def get_character_aliases(primary_name: str) -> List[str]:
    """
    Get all aliases for a character by their primary name.
    
    Args:
        primary_name: The primary name of the character (case-insensitive)
        
    Returns:
        List of aliases, or empty list if character not found
    """
    for char_info in CHARACTERS.values():
        if char_info["primary_name"].lower() == primary_name.lower():
            return char_info["aliases"]
    return []

if __name__ == "__main__":
    # Example usage
    print("Bhagavad Gita Character Database")
    print("-" * 30)
    print(f"Total characters: {len(CHARACTERS)}")
    print("\nSample character information for 'Krishna':")
    print(get_character_info("Krishna"))
