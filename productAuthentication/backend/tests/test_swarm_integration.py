#!/usr/bin/env python3
"""
Test script to verify Swarm integration is working
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.swarm_service import SwarmService
from app.core.config import settings

async def test_swarm_integration():
    """Test Swarm service integration"""
    print("🔍 Testing Swarm Integration...")
    print(f"Swarm Gateway: {settings.SWARM_GATEWAY}")
    
    # Initialize Swarm service
    swarm_service = SwarmService()
    
    print(f"Using Mock Service: {swarm_service.use_mock}")
    print(f"Swarm API URL: {swarm_service.swarm_api_url}")
    
    # Test data
    test_product_data = {
        "id": 1,
        "product_name": "Test Product",
        "product_description": "A test product for Swarm integration",
        "manufacturing_date": "2024-01-01T00:00:00Z",
        "batch_number": "TEST001",
        "category": "electronics",
        "qr_code_hash": "test_hash_123",
        "manufacturer_id": 1,
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    try:
        # Test 1: Store product data
        print("\n📤 Testing product data storage...")
        store_result = await swarm_service.store_product_data(test_product_data)
        
        if store_result.get("success"):
            print("✅ Product data stored successfully!")
            print(f"   Swarm Hash: {store_result.get('swarm_hash')}")
            print(f"   Public URL: {store_result.get('public_url')}")
            
            # Test 2: Retrieve product data
            print("\n📥 Testing product data retrieval...")
            swarm_hash = store_result.get('swarm_hash')
            retrieve_result = await swarm_service.retrieve_product_data(swarm_hash)
            
            if retrieve_result.get("success"):
                print("✅ Product data retrieved successfully!")
                retrieved_data = retrieve_result.get('product_data')
                print(f"   Retrieved Product Name: {retrieved_data.get('product_name')}")
                print(f"   Retrieved Batch Number: {retrieved_data.get('batch_number')}")
                
                # Verify data integrity
                if retrieved_data.get('product_name') == test_product_data['product_name']:
                    print("✅ Data integrity verified!")
                else:
                    print("❌ Data integrity check failed!")
            else:
                print(f"❌ Failed to retrieve product data: {retrieve_result.get('error')}")
        else:
            print(f"❌ Failed to store product data: {store_result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error during Swarm integration test: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Check connection status
    print("\n🔗 Testing Swarm connection...")
    try:
        is_connected = await swarm_service.is_connected()
        print(f"Swarm Connection Status: {'✅ Connected' if is_connected else '❌ Not Connected'}")
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
    
    # Test 4: Get node info
    print("\n📊 Getting Swarm node info...")
    try:
        node_info = await swarm_service.get_node_info()
        print(f"Node Info: {node_info}")
    except Exception as e:
        print(f"❌ Failed to get node info: {e}")

if __name__ == "__main__":
    asyncio.run(test_swarm_integration())
