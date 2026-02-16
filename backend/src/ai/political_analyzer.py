"""
Political Risk Analyzer using Groq Cloud API (Llama models).
Analyzes tweets for political threats, grievances, and support.
Free alternative to Gemini.
"""
import json
import logging
import os
from typing import Dict, Optional, List
from groq import Groq
from src.utils.config import settings

logger = logging.getLogger(__name__)

# Initialize Groq client
client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None

class PoliticalAnalyzer:
    """Analyzes tweets for political risk and sentiment using Groq."""
    
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        """Initialize the political analyzer."""
        self.model_name = model_name
        logger.info(f"Initialized Groq Political Analyzer with model: {self.model_name}")
    
    def _create_analysis_prompt(self, tweet_text: str, username: str) -> str:
        """Create the analysis prompt for Groq."""
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

**CRITICAL: Respond ONLY with valid JSON. No conversation or markdown.**

**Output Format:**
{{
  "category": "ATTACK|GRIEVANCE|SUPPORT|NEUTRAL",
  "portfolio": "Education|Home|Power|Urban Development|General",
  "urgency_score": 1-5,
  "sentiment_score": -1.0 to 1.0,
  "summary": "One sentence professional analysis",
  "action_required": true|false
}}"""

    async def analyze_tweet(self, tweet_text: str, username: str) -> Optional[Dict]:
        """Analyze a single tweet using Groq."""
        if not client: return None
        try:
            prompt = self._create_analysis_prompt(tweet_text, username)
            completion = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a political data scientist providing raw JSON analysis."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            
            return json.loads(completion.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error in Groq analysis: {e}")
            return None

    async def analyze_batch(self, tweets_data: List[Dict]) -> List[Optional[Dict]]:
        """Analyze a batch of tweets in a single Groq call."""
        if not client or not tweets_data: return [None] * len(tweets_data)
        
        try:
            logger.info(f"🚀 Batch analyzing {len(tweets_data)} tweets with Groq...")
            
            # Simple batch list
            batch_list = [{"tweet_id": str(t['tweet_id']), "text": t['text'], "username": t['username']} for t in tweets_data]
            
            prompt = f"""You are a Political Risk & Sentiment Analyst for the Office of Ashish Sood, Cabinet Minister (Govt of NCT of Delhi).

Analyze the following list of tweets.

**Minister's Portfolios:** Education, Home, Power, Urban Development.

**Classification Guidelines:**
- ATTACK: Personal insults, political mockery, or corruption allegations against Minister/AAP
- GRIEVANCE: Specific citizen issues (power cuts, bad roads, etc.)
- SUPPORT: Praise or defense of Minister/AAP
- NEUTRAL: General news

**Urgency Scoring (1-5):** 5 is highest (crisis), 1 is minimal.
**Sentiment Scoring (-1.0 to 1.0):** -1.0 is highly negative, 1.0 is highly positive.

**Tweets to analyze:**
{json.dumps(batch_list)}

**CRITICAL: Respond ONLY with a valid JSON array of objects. No explanation.**
Each object MUST include the "tweet_id" exactly as provided.

Output Format for each object:
{{
  "tweet_id": "...",
  "category": "ATTACK|GRIEVANCE|SUPPORT|NEUTRAL",
  "portfolio": "Education|Home|Power|Urban Development|General",
  "urgency_score": 1-5,
  "sentiment_score": -1.0 to 1.0,
  "summary": "One sentence professional analysis",
  "action_required": true|false
}}"""

            completion = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Return ONLY a JSON array. No text before or after."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"} if "70b" in self.model_name else None,
                temperature=0.1
            )
            
            # The 70b-versatile supports json_object which might wrap the array in an object
            resp = json.loads(completion.choices[0].message.content)
            
            # If it wrapped it in a key (like "results"), extract it
            if isinstance(resp, dict):
                for val in resp.values():
                    if isinstance(val, list):
                        results_list = val
                        break
                else:
                    results_list = [resp] # maybe single object
            else:
                results_list = resp

            # Create a lookup map by ID
            results_map = {str(item.get('tweet_id')): item for item in results_list if isinstance(item, dict)}
            
            return [results_map.get(str(tweet['tweet_id'])) for tweet in tweets_data]
            
        except Exception as e:
            logger.error(f"❌ Groq Batch analysis failed: {str(e)}")
            return [None] * len(tweets_data)

# Global instances
_analyzer = None

def get_political_analyzer() -> PoliticalAnalyzer:
    global _analyzer
    if _analyzer is None: _analyzer = PoliticalAnalyzer()
    return _analyzer

async def analyze_political_tweet(tweet_text: str, username: str) -> Optional[Dict]:
    return await get_political_analyzer().analyze_tweet(tweet_text, username)

async def analyze_batch_tweets(tweets_data: List[Dict]) -> List[Optional[Dict]]:
    return await get_political_analyzer().analyze_batch(tweets_data)
