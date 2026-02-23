"""
Automatic Conversation Logger
Logs all Q&A interactions to markdown file
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ConversationLogger:
    """Automatically log all conversations to markdown file"""
    
    def __init__(self, log_file: str = "CONVERSATION_HISTORY.md"):
        self.log_file = Path(log_file)
        self._initialize_log_file()
    
    def _initialize_log_file(self) -> None:
        """Initialize the log file if it doesn't exist"""
        if not self.log_file.exists():
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("# Bhagavad Gita RAG - Conversation History\n\n")
                f.write(f"**Started**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")
    
    def log_conversation(
        self,
        question: str,
        answer: str,
        sources: list,
        confidence: Optional[float] = None,
        processing_time_ms: Optional[float] = None,
        metadata: Optional[dict] = None
    ) -> None:
        """
        Log a single conversation exchange
        
        Args:
            question: User's question
            answer: System's answer
            sources: List of source citations
            confidence: Confidence score
            processing_time_ms: Processing time
            metadata: Additional metadata
        """
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                # Write conversation header
                f.write(f"## Conversation - {timestamp}\n\n")
                
                # Write question
                f.write(f"### 🙋 Question\n")
                f.write(f"{question}\n\n")
                
                # Write answer
                f.write(f"### 💬 Answer\n")
                f.write(f"{answer}\n\n")
                
                # Write sources if available
                if sources:
                    f.write(f"### 📚 Sources ({len(sources)} found)\n\n")
                    for i, source in enumerate(sources, 1):
                        # Handle both dict and object sources
                        if isinstance(source, dict):
                            verse_ref = source.get('verse_reference', '')
                            page = source.get('page', '')
                            excerpt = source.get('excerpt', '')
                            score = source.get('similarity_score', 0)
                        else:
                            verse_ref = getattr(source, 'verse_reference', '')
                            page = getattr(source, 'page', '')
                            excerpt = getattr(source, 'excerpt', '')
                            score = getattr(source, 'similarity_score', 0)
                        
                        ref_text = verse_ref or f"Page {page}" if page else "Unknown"
                        f.write(f"{i}. **{ref_text}** (similarity: {score:.3f})\n")
                        if excerpt:
                            # Truncate long excerpts
                            excerpt_short = excerpt[:200] + "..." if len(excerpt) > 200 else excerpt
                            f.write(f"   > {excerpt_short}\n\n")
                
                # Write metadata
                f.write(f"### 📊 Metadata\n")
                if confidence is not None:
                    f.write(f"- **Confidence**: {confidence:.3f}\n")
                if processing_time_ms is not None:
                    f.write(f"- **Processing Time**: {processing_time_ms:.2f}ms\n")
                if metadata:
                    for key, value in metadata.items():
                        f.write(f"- **{key.replace('_', ' ').title()}**: {value}\n")
                
                f.write("\n---\n\n")
            
            logger.info(f"Logged conversation at {timestamp}")
            
        except Exception as e:
            logger.error(f"Error logging conversation: {e}")
    
    def log_error(self, question: str, error: str) -> None:
        """
        Log a failed conversation attempt
        
        Args:
            question: User's question
            error: Error message
        """
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"## ❌ Error - {timestamp}\n\n")
                f.write(f"### Question\n")
                f.write(f"{question}\n\n")
                f.write(f"### Error\n")
                f.write(f"```\n{error}\n```\n\n")
                f.write("---\n\n")
            
            logger.info(f"Logged error at {timestamp}")
            
        except Exception as e:
            logger.error(f"Error logging error: {e}")
    
    def add_session_marker(self, marker: str) -> None:
        """
        Add a session marker to the log
        
        Args:
            marker: Marker text (e.g., "System Restart", "New Session")
        """
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n## 🔄 {marker} - {timestamp}\n\n")
                f.write("---\n\n")
            
        except Exception as e:
            logger.error(f"Error adding session marker: {e}")
    
    def get_conversation_count(self) -> int:
        """Get total number of conversations logged"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Count conversation headers
                return content.count("## Conversation -")
        except Exception as e:
            logger.error(f"Error counting conversations: {e}")
            return 0
    
    def export_to_json(self, output_file: str = "conversations.json") -> None:
        """
        Export conversations to JSON format
        
        Args:
            output_file: Output JSON file path
        """
        # This is a placeholder - would need to parse the markdown
        # For now, just log that it was requested
        logger.info(f"JSON export requested to {output_file}")
        # TODO: Implement markdown parsing to JSON
