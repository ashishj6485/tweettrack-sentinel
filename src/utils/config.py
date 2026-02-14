"""
Configuration management for TweetTrack Sentinel.
Loads and validates environment variables.
"""
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices

# Get the project root directory (2 levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / '.env'


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Twitter Authentication
    twitter_username: str = Field(default='')
    twitter_email: str = Field(default='')
    twitter_password: str = Field(default='')
    
    # AI Summarization (Gemini API)
    gemini_api_key: str = Field(default='')
    
    # WhatsApp Alerts (Twilio)
    twilio_account_sid: str = Field(default='')
    twilio_auth_token: str = Field(default='')
    twilio_whatsapp_from: str = Field(default='')
    twilio_whatsapp_to: str = Field(default='')  # Comma-separated
    
    # Database
    database_url: str = Field(default='sqlite:///./tweettrack.db')
    
    # Polling Configuration
    poll_interval_seconds: int = Field(default=300)
    
    # Monitored Accounts
    monitored_accounts_str: str = Field(default='', validation_alias=AliasChoices('MONITORED_ACCOUNTS'))
    
    # API Configuration
    api_host: str = Field(default='0.0.0.0')
    api_port: int = Field(default=8000, validation_alias=AliasChoices('PORT', 'API_PORT'))
    
    # Security
    secret_key: str = Field(default='insecure-dev-key-change-in-production')
    algorithm: str = Field(default='HS256')
    
    # Logging
    log_level: str = Field(default='INFO')
    
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )
    
    @property
    def monitored_accounts(self) -> List[str]:
        """Parse comma-separated monitored accounts into a list."""
        if not self.monitored_accounts_str:
            return []
        return [account.strip() for account in self.monitored_accounts_str.split(',') if account.strip()]
    
    @property
    def whatsapp_recipients(self) -> List[str]:
        """Parse comma-separated WhatsApp recipient numbers into a list."""
        if not self.twilio_whatsapp_to:
            return []
        return [num.strip() for num in self.twilio_whatsapp_to.split(',') if num.strip()]


# Global settings instance
# Explicitly load .env file first for safety with some OS environments
from dotenv import load_dotenv
load_dotenv(ENV_FILE)
settings = Settings()
