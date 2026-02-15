"""
Polling service for continuous monitoring of Twitter accounts.
"""
import asyncio
import logging
from datetime import datetime
from typing import List
from src.scraper.twitter_scraper import get_scraper
from src.ai.summarizer import summarize_tweet
from src.database.db import get_db
from src.database.operations import (
    create_tweet,
    tweet_exists,
    update_account_last_checked,
    get_monitored_accounts,
    cleanup_old_tweets
)
from src.utils.config import settings
from src.alerts.task_queue import get_task_queue

# Configure logging
logger = logging.getLogger(__name__)


class PollingService:
    """Service for polling Twitter accounts at regular intervals."""
    
    def __init__(self, poll_interval: int = None):
        """
        Initialize polling service.
        
        Args:
            poll_interval: Polling interval in seconds (defaults to config setting)
        """
        self.poll_interval = poll_interval or settings.poll_interval_seconds
        self.is_running = False
        self.scraper = None
        self.task_queue = get_task_queue()
        logger.info(f"⏰ Initialized polling service (interval: {self.poll_interval}s)")
    
    async def start(self):
        """Start the polling service."""
        if self.is_running:
            logger.warning("⚠️ Polling service is already running")
            return
        
        logger.info("🚀 Starting polling service...")
        self.is_running = True
        
        # Get scraper instance
        self.scraper = await get_scraper()
        
        # Start async task queue worker
        logger.info("🔧 About to start task queue worker...")
        try:
            await self.task_queue.start()
            logger.info("✅ Task queue worker started successfully!")
        except Exception as e:
            logger.error(f"❌ Failed to start task queue: {str(e)}")
        
        # Sync accounts from config
        self._sync_accounts_from_config()
        
        # Run polling loop
        await self._polling_loop()
    
    def stop(self):
        """Stop the polling service."""
        logger.info("🛑 Stopping polling service...")
        self.is_running = False
    
    async def _polling_loop(self):
        """Main polling loop."""
        while self.is_running:
            try:
                logger.info("=" * 60)
                logger.info(f"🔄 Starting poll cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Poll all monitored accounts
                await self._poll_accounts()
                
                # Cleanup old tweets
                self._cleanup_old_tweets()
                
                logger.info(f"✅ Poll cycle completed. Next poll in {self.poll_interval}s")
                logger.info("=" * 60)
                
                # Wait for next poll
                await asyncio.sleep(self.poll_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in polling loop: {str(e)}")
                # Wait a bit before retrying
                await asyncio.sleep(30)
    
    async def _poll_accounts(self):
        """Poll all monitored accounts for new tweets."""
        with get_db() as db:
            accounts = get_monitored_accounts(db, active_only=True)
            
            if not accounts:
                logger.warning("⚠️ No monitored accounts found in database")
                # Add accounts from config if none exist
                self._sync_accounts_from_config()
                return
            
            logger.info(f"📊 Polling {len(accounts)} monitored accounts...")
            
            for account in accounts:
                await self._poll_account(account.username)
                # Small delay between accounts to avoid rate limiting
                await asyncio.sleep(2)
    
    async def _poll_account(self, username: str):
        """
        Poll a single account for new tweets.
        
        Args:
            username: Twitter username to poll
        """
        try:
            logger.info(f"🔍 Polling @{username}...")
            
            # Fetch recent tweets
            tweets = await self.scraper.get_user_tweets(username, count=20)
            
            if not tweets:
                logger.info(f"ℹ️ No tweets found for @{username}")
                with get_db() as db:
                    update_account_last_checked(db, username)
                return
            
            # Process each tweet
            new_tweet_count = 0
            for tweet_data in tweets:
                is_new = await self._process_tweet(tweet_data)
                if is_new:
                    new_tweet_count += 1
            
            # Update last checked timestamp
            with get_db() as db:
                update_account_last_checked(db, username)
            
            if new_tweet_count > 0:
                logger.info(f"✨ Found {new_tweet_count} new tweet(s) from @{username}")
            else:
                logger.info(f"ℹ️ No new tweets from @{username}")
                
        except Exception as e:
            logger.error(f"❌ Error polling @{username}: {str(e)}")
            if "Forbidden" in str(e) or "403" in str(e):
                logger.error(f"🚫 Twitter access Forbidden for @{username}. Authentication may have failed.")
    
    async def _process_tweet(self, tweet_data: dict) -> bool:
        """
        Process a single tweet: check if new, generate summary, store in DB.
        
        Args:
            tweet_data: Tweet metadata dictionary
        
        Returns:
            True if tweet was new and stored, False otherwise
        """
        try:
            tweet_id = tweet_data['tweet_id']
            
            # Check if tweet already exists
            with get_db() as db:
                if tweet_exists(db, tweet_id):
                    return False
            
            # Generate AI summary
            logger.info(f"🤖 Generating summary for tweet {tweet_id}...")
            summary = summarize_tweet(tweet_data['text'])
            
            # Store in database
            with get_db() as db:
                tweet_db = create_tweet(
                    db=db,
                    tweet_id=tweet_id,
                    account_username=tweet_data['username'],
                    text=tweet_data['text'],
                    summary=summary,
                    link=tweet_data['link'],
                    posted_at=tweet_data['posted_at']
                )
                
                # Add to async queue for political analysis & WhatsApp alerts
                # This runs in background and won't block polling
                await self.task_queue.add_task(
                    tweet_id=tweet_db.id,
                    tweet_data={
                        'username': tweet_data['username'],
                        'text': tweet_data['text'],
                        'link': tweet_data['link']
                    }
                )
            
            logger.info(f"✅ Saved new tweet {tweet_id} from @{tweet_data['username']}")
            
            # TODO: Send alerts (WhatsApp, web push) - Phase 2
            # For now, just log
            logger.info(f"📢 NEW TWEET from @{tweet_data['username']}:")
            logger.info(f"   Text: {tweet_data['text'][:100]}...")
            logger.info(f"   Summary: {summary}")
            logger.info(f"   Link: {tweet_data['link']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing tweet: {str(e)}")
            return False
    
    def _cleanup_old_tweets(self):
        """Clean up tweets older than 24 hours."""
        try:
            with get_db() as db:
                deleted_count = cleanup_old_tweets(db, hours=24)
                if deleted_count > 0:
                    logger.info(f"🗑️ Cleaned up {deleted_count} old tweet(s)")
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {str(e)}")
    
    def _sync_accounts_from_config(self):
        """Sync monitored accounts from config to database."""
        from src.database.operations import create_monitored_account, get_monitored_account
        
        try:
            with get_db() as db:
                for username in settings.monitored_accounts:
                    if not get_monitored_account(db, username):
                        create_monitored_account(db, username)
                        logger.info(f"➕ Added monitored account: @{username}")
        except Exception as e:
            logger.error(f"❌ Error syncing accounts from config: {str(e)}")


# Global polling service instance
_polling_service = None


def get_polling_service() -> PollingService:
    """Get or create global polling service instance."""
    global _polling_service
    if _polling_service is None:
        _polling_service = PollingService()
    return _polling_service
