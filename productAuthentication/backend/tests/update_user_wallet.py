#!/usr/bin/env python3
"""
Update user's wallet address directly in the database
"""

import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import SessionLocal
from app.models.user import User

# Valid Hardhat address (Account 0)
VALID_WALLET_ADDRESS = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"

def update_user_wallet():
    """Update user's wallet address in database"""
    
    print("🔧 Updating User Wallet Address in Database...")
    print(f"New Wallet Address: {VALID_WALLET_ADDRESS}")
    print("-" * 50)
    
    try:
        # Create database session
        db = SessionLocal()
        
        # Find the manufacturer user
        user = db.query(User).filter(User.email == "manufacturer@example.com").first()
        
        if user:
            print(f"✅ Found user: {user.full_name} ({user.email})")
            print(f"   Current wallet address: {user.wallet_address}")
            
            # Update wallet address
            user.wallet_address = VALID_WALLET_ADDRESS
            db.commit()
            
            print(f"✅ Wallet address updated to: {user.wallet_address}")
            
            # Verify the update
            db.refresh(user)
            print(f"   Verification: {user.wallet_address}")
            
        else:
            print("❌ User not found")
            
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_user_wallet()
