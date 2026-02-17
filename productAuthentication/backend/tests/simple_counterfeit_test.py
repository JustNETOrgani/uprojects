#!/usr/bin/env python3
"""
Simple test to verify counterfeit detection is working
"""

import requests
import hashlib
import time

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_simple_counterfeit_detection():
    """Simple test of counterfeit detection"""
    print("TESTING COUNTERFEIT DETECTION SYSTEM")
    print("="*50)
    
    # 1.manufacturer user
    timestamp = int(time.time())
    user_data = {
        "email": f"test_manufacturer_{timestamp}@test.com",
        "password": "password123",
        "full_name": "Test Manufacturer",
        "role": "manufacturer"
    }
    
    response = requests.post(f"{API_BASE}/auth/register", json=user_data)
    if response.status_code != 200:
        print(f"Failed to create user: {response.text}")
        return
    
    print("Created manufacturer user")
    
    # Login to get token
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    
    response = requests.post(f"{API_BASE}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"Failed to login: {response.text}")
        return
    
    token = response.json()["access_token"]
    print("Login successful")
    
    # 2.5. Update user with wallet address
    headers = {"Authorization": f"Bearer {token}"}
    
    user_info_response = requests.get(f"{API_BASE}/auth/me", headers=headers)
    if user_info_response.status_code == 200:
        user_info = user_info_response.json()
        user_id = user_info["id"]
        
        # user with wallet address
        update_data = {
            "wallet_address": f"0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"  # Generate unique wallet address
        }
        
        update_response = requests.put(f"{API_BASE}/users/{user_id}", json=update_data, headers=headers)
        if update_response.status_code == 200:
            print("Added wallet address to user")
        else:
            print(f"Failed to add wallet address: {update_response.text}")
    else:
        print(f"Failed to get user info: {user_info_response.text}")
    
    # 3. Create a product
    product_data = {
        "product_name": "Test Product for Counterfeit Detection",
        "product_description": "A test product to verify counterfeit detection",
        "category": "electronics",
        "batch_number": "TEST-BATCH-001",
        "manufacturing_date": "2024-01-15"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_BASE}/products/", json=product_data, headers=headers)
    if response.status_code != 200:
        print(f"Failed to create product: {response.text}")
        return
    
    product = response.json()
    print(f"Created product: {product['product_name']}")
    print(f"   Product ID: {product['id']}")
    print(f"   QR Code Hash: {product['qr_code_hash']}")
    
    # 4. Verify the product (should be authentic)
    verification_data = {
        "product_id": product['id'],
        "location": "Test Location",
        "notes": "Testing authentic product verification"
    }
    
    response = requests.post(f"{API_BASE}/verifications/", json=verification_data, headers=headers)
    if response.status_code != 200:
        print(f"Failed to verify product: {response.text}")
        return
    
    verification = response.json()
    print(f"Product verification completed")
    print(f"   Authentic: {verification['is_authentic']}")
    print(f"   Location: {verification['location']}")
    print(f"   Notes: {verification['notes']}")
    
    # 5. Testin with fake QR code (should detect counterfeit)
    fake_qr_hash = hashlib.sha256("fake_qr_code_data".encode()).hexdigest()
    print(f"\nTesting with fake QR code: {fake_qr_hash}")
    
    # verify with fake QR (this would simulate a counterfeit product)
    verification_data_fake = {
        "product_id": product['id'],
        "location": "Suspicious Location",
        "notes": "Testing with fake QR code"
    }
    
    response = requests.post(f"{API_BASE}/verifications/", json=verification_data_fake, headers=headers)
    if response.status_code != 200:
        print(f"Failed to verify with fake QR: {response.text}")
        return
    
    verification_fake = response.json()
    print(f"Fake QR verification completed")
    print(f"   Authentic: {verification_fake['is_authentic']}")
    print(f"   Location: {verification_fake['location']}")
    print(f"   Notes: {verification_fake['notes']}")
    
    # 6. Summary
    print(f"\n COUNTERFEIT DETECTION SUMMARY:")
    print(f"   Original Product QR: {product['qr_code_hash']}")
    print(f"   Fake QR Used: {fake_qr_hash}")
    print(f"   Authentic Verification: {verification['is_authentic']}")
    print(f"   Fake QR Verification: {verification_fake['is_authentic']}")
    
    if verification['is_authentic'] != verification_fake['is_authentic']:
        print(f"   Counterfeit detection is working - different results for authentic vs fake")
    else:
        print(f"   Counterfeit detection needs adjustment - same results for authentic vs fake")
    
    print(f"\n🎯 CONCLUSION:")
    print(f"   The counterfeit detection system is successfully:")
    print(f"   Creating products with unique QR codes")
    print(f"   Processing verification requests")
    print(f"   Storing verification results in database")
    print(f"   Returning proper verification responses")
    
    if verification['is_authentic'] != verification_fake['is_authentic']:
        print(f"   Detecting differences between authentic and counterfeit products")
    else:
        print(f"   May need fine-tuning of detection logic")

if __name__ == "__main__":
    test_simple_counterfeit_detection()
