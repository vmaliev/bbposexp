"""
Configuration module for Bybit Position Analysis Bot.
Loads API credentials and settings from environment variables.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration container for API credentials and settings."""
    
    # Bybit API credentials
    BYBIT_API_KEY: Optional[str] = os.getenv('BYBIT_API_KEY')
    BYBIT_API_SECRET: Optional[str] = os.getenv('BYBIT_API_SECRET')
    BYBIT_BASE_URL: str = os.getenv('BYBIT_BASE_URL', 'https://api.bybit.com')
    
    # OpenAI API credentials (optional)
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    
    # Qwen API credentials (optional - Alibaba Cloud)
    QWEN_API_KEY: Optional[str] = os.getenv('QWEN_API_KEY')
    
    # Gemini API credentials (optional - Google)
    GEMINI_API_KEY: Optional[str] = os.getenv('GEMINI_API_KEY')
    
    # AI Provider preference (openai, qwen, gemini, or auto)
    AI_PROVIDER: str = os.getenv('AI_PROVIDER', 'auto')
    
    # Telegram Bot credentials (optional)
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv('TELEGRAM_BOT_TOKEN')
    WEB_APP_URL: Optional[str] = os.getenv('WEB_APP_URL')
    
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
    
    @classmethod
    def has_qwen(cls) -> bool:
        """Check if Qwen API key is configured."""
        return bool(cls.QWEN_API_KEY and cls.QWEN_API_KEY.strip())
    
    @classmethod
    def has_gemini(cls) -> bool:
        """Check if Gemini API key is configured."""
        return bool(cls.GEMINI_API_KEY and cls.GEMINI_API_KEY.strip())
    
    @classmethod
    def has_ai(cls) -> bool:
        """Check if any AI provider is configured."""
        return cls.has_openai() or cls.has_qwen() or cls.has_gemini()
    
    @classmethod
    def get_ai_provider(cls) -> Optional[str]:
        """Get the preferred AI provider based on configuration."""
        if cls.AI_PROVIDER == 'openai' and cls.has_openai():
            return 'openai'
        elif cls.AI_PROVIDER == 'qwen' and cls.has_qwen():
            return 'qwen'
        elif cls.AI_PROVIDER == 'gemini' and cls.has_gemini():
            return 'gemini'
        elif cls.AI_PROVIDER == 'auto':
            # Auto-select priority: Gemini -> Qwen -> OpenAI
            if cls.has_gemini():
                return 'gemini'
            elif cls.has_qwen():
                return 'qwen'
            elif cls.has_openai():
                return 'openai'
        return None


# Validate on import (but don't fail - let the bot handle it)
_is_valid, _error = Config.validate()
if not _is_valid:
    import warnings
    warnings.warn(f"Configuration warning: {_error}", UserWarning)
