"""
AI Summarization module using Google Gemini API (new SDK).
"""
import logging
from typing import Optional
from google import genai
from src.utils.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Gemini client (new SDK - uses stable v1 API)
client = genai.Client(api_key=settings.gemini_api_key)


class GeminiSummarizer:
    """AI summarizer using Google Gemini API."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-lite"):
        """Initialize Gemini summarizer."""
        self.model_name = model_name
        logger.info(f"Initialized Gemini summarizer with model: {self.model_name}")
    
    def summarize(self, tweet_text: str, max_retries: int = 3) -> Optional[str]:
        """
        Generate a concise summary of a tweet.
        
        Args:
            tweet_text: The tweet text to summarize
            max_retries: Maximum number of retry attempts
        
        Returns:
            Concise summary string, or None if failed
        """
        prompt = f"""You are a tweet summarizer. Summarize this tweet in one clear, concise sentence. 
DO NOT repeat the tweet text. Provide a meaningful summary that captures the key point.
If the tweet is in Hindi, summarize in Hindi. If English, summarize in English.
Keep the summary under 100 characters.

Tweet: {tweet_text}

Summary:"""
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"Generating summary (attempt {attempt + 1}/{max_retries})...")
                
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )
                
                summary = response.text.strip()
                
                # Validate summary - make sure it's not just repeating the tweet
                if not summary:
                    logger.warning("Empty summary received")
                    continue
                
                # Check if summary is just a copy of the tweet text
                if summary == tweet_text or summary == tweet_text[:len(summary)]:
                    logger.warning("Summary is just repeating tweet text, retrying...")
                    continue
                
                # Truncate if needed
                if len(summary) > 200:
                    summary = summary[:197] + "..."
                
                logger.debug(f"Summary generated: {summary[:50]}...")
                return summary
                
            except Exception as e:
                logger.error(f"Error generating summary (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    logger.debug("Retrying...")
                    continue
                else:
                    logger.error("All retry attempts failed")
                    return None
        
        return None
    
    def summarize_batch(self, tweets: list[str]) -> list[Optional[str]]:
        """
        Generate summaries for multiple tweets.
        
        Args:
            tweets: List of tweet texts
        
        Returns:
            List of summaries (or None for failed items)
        """
        summaries = []
        for i, tweet in enumerate(tweets):
            logger.info(f"Summarizing tweet {i+1}/{len(tweets)}...")
            summary = self.summarize(tweet)
            summaries.append(summary)
        
        return summaries


# Global summarizer instance
_summarizer = None


def get_summarizer() -> GeminiSummarizer:
    """Get or create global summarizer instance."""
    global _summarizer
    if _summarizer is None:
        _summarizer = GeminiSummarizer()
    return _summarizer


from src.ai.groq_summarizer import summarize_tweet as groq_summarize

def summarize_tweet(tweet_text: str) -> str:
    """
    Convenience function to summarize a single tweet.
    Now using Groq as the primary engine.
    """
    return groq_summarize(tweet_text)
