#!/usr/bin/env python3
"""
Test product registration and verification
"""

import requests
import json
import hashlib
import time

# Configuration
API_BASE_URL = "http://localhost:8000"
MANUFACTURER_DATA = {
    "email": "manufacturer@example.com",
    "password": "password123"
}

def test_product_registration():
    """Test product registration and verification"""
    
    print("🔍 Testing Product Registration and Verification...")
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
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Check user info and wallet address
        print("\n1.5. Checking user info and wallet address...")
        user_response = requests.get(
            f"{API_BASE_URL}/api/v1/auth/me",
            headers=headers
        )
        
        if user_response.status_code == 200:
            user_info = user_response.json()
            print(f"   User: {user_info.get('full_name')} ({user_info.get('role')})")
            print(f"   Wallet Address: {user_info.get('wallet_address') or 'Not set'}")
            
            if not user_info.get('wallet_address'):
                print("   ⚠️  No wallet address set - blockchain registration will fail")
        else:
            print(f"❌ Failed to get user info: {user_response.status_code}")
        
        # Test product registration
        print("\n2. Testing product registration...")
        product_data = {
            "product_name": "Test Product",
            "product_description": "A test product for verification",
            "manufacturing_date": "2024-01-01T00:00:00",
            "batch_number": "BATCH-001",
            "category": "electronics",
            "qr_code_hash": hashlib.sha256(f"TEST-{int(time.time())}".encode()).hexdigest()
        }
        
        print(f"   Product Data: {json.dumps(product_data, indent=2)}")
        
        # Register product via backend API
        product_response = requests.post(
            f"{API_BASE_URL}/api/v1/products/",
            json=product_data,
            headers=headers
        )
        
        if product_response.status_code == 200:
            product_result = product_response.json()
            print("✅ Product registered successfully!")
            print(f"   Product ID: {product_result.get('id')}")
            print(f"   QR Code Hash: {product_result.get('qr_code_hash')}")
            
            # Test blockchain verification
            print("\n3. Testing blockchain verification...")
            verify_data = {
                "location": "Test Location",
                "notes": "Test verification"
            }
            
            verify_response = requests.post(
                f"{API_BASE_URL}/api/v1/blockchain/products/{product_result['id']}/verify?location=Test%20Location&notes=Test%20verification",
                headers=headers
            )
            
            if verify_response.status_code == 200:
                verify_result = verify_response.json()
                print("✅ Product verified on blockchain successfully!")
                print(f"   Verification Result: {json.dumps(verify_result, indent=2)}")
            else:
                print(f"❌ Blockchain verification failed: {verify_response.status_code}")
                print(f"   Response: {verify_response.text}")
                
            # Test getting product details
            print("\n4. Testing product details retrieval...")
            details_response = requests.get(
                f"{API_BASE_URL}/api/v1/products/{product_result['id']}",
                headers=headers
            )
            
            if details_response.status_code == 200:
                details_result = details_response.json()
                print("✅ Product details retrieved successfully!")
                print(f"   Product Details: {json.dumps(details_result, indent=2)}")
            else:
                print(f"❌ Product details failed: {details_response.status_code}")
                print(f"   Response: {details_response.text}")
                
            # Test QR code verification
            print("\n5. Testing QR code verification...")
            qr_hash = product_result.get('qr_code_hash')
            if qr_hash:
                qr_response = requests.get(
                    f"{API_BASE_URL}/api/v1/blockchain/products/qr/{qr_hash}",
                    headers=headers
                )
                
                if qr_response.status_code == 200:
                    qr_result = qr_response.json()
                    print("✅ QR code verification successful!")
                    print(f"   QR Result: {json.dumps(qr_result, indent=2)}")
                else:
                    print(f"❌ QR code verification failed: {qr_response.status_code}")
                    print(f"   Response: {qr_response.text}")
            else:
                print("❌ No QR code hash found in product")
                
        else:
            print(f"❌ Product registration failed: {product_response.status_code}")
            print(f"   Response: {product_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the backend server is running")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_product_registration()
