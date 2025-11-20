"""
Configuration module for Bybit Position Analysis Bot.
Loads API credentials and settings from environment variables.
"""

import os
from typing import Optional


class Config:
    """Configuration container for API credentials and settings."""
    
    # Bybit API credentials
    BYBIT_API_KEY: Optional[str] = os.getenv('BYBIT_API_KEY')
    BYBIT_API_SECRET: Optional[str] = os.getenv('BYBIT_API_SECRET')
    BYBIT_BASE_URL: str = os.getenv('BYBIT_BASE_URL', 'https://api.bybit.com')
    
    # OpenAI API credentials (optional)
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    
    # Request settings
    RECV_WINDOW: int = 5000  # milliseconds
    
    @classmethod
    def validate(cls) -> tuple[bool, str]:
        """
        Validate that required configuration is present.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not cls.BYBIT_API_KEY:
            return False, "BYBIT_API_KEY environment variable is not set"
        
        if not cls.BYBIT_API_SECRET:
            return False, "BYBIT_API_SECRET environment variable is not set"
        
        if not cls.BYBIT_API_KEY.strip():
            return False, "BYBIT_API_KEY is empty"
        
        if not cls.BYBIT_API_SECRET.strip():
            return False, "BYBIT_API_SECRET is empty"
        
        return True, ""
    
    @classmethod
    def has_openai(cls) -> bool:
        """Check if OpenAI API key is configured."""
        return bool(cls.OPENAI_API_KEY and cls.OPENAI_API_KEY.strip())


# Validate on import (but don't fail - let the bot handle it)
_is_valid, _error = Config.validate()
if not _is_valid:
    import warnings
    warnings.warn(f"Configuration warning: {_error}", UserWarning)
