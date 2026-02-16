"""
Diagnostic script for Groq AI.
"""
import sys
import asyncio

# Fix Windows encoding issues
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from src.ai.summarizer import summarize_tweet

async def main():
    print("\n🔍 Testing Groq AI Summarization...")
    print("="*60)
    
    test_tweet = "The Ministry of Power is working on a new scheme to upgrade transformers across Delhi to ensure 24x7 electricity."
    result = summarize_tweet(test_tweet)
    
    print(f"Input: {test_tweet}")
    print(f"Output: {result}")
    
    if "[AI Analysis Offline]" in result:
        print("\n❌ Groq AI is NOT working correctly.")
    else:
        print("\n✅ Groq AI is working successfully!")

if __name__ == "__main__":
    asyncio.run(main())
