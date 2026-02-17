#!/usr/bin/env python3
"""
Test blockchain service initialization
"""

import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.blockchain_service import BlockchainService
from app.core.config import settings
import asyncio

async def test_blockchain_init():
    """Test blockchain service initialization"""
    
    print("🔍 Testing Blockchain Service Initialization...")
    print(f"ETHEREUM_NETWORK: {settings.ETHEREUM_NETWORK}")
    print(f"CONTRACT_ADDRESS: {settings.CONTRACT_ADDRESS}")
    print("-" * 50)
    
    try:
        # Create blockchain service
        print("1. Creating BlockchainService instance...")
        blockchain_service = BlockchainService()
        
        print("2. Initializing blockchain service...")
        await blockchain_service.initialize()
        
        print("3. Testing connection...")
        is_connected = await blockchain_service.is_connected()
        print(f"   Connected: {is_connected}")
        
        if is_connected:
            print("4. Getting network info...")
            network_info = await blockchain_service.get_network_info()
            print(f"   Network Info: {network_info}")
            
            print("5. Testing contract interaction...")
            total_products = await blockchain_service.get_total_products()
            print(f"   Total Products: {total_products}")
            
            print("✅ Blockchain service initialized successfully!")
        else:
            print("❌ Blockchain service not connected")
            
    except Exception as e:
        print(f"❌ Error during initialization: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_blockchain_init())
