"""
Security utilities for Tobey Finance Bank
"""

import bcrypt
from cryptography.fernet import Fernet
import base64
import os


class SecurityManager:
    """Security manager for password hashing and encryption"""
    
    def __init__(self, key: bytes = None):
        if key is None:
            key = Fernet.generate_key()
        self.key = key
        self.cipher = Fernet(self.key)
    
    @staticmethod
    def hash_password(password: str) -> bytes:
        """Hash a password for storing."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    @staticmethod
    def verify_password(password: str, hashed: bytes) -> bool:
        """Verify a stored password against one provided by user."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    
    def encrypt(self, data: str) -> bytes:
        """Encrypt data using Fernet symmetric encryption."""
        return self.cipher.encrypt(data.encode('utf-8'))
    
    def decrypt(self, token: bytes) -> str:
        """Decrypt data using Fernet symmetric encryption."""
        return self.cipher.decrypt(token).decode('utf-8')
    
    @staticmethod
    def generate_key() -> bytes:
        """Generate a new Fernet key."""
        return Fernet.generate_key() 