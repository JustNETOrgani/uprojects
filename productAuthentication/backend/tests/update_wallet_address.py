#!/usr/bin/env python3
"""
Update user's wallet address with valid Hardhat address
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8000"
MANUFACTURER_DATA = {
    "email": "manufacturer@example.com",
    "password": "password123"
}

# Valid Hardhat address (Account 0)
VALID_WALLET_ADDRESS = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"

def update_wallet_address():
    """Update user's wallet address"""
    
    print("🔧 Updating User Wallet Address...")
    print(f"API URL: {API_BASE_URL}")
    print(f"New Wallet Address: {VALID_WALLET_ADDRESS}")
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
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Update wallet address
        print("\n2. Updating wallet address...")
        update_data = {
            "wallet_address": VALID_WALLET_ADDRESS
        }
        
        update_response = requests.put(
            f"{API_BASE_URL}/api/v1/auth/update-profile",
            json=update_data,
            headers=headers
        )
        
        if update_response.status_code == 200:
            print("✅ Wallet address updated successfully!")
            
            # Verify the update
            print("\n3. Verifying wallet address update...")
            user_response = requests.get(
                f"{API_BASE_URL}/api/v1/auth/me",
                headers=headers
            )
            
            if user_response.status_code == 200:
                user_info = user_response.json()
                print(f"   Current Wallet Address: {user_info.get('wallet_address')}")
                
                if user_info.get('wallet_address') == VALID_WALLET_ADDRESS:
                    print("✅ Wallet address verification successful!")
                else:
                    print("❌ Wallet address verification failed")
            else:
                print(f"❌ Failed to verify update: {user_response.status_code}")
        else:
            print(f"❌ Failed to update wallet address: {update_response.status_code}")
            print(f"   Response: {update_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the backend server is running")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_wallet_address()
