"""
Twitter scraper using twikit library.
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime
from twikit import Client
from twikit.tweet import Tweet as TwikitTweet
from src.utils.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class TwitterScraper:
    """Twitter scraper using twikit for unofficial API access."""
    
    def __init__(self):
        """Initialize Twitter scraper."""
        self.client = Client('en-US')
        self.is_authenticated = False
        self.cookie_path = 'cookies.json'
        logger.info("🐦 Initialized Twitter scraper")
    
    async def authenticate(self) -> bool:
        """
        Authenticate with Twitter using credentials or cookies.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # 1. Try loading existing cookies
            import os
            if os.path.exists(self.cookie_path):
                try:
                    logger.info("🍪 Loading existing cookies...")
                    self.client.load_cookies(self.cookie_path)
                    self.is_authenticated = True
                    logger.info("✅ Successfully authenticated using cookies")
                    return True
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load cookies: {str(e)}")
            
            # 2. If no cookies or loading failed, try login
            logger.info("🔐 Attempting to authenticate with Twitter credentials...")
            
            # Check if we have credentials
            if not settings.twitter_username or not settings.twitter_password:
                logger.error("❌ No Twitter credentials found in .env")
                return False

            await self.client.login(
                auth_info_1=settings.twitter_username,
                auth_info_2=settings.twitter_email,
                password=settings.twitter_password
            )
            
            # Save cookies for next time
            self.client.save_cookies(self.cookie_path)
            self.is_authenticated = True
            logger.info(f"✅ Successfully authenticated and saved cookies to {self.cookie_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Authentication failed: {str(e)}")
            self.is_authenticated = False
            return False

    async def load_cookies_from_dict(self, cookies: dict) -> bool:
        """
        Manually load cookies from a dictionary.
        This is useful if automated login is blocked.
        """
        try:
            import json
            with open(self.cookie_path, 'w') as f:
                json.dump(cookies, f)
            
            self.client.load_cookies(self.cookie_path)
            self.is_authenticated = True
            logger.info("✅ Successfully loaded manual cookies")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load manual cookies: {str(e)}")
            return False
    
    async def get_user_tweets(
        self,
        username: str,
        count: int = 20,
        tweet_type: str = 'Tweets'
    ) -> List[Dict]:
        """
        Fetch recent tweets from a user's timeline.
        
        Args:
            username: Twitter username (without @)
            count: Number of tweets to fetch
            tweet_type: Type of tweets ('Tweets', 'Replies', 'Media', 'Likes')
        
        Returns:
            List of tweet dictionaries with metadata
        """
        if not self.is_authenticated:
            logger.warning("⚠️ Not authenticated. Attempting to authenticate...")
            await self.authenticate()
        
        try:
            logger.info(f"📥 Fetching tweets from @{username}...")
            
            # Get user
            user = await self.client.get_user_by_screen_name(username)
            
            # Get user tweets
            tweets = await user.get_tweets(tweet_type, count=count)
            
            # Parse tweets
            parsed_tweets = []
            for tweet in tweets:
                parsed_tweet = self._parse_tweet(tweet, username)
                parsed_tweets.append(parsed_tweet)
            
            logger.info(f"✅ Fetched {len(parsed_tweets)} tweets from @{username}")
            return parsed_tweets
            
        except Exception as e:
            logger.error(f"❌ Error fetching tweets from @{username}: {str(e)}")
            return []
    
    async def search_tweets(self, keyword: str, count: int = 20) -> List[Dict]:
        """
        Search for tweets containing a keyword.
        
        Args:
            keyword: Keyword to search for
            count: Number of tweets to fetch
        
        Returns:
            List of tweet dictionaries
        """
        if not self.is_authenticated:
            logger.warning("⚠️ Not authenticated. Attempting to authenticate...")
            await self.authenticate()
        
        try:
            logger.info(f"🔍 Searching for tweets with keyword: '{keyword}'...")
            
            # Search tweets
            tweets = await self.client.search_tweet(keyword, product='Latest', count=count)
            
            # Parse tweets
            parsed_tweets = []
            for tweet in tweets:
                # Extract username from user object
                username = tweet.user.screen_name if hasattr(tweet, 'user') else 'unknown'
                parsed_tweet = self._parse_tweet(tweet, username)
                parsed_tweets.append(parsed_tweet)
            
            logger.info(f"✅ Found {len(parsed_tweets)} tweets for keyword '{keyword}'")
            return parsed_tweets
            
        except Exception as e:
            logger.error(f"❌ Error searching tweets for '{keyword}': {str(e)}")
            return []
    
    def _parse_tweet(self, tweet: TwikitTweet, username: str = None) -> Dict:
        """
        Parse a twikit Tweet object into a standardized dictionary.
        
        Args:
            tweet: Twikit tweet object
            username: Twitter username (if not in tweet object)
        
        Returns:
            Dictionary with tweet metadata
        """
        try:
            # Extract username
            if username is None:
                username = tweet.user.screen_name if hasattr(tweet, 'user') else 'unknown'
            
            # Extract tweet ID
            tweet_id = str(tweet.id)
            
            # Extract text
            text = tweet.text if hasattr(tweet, 'text') else tweet.full_text if hasattr(tweet, 'full_text') else ''
            
            # Extract timestamp
            created_at_str = tweet.created_at if hasattr(tweet, 'created_at') else None
            posted_at = self._parse_timestamp(created_at_str) if created_at_str else datetime.utcnow()
            
            # Generate tweet link
            link = f"https://twitter.com/{username}/status/{tweet_id}"
            
            # Display name
            display_name = tweet.user.name if hasattr(tweet, 'user') else username
            
            return {
                'tweet_id': tweet_id,
                'username': username,
                'display_name': display_name,
                'text': text,
                'link': link,
                'posted_at': posted_at
            }
            
        except Exception as e:
            logger.error(f"❌ Error parsing tweet: {str(e)}")
            return {
                'tweet_id': 'unknown',
                'username': username or 'unknown',
                'display_name': username or 'unknown',
                'text': '',
                'link': '',
                'posted_at': datetime.utcnow()
            }
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """
        Parse Twitter timestamp string to datetime object.
        
        Args:
            timestamp_str: Timestamp string from Twitter
        
        Returns:
            Datetime object in UTC
        """
        try:
            # Try different timestamp formats
            formats = [
                '%a %b %d %H:%M:%S %z %Y',  # Twitter's standard format
                '%Y-%m-%dT%H:%M:%S.%fZ',     # ISO format
                '%Y-%m-%d %H:%M:%S'          # Simple format
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(timestamp_str, fmt)
                    # Convert to UTC if timezone-aware
                    if dt.tzinfo is not None:
                        dt = dt.replace(tzinfo=None)  # Remove timezone for consistency
                    return dt
                except ValueError:
                    continue
            
            # If all formats fail, return current time
            logger.warning(f"⚠️ Could not parse timestamp: {timestamp_str}")
            return datetime.utcnow()
            
        except Exception as e:
            logger.error(f"❌ Error parsing timestamp: {str(e)}")
            return datetime.utcnow()


# Global scraper instance
_scraper = None


async def get_scraper() -> TwitterScraper:
    """Get or create global scraper instance."""
    global _scraper
    if _scraper is None:
        _scraper = TwitterScraper()
        await _scraper.authenticate()
    return _scraper
