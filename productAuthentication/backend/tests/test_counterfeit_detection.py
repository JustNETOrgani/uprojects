#!/usr/bin/env python3
"""
Test script to demonstrate counterfeit detection system
This script shows how the system detects counterfeit products vs authentic ones
"""

import requests
import json
import hashlib
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def create_test_user(email: str, password: str, role: str = "consumer") -> Dict[str, Any]:
    """Create a test user for authentication or return existing user"""
    # First try to login with existing user
    login_data = {
        "username": email,
        "password": password
    }
    
    login_response = requests.post(f"{API_BASE}/auth/login", data=login_data)
    if login_response.status_code == 200:
        print(f"✅ Using existing user: {email}")
        return {"email": email, "token": login_response.json()["access_token"]}
    
    # If login fails, create new user
    user_data = {
        "email": email,
        "password": password,
        "full_name": f"Test {role.title()}",
        "role": role
    }
    
    response = requests.post(f"{API_BASE}/auth/register", json=user_data)
    if response.status_code == 200:
        print(f"✅ Created new user: {email}")
        return response.json()
    else:
        print(f"Failed to create user: {response.text}")
        return None

def login_user(email: str, password: str) -> str:
    """Login user and get access token"""
    login_data = {
        "username": email,
        "password": password
    }
    
    response = requests.post(f"{API_BASE}/auth/login", data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Failed to login: {response.text}")
        return None

def create_test_product(token: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a test product"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"Creating product with data: {product_data}")
    response = requests.post(f"{API_BASE}/products/", json=product_data, headers=headers)
    print(f"Response status: {response.status_code}")
    print(f"Response text: {response.text}")
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to create product: {response.text}")
        return None

def verify_product(token: str, product_id: int, location: str, notes: str = "") -> Dict[str, Any]:
    """Verify a product and get counterfeit detection results"""
    headers = {"Authorization": f"Bearer {token}"}
    
    verification_data = {
        "product_id": product_id,
        "location": location,
        "notes": notes
    }
    
    response = requests.post(f"{API_BASE}/verifications/", json=verification_data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to verify product: {response.text}")
        return None

def analyze_counterfeit(token: str, product_id: int, qr_code_hash: str = None, location: str = None) -> Dict[str, Any]:
    """Perform detailed counterfeit analysis"""
    headers = {"Authorization": f"Bearer {token}"}
    
    params = {}
    if qr_code_hash:
        params["qr_code_hash"] = qr_code_hash
    if location:
        params["location"] = location
    
    response = requests.post(f"{API_BASE}/verifications/analyze-counterfeit/{product_id}", params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to analyze counterfeit: {response.text}")
        return None

def generate_fake_qr_hash() -> str:
    """Generate a fake QR code hash for counterfeit testing"""
    return hashlib.sha256(f"fake_product_{time.time()}".encode()).hexdigest()

def test_authentic_product():
    """Test verification of an authentic product"""
    print("\n" + "="*60)
    print("TESTING AUTHENTIC PRODUCT DETECTION")
    print("="*60)
    
    # Create test user with unique email and wallet address
    user = create_test_user("manufacturer_auth@test.com", "password123", "manufacturer")
    
    # Update user with wallet address if creation was successful
    if user and "token" in user:
        token = user["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Update user with wallet address
        update_data = {
            "wallet_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        }
        
        # Get current user info to get user ID
        user_info_response = requests.get(f"{API_BASE}/auth/me", headers=headers)
        if user_info_response.status_code == 200:
            user_info = user_info_response.json()
            user_id = user_info["id"]
            
            # Update user with wallet address
            update_response = requests.put(f"{API_BASE}/users/{user_id}", json=update_data, headers=headers)
            if update_response.status_code == 200:
                print(f"✅ Added wallet address to user")
            else:
                print(f"⚠️  Failed to add wallet address: {update_response.text}")
    if not user:
        return
    
    # Get token from user object
    if "token" in user:
        token = user["token"]
    else:
        token = login_user("manufacturer_auth@test.com", "password123")
        if not token:
            return
    
    # Create authentic product
    authentic_product = create_test_product(token, {
        "product_name": "Authentic iPhone 15",
        "product_description": "Genuine Apple iPhone 15 with valid serial number",
        "category": "electronics",
        "batch_number": "IP15-2024-001",
        "manufacturing_date": "2024-01-15"
    })
    
    if not authentic_product:
        return
    
    print(f"✅ Created authentic product: {authentic_product['product_name']}")
    print(f"   Product ID: {authentic_product['id']}")
    print(f"   QR Code Hash: {authentic_product.get('qr_code_hash', 'N/A')}")
    
    # Verify authentic product
    verification_result = verify_product(
        token, 
        authentic_product['id'], 
        "Apple Store - San Francisco",
        "Verified at official Apple Store"
    )
    
    if verification_result:
        print(f"\n🔍 Verification Result:")
        print(f"   Authentic: {verification_result['is_authentic']}")
        print(f"   Location: {verification_result['location']}")
        print(f"   Notes: {verification_result['notes']}")
        print(f"   Verification Date: {verification_result['verification_date']}")
        print(f"   ✅ Product verification completed successfully!")

def test_counterfeit_product():
    """Test verification of a counterfeit product"""
    print("\n" + "="*60)
    print("TESTING COUNTERFEIT PRODUCT DETECTION")
    print("="*60)
    
    # Create test user with unique email and wallet address
    user = create_test_user("manufacturer_fake@test.com", "password123", "manufacturer")
    
    # Update user with wallet address if creation was successful
    if user and "token" in user:
        token = user["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Update user with wallet address
        update_data = {
            "wallet_address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"  # Different wallet
        }
        
        # Get current user info to get user ID
        user_info_response = requests.get(f"{API_BASE}/auth/me", headers=headers)
        if user_info_response.status_code == 200:
            user_info = user_info_response.json()
            user_id = user_info["id"]
            
            # Update user with wallet address
            update_response = requests.put(f"{API_BASE}/users/{user_id}", json=update_data, headers=headers)
            if update_response.status_code == 200:
                print(f"✅ Added wallet address to user")
            else:
                print(f"⚠️  Failed to add wallet address: {update_response.text}")
    if not user:
        return
    
    # Get token from user object
    if "token" in user:
        token = user["token"]
    else:
        token = login_user("manufacturer_fake@test.com", "password123")
        if not token:
            return
    
    # Create counterfeit product (with fake QR code)
    counterfeit_product = create_test_product(token, {
        "product_name": "Fake iPhone 15",
        "product_description": "Counterfeit iPhone with fake serial number",
        "category": "electronics",
        "batch_number": "FAKE-001",
        "manufacturing_date": "2024-01-15"
    })
    
    if not counterfeit_product:
        return
    
    print(f"❌ Created counterfeit product: {counterfeit_product['product_name']}")
    print(f"   Product ID: {counterfeit_product['id']}")
    print(f"   QR Code Hash: {counterfeit_product.get('qr_code_hash', 'N/A')}")
    
    # Try to verify with fake QR code
    fake_qr_hash = generate_fake_qr_hash()
    print(f"   Using fake QR hash: {fake_qr_hash}")
    
    # Perform detailed counterfeit analysis
    analysis_result = analyze_counterfeit(
        token, 
        counterfeit_product['id'], 
        qr_code_hash=fake_qr_hash,
        location="Unknown location"
    )
    
    if analysis_result:
        print(f"\n🔍 Counterfeit Analysis Result:")
        print(f"   Authentic: {analysis_result['detection_result']['is_authentic']}")
        print(f"   Risk Score: {analysis_result['risk_assessment']['risk_score']}")
        print(f"   Risk Level: {analysis_result['risk_assessment']['risk_level']}")
        print(f"   Detection Reasons: {analysis_result['detection_result']['detection_reasons']}")
        print(f"   Recommendation: {analysis_result['risk_assessment']['recommendation']}")
        
        print(f"\n📊 Pattern Analysis:")
        print(f"   Total Verifications: {analysis_result['pattern_analysis']['total_verifications']}")
        print(f"   Authentic Verifications: {analysis_result['pattern_analysis']['authentic_verifications']}")
        print(f"   Counterfeit Verifications: {analysis_result['pattern_analysis']['counterfeit_verifications']}")
        print(f"   Suspicious Patterns: {analysis_result['pattern_analysis']['suspicious_patterns']}")
        print(f"   ✅ Counterfeit analysis completed successfully!")

def test_qr_code_mismatch():
    """Test detection when QR code doesn't match the product"""
    print("\n" + "="*60)
    print("TESTING QR CODE MISMATCH DETECTION")
    print("="*60)
    
    # Create test user with unique email and wallet address
    user = create_test_user("manufacturer_qr@test.com", "password123", "manufacturer")
    
    # Update user with wallet address if creation was successful
    if user and "token" in user:
        token = user["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Update user with wallet address
        update_data = {
            "wallet_address": "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC"  # Different wallet
        }
        
        # Get current user info to get user ID
        user_info_response = requests.get(f"{API_BASE}/auth/me", headers=headers)
        if user_info_response.status_code == 200:
            user_info = user_info_response.json()
            user_id = user_info["id"]
            
            # Update user with wallet address
            update_response = requests.put(f"{API_BASE}/users/{user_id}", json=update_data, headers=headers)
            if update_response.status_code == 200:
                print(f"✅ Added wallet address to user")
            else:
                print(f"⚠️  Failed to add wallet address: {update_response.text}")
    if not user:
        return
    
    # Get token from user object
    if "token" in user:
        token = user["token"]
    else:
        token = login_user("manufacturer_qr@test.com", "password123")
        if not token:
            return
    
    # Create a product
    product = create_test_product(token, {
        "product_name": "Test Product",
        "product_description": "Product for QR mismatch testing",
        "category": "other",
        "batch_number": "TEST-001",
        "manufacturing_date": "2024-01-15"
    })
    
    if not product:
        return
    
    print(f"📦 Created test product: {product['product_name']}")
    print(f"   Original QR Hash: {product.get('qr_code_hash', 'N/A')}")
    
    # Try to verify with mismatched QR code
    mismatched_qr = hashlib.sha256("completely_different_qr_code".encode()).hexdigest()
    print(f"   Using mismatched QR: {mismatched_qr}")
    
    # Perform analysis with mismatched QR
    analysis_result = analyze_counterfeit(
        token, 
        product['id'], 
        qr_code_hash=mismatched_qr,
        location="Test location"
    )
    
    if analysis_result:
        print(f"\n🔍 QR Mismatch Analysis:")
        print(f"   Authentic: {analysis_result['detection_result']['is_authentic']}")
        print(f"   Risk Score: {analysis_result['risk_assessment']['risk_score']}")
        print(f"   Detection Reasons: {analysis_result['detection_result']['detection_reasons']}")
        print(f"   Recommendation: {analysis_result['risk_assessment']['recommendation']}")
        print(f"   ✅ QR mismatch analysis completed successfully!")

def test_multiple_verifications():
    """Test detection of suspicious verification patterns"""
    print("\n" + "="*60)
    print("TESTING MULTIPLE VERIFICATION DETECTION")
    print("="*60)
    
    # Create test user with unique email and wallet address
    user = create_test_user("manufacturer_multi@test.com", "password123", "manufacturer")
    
    # Update user with wallet address if creation was successful
    if user and "token" in user:
        token = user["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Update user with wallet address
        update_data = {
            "wallet_address": "0x90F79bf6EB2c4f870365E785982E1f101E93b906"  # Different wallet
        }
        
        # Get current user info to get user ID
        user_info_response = requests.get(f"{API_BASE}/auth/me", headers=headers)
        if user_info_response.status_code == 200:
            user_info = user_info_response.json()
            user_id = user_info["id"]
            
            # Update user with wallet address
            update_response = requests.put(f"{API_BASE}/users/{user_id}", json=update_data, headers=headers)
            if update_response.status_code == 200:
                print(f"✅ Added wallet address to user")
            else:
                print(f"⚠️  Failed to add wallet address: {update_response.text}")
    if not user:
        return
    
    # Get token from user object
    if "token" in user:
        token = user["token"]
    else:
        token = login_user("manufacturer_multi@test.com", "password123")
        if not token:
            return
    
    # Create a product
    product = create_test_product(token, {
        "product_name": "Suspicious Product",
        "product_description": "Product with multiple verifications",
        "category": "other",
        "batch_number": "SUSP-001",
        "manufacturing_date": "2024-01-15"
    })
    
    if not product:
        return
    
    print(f"📦 Created product: {product['product_name']}")
    
    # Perform multiple verifications (simulating suspicious activity)
    for i in range(5):
        verification_result = verify_product(
            token, 
            product['id'], 
            f"Location {i+1}",
            f"Verification attempt {i+1}"
        )
        print(f"   Verification {i+1}: {'✅' if verification_result else '❌'}")
    
    # Analyze the product after multiple verifications
    analysis_result = analyze_counterfeit(
        token, 
        product['id'], 
        location="Multiple locations"
    )
    
    if analysis_result:
        print(f"\n🔍 Multiple Verification Analysis:")
        print(f"   Total Verifications: {analysis_result['pattern_analysis']['total_verifications']}")
        print(f"   Verification Frequency: {analysis_result['pattern_analysis']['verification_frequency']}")
        print(f"   Suspicious Patterns: {analysis_result['pattern_analysis']['suspicious_patterns']}")
        print(f"   Risk Score: {analysis_result['risk_assessment']['risk_score']}")
        print(f"   Risk Level: {analysis_result['risk_assessment']['risk_level']}")
        print(f"   ✅ Multiple verification analysis completed successfully!")

def main():
    """Run all counterfeit detection tests"""
    print("🚀 STARTING COUNTERFEIT DETECTION SYSTEM TESTS")
    print("This demonstrates how the system detects counterfeit vs authentic products")
    
    try:
        # Test authentic product detection
        test_authentic_product()
        
        # Test counterfeit product detection
        test_counterfeit_product()
        
        # Test QR code mismatch detection
        test_qr_code_mismatch()
        
        # Test multiple verification detection
        test_multiple_verifications()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)
        print("\n📋 SUMMARY:")
        print("The counterfeit detection system now includes:")
        print("1. QR Code Hash Validation")
        print("2. Blockchain Verification")
        print("3. Location Anomaly Detection")
        print("4. Multiple Verification Pattern Analysis")
        print("5. Manufacturer Verification")
        print("6. Product Details Validation")
        print("7. Batch Number Validation")
        print("8. Risk Scoring and Recommendations")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
