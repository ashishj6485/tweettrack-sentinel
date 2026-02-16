"""
Diagnostic script for Groq AI and WhatsApp Alerts.
"""
import sys
import asyncio

# Fix Windows encoding issues
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from src.ai.summarizer import summarize_tweet
from src.ai.political_analyzer import analyze_political_tweet
from src.alerts.whatsapp_service import get_whatsapp_service

async def test_full_pipeline():
    print("\n🔍 Testing TweetTrack Sentinel Pipeline (Groq + WhatsApp)...")
    print("="*60)
    
    test_tweet_text = "The education system in Delhi is failing! Schools are overcrowded and lack basic facilities. Needs immediate attention @MinisterSood"
    username = "citizen_delhi"
    
    # 1. Test Summarization
    print("\n1. Testing AI Summarization (Groq)...")
    summary = summarize_tweet(test_tweet_text)
    print(f"Summary: {summary}")
    
    # 2. Test Political Analysis
    print("\n2. Testing Political Risk Analysis (Groq)...")
    analysis = await analyze_political_tweet(test_tweet_text, username)
    print(f"Analysis: {analysis}")
    
    if analysis:
        # 3. Test WhatsApp Alert
        print("\n3. Testing WhatsApp Alert Service (Twilio)...")
        whatsapp = get_whatsapp_service()
        
        tweet_data = {
            'username': username,
            'text': test_tweet_text,
            'link': 'https://twitter.com/test/status/123456789'
        }
        
        should_send = whatsapp.should_send_alert(analysis)
        print(f"Should send alert: {should_send}")
        
        if should_send:
            print("Sending WhatsApp alert...")
            success = await whatsapp.send_alert(tweet_data, analysis)
            if success:
                print("✅ WhatsApp alert sent successfully!")
            else:
                print("❌ WhatsApp alert failed to send. Check Twilio sandbox/verification.")
        else:
            print("⏭️ Alert criteria not met.")
    else:
        print("❌ Political analysis failed.")

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
