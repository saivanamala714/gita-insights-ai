#!/usr/bin/env python3
"""
Local Embedding Generation Script
Run this script locally to pre-generate embeddings before deployment.
This avoids the need to generate embeddings on the server every time.

Usage:
    python generate_embeddings_local.py
"""

import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Generate embeddings locally and save to vector store"""
    try:
        # Import required services
        from src.services.document_processor import DocumentProcessor
        from src.services.embeddings import EmbeddingService
        from src.services.vector_store import VectorStore
        from src.config.settings import get_settings
        
        settings = get_settings()
        
        logger.info("=" * 60)
        logger.info("Starting Local Embedding Generation")
        logger.info("=" * 60)
        
        # Check if vector store already exists
        vector_store_path = settings.full_vector_store_path
        if vector_store_path.exists():
            response = input(f"\nVector store already exists at {vector_store_path}.\nDo you want to regenerate? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                logger.info("Skipping regeneration. Exiting.")
                return
            logger.info("Regenerating vector store...")
        
        # Initialize services
        logger.info("Initializing services...")
        doc_processor = DocumentProcessor(settings)
        embedding_service = EmbeddingService(settings)
        vector_store = VectorStore(settings)
        
        # Process PDF
        logger.info(f"Processing PDF: {settings.pdf_path}")
        chunks = doc_processor.process_pdf(settings.pdf_path)
        logger.info(f"Created {len(chunks)} chunks from PDF")
        
        # Generate embeddings
        logger.info("Generating embeddings (this may take several minutes)...")
        texts = [chunk.text for chunk in chunks]
        embeddings = embedding_service.embed_texts(texts, show_progress=True)
        logger.info(f"Generated embeddings with shape: {embeddings.shape}")
        
        # Initialize and populate vector store
        logger.info("Building vector store...")
        dimension = embedding_service.get_embedding_dimension()
        vector_store.initialize(dimension)
        vector_store.add_documents(chunks, embeddings)
        
        # Save vector store
        logger.info(f"Saving vector store to {vector_store_path}...")
        vector_store.save()
        
        # Display statistics
        stats = vector_store.get_stats()
        logger.info("=" * 60)
        logger.info("Embedding Generation Complete!")
        logger.info("=" * 60)
        logger.info(f"Total chunks: {stats['total_chunks']}")
        logger.info(f"Embedding dimension: {stats['dimension']}")
        logger.info(f"Vector store location: {vector_store_path}")
        logger.info(f"Index file size: {(vector_store_path / 'index.faiss').stat().st_size / 1024 / 1024:.2f} MB")
        logger.info(f"Metadata file size: {(vector_store_path / 'metadata.pkl').stat().st_size / 1024 / 1024:.2f} MB")
        logger.info("=" * 60)
        logger.info("\nYou can now deploy your application with pre-generated embeddings!")
        logger.info("The vector store will be included in your Docker image.")
        
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
