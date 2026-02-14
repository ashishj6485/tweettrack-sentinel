"""
Database CRUD operations.
"""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from src.database.models import MonitoredAccount, Tweet, KeywordSearch, SearchResult


# Monitored Accounts Operations

def create_monitored_account(db: Session, username: str, display_name: str = None) -> MonitoredAccount:
    """Create a new monitored account."""
    account = MonitoredAccount(username=username, display_name=display_name or username)
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def get_monitored_accounts(db: Session, active_only: bool = True) -> List[MonitoredAccount]:
    """Get all monitored accounts."""
    query = db.query(MonitoredAccount)
    if active_only:
        query = query.filter(MonitoredAccount.is_active == True)
    return query.all()


def get_monitored_account(db: Session, username: str) -> Optional[MonitoredAccount]:
    """Get a specific monitored account by username."""
    return db.query(MonitoredAccount).filter(MonitoredAccount.username == username).first()


def update_account_last_checked(db: Session, username: str) -> None:
    """Update the last_checked timestamp for an account."""
    account = get_monitored_account(db, username)
    if account:
        account.last_checked = datetime.utcnow()
        db.commit()


def deactivate_monitored_account(db: Session, username: str) -> bool:
    """Deactivate a monitored account."""
    account = get_monitored_account(db, username)
    if account:
        account.is_active = False
        db.commit()
        return True
    return False


# Tweet Operations

def create_tweet(
    db: Session,
    tweet_id: str,
    account_username: str,
    text: str,
    summary: str,
    link: str,
    posted_at: datetime
) -> Tweet:
    """Create a new tweet record."""
    tweet = Tweet(
        tweet_id=tweet_id,
        account_username=account_username,
        text=text,
        summary=summary,
        link=link,
        posted_at=posted_at,
        scraped_at=datetime.utcnow()
    )
    db.add(tweet)
    db.commit()
    db.refresh(tweet)
    return tweet


def get_tweet_by_id(db: Session, tweet_id: str) -> Optional[Tweet]:
    """Get a tweet by its tweet_id."""
    return db.query(Tweet).filter(Tweet.tweet_id == tweet_id).first()


def tweet_exists(db: Session, tweet_id: str) -> bool:
    """Check if a tweet already exists in the database."""
    return db.query(Tweet).filter(Tweet.tweet_id == tweet_id).first() is not None


from datetime import datetime, timedelta, timezone

def get_recent_tweets(db: Session, hours: int = 24) -> List[Tweet]:
    """Get tweets POSTED in the last N hours (ordered newest first)."""
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    return db.query(Tweet).filter(Tweet.posted_at >= cutoff_time).order_by(Tweet.posted_at.desc()).all()


def get_tweets_by_account(db: Session, username: str, hours: int = 24) -> List[Tweet]:
    """Get tweets from a specific account POSTED in the last N hours."""
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    return db.query(Tweet).filter(
        Tweet.account_username == username,
        Tweet.posted_at >= cutoff_time
    ).order_by(Tweet.posted_at.desc()).all()


def mark_tweet_alerted(db: Session, tweet_id: str) -> None:
    """Mark a tweet as alerted."""
    tweet = get_tweet_by_id(db, tweet_id)
    if tweet:
        tweet.is_alerted = True
        db.commit()


def cleanup_old_tweets(db: Session, hours: int = 48) -> int:
    """Delete tweets scraped more than N hours ago. Returns count of deleted tweets."""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    deleted_count = db.query(Tweet).filter(Tweet.scraped_at < cutoff_time).delete()
    db.commit()
    return deleted_count


# Keyword Search Operations

def create_keyword_search(db: Session, keyword: str) -> KeywordSearch:
    """Create a new keyword search record."""
    search = KeywordSearch(keyword=keyword)
    db.add(search)
    db.commit()
    db.refresh(search)
    return search


def create_search_result(
    db: Session,
    search_id: int,
    tweet_id: str,
    account_username: str,
    text: str,
    summary: str,
    link: str,
    posted_at: datetime
) -> SearchResult:
    """Create a new search result."""
    result = SearchResult(
        search_id=search_id,
        tweet_id=tweet_id,
        account_username=account_username,
        text=text,
        summary=summary,
        link=link,
        posted_at=posted_at
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def get_search_results(db: Session, search_id: int) -> List[SearchResult]:
    """Get all results for a keyword search."""
    return db.query(SearchResult).filter(SearchResult.search_id == search_id).order_by(SearchResult.posted_at.desc()).all()
