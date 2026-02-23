"""Admin authentication configuration."""
import os
from passlib.context import CryptContext
from typing import Optional
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AdminConfig:
    """Admin configuration manager."""
    
    ADMIN_API_KEY = os.getenv('ADMIN_API_KEY')
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH')
    
    # Session settings
    SESSION_TIMEOUT_MINUTES = int(os.getenv('SESSION_TIMEOUT_MINUTES', '60'))
    
    @staticmethod
    def verify_api_key(api_key: str) -> bool:
        """Verify admin API key."""
        if not AdminConfig.ADMIN_API_KEY:
            return False
        return api_key == AdminConfig.ADMIN_API_KEY
    
    @staticmethod
    def verify_password(password: str) -> bool:
        """Verify admin password."""
        if not AdminConfig.ADMIN_PASSWORD_HASH:
            return False
        return pwd_context.verify(password, AdminConfig.ADMIN_PASSWORD_HASH)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate a secure API key."""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def verify_credentials(username: str, password: str) -> bool:
        """Verify admin username and password."""
        if username != AdminConfig.ADMIN_USERNAME:
            return False
        return AdminConfig.verify_password(password)


# Global instance
admin_config = AdminConfig()
