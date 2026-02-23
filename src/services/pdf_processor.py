"""
PDF Processing Service using PyMuPDF (fitz)
Extracts text with metadata preservation for Bhagavad Gita
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class PDFDocument:
    """Represents a processed PDF document with metadata"""
    
    def __init__(self, text: str, page: int, metadata: Optional[Dict] = None):
        self.text = text
        self.page = page
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "text": self.text,
            "page": self.page,
            "metadata": self.metadata
        }


class PDFProcessor:
    """Process PDF files and extract structured text with metadata"""
    
    def __init__(self):
        self.verse_pattern = re.compile(r'(?:Bg\.?\s*)?(\d+)\.(\d+)')
        self.chapter_pattern = re.compile(r'Chapter\s+(\d+)', re.IGNORECASE)
    
    def extract_text_from_pdf(self, pdf_path: Path) -> List[PDFDocument]:
        """
        Extract text from PDF with page-level granularity
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of PDFDocument objects
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        logger.info(f"Opening PDF: {pdf_path}")
        documents = []
        
        try:
            with fitz.open(pdf_path) as pdf:
                total_pages = len(pdf)
                logger.info(f"Processing {total_pages} pages")
                
                for page_num in range(total_pages):
                    page = pdf[page_num]
                    text = page.get_text("text")
                    
                    # Skip empty or very short pages
                    if not text or len(text.strip()) < 50:
                        continue
                    
                    # Clean the text
                    cleaned_text = self._clean_text(text)
                    
                    # Extract metadata
                    metadata = self._extract_metadata(cleaned_text, page_num + 1)
                    
                    documents.append(PDFDocument(
                        text=cleaned_text,
                        page=page_num + 1,
                        metadata=metadata
                    ))
                
                logger.info(f"Extracted {len(documents)} pages with content")
                return documents
                
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text
        
        Args:
            text: Raw text from PDF
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers (standalone numbers)
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        
        # Remove common headers/footers
        text = re.sub(r'Bhagavad-gītā As It Is\s+\d+', '', text)
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def _extract_metadata(self, text: str, page_num: int) -> Dict:
        """
        Extract metadata from text (chapter, verse references)
        
        Args:
            text: Cleaned text
            page_num: Page number
            
        Returns:
            Metadata dictionary
        """
        metadata = {"page": page_num}
        
        # Extract chapter number
        chapter_match = self.chapter_pattern.search(text)
        if chapter_match:
            metadata["chapter"] = int(chapter_match.group(1))
        
        # Extract verse references
        verse_matches = self.verse_pattern.findall(text)
        if verse_matches:
            verses = []
            for chapter, verse in verse_matches:
                verses.append(f"Bg {chapter}.{verse}")
            metadata["verses"] = verses[:5]  # Keep first 5 verse references
            
            # Set primary verse if found
            if verse_matches:
                metadata["chapter"] = int(verse_matches[0][0])
                metadata["verse"] = int(verse_matches[0][1])
        
        return metadata
    
    def extract_verse(self, pdf_path: Path, chapter: int, verse: int) -> Optional[str]:
        """
        Extract a specific verse from the PDF
        
        Args:
            pdf_path: Path to PDF file
            chapter: Chapter number
            verse: Verse number
            
        Returns:
            Verse text if found, None otherwise
        """
        documents = self.extract_text_from_pdf(pdf_path)
        
        verse_ref = f"Bg {chapter}.{verse}"
        verse_pattern = re.compile(rf'(?:Bg\.?\s*)?{chapter}\.{verse}')
        
        for doc in documents:
            if verse_pattern.search(doc.text):
                # Extract surrounding context
                return self._extract_verse_context(doc.text, chapter, verse)
        
        return None
    
    def _extract_verse_context(self, text: str, chapter: int, verse: int) -> str:
        """
        Extract verse with surrounding context
        
        Args:
            text: Text containing the verse
            chapter: Chapter number
            verse: Verse number
            
        Returns:
            Verse text with context
        """
        # Find the verse reference
        pattern = re.compile(rf'(?:Bg\.?\s*)?{chapter}\.{verse}[^\d]')
        match = pattern.search(text)
        
        if not match:
            return text
        
        # Extract ~500 characters around the verse
        start = max(0, match.start() - 200)
        end = min(len(text), match.end() + 300)
        
        return text[start:end].strip()
