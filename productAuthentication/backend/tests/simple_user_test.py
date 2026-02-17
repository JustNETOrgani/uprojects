#!/usr/bin/env python3
"""
Simple test to create a user
"""

import requests
import time

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_user_creation():
    """Simple test to create a user"""
    print("👤 TESTING USER CREATION")
    print("="*30)
    
    # Create a user
    timestamp = int(time.time())
    user_data = {
        "email": f"simple_test_{timestamp}@test.com",
        "password": "password123",
        "full_name": "Simple Test User",
        "role": "consumer"
    }
    
    print(f"Creating user with email: {user_data['email']}")
    response = requests.post(f"{API_BASE}/auth/register", json=user_data)
    
    print(f"Response status: {response.status_code}")
    print(f"Response text: {response.text}")
    
    if response.status_code == 200:
        print("✅ User created successfully")
        user = response.json()
        print(f"   User ID: {user.get('id')}")
        print(f"   Email: {user.get('email')}")
        print(f"   Role: {user.get('role')}")
    else:
        print("❌ User creation failed")

if __name__ == "__main__":
    test_user_creation()
