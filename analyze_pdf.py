import os
import re
from PyPDF2 import PdfReader
from typing import List, Dict, Tuple
import json

def extract_pdf_structure(pdf_path: str) -> Dict:
    """Extract the structure of the Bhagavad Gita PDF."""
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    # Extract text from first 50 pages to analyze structure
    sample_text = ""
    for page_num in range(min(50, total_pages)):
        sample_text += reader.pages[page_num].extract_text() + "\n\n"
    
    # Look for chapter and verse patterns
    chapter_pattern = re.compile(r'Chapter\s+(\d+)', re.IGNORECASE)
    verse_pattern = re.compile(r'(\d+)\.(\d+)')
    
    # Find all chapter headings
    chapters = []
    current_chapter = None
    
    for page_num in range(total_pages):
        page_text = reader.pages[page_num].extract_text()
        
        # Look for chapter headings
        chapter_match = chapter_pattern.search(page_text)
        if chapter_match:
            chapter_num = int(chapter_match.group(1))
            # Get the chapter title (next line after chapter number)
            lines = page_text.split('\n')
            for i, line in enumerate(lines):
                if chapter_match.group(0) in line:
                    title_line = lines[i+1].strip() if i+1 < len(lines) else ""
                    chapters.append({
                        'number': chapter_num,
                        'title': title_line,
                        'start_page': page_num + 1
                    })
                    break
    
    # Extract verses from each chapter
    for chapter in chapters:
        start_page = chapter['start_page'] - 1
        end_page = min(start_page + 20, total_pages)  # Look 20 pages ahead or until next chapter
        
        chapter_text = ""
        for page_num in range(start_page, end_page):
            chapter_text += reader.pages[page_num].extract_text() + "\n"
        
        # Find all verses in this chapter
        verses = []
        verse_matches = list(re.finditer(r'(\d+)\.(\d+)\s+(.*?)(?=\n\d+\.\d+|$)', 
                                       chapter_text, re.DOTALL))
        
        for match in verse_matches:
            verse_num = int(match.group(2))
            verse_text = match.group(3).strip()
            verses.append({
                'number': verse_num,
                'text': verse_text
            })
        
        chapter['verses'] = verses
        chapter['verse_count'] = len(verses)
    
    return {
        'total_pages': total_pages,
        'chapters': chapters,
        'total_verses': sum(len(c['verses']) for c in chapters)
    }

def save_analysis_to_json(structure: Dict, output_path: str):
    """Save the PDF structure analysis to a JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    pdf_path = "11-Bhagavad-gita_As_It_Is.pdf"
    output_path = "gita_structure.json"
    
    print(f"Analyzing PDF: {pdf_path}")
    structure = extract_pdf_structure(pdf_path)
    
    print(f"Found {len(structure['chapters'])} chapters and {structure['total_verses']} verses")
    
    save_analysis_to_json(structure, output_path)
    print(f"Analysis saved to {output_path}")
