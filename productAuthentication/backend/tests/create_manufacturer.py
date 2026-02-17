#!/usr/bin/env python3
"""
Script to create a manufacturer user for the Anti-Counterfeit application
"""

import requests
import json
import sys

# Configuration
API_BASE_URL = "http://localhost:8000"
MANUFACTURER_DATA = {
    "email": "manufacturer@example.com",
    "password": "password123",
    "full_name": "John Manufacturer",
    "role": "manufacturer",
    "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"  # e.g wallet address
}

def create_manufacturer_user():
    """Create a manufacturer user via the API"""
    
    print("🚀 Creating Manufacturer User...")
    print(f"API URL: {API_BASE_URL}")
    print(f"User Data: {json.dumps(MANUFACTURER_DATA, indent=2)}")
    print("-" * 50)
    
    try:
        # Create the user
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/register",
            json=MANUFACTURER_DATA,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Manufacturer user created successfully!")
            print(f"User ID: {user_data.get('id')}")
            print(f"Email: {user_data.get('email')}")
            print(f"Role: {user_data.get('role')}")
            print(f"Full Name: {user_data.get('full_name')}")
            print("\n🔑 Login Credentials:")
            print(f"Email: {MANUFACTURER_DATA['email']}")
            print(f"Password: {MANUFACTURER_DATA['password']}")
            
            # Now let's login to get a token
            print("\n🔐 Testing login...")
            login_response = requests.post(
                f"{API_BASE_URL}/api/v1/auth/login",
                data={
                    "username": MANUFACTURER_DATA["email"],
                    "password": MANUFACTURER_DATA["password"]
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                print("✅ Login successful!")
                print(f"Access Token: {token_data.get('access_token')[:20]}...")
                
                # Test getting user info
                user_response = requests.get(
                    f"{API_BASE_URL}/api/v1/auth/me",
                    headers={"Authorization": f"Bearer {token_data['access_token']}"}
                )
                
                if user_response.status_code == 200:
                    user_info = user_response.json()
                    print(f"✅ User info retrieved: {user_info.get('full_name')} ({user_info.get('role')})")
                
            else:
                print(f"❌ Login failed: {login_response.text}")
                
        else:
            print(f"❌ Failed to create user: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the backend server is running on http://localhost:8000")
        print("   Run: cd backend && source venv/bin/activate && uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def create_admin_user():
    """Create an admin user (useful for testing)"""
    
    admin_data = {
        "email": "admin@example.com",
        "password": "admin123",
        "full_name": "System Administrator",
        "role": "admin",
        "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
    }
    
    print("🚀 Creating Admin User...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/register",
            json=admin_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Admin user created successfully!")
            print(f"Email: {admin_data['email']}")
            print(f"Password: {admin_data['password']}")
        else:
            print(f"❌ Failed to create admin: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "admin":
        create_admin_user()
    else:
        create_manufacturer_user()
        
    print("\n📝 Next Steps:")
    print("1. Visit http://localhost:3000")
    print("2. Login with the credentials above")
    print("3. Connect MetaMask wallet")
    print("4. Start registering products!")
