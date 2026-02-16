"""
AI Summarization module using Groq Cloud API.
"""
import os
import logging
from typing import Optional
from groq import Groq
from src.utils.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Groq client
client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None

class GroqSummarizer:
    """AI summarizer using Groq Cloud API (Llama models)."""
    
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        """Initialize Groq summarizer."""
        self.model_name = model_name
        if not client:
            logger.error("❌ Groq API key not found in environment variables!")
        else:
            logger.info(f"✅ Initialized Groq summarizer with model: {self.model_name}")
    
    def summarize(self, tweet_text: str, max_retries: int = 3) -> Optional[str]:
        """
        Generate a concise summary of a tweet using Groq.
        """
        if not client:
            return None

        prompt = f"""Summarize this tweet in one clean, concise sentence. 
DO NOT repeat the tweet text. Capturing the key point is the goal.
If the tweet is in Hindi, summarize in Hindi. If English, summarize in English.
Keep the summary under 120 characters.

Tweet: {tweet_text}

Summary:"""
        
        for attempt in range(max_retries):
            try:
                completion = client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a professional social media analyst."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5,
                    max_tokens=100
                )
                
                summary = completion.choices[0].message.content.strip()
                
                if not summary or summary == tweet_text:
                    continue
                    
                return summary
                
            except Exception as e:
                logger.error(f"Error generating Groq summary (attempt {attempt + 1}): {str(e)}")
                if "429" in str(e): # Rate limit
                    logger.warning("Groq rate limit hit, consider 8b model")
                if attempt == max_retries - 1:
                    return None
        
        return None

# Global summarizer instance
_summarizer = None

def get_summarizer() -> GroqSummarizer:
    """Get or create global summarizer instance."""
    global _summarizer
    if _summarizer is None:
        # We can use llama-3.1-8b-instant if 70b is too slow or hitting limits
        _summarizer = GroqSummarizer()
    return _summarizer

def summarize_tweet(tweet_text: str) -> str:
    """Convenience function to summarize a single tweet."""
    summarizer = get_summarizer()
    summary = summarizer.summarize(tweet_text)
    
    if summary is None:
        return "[AI Analysis Offline] Waiting for quota reset..."
    
    return summary
