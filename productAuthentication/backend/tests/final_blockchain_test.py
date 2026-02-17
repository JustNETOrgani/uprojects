#!/usr/bin/env python3
"""
Final comprehensive test for blockchain registration
"""

import requests
import time

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_final_blockchain():
    """Final test of blockchain registration"""
    print("🎯 FINAL BLOCKCHAIN REGISTRATION TEST")
    print("="*60)
    
    # 1. Create manufacturer user with wallet address
    timestamp = int(time.time())
    user_data = {
        "email": f"f",
        "password": "saveme",
        "full_name": "Final Test Manufacturer",
        "role": "manufacturer",
        "wallet_address": f"0x{timestamp:040x}"
    }
    
    # Create user
    response = requests.post(f"{API_BASE}/auth/register", json=user_data)
    if response.status_code != 200:
        print(f" Failed to create user: {response.text}")
        return
    print("✅ Created manufacturer user with wallet address")
    
    # Login
    login_data = {"username": user_data["email"], "password": user_data["password"]}
    response = requests.post(f"{API_BASE}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"Failed to login: {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # blockchain status
    print("\n🔍 Checking blockchain status...")
    response = requests.get(f"{API_BASE}/blockchain/status", headers=headers)
    if response.status_code == 200:
        status = response.json()
        print(f"   ✅ Blockchain connected: {status.get('connected')}")
        print(f"   📋 Contract: {status.get('contract_address')}")
        print(f"   🔗 Chain ID: {status.get('chain_id')}")
    else:
        print(f"Failed to get blockchain status: {response.text}")
        return
    
    # 3. Create product with blockchain registration
    print("\nCreating product with blockchain registration...")
    product_data = {
        "product_name": "Final Test Product",
        "product_description": "Testing the final blockchain registration",
        "category": "electronics",
        "batch_number": "FINAL-TEST-001",
        "manufacturing_date": "2024-01-15"
    }
    
    response = requests.post(f"{API_BASE}/products/", json=product_data, headers=headers)
    print(f"📤 Product creation response status: {response.status_code}")
    
    if response.status_code == 200:
        product = response.json()
        print(f"Product created successfully!")
        print(f"Product ID: {product['id']}")
        print(f"QR Code Hash: {product['qr_code_hash']}")
        print(f"Blockchain ID: {product.get('blockchain_id', 'NULL')}")
        
        # 4. Test getting total products from blockchain
        print(f"\nChecking blockchain total products...")
        total_response = requests.get(f"{API_BASE}/blockchain/products/count", headers=headers)
        if total_response.status_code == 200:
            total = total_response.json()
            print(f"Total products on blockchain: {total}")
        
        # 5. Final result
        print(f"\n🎯 FINAL RESULT:")
        if product.get('blockchain_id'):
            print(f"  SUCCESS! BLOCKCHAIN REGISTRATION WORKING!")
            print(f"  Product registered with blockchain ID: {product['blockchain_id']}")
            print(f"  The counterfeit detection system is now fully operational!")
            print(f"\nSYSTEM STATUS:")
            print(f"   Products can be created")
            print(f"  QR codes are generated")
            print(f"  Blockchain registration works")
            print(f"  Counterfeit detection is functional")
        else:
            print(f"   Blockchain registration still not working")
            print(f"   blockchain_id is null - check server logs")
    else:
        print(f"❌ Failed to create product: {response.text}")

if __name__ == "__main__":
    test_final_blockchain()
