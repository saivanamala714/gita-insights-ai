"""Firestore configuration and initialization."""
import os
from google.cloud import firestore
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class FirestoreConfig:
    """Firestore configuration manager."""
    
    def __init__(self):
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        self.database_id = os.getenv('FIRESTORE_DATABASE_ID', '(default)')
        self.collection_prefix = os.getenv('FIRESTORE_COLLECTION_PREFIX', 'prod')
        self._client: Optional[firestore.Client] = None
    
    @property
    def client(self) -> firestore.Client:
        """Get or create Firestore client."""
        if self._client is None:
            try:
                self._client = firestore.Client(
                    project=self.project_id,
                    database=self.database_id
                )
                logger.info(f"Firestore client initialized for project: {self.project_id}")
            except Exception as e:
                logger.error(f"Failed to initialize Firestore client: {e}")
                raise
        return self._client
    
    def get_collection_name(self, base_name: str) -> str:
        """Get prefixed collection name."""
        return f"{self.collection_prefix}_{base_name}"
    
    def health_check(self) -> bool:
        """Check if Firestore is accessible."""
        try:
            # Try to access a collection to verify connection
            self.client.collection('health_check').limit(1).get()
            return True
        except Exception as e:
            logger.error(f"Firestore health check failed: {e}")
            return False


# Global instance
firestore_config = FirestoreConfig()
