#!/usr/bin/env python3
"""
Test script to check blockchain connection
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8000"
MANUFACTURER_DATA = {
    "email": "manufacturer@example.com",
    "password": "password123"
}

def test_blockchain_connection():
    """Test the blockchain connection"""
    
    print("🔍 Testing Blockchain Connection...")
    print(f"API URL: {API_BASE_URL}")
    print("-" * 50)
    
    try:
        # First, login to get a token
        print("1. Logging in to get access token...")
        login_response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/login",
            data={
                "username": MANUFACTURER_DATA["email"],
                "password": MANUFACTURER_DATA["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return
        
        token_data = login_response.json()
        access_token = token_data.get('access_token')
        print(f"✅ Login successful! Token: {access_token[:20]}...")
        
        # Now test blockchain status
        print("\n2. Testing blockchain status...")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        blockchain_response = requests.get(
            f"{API_BASE_URL}/api/v1/blockchain/status",
            headers=headers
        )
        
        if blockchain_response.status_code == 200:
            blockchain_data = blockchain_response.json()
            print("✅ Blockchain status retrieved successfully!")
            print(json.dumps(blockchain_data, indent=2))
            
            # Check if connected
            if blockchain_data.get('connected'):
                print("\n🎉 Blockchain is connected and working!")
            else:
                print("\n⚠️  Blockchain is not connected. Issues:")
                print(f"   - Network: {blockchain_data.get('network')}")
                print(f"   - Contract Address: {blockchain_data.get('contract_address')}")
                print(f"   - Chain ID: {blockchain_data.get('chain_id')}")
        else:
            print(f"❌ Blockchain status failed: {blockchain_response.status_code}")
            print(f"Response: {blockchain_response.text}")
            
        # Test total products
        print("\n3. Testing total products count...")
        products_response = requests.get(
            f"{API_BASE_URL}/api/v1/blockchain/products/count",
            headers=headers
        )
        
        if products_response.status_code == 200:
            products_data = products_response.json()
            print("✅ Products count retrieved successfully!")
            print(json.dumps(products_data, indent=2))
        else:
            print(f"❌ Products count failed: {products_response.status_code}")
            print(f"Response: {products_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the backend server is running")
        print("   Run: cd backend && source venv/bin/activate && uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_blockchain_connection()
