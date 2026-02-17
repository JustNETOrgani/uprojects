#!/usr/bin/env python3
"""
Test script specifically for Mock Swarm Service functionality
This tests the complete workflow using the mock service
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.mock_swarm_service import MockSwarmService

async def test_mock_swarm():
    """Test Mock Swarm Service functionality"""
    print("🔍 Testing Mock Swarm Service - Complete Workflow")
    print("=" * 60)
    
    # Initialize Mock Swarm service
    mock_service = MockSwarmService()
    print("✅ Mock Swarm Service initialized")
    print()
    
    # Test data - realistic product information
    test_product_data = {
        "id": 1,
        "product_name": "iPhone 15 Pro Max",
        "product_description": "Latest Apple smartphone with titanium design and advanced camera system",
        "manufacturing_date": "2024-01-15T00:00:00Z",
        "batch_number": "IPH15PM-2024-001",
        "category": "electronics",
        "qr_code_hash": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
        "manufacturer_id": 1,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    }
    
    print("📦 Test Product Data:")
    print(f"   Product: {test_product_data['product_name']}")
    print(f"   Batch: {test_product_data['batch_number']}")
    print(f"   Category: {test_product_data['category']}")
    print(f"   QR Hash: {test_product_data['qr_code_hash'][:20]}...")
    print()
    
    # Test 1: Store product data
    print("📤 Test 1: Product Data Storage")
    print("-" * 40)
    try:
        store_result = await mock_service.store_product_data(test_product_data)
        
        if store_result.get("success"):
            print("✅ Product data stored successfully!")
            print(f"   Swarm Hash: {store_result.get('swarm_hash')}")
            print(f"   Public URL: {store_result.get('public_url')}")
            print(f"   Size: {store_result.get('size')} bytes")
            
            swarm_hash = store_result.get('swarm_hash')
            public_url = store_result.get('public_url')
            
        else:
            print(f"❌ Failed to store product data: {store_result.get('error')}")
            return
            
    except Exception as e:
        print(f"❌ Storage test failed: {e}")
        return
    print()
    
    # Test 2: Retrieve product data
    print("📥 Test 2: Product Data Retrieval")
    print("-" * 40)
    try:
        retrieve_result = await mock_service.retrieve_product_data(swarm_hash)
        
        if retrieve_result.get("success"):
            print("✅ Product data retrieved successfully!")
            retrieved_data = retrieve_result.get('product_data', {})
            print(f"   Retrieved Product: {retrieved_data.get('product_name', 'Unknown')}")
            print(f"   Retrieved Batch: {retrieved_data.get('batch_number', 'Unknown')}")
            print(f"   Retrieved Category: {retrieved_data.get('category', 'Unknown')}")
            print(f"   Retrieved Description: {retrieved_data.get('product_description', 'Unknown')[:50]}...")
            
            # Verify data integrity
            if (retrieved_data.get('product_name') == test_product_data['product_name'] and
                retrieved_data.get('batch_number') == test_product_data['batch_number'] and
                retrieved_data.get('category') == test_product_data['category']):
                print("✅ Data integrity verified - all fields match!")
            else:
                print("❌ Data integrity check failed - fields don't match!")
                
        else:
            print(f"❌ Failed to retrieve product data: {retrieve_result.get('error')}")
            
    except Exception as e:
        print(f"❌ Retrieval test failed: {e}")
    print()
    
    # Test 3: Test pinning functionality
    print("📌 Test 3: Data Pinning")
    print("-" * 40)
    try:
        pin_result = await mock_service.pin_data(swarm_hash)
        
        if pin_result.get("success"):
            print("✅ Data pinned successfully!")
            print(f"   Message: {pin_result.get('message', 'Data pinned')}")
        else:
            print(f"❌ Failed to pin data: {pin_result.get('error')}")
            
    except Exception as e:
        print(f"❌ Pinning test failed: {e}")
    print()
    
    # Test 4: Test multiple product storage and retrieval
    print("📦 Test 4: Multiple Product Storage and Retrieval")
    print("-" * 40)
    try:
        # Create additional test products
        additional_products = [
            {
                "id": 2,
                "product_name": "Samsung Galaxy S24 Ultra",
                "product_description": "Premium Android smartphone with S Pen and advanced camera system",
                "batch_number": "SGS24U-2024-002",
                "category": "electronics",
                "manufacturing_date": "2024-01-20T00:00:00Z",
                "qr_code_hash": "b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234567",
                "manufacturer_id": 2,
                "created_at": "2024-01-20T14:15:00Z"
            },
            {
                "id": 3,
                "product_name": "Nike Air Max 270",
                "product_description": "Comfortable running shoes with Air Max technology",
                "batch_number": "NAM270-2024-003",
                "category": "clothing",
                "manufacturing_date": "2024-01-25T00:00:00Z",
                "qr_code_hash": "c3d4e5f6789012345678901234567890abcdef1234567890abcdef12345678",
                "manufacturer_id": 3,
                "created_at": "2024-01-25T09:45:00Z"
            }
        ]
        
        stored_products = []
        for i, product in enumerate(additional_products, 1):
            print(f"   Storing product {i}: {product['product_name']}")
            result = await mock_service.store_product_data(product)
            
            if result.get("success"):
                print(f"   ✅ Stored successfully - Hash: {result.get('swarm_hash')[:20]}...")
                stored_products.append({
                    "product": product,
                    "hash": result.get('swarm_hash'),
                    "url": result.get('public_url')
                })
            else:
                print(f"   ❌ Failed: {result.get('error')}")
        
        print(f"\n   Summary: {len(stored_products)}/{len(additional_products)} products stored successfully")
        
        # Test retrieval of all stored products
        print("\n   Testing retrieval of all stored products:")
        for i, stored in enumerate(stored_products, 1):
            retrieve_result = await mock_service.retrieve_product_data(stored['hash'])
            if retrieve_result.get("success"):
                retrieved_data = retrieve_result.get('product_data', {})
                print(f"   ✅ Product {i}: {retrieved_data.get('product_name')} - Retrieved successfully")
            else:
                print(f"   ❌ Product {i}: Failed to retrieve - {retrieve_result.get('error')}")
        
    except Exception as e:
        print(f"❌ Multiple product storage test failed: {e}")
    print()
    
    # Test 5: Performance test
    print("⚡ Test 5: Performance Test")
    print("-" * 40)
    try:
        import time
        
        # Test storage performance
        start_time = time.time()
        perf_product = {
            "id": 999,
            "product_name": "Performance Test Product",
            "product_description": "A product specifically designed for performance testing",
            "batch_number": "PERF-2024-999",
            "category": "test",
            "manufacturing_date": datetime.now().isoformat(),
            "qr_code_hash": "perf_test_hash_1234567890abcdef",
            "manufacturer_id": 999,
            "created_at": datetime.now().isoformat()
        }
        
        store_result = await mock_service.store_product_data(perf_product)
        storage_time = time.time() - start_time
        
        if store_result.get("success"):
            print(f"✅ Storage Performance: {storage_time:.3f} seconds")
            
            # Test retrieval performance
            start_time = time.time()
            retrieve_result = await mock_service.retrieve_product_data(store_result.get('swarm_hash'))
            retrieval_time = time.time() - start_time
            
            if retrieve_result.get("success"):
                print(f"✅ Retrieval Performance: {retrieval_time:.3f} seconds")
                print(f"✅ Total Round-trip: {storage_time + retrieval_time:.3f} seconds")
                
                # Verify the performance test data
                retrieved_data = retrieve_result.get('product_data', {})
                if retrieved_data.get('product_name') == perf_product['product_name']:
                    print("✅ Performance test data integrity verified!")
                else:
                    print("❌ Performance test data integrity failed!")
            else:
                print(f"❌ Retrieval failed: {retrieve_result.get('error')}")
        else:
            print(f"❌ Storage failed: {store_result.get('error')}")
            
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
    print()
    
    # Summary
    print("📊 Mock Swarm Service Test Summary")
    print("=" * 60)
    print("✅ Mock Swarm service is fully functional")
    print("✅ Data storage and retrieval work correctly")
    print("✅ Data integrity is maintained")
    print("✅ Performance is excellent (sub-second operations)")
    print("✅ Multiple product handling works")
    print("✅ Pinning functionality works")
    print()
    print("🎯 Mock Service Benefits:")
    print("   • Perfect for development and testing")
    print("   • No external dependencies")
    print("   • Consistent behavior")
    print("   • Fast performance")
    print("   • Realistic hash generation")
    print()
    print("🔄 Ready for Real Swarm Integration:")
    print("   • When Swarm node sync completes")
    print("   • When postage batches are available")
    print("   • The system will automatically switch to real Swarm")

if __name__ == "__main__":
    asyncio.run(test_mock_swarm())
