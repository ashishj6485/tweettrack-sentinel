"""
Database models for TweetTrack Sentinel.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class MonitoredAccount(Base):
    """Model for Twitter accounts being monitored."""
    __tablename__ = 'monitored_accounts'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200))
    is_active = Column(Boolean, default=True)
    last_checked = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<MonitoredAccount(username='{self.username}')>"


class Tweet(Base):
    """Model for storing scraped tweets."""
    __tablename__ = "tweets"
    
    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(String, unique=True, nullable=False, index=True)
    account_id = Column(Integer, default=0)  # Legacy column - DB has NOT NULL constraint
    account_username = Column(String, nullable=False)
    text = Column(String, nullable=False)
    summary = Column(String)
    link = Column(String)
    posted_at = Column(DateTime(timezone=True))
    scraped_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # WhatsApp alert tracking
    is_alert_sent = Column(Boolean, default=False, index=True)
    analysis_data = Column(String)  # JSON string of AI analysis results
    is_alerted = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Tweet(tweet_id='{self.tweet_id}', username='{self.account_username}')>"


class KeywordSearch(Base):
    """Model for keyword search history."""
    __tablename__ = 'keyword_searches'
    
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to search results
    results = relationship("SearchResult", back_populates="search", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<KeywordSearch(keyword='{self.keyword}')>"


class SearchResult(Base):
    """Model for keyword search results."""
    __tablename__ = 'search_results'
    
    id = Column(Integer, primary_key=True, index=True)
    search_id = Column(Integer, ForeignKey('keyword_searches.id'), nullable=False)
    tweet_id = Column(String(100), nullable=False)
    account_username = Column(String(100), nullable=False)
    text = Column(Text, nullable=False)
    summary = Column(Text)
    link = Column(String(500))
    posted_at = Column(DateTime, nullable=False)
    found_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to search
    search = relationship("KeywordSearch", back_populates="results")
    
    def __repr__(self):
        return f"<SearchResult(tweet_id='{self.tweet_id}')>"
