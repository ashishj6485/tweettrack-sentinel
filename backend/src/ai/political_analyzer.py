"""
Gemini AI Political Risk Analyzer for Minister Ashish Sood's Office.
Analyzes tweets for political threats, grievances, and support.
Uses new google-genai SDK (stable v1 API).
"""
import json
import logging
from typing import Dict, Optional, List
from google import genai
from src.utils.config import settings

logger = logging.getLogger(__name__)

# Initialize Gemini client (new SDK - uses stable v1 API)
client = genai.Client(api_key=settings.gemini_api_key)


class PoliticalAnalyzer:
    """Analyzes tweets for political risk and sentiment."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-lite"):
        """Initialize the political analyzer."""
        self.model_name = model_name
        logger.info(f"Initialized Political Analyzer with model: {self.model_name}")
    
    def _create_analysis_prompt(self, tweet_text: str, username: str) -> str:
        """Create the analysis prompt for Gemini."""
        return f"""You are a Political Risk & Sentiment Analyst for the Office of Ashish Sood, Cabinet Minister (Govt of NCT of Delhi).

**Minister's Portfolios:**
1. Education (Schooling, Higher Ed, Technical)
2. Home (Law & Order, Coordination)
3. Power (Electricity, Billing, Infrastructure)
4. Urban Development (Infrastructure, Planning, Local Colonies)

**Your Task:**
Analyze this tweet from @{username} and classify it.

**Tweet:**
{tweet_text}

**Classification Guidelines:**
- ATTACK: Personal insults, political mockery, or corruption allegations against Minister/AAP
- GRIEVANCE: Specific citizen issues (e.g., power outage, school problems, law & order)
- SUPPORT: Praise or defense of Minister's work or AAP government
- NEUTRAL: General news or mentions without strong emotion

**Portfolio Mapping:**
- Education: Schools, colleges, teachers, exams, curriculum
- Home: Police, safety, crime, law & order
- Power: Electricity, transformers, billing, outages
- Urban Dev: Roads, infrastructure, colonies, planning
- General: If not specific to above portfolios

**Urgency Scoring (1-5):**
- 5: Emergency/Crisis (transformer blast, riot, major corruption allegation)
- 4: High priority (power outage affecting area, serious complaint)
- 3: Medium (general grievance, moderate criticism)
- 2: Low (minor mention, soft criticism)
- 1: Minimal (neutral news, casual mention)

**Sentiment Scoring (-1.0 to 1.0):**
- 1.0: Highly positive/supportive
- 0.5: Somewhat positive
- 0.0: Neutral
- -0.5: Somewhat negative
- -1.0: Highly negative/attack

**CRITICAL: Respond ONLY with valid JSON. No explanation outside JSON. No markdown. Pure JSON only.**

