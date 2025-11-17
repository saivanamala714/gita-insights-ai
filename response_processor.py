"""
Response Processor Module

This module provides functionality to check and correct grammatical errors in text responses
before they are sent to the client. It uses LanguageTool for grammar checking when available.
"""
import logging
from typing import Dict, Any, Optional
import os

# Try to import language_tool_python, but make it optional
try:
    import language_tool_python
    LANGUAGE_TOOL_AVAILABLE = True
except (ImportError, OSError) as e:
    LANGUAGE_TOOL_AVAILABLE = False
    logging.warning(f"LanguageTool not available: {e}")

class ResponseProcessor:
    """Processes API responses to ensure grammatical correctness."""
    
    def __init__(self):
        """Initialize the ResponseProcessor."""
        self.enabled = False
        self.tool = None
        
        # Only try to initialize LanguageTool if it's available
        if LANGUAGE_TOOL_AVAILABLE:
            try:
                # Try to use a local LanguageTool server if available
                if os.path.exists('/usr/local/Cellar/languagetool'):
                    self.tool = language_tool_python.LanguageTool(
                        'en-US',
                        config={
                            'cacheSize': 1000,
                            'pipelineCaching': True
                        }
                    )
                else:
                    # Fall back to the default (will download if needed)
                    self.tool = language_tool_python.LanguageTool('en-US')
                
                self.enabled = True
                logging.info("LanguageTool grammar checker initialized successfully.")
                
            except Exception as e:
                self.enabled = False
                logging.error(f"Failed to initialize LanguageTool: {e}")
                logging.warning("Grammar checking will be disabled. For better results, install Java 8+.")
        else:
            logging.info("LanguageTool not available. Grammar checking will be limited.")
    
    def process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the API response to correct any grammatical errors.
        
        Args:
            response: The API response dictionary containing 'answer' and 'sources' keys
            
        Returns:
            Dict[str, Any]: The processed response with corrected grammar if possible
        """
        if not self.enabled or 'answer' not in response:
            return response
            
        try:
            original_text = response['answer']
            
            # Only process if the answer is a string and not empty
            if not isinstance(original_text, str) or not original_text.strip():
                return response
                
            # Check and correct grammar
            matches = self.tool.check(original_text)
            if matches:
                corrected_text = language_tool_python.utils.correct(original_text, matches)
                
                # Only update if the correction is different from the original
                if corrected_text != original_text:
                    response['answer'] = corrected_text
                    # Add a note about the correction if not already present
                    if 'grammar_corrected' not in response.get('metadata', {}):
                        if 'metadata' not in response:
                            response['metadata'] = {}
                        response['metadata']['grammar_corrected'] = True
                        response['metadata']['original_answer'] = original_text
                    logging.debug("Grammar corrections applied to response.")
            
            return response
            
        except Exception as e:
            logging.error(f"Error processing response for grammar: {e}")
            # Return the original response if there's an error
            return response

# Global instance for easy importing
response_processor = ResponseProcessor()

def get_processor() -> ResponseProcessor:
    """Get the global response processor instance."""
    return response_processor
