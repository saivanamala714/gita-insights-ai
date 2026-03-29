"""
Simple test script for RAG system
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config.settings import get_settings
from src.services.rag_orchestrator import RAGOrchestrator


async def test_rag():
    """Test the RAG system"""
    print("=" * 60)
    print("Testing Bhagavad Gita RAG System")
    print("=" * 60)
    
    # Get settings
    settings = get_settings()
    print(f"\nSettings:")
    print(f"  - Embedding Model: {settings.embedding_model_name}")
    print(f"  - LLM Provider: {settings.llm_provider}")
    print(f"  - Chunk Size: {settings.chunk_size}")
    print(f"  - Top K: {settings.vector_top_k}")
    
    # Initialize RAG
    print("\n" + "=" * 60)
    print("Initializing RAG Orchestrator...")
    print("=" * 60)
    rag = RAGOrchestrator(settings)
    
    # Try to load existing index
    print("\nAttempting to load existing index...")
    if rag.load_index():
        print("✓ Index loaded successfully")
    else:
        print("✗ No existing index found")
        print("\nIndexing PDF (this may take a few minutes)...")
        stats = rag.index_pdf()
        print(f"\n✓ Indexing complete:")
        print(f"  - Chunks created: {stats['chunks_created']}")
        print(f"  - Embeddings generated: {stats['embeddings_generated']}")
        print(f"  - Time: {stats['processing_time_ms']:.2f}ms")
    
    # Get stats
    print("\n" + "=" * 60)
    print("System Statistics")
    print("=" * 60)
    stats = rag.get_stats()
    for key, value in stats.items():
        print(f"  - {key}: {value}")
    
    # Test questions
    test_questions = [
        "What does Krishna say about duty?",
        "What is karma yoga?",
        "Who is Arjuna?",
        "What happens to the soul after death?",
    ]
    
    print("\n" + "=" * 60)
    print("Testing Questions")
    print("=" * 60)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n[Question {i}] {question}")
        print("-" * 60)
        
        try:
            response = rag.answer_question(question, top_k=3)
            
            print(f"\n[Answer]")
            print(response.answer)
            
            print(f"\n[Sources] ({len(response.sources)} found)")
            for j, source in enumerate(response.sources, 1):
                ref = source.verse_reference or f"Page {source.page}"
                score = source.similarity_score or 0
                print(f"  {j}. {ref} (score: {score:.3f})")
                print(f"     {source.excerpt[:100]}...")
            
            print(f"\n[Metadata]")
            print(f"  - Confidence: {response.confidence:.3f}")
            print(f"  - Processing time: {response.processing_time_ms:.2f}ms")
            
        except Exception as e:
            print(f"✗ Error: {e}")
        
        print()
    
    print("=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    # Check if OpenAI API key is set
    settings = get_settings()
    if settings.llm_provider == "openai" and not settings.openai_api_key:
        print("ERROR: OPENAI_API_KEY not set in environment")
        print("Please set it in .env file or environment variables")
        sys.exit(1)
    
    asyncio.run(test_rag())
