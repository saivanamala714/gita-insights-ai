"""
Text Chunking Service
Implements semantic chunking with verse boundary preservation
"""

import logging
import re
from typing import Dict, List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..config.settings import Settings, get_settings

logger = logging.getLogger(__name__)


class Chunk:
    """Represents a text chunk with metadata"""
    
    def __init__(self, text: str, metadata: Dict):
        self.text = text
        self.metadata = metadata
        self.chunk_id = f"{metadata.get('page', 0)}_{metadata.get('chunk_index', 0)}"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "text": self.text,
            "metadata": self.metadata,
            "chunk_id": self.chunk_id
        }


class TextChunker:
    """Chunk text while preserving semantic boundaries"""
    
    def __init__(self, settings: Settings = None):
        self.settings = settings or get_settings()
        self.verse_pattern = re.compile(r'(?:Bg\.?\s*)?(\d+)\.(\d+)')
        
        # Initialize text splitter
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            length_function=len,
            separators=[
                "\n\n",  # Paragraph breaks
                "\n",    # Line breaks
                ". ",    # Sentences
                "! ",
                "? ",
                "; ",
                ", ",
                " ",     # Words
                ""       # Characters
            ]
        )
    
    def chunk_documents(self, documents: List) -> List[Chunk]:
        """
        Chunk a list of PDF documents
        
        Args:
            documents: List of PDFDocument objects
            
        Returns:
            List of Chunk objects
        """
        all_chunks = []
        
        for doc in documents:
            chunks = self._chunk_single_document(doc)
            all_chunks.extend(chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks
    
    def _chunk_single_document(self, document) -> List[Chunk]:
        """
        Chunk a single document
        
        Args:
            document: PDFDocument object
            
        Returns:
            List of Chunk objects
        """
        # Check if document is verse-based (has verse references)
        has_verses = bool(self.verse_pattern.search(document.text))
        
        if has_verses:
            # Use verse-aware chunking
            return self._chunk_with_verse_preservation(document)
        else:
            # Use standard semantic chunking
            return self._chunk_standard(document)
    
    def _chunk_standard(self, document) -> List[Chunk]:
        """
        Standard semantic chunking
        
        Args:
            document: PDFDocument object
            
        Returns:
            List of Chunk objects
        """
        text_chunks = self.splitter.split_text(document.text)
        
        chunks = []
        for idx, text in enumerate(text_chunks):
            metadata = {
                **document.metadata,
                "chunk_index": idx,
                "total_chunks": len(text_chunks),
                "chunk_type": "standard"
            }
            chunks.append(Chunk(text=text, metadata=metadata))
        
        return chunks
    
    def _chunk_with_verse_preservation(self, document) -> List[Chunk]:
        """
        Chunk while preserving verse boundaries
        
        Args:
            document: PDFDocument object
            
        Returns:
            List of Chunk objects
        """
        # Split by verses first
        verse_sections = self._split_by_verses(document.text)
        
        chunks = []
        chunk_index = 0
        
        for verse_ref, verse_text in verse_sections:
            # If verse text is too long, split it
            if len(verse_text) > self.settings.chunk_size * 1.5:
                text_chunks = self.splitter.split_text(verse_text)
            else:
                text_chunks = [verse_text]
            
            for text in text_chunks:
                metadata = {
                    **document.metadata,
                    "chunk_index": chunk_index,
                    "chunk_type": "verse_aware",
                    "verse_reference": verse_ref
                }
                
                # Extract chapter and verse from reference
                match = self.verse_pattern.search(verse_ref)
                if match:
                    metadata["chapter"] = int(match.group(1))
                    metadata["verse"] = int(match.group(2))
                
                chunks.append(Chunk(text=text, metadata=metadata))
                chunk_index += 1
        
        return chunks
    
    def _split_by_verses(self, text: str) -> List[tuple]:
        """
        Split text by verse references
        
        Args:
            text: Text to split
            
        Returns:
            List of (verse_reference, text) tuples
        """
        sections = []
        matches = list(self.verse_pattern.finditer(text))
        
        if not matches:
            return [("unknown", text)]
        
        for i, match in enumerate(matches):
            verse_ref = f"Bg {match.group(1)}.{match.group(2)}"
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            
            verse_text = text[start:end].strip()
            if verse_text:
                sections.append((verse_ref, verse_text))
        
        # Handle text before first verse
        if matches[0].start() > 0:
            pre_text = text[:matches[0].start()].strip()
            if pre_text:
                sections.insert(0, ("intro", pre_text))
        
        return sections
    
    def merge_small_chunks(self, chunks: List[Chunk], min_size: int = 100) -> List[Chunk]:
        """
        Merge chunks that are too small
        
        Args:
            chunks: List of chunks
            min_size: Minimum chunk size
            
        Returns:
            List of merged chunks
        """
        if not chunks:
            return []
        
        merged = []
        current_chunk = None
        
        for chunk in chunks:
            if current_chunk is None:
                current_chunk = chunk
            elif len(current_chunk.text) < min_size:
                # Merge with current
                current_chunk.text += " " + chunk.text
                current_chunk.metadata["merged"] = True
            else:
                merged.append(current_chunk)
                current_chunk = chunk
        
        if current_chunk:
            merged.append(current_chunk)
        
        logger.info(f"Merged {len(chunks)} chunks into {len(merged)} chunks")
        return merged