**Output Format:**
{{
  "original_tweet": "{tweet_text[:100]}...",
  "category": "ATTACK|GRIEVANCE|SUPPORT|NEUTRAL",
  "portfolio": "Education|Home|Power|Urban Dev|General",
  "urgency_score": 1-5,
  "sentiment_score": -1.0 to 1.0,
  "summary": "One sentence analysis",
  "action_required": true|false,
  "key_keywords": ["keyword1", "keyword2", "keyword3"]
}}"""
    
    async def analyze_tweet(self, tweet_text: str, username: str) -> Optional[Dict]:
        """
        Analyze a tweet for political risk and sentiment.
        
        Args:
            tweet_text: The tweet content
            username: Twitter handle of poster
        
        Returns:
            Dict with analysis results or None if failed
        """
        try:
            prompt = self._create_analysis_prompt(tweet_text, username)
            
            # Generate analysis using new SDK
            logger.info(f"Analyzing tweet from @{username}...")
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            
            # Parse JSON response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()
            
            # Parse JSON
            analysis = json.loads(response_text)
            
            # Validate required fields
            required_fields = ["category", "portfolio", "urgency_score", "sentiment_score", "summary"]
            for field in required_fields:
                if field not in analysis:
                    logger.error(f"Missing required field: {field}")
                    return None
            
            logger.info(f"Analysis complete: {analysis['category']} (Urgency: {analysis['urgency_score']})")
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Response was: {response_text[:200] if 'response_text' in locals() else 'N/A'}")
            return None
        except Exception as e:
            logger.error(f"Error analyzing tweet: {str(e)}")
            return None


    async def analyze_batch(self, tweets_data: List[Dict]) -> List[Optional[Dict]]:
        """
        Analyze a batch of tweets in a single Gemini call.
        
        Args:
            tweets_data: List of dicts with {'tweet_id': str, 'text': str, 'username': str}
        
        Returns:
            List of analysis dicts (matched to input order)
        """
        if not tweets_data:
            return []
            
        try:
            logger.info(f"🚀 Batch analyzing {len(tweets_data)} tweets...")
            prompt = self._create_batch_analysis_prompt(tweets_data)
            
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            
            response_text = response.text.strip()
            
            # Remove markdown code blocks
            if "```" in response_text:
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                else:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON array
            results_list = json.loads(response_text)
            
            # Map results back to input order for safety
            if not isinstance(results_list, list):
                logger.error("Gemini did not return a JSON array for batch")
                return [None] * len(tweets_data)
                
            # Create a lookup map by ID
            results_map = {str(item.get('tweet_id')): item for item in results_list}
            
            final_ordered_results = []
            for tweet in tweets_data:
                res = results_map.get(str(tweet['tweet_id']))
                final_ordered_results.append(res)
                
            logger.info(f"✅ Finished batch analysis of {len(tweets_data)} tweets")
            return final_ordered_results
            
        except Exception as e:
            logger.error(f"❌ Batch analysis failed: {str(e)}")
            return [None] * len(tweets_data)

    def _create_batch_analysis_prompt(self, tweets_data: List[Dict]) -> str:
        """Create a prompt for batch analysis."""
        # Simple list of tweets for the prompt
        formatted_tweets = []
        for t in tweets_data:
            formatted_tweets.append({
                "tweet_id": str(t['tweet_id']),
                "username": t['username'],
                "text": t['text']
            })
            
        tweets_json = json.dumps(formatted_tweets, ensure_ascii=False)
        
        return f"""You are a Political Risk & Sentiment Analyst for the Office of Ashish Sood, Cabinet Minister (Govt of NCT of Delhi).

Analyze the following list of tweets. Follow the guidelines for each.

**Minister's Portfolios:** Education, Home, Power, Urban Development.

**Analysis Guidelines:**
- ATTACK: insults, mockery, or corruption allegations against Minister/AAP
- GRIEVANCE: Specific citizen issues (power cut, bad roads, etc.)
- SUPPORT: Praise or defense of Minister/AAP
- NEUTRAL: General news

**CRITICAL: Respond ONLY with a valid JSON array of objects. No explanation.**
Each object MUST include the "tweet_id" exactly as provided.

**Tweets to analyze:**
{tweets_json}

**Output Structure Example:**
[
  {{
    "tweet_id": "123",
    "category": "ATTACK",
    "portfolio": "Education",
    "urgency_score": 5,
    "sentiment_score": -0.8,
    "summary": "Reasoning sentence",
    "action_required": true
  }}
]"""


# Global analyzer instance
_analyzer = None


def get_political_analyzer() -> PoliticalAnalyzer:
    """Get or create global analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = PoliticalAnalyzer()
    return _analyzer


async def analyze_political_tweet(tweet_text: str, username: str) -> Optional[Dict]:
    """
    Convenience function to analyze a tweet.
    
    Args:
        tweet_text: Tweet content
        username: Twitter handle
    
    Returns:
        Analysis dict or None
    """
    analyzer = get_political_analyzer()
    return await analyzer.analyze_tweet(tweet_text, username)


async def analyze_batch_tweets(tweets_data: List[Dict]) -> List[Optional[Dict]]:
    """
    Convenience function to analyze a batch of tweets.
    
    Args:
        tweets_data: List of dicts with {'tweet_id': str, 'text': str, 'username': str}
    
    Returns:
        List of analysis dicts
    """
    analyzer = get_political_analyzer()
    return await analyzer.analyze_batch(tweets_data)
