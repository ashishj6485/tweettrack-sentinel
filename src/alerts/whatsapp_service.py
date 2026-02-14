"""WhatsApp Alert Service using Twilio. Supports multiple recipients."""
import logging
from typing import Dict, List
from twilio.rest import Client
from src.utils.config import settings

logger = logging.getLogger(__name__)


class WhatsAppAlertService:
    """Service for sending WhatsApp alerts via Twilio to multiple recipients."""
    
    def __init__(self):
        """Initialize Twilio client."""
        self.account_sid = settings.twilio_account_sid
        self.auth_token = settings.twilio_auth_token
        self.from_number = settings.twilio_whatsapp_from
        self.to_numbers = settings.whatsapp_recipients  # List of recipients
        
        # Only initialize client if credentials are provided
        self.client = None
        if self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                logger.info(f"WhatsApp Alert Service initialized ({len(self.to_numbers)} recipients)")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
        else:
            logger.warning("Twilio credentials not configured. WhatsApp alerts disabled.")
    
    def _format_message(self, tweet_data: Dict, analysis: Dict) -> str:
        """Format WhatsApp message."""
        tweet_text = tweet_data.get('text', '')
        username = tweet_data.get('username', 'Unknown')
        tweet_link = tweet_data.get('link', '')
        
        category = analysis.get('category', 'NEUTRAL')
        portfolio = analysis.get('portfolio', 'General')
        summary = analysis.get('summary', 'No summary available')
        
        # Create headline based on category
        if category == 'ATTACK':
            headline = f"Political Attack Detected - {portfolio}"
        elif category == 'GRIEVANCE':
            headline = f"Citizen Grievance - {portfolio}"
        elif category == 'SUPPORT':
            headline = f"Support Message - {portfolio}"
        else:
            headline = f"Mention - {portfolio}"
        
        primary_statement = tweet_text[:200] if len(tweet_text) > 200 else tweet_text
        reason = analysis.get('summary', 'AI analysis unavailable')
        
        message = f"""TweetTrack Sentinel
-----------------
Caption: {headline}

{primary_statement}
-----------------
By: @{username}
-----------------
Classification: {category}
Portfolio: {portfolio}
Urgency: {analysis.get('urgency_score', 0)}/5
Sentiment: {analysis.get('sentiment_score', 0.0):.2f}
-----------------
Reason: {reason}
-----------------
Post Link: {tweet_link}"""
        
        return message
    
    async def send_alert(self, tweet_data: Dict, analysis: Dict, max_retries: int = 3) -> bool:
        """
        Send WhatsApp alert to ALL recipients.
        
        Returns:
            True if sent to at least one recipient successfully
        """
        if not self.client:
            logger.warning("Twilio client not initialized. Skipping WhatsApp alert.")
            return False
        
        if not self.to_numbers:
            logger.warning("No WhatsApp recipients configured.")
            return False
        
        message_body = self._format_message(tweet_data, analysis)
        
        any_success = False
        for to_number in self.to_numbers:
            success = await self._send_to_number(message_body, to_number, max_retries)
            if success:
                any_success = True
        
        return any_success
    
    async def _send_to_number(self, message_body: str, to_number: str, max_retries: int = 3) -> bool:
        """Send message to a single WhatsApp number with retries."""
        for attempt in range(max_retries):
            try:
                logger.info(f"Sending WhatsApp alert to {to_number} (attempt {attempt + 1}/{max_retries})...")
                
                message = self.client.messages.create(
                    body=message_body,
                    from_=self.from_number,
                    to=to_number
                )
                
                logger.info(f"WhatsApp alert sent to {to_number}! SID: {message.sid}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to send to {to_number} (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    continue
                else:
                    logger.error(f"All retry attempts failed for {to_number}")
                    return False
        
        return False
    
    def should_send_alert(self, analysis: Dict) -> bool:
        """
        Determine if alert should be sent based on analysis.
        Sends alert for EVERY new tweet (urgency >= 1).
        """
        category = analysis.get('category', 'NEUTRAL')
        urgency = analysis.get('urgency_score', 0)
        
        # Send alert for EVERY tweet
        if urgency >= 1:
            logger.info(f"Alert triggered: {category} (Urgency: {urgency}/5)")
            return True
        
        # If somehow urgency is 0, still send for ATTACK category
        if category == 'ATTACK':
            logger.info(f"ATTACK category - Alert triggered")
            return True
        
        logger.info(f"No alert (category: {category}, urgency: {urgency})")
        return False


# Global service instance
_whatsapp_service = None


def get_whatsapp_service() -> WhatsAppAlertService:
    """Get or create global WhatsApp service instance."""
    global _whatsapp_service
    if _whatsapp_service is None:
        _whatsapp_service = WhatsAppAlertService()
    return _whatsapp_service
