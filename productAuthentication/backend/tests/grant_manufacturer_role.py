#!/usr/bin/env python3
"""
Grant MANUFACTURER_ROLE to test wallet addresses
"""

import requests

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def grant_manufacturer_role():
    """Grant MANUFACTURER_ROLE to test wallet addresses"""
    print("🔐 GRANTING MANUFACTURER ROLE TO TEST WALLETS")
    print("="*60)
    
    # Create admin user first
    admin_data = {
        "email": "admin@test.com",
        "password": "admin123",
        "full_name": "Admin User",
        "role": "admin"
    }
    
    # Try to create admin or login if exists
    response = requests.post(f"{API_BASE}/auth/register", json=admin_data)
    if response.status_code == 422:  # User exists
        pass
    elif response.status_code != 200:
        print(f"❌ Failed to create admin: {response.text}")
        return
    
    # Login as admin
    login_data = {"username": admin_data["email"], "password": admin_data["password"]}
    response = requests.post(f"{API_BASE}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"❌ Failed to login as admin: {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Admin login successful")
    
    # Test wallet addresses that need MANUFACTURER_ROLE
    test_wallets = [
        "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
        "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC", 
        "0x90F79bf6EB2c4f870365E785982E1f101E93b906",
        "0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65",
        "0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc"
    ]
    
    for wallet in test_wallets:
        print(f"\n🔑 Granting MANUFACTURER_ROLE to {wallet}")
        
        grant_data = {
            "role": "MANUFACTURER_ROLE",
            "account": wallet
        }
        
        response = requests.post(f"{API_BASE}/blockchain/grant-role", json=grant_data, headers=headers)
        if response.status_code == 200:
            print(f"   ✅ Successfully granted MANUFACTURER_ROLE")
        else:
            print(f"   ❌ Failed to grant role: {response.text}")
    
    print(f"\n🎯 Role granting completed!")
    print(f"   Test wallets should now be able to register products on blockchain")

if __name__ == "__main__":
    grant_manufacturer_role()
