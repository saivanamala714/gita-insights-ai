"""
Configuration settings for the RAG system
Uses pydantic-settings for environment variable management
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    app_name: str = "Bhagavad Gita RAG API"
    app_version: str = "2.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8080
    
    # Paths
    project_root: Path = Path(__file__).parent.parent.parent
    pdf_path: str = "11-Bhagavad-gita_As_It_Is.pdf"
    vector_store_path: str = "data/vector_store"
    logs_path: str = "logs"
    
    # Embedding Model
    embedding_model_name: str = "BAAI/bge-base-en-v1.5"
    embedding_dimension: int = 768  # bge-base-en-v1.5 dimension
    embedding_batch_size: int = 32
    
    # Chunking
    chunk_size: int = 1200
    chunk_overlap: int = 200
    
    # Vector Store (FAISS)
    vector_top_k: int = 5
    similarity_threshold: float = 0.7
    use_mmr: bool = True
    mmr_diversity_score: float = 0.3
    
    # LLM Settings
    llm_provider: str = "openai"  # "openai" or "ollama"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.1
    openai_max_tokens: int = 1000
    
    # Ollama settings (if using local LLM)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    
    # RAG Settings
    max_context_length: int = 4000  # characters
    include_sources: bool = True
    min_sources: int = 1
    max_sources: int = 5
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # "json" or "text"
    
    # CORS
    cors_origins: list[str] = [
        "https://mysupernews.web.app",
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def full_pdf_path(self) -> Path:
        """Get full path to PDF file"""
        return self.project_root / self.pdf_path
    
    @property
    def full_vector_store_path(self) -> Path:
        """Get full path to vector store directory"""
        return self.project_root / self.vector_store_path
    
    @property
    def full_logs_path(self) -> Path:
        """Get full path to logs directory"""
        return self.project_root / self.logs_path


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
