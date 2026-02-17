#!/usr/bin/env python3
"""
Test to check blockchain registration process
"""

import requests
import time

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_blockchain_registration():
    """Test blockchain registration process"""
    print("🔗 TESTING BLOCKCHAIN REGISTRATION")
    print("="*50)
    
    # 1. Create a manufacturer user
    timestamp = int(time.time())
    user_data = {
        "email": f"blockchain_test_{timestamp}@test.com",
        "password": "password123",
        "full_name": "Blockchain Test Manufacturer",
        "role": "manufacturer"
    }
    
    response = requests.post(f"{API_BASE}/auth/register", json=user_data)
    if response.status_code != 200:
        print(f"❌ Failed to create user: {response.text}")
        return
    
    print("✅ Created manufacturer user")
    
    # 2. Login to get token
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    
    response = requests.post(f"{API_BASE}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"❌ Failed to login: {response.text}")
        return
    
    token = response.json()["access_token"]
    print("✅ Login successful")
    
    # 3. Update user with wallet address
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get current user info to get user ID
    user_info_response = requests.get(f"{API_BASE}/auth/me", headers=headers)
    if user_info_response.status_code == 200:
        user_info = user_info_response.json()
        user_id = user_info["id"]
        
        # Update user with wallet address (use one of the Hardhat test addresses)
        test_addresses = [
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
            "0x70997970C51812dc3A010C7d01b50e0d17dc79C8", 
            "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
            "0x90F79bf6EB2c4f870365E785982E1f101E93b906",
            "0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65"
        ]
        wallet_index = timestamp % len(test_addresses)
        update_data = {
            "wallet_address": test_addresses[wallet_index]
        }
        
        print(f"Updating user {user_id} with wallet address: {update_data['wallet_address']}")
        update_response = requests.put(f"{API_BASE}/users/{user_id}", json=update_data, headers=headers)
        print(f"Update response status: {update_response.status_code}")
        print(f"Update response text: {update_response.text}")
        
        if update_response.status_code == 200:
            print("✅ Added wallet address to user")
            print(f"   Wallet Address: {update_data['wallet_address']}")
        else:
            print(f"⚠️  Failed to add wallet address: {update_response.text}")
    else:
        print(f"⚠️  Failed to get user info: {user_info_response.text}")
    
    # 4. Create a product (this should trigger blockchain registration)
    product_data = {
        "product_name": "Blockchain Test Product",
        "product_description": "A test product to verify blockchain registration",
        "category": "electronics",
        "batch_number": "BLOCKCHAIN-TEST-001",
        "manufacturing_date": "2024-01-15"
    }
    
    print(f"\n📦 Creating product with blockchain registration...")
    response = requests.post(f"{API_BASE}/products/", json=product_data, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to create product: {response.text}")
        return
    
    product = response.json()
    print(f"✅ Created product: {product['product_name']}")
    print(f"   Product ID: {product['id']}")
    print(f"   QR Code Hash: {product['qr_code_hash']}")
    print(f"   Blockchain ID: {product.get('blockchain_id', 'NULL')}")
    
    if product.get('blockchain_id'):
        print(f"   ✅ Blockchain registration successful!")
        print(f"   📋 Blockchain ID: {product['blockchain_id']}")
    else:
        print(f"   ❌ Blockchain registration failed - blockchain_id is null")
        print(f"   🔍 This could be due to:")
        print(f"      - Blockchain service not initialized")
        print(f"      - Contract address mismatch")
        print(f"      - Network connection issues")
        print(f"      - Transaction failure")
    
    # 5. Check blockchain network status
    print(f"\n🌐 Checking blockchain network status...")
    try:
        network_response = requests.get(f"{API_BASE}/blockchain/status", headers=headers)
        if network_response.status_code == 200:
            network_info = network_response.json()
            print(f"   Network: {network_info.get('network')}")
            print(f"   Connected: {network_info.get('connected')}")
            print(f"   Contract Address: {network_info.get('contract_address')}")
            print(f"   Chain ID: {network_info.get('chain_id')}")
        else:
            print(f"   ❌ Failed to get network info: {network_response.text}")
    except Exception as e:
        print(f"   ❌ Error checking network: {e}")
    
    # 6. Check total products on blockchain
    print(f"\n📊 Checking total products on blockchain...")
    try:
        total_response = requests.get(f"{API_BASE}/blockchain/products/count", headers=headers)
        if total_response.status_code == 200:
            total_products = total_response.json()
            print(f"   Total products on blockchain: {total_products}")
        else:
            print(f"   ❌ Failed to get total products: {total_response.text}")
    except Exception as e:
        print(f"   ❌ Error checking total products: {e}")
    
    print(f"\n🎯 BLOCKCHAIN REGISTRATION SUMMARY:")
    print(f"   Product Created: ✅")
    print(f"   QR Code Generated: ✅")
    print(f"   Blockchain Registration: {'✅' if product.get('blockchain_id') else '❌'}")
    
    if not product.get('blockchain_id'):
        print(f"\n🔧 TROUBLESHOOTING:")
        print(f"   1. Check if local blockchain is running: npx hardhat node")
        print(f"   2. Verify contract is deployed: npx hardhat run scripts/deploy.js --network localhost")
        print(f"   3. Check contract address in config: {product.get('blockchain_id', 'NULL')}")
        print(f"   4. Check server logs for blockchain errors")

if __name__ == "__main__":
    test_blockchain_registration()
