"""
FastAPI application for TweetTrack Sentinel.
Provides REST API endpoints for the frontend.
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging
from pydantic import BaseModel

from src.database.db import get_db_session
from src.database import operations as db_ops
from src.scraper.twitter_scraper import get_scraper
from src.ai.summarizer import summarize_tweet
from src.utils.timezone import utc_to_ist, format_ist

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TweetTrack Sentinel API",
    description="Real-time Twitter monitoring and alerting system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API

class TweetResponse(BaseModel):
    """Response model for tweet data."""
    id: int
    tweet_id: str
    account_username: str
    text: str
    summary: str
    link: str
    posted_at: str  # ISO format in IST
    posted_at_relative: str  # e.g., "5 minutes ago"
    scraped_at: str
    
    class Config:
        from_attributes = True


class AccountResponse(BaseModel):
    """Response model for monitored account."""
    id: int
    username: str
    display_name: Optional[str] = None
    is_active: bool
    last_checked: Optional[str] = None
    
    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    """Request model for keyword search."""
    keyword: str
    count: int = 20


class SearchResultResponse(BaseModel):
    """Response model for search results."""
    tweet_id: str
    account_username: str
    text: str
    summary: str
    link: str
    posted_at: str
    posted_at_relative: str


class AddAccountRequest(BaseModel):
    """Request model for adding a monitored account."""
    username: str
    display_name: str = None


# Dependency to get database session
def get_db():
    """Dependency for database session."""
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()


# Helper function to convert tweet to response
def tweet_to_response(tweet) -> TweetResponse:
    """Convert database tweet model to API response."""
    from src.utils.timezone import get_relative_time
    
    return TweetResponse(
        id=tweet.id,
        tweet_id=tweet.tweet_id,
        account_username=tweet.account_username,
        text=tweet.text,
        summary=tweet.summary or "No summary available",
        link=tweet.link,
        posted_at=format_ist(tweet.posted_at, '%Y-%m-%d %H:%M:%S %Z'),
        posted_at_relative=get_relative_time(tweet.posted_at),
        scraped_at=format_ist(tweet.scraped_at, '%Y-%m-%d %H:%M:%S %Z')
    )


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "TweetTrack Sentinel API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/health")
@app.get("/health")  # For Render health checks
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/tweets/recent", response_model=List[TweetResponse])
async def get_recent_tweets_api(hours: int = 24, account: str = None, db: Session = Depends(get_db)):
    """
    Get recent tweets (POSTED in last N hours).
    
    Args:
        hours: Number of hours to look back (default: 24)
        account: Optional username to filter by specific account
        db: Database session
    
    Returns:
        List of recent tweets
    """
    try:
        if account:
            # Filter by specific account
            tweets = db_ops.get_tweets_by_account(db, account, hours)
        else:
            # Get all recent tweets
            tweets = db_ops.get_recent_tweets(db, hours=hours)
        return [tweet_to_response(tweet) for tweet in tweets]
    except Exception as e:
        logger.error(f"Error fetching recent tweets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tweets/by-account/{username}", response_model=List[TweetResponse])
async def get_tweets_by_account(username: str, hours: int = 24, db: Session = Depends(get_db)):
    """
    Get tweets from a specific account.
    
    Args:
        username: Twitter username
        hours: Number of hours to look back (default: 24)
        db: Database session
    
    Returns:
        List of tweets from the account
    """
    try:
        tweets = db_ops.get_tweets_by_account(db, username, hours=hours)
        return [tweet_to_response(tweet) for tweet in tweets]
    except Exception as e:
        logger.error(f"Error fetching tweets for @{username}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search/keywords", response_model=List[SearchResultResponse])
async def search_keywords(request: SearchRequest, db: Session = Depends(get_db)):
    """
    Search for tweets containing a keyword.
    
    Args:
        request: Search request with keyword and count
        db: Database session
    
    Returns:
        List of matching tweets
    """
    try:
        logger.info(f"🔍 Searching for keyword: '{request.keyword}'")
        
        # Get scraper and search
        scraper = await get_scraper()
        tweets = await scraper.search_tweets(request.keyword, count=request.count)
        
        if not tweets:
            return []
        
        # Create search record
        search = db_ops.create_keyword_search(db, request.keyword)
        
        # Process and store results
        results = []
        for tweet_data in tweets:
            # Generate summary
            summary = summarize_tweet(tweet_data['text'])
            
            # Store search result
            db_ops.create_search_result(
                db=db,
                search_id=search.id,
                tweet_id=tweet_data['tweet_id'],
                account_username=tweet_data['username'],
                text=tweet_data['text'],
                summary=summary,
                link=tweet_data['link'],
                posted_at=tweet_data['posted_at']
            )
            
            # Add to results
            from src.utils.timezone import get_relative_time
            results.append(SearchResultResponse(
                tweet_id=tweet_data['tweet_id'],
                account_username=tweet_data['username'],
                text=tweet_data['text'],
                summary=summary,
                link=tweet_data['link'],
                posted_at=format_ist(tweet_data['posted_at'], '%Y-%m-%d %H:%M:%S %Z'),
                posted_at_relative=get_relative_time(tweet_data['posted_at'])
            ))
        
        logger.info(f"✅ Found {len(results)} results for '{request.keyword}'")
        return results
        
    except Exception as e:
        logger.error(f"Error searching for keyword '{request.keyword}': {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/accounts", response_model=List[AccountResponse])
async def get_monitored_accounts(active_only: bool = True, db: Session = Depends(get_db)):
    """
    Get list of monitored accounts.
    
    Args:
        active_only: Only return active accounts (default: True)
        db: Database session
    
    Returns:
        List of monitored accounts
    """
    try:
        accounts = db_ops.get_monitored_accounts(db, active_only=active_only)
        return [
            AccountResponse(
                id=acc.id,
                username=acc.username,
                display_name=acc.display_name,
                is_active=acc.is_active,
                last_checked=format_ist(acc.last_checked, '%Y-%m-%d %H:%M:%S %Z') if acc.last_checked else "Never"
            )
            for acc in accounts
        ]
    except Exception as e:
        logger.error(f"Error fetching monitored accounts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/accounts", response_model=AccountResponse)
async def add_monitored_account(request: AddAccountRequest, db: Session = Depends(get_db)):
    """
    Add a new monitored account.
    
    Args:
        request: Account details
        db: Database session
    
    Returns:
        Created account
    """
    try:
        # Check if account already exists
        existing = db_ops.get_monitored_account(db, request.username)
        if existing:
            raise HTTPException(status_code=400, detail=f"Account @{request.username} is already monitored")
        
        # Create account
        account = db_ops.create_monitored_account(
            db,
            username=request.username,
            display_name=request.display_name or request.username
        )
        
        logger.info(f"➕ Added monitored account: @{request.username}")
        
        return AccountResponse(
            id=account.id,
            username=account.username,
            display_name=account.display_name,
            is_active=account.is_active,
            last_checked=format_ist(account.last_checked, '%Y-%m-%d %H:%M:%S %Z') if account.last_checked else "Never"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding account @{request.username}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/accounts/{username}")
async def remove_monitored_account(username: str, db: Session = Depends(get_db)):
    """
    Deactivate a monitored account.
    
    Args:
        username: Twitter username
        db: Database session
    
    Returns:
        Success message
    """
    try:
        success = db_ops.deactivate_monitored_account(db, username)
        if not success:
            raise HTTPException(status_code=404, detail=f"Account @{username} not found")
        
        logger.info(f"🗑️ Deactivated monitored account: @{username}")
        return {"message": f"Account @{username} deactivated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing account @{username}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("🚀 Starting TweetTrack Sentinel API...")
    
    # Initialize database
    from src.database.db import init_db
    init_db()
    
    logger.info("✅ TweetTrack Sentinel API is ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("👋 Shutting down TweetTrack Sentinel API...")
