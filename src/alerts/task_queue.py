"""
Async task queue for processing tweets without blocking polling.
Uses asyncio queues for simple background processing.
"""
import asyncio
import logging
import json
from typing import Dict
from src.ai.political_analyzer import analyze_political_tweet
from src.alerts.whatsapp_service import get_whatsapp_service
from src.database.db import get_db_session
from src.database.models import Tweet

logger = logging.getLogger(__name__)


class AsyncTaskQueue:
    """Simple async task queue for processing tweets."""
    
    def __init__(self):
        """Initialize the task queue."""
        self.queue = asyncio.Queue()
        self.is_running = False
        self.worker_task = None
        logger.info("✅ Async task queue initialized")
    
    async def add_task(self, tweet_id: int, tweet_data: Dict):
        """
        Add a tweet for analysis to the queue.
        
        Args:
            tweet_id: Database ID of the tweet
            tweet_data: Tweet information (text, username, link)
        """
        await self.queue.put({
            'tweet_id': tweet_id,
            'tweet_data': tweet_data
        })
        logger.info(f"➕ Added tweet {tweet_id} to analysis queue (queue size: {self.queue.qsize()})")
    
    async def _process_batch(self, batch: list):
        """
        Process a batch of tweets: analyze in bulk and send alerts.
        """
        if not batch:
            return
            
        tweets_to_analyze = []
        for task in batch:
            tweets_to_analyze.append({
                'tweet_id': task['tweet_id'],
                'username': task['tweet_data']['username'],
                'text': task['tweet_data']['text']
            })
            
        try:
            logger.info(f"🔍 Processing batch of {len(batch)} tweets...")
            
            # Step 1: Analyze with Gemini AI in batch
            from src.ai.political_analyzer import analyze_batch_tweets
            analysis_results = await analyze_batch_tweets(tweets_to_analyze)
            
            whatsapp_service = get_whatsapp_service()
            db = get_db_session()
            
            try:
                for task, analysis in zip(batch, analysis_results):
                    tweet_id = task['tweet_id']
                    tweet_data = task['tweet_data']
                    
                    # Handle failed analysis for specific tweet in batch
                    if not analysis:
                        logger.warning(f"⚠️ Analysis failed for tweet {tweet_id}, using fallback.")
                        analysis = {
                            "category": "MENTION",
                            "portfolio": "General",
                            "urgency_score": 3,
                            "sentiment_score": 0.0,
                            "summary": "[AI Analysis Offline] Please review tweet link.",
                            "action_required": True
                        }
                    
                    # Update database
                    tweet = db.query(Tweet).filter(Tweet.id == tweet_id).first()
                    if tweet:
                        tweet.analysis_data = json.dumps(analysis)
                        db.commit()
                        
                    # Send WhatsApp alert (Mark as sent if already done by some other process)
                    if tweet and not tweet.is_alert_sent and whatsapp_service.should_send_alert(analysis):
                        success = await whatsapp_service.send_alert(tweet_data, analysis)
                        if success:
                            tweet.is_alert_sent = True
                            db.commit()
                            logger.info(f"✅ Alert sent for tweet {tweet_id}")
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"❌ Error processing batch: {str(e)}")

    async def _worker(self):
        """Background worker that collects tasks and processes them in batches."""
        logger.info("🔧 Starting batch-enabled async task worker...")
        
        while self.is_running:
            batch = []
            
            # Wait for at least one task to start a batch
            try:
                # Initial wait for the first task
                task = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                batch.append(task)
                
                # Try to fill the batch up to 10 within a short window
                # We use a smaller timeout here to process quickly
                while len(batch) < 10:
                    try:
                        task = await asyncio.wait_for(self.queue.get(), timeout=2.0)
                        batch.append(task)
                    except asyncio.TimeoutError:
                        # Timeout reached, process whatever we have in batch
                        break
            except asyncio.TimeoutError:
                # No tasks at all, continue loop
                continue
                
            # Process the batch
            if batch:
                await self._process_batch(batch)
                
                # Mark all as done
                for _ in range(len(batch)):
                    self.queue.task_done()
        
        logger.info("🛑 Async task worker stopped")
    
    async def start(self):
        """Start the background worker."""
        if self.is_running:
            logger.warning("⚠️ Worker already running")
            return
        
        self.is_running = True
        self.worker_task = asyncio.create_task(self._worker())
        logger.info("✅ Batch task worker started")
    
    async def stop(self):
        """Stop the background worker."""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.worker_task:
            await self.worker_task
        
        logger.info("✅ Batch task worker stopped")


# Global task queue instance
_task_queue = None


def get_task_queue() -> AsyncTaskQueue:
    """Get or create global task queue instance."""
    global _task_queue
    if _task_queue is None:
        _task_queue = AsyncTaskQueue()
    return _task_queue
