#!/usr/bin/env python3
"""
Simple test to verify blockchain connectivity and registration
"""

import requests
import time

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_blockchain_directly():
    """Test blockchain connectivity directly"""
    print("TESTING BLOCKCHAIN CONNECTIVITY")
    print("="*50)
    
    # 1. Create and login user
    timestamp = int(time.time())
    user_data = {
        "email": f"blockchain_direct_{timestamp}@test.com",
        "password": "password123",
        "full_name": "Blockchain Direct Test",
        "role": "manufacturer"
    }
    
    # Create user
    response = requests.post(f"{API_BASE}/auth/register", json=user_data)
    if response.status_code != 200:
        print(f"Failed to create user: {response.text}")
        return
    print("Created user")
    
    # Login
    login_data = {"username": user_data["email"], "password": user_data["password"]}
    response = requests.post(f"{API_BASE}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"Failed to login: {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful")
    
    # 2. Test blockchain status
    print("\n🔍 Testing blockchain status...")
    response = requests.get(f"{API_BASE}/blockchain/status", headers=headers)
    if response.status_code == 200:
        status = response.json()
        print(f"   Network: {status.get('network')}")
        print(f"   Connected: {status.get('connected')}")
        print(f"   Contract Address: {status.get('contract_address')}")
        print(f"   Chain ID: {status.get('chain_id')}")
        print(f"   Latest Block: {status.get('latest_block')}")
        
        if not status.get('connected'):
            print("Blockchain not connected!")
            return
        
        print("Blockchain connected")
    else:
        print(f"Failed to get blockchain status: {response.text}")
        return
    
    # 3. Update user with valid wallet address
    print("\n👛 Adding wallet address...")
    user_info_response = requests.get(f"{API_BASE}/auth/me", headers=headers)
    if user_info_response.status_code == 200:
        user_info = user_info_response.json()
        user_id = user_info["id"]
        
        test_wallets = [
            "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
            "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC", 
            "0x90F79bf6EB2c4f870365E785982E1f101E93b906",
            "0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65",
            "0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc"
        ]
        wallet_address = test_wallets[timestamp % len(test_wallets)]
        update_data = {"wallet_address": wallet_address}
        
        update_response = requests.put(f"{API_BASE}/users/{user_id}", json=update_data, headers=headers)
        if update_response.status_code == 200:
            print(f"Added wallet address: {wallet_address}")
        else:
            print(f"Failed to add wallet address: {update_response.text}")
            return
    else:
        print(f"Failed to get user info: {user_info_response.text}")
        return
    
    # 4.  product and test blockchain registration
    print("\nCreating product with blockchain registration...")
    product_data = {
        "product_name": "Direct Blockchain Test Product",
        "product_description": "Testing direct blockchain registration",
        "category": "electronics",
        "batch_number": "DIRECT-TEST-001",
        "manufacturing_date": "2024-01-15"
    }
    
    response = requests.post(f"{API_BASE}/products/", json=product_data, headers=headers)
    if response.status_code == 200:
        product = response.json()
        print(f"✅ Product created successfully!")
        print(f"   Product ID: {product['id']}")
        print(f"   Product Name: {product['product_name']}")
        print(f"   QR Code Hash: {product['qr_code_hash']}")
        print(f"   Blockchain ID: {product.get('blockchain_id', 'NULL')}")
        
        if product.get('blockchain_id'):
            print(f"🎉 SUCCESS! Blockchain registration worked!")
            print(f"   Blockchain ID: {product['blockchain_id']}")
            
            # getting total products
            total_response = requests.get(f"{API_BASE}/blockchain/products/count", headers=headers)
            if total_response.status_code == 200:
                total = total_response.json()
                print(f"   Total products on blockchain: {total}")
        else:
            print(f"Blockchain registration failed - blockchain_id is null")
            print(f"   This suggests the blockchain transaction failed")
    else:
        print(f"Failed to create product: {response.text}")
        return
    
    print(f"\n🎯 FINAL RESULT:")
    if product.get('blockchain_id'):
        print(f"   ✅ BLOCKCHAIN REGISTRATION SUCCESSFUL!")
        print(f"   The issue has been RESOLVED!")
    else:
        print(f"   Blockchain registration still failing")
        print(f"   Check server logs for detailed error messages")

if __name__ == "__main__":
    test_blockchain_directly()
