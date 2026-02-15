"""
Initialize monitored accounts in the database.
Run this once after deploying to cloud to populate the monitored_accounts table.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from src.database.db import get_db_session, init_db
from src.database.models import MonitoredAccount
from src.utils.config import settings

def init_accounts():
    """Initialize monitored accounts from config."""
    print("🔧 Initializing database and accounts...")
    
    # Initialize database tables
    init_db()
    
    # Get accounts from config
    accounts = settings.monitored_accounts
    
    if not accounts:
        print("⚠️  No accounts found in MONITORED_ACCOUNTS environment variable")
        return
    
    print(f"📋 Found {len(accounts)} accounts to monitor: {', '.join(accounts)}")
    
    # Add accounts to database
    db = get_db_session()
    try:
        added = 0
        skipped = 0
        
        for username in accounts:
            # Check if account already exists
            existing = db.query(MonitoredAccount).filter(
                MonitoredAccount.username == username
            ).first()
            
            if existing:
                print(f"   ⏭️  Skipping {username} (already exists)")
                skipped += 1
                continue
            
            # Add new account
            account = MonitoredAccount(
                username=username,
                display_name=username,  # Can be updated later
                is_active=True
            )
            db.add(account)
            print(f"   ✅ Added {username}")
            added += 1
        
        db.commit()
        print(f"\n🎉 Done! Added {added} new accounts, skipped {skipped} existing")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_accounts()
