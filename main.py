"""
TweetTrack Sentinel - Main application entry point.

Starts both the FastAPI server and the polling service.
"""
import asyncio
import logging
import signal
import sys
from threading import Thread
import uvicorn

from src.database.db import init_db
from src.scraper.polling_service import get_polling_service
from src.utils.config import settings

# Configure logging with UTF-8 encoding (Windows cp1252 can't handle emojis)
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('tweettrack.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class Application:
    """Main application orchestrator."""
    
    def __init__(self):
        self.polling_service = None
        self.polling_task = None
        self.is_running = False
    
    async def start_polling_service(self):
        """Start the polling service in background."""
        logger.info("🔄 Starting polling service...")
        self.polling_service = get_polling_service()
        await self.polling_service.start()
    
    def run_polling_in_thread(self):
        """Run polling service in a separate thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.start_polling_service())
    
    def start(self):
        """Start the application."""
        logger.info("=" * 80)
        logger.info("🐦 TweetTrack Sentinel - Starting...")
        logger.info("=" * 80)
        
        # Initialize database
        logger.info("📊 Initializing database...")
        init_db()
        
        # Start polling service in background thread
        logger.info("🚀 Launching polling service...")
        polling_thread = Thread(target=self.run_polling_in_thread, daemon=True)
        polling_thread.start()
        
        # Start FastAPI server
        logger.info(f"🌐 Starting API server on {settings.api_host}:{settings.api_port}...")
        logger.info("=" * 80)
        
        try:
            uvicorn.run(
                "src.api.main:app",
                host=settings.api_host,
                port=settings.api_port,
                reload=False,
                log_level=settings.log_level.lower()
            )
        except KeyboardInterrupt:
            logger.info("\n🛑 Received shutdown signal...")
            self.shutdown()
    
    def shutdown(self):
        """Graceful shutdown."""
        logger.info("👋 Shutting down TweetTrack Sentinel...")
        if self.polling_service:
            self.polling_service.stop()
        logger.info("✅ Shutdown complete")
        sys.exit(0)


def main():
    """Main entry point."""
    app = Application()
    
    # Handle shutdown signals
    def signal_handler(sig, frame):
        logger.info("\n🛑 Received interrupt signal...")
        app.shutdown()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start application
    app.start()


if __name__ == "__main__":
    main()
