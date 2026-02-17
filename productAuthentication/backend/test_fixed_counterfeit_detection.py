#!/usr/bin/env python3
"""
Comprehensive test to verify all counterfeit detection fixes are working correctly
This test validates the fixes made based on the documentation requirements
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

def setup_user_with_wallet(token: str, wallet_address: str) -> bool:
    """Setup user with wallet address"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get current user info
    user_info_response = requests.get(f"{API_BASE}/auth/me", headers=headers)
    if user_info_response.status_code == 200:
        user_info = user_info_response.json()
        user_id = user_info["id"]
        
        # Update user with wallet address
        update_data = {"wallet_address": wallet_address}
        update_response = requests.put(f"{API_BASE}/users/{user_id}", json=update_data, headers=headers)
        if update_response.status_code == 200:
            print(f"✅ Added wallet address to user")
            return True
        else:
            print(f"⚠️  Failed to add wallet address: {update_response.text}")
            return False
    return False

def create_test_product(token: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a test product"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(f"{API_BASE}/products/", json=product_data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to create product: {response.text}")
        return None

def verify_product_with_qr(token: str, product_id: int, location: str, qr_code_hash: str = None, notes: str = "") -> Dict[str, Any]:
    """Verify a product with optional QR code hash"""
    headers = {"Authorization": f"Bearer {token}"}
    
    verification_data = {
        "product_id": product_id,
        "location": location,
        "notes": notes
    }
    
    if qr_code_hash:
        verification_data["qr_code_hash"] = qr_code_hash
    
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

def test_qr_code_validation():
    """Test QR code hash validation logic"""
    print("\n" + "="*60)
    print("TESTING QR CODE HASH VALIDATION")
    print("="*60)
    
    # Create test user
    user = create_test_user("qr_test@test.com", "password123", "manufacturer")
    if not user:
        return False
    
    token = user.get("token") or user.get("access_token")
    if not token:
        return False
    
    # Setup wallet
    setup_user_with_wallet(token, "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266")
    
    # Create product
    product = create_test_product(token, {
        "product_name": "QR Test Product",
        "product_description": "Product for QR validation testing",
        "category": "electronics",
        "batch_number": "QR-TEST-001",
        "manufacturing_date": "2024-01-15"
    })
    
    if not product:
        return False
    
    print(f"✅ Created product: {product['product_name']}")
    print(f"   Original QR Hash: {product.get('qr_code_hash', 'N/A')}")
    
    # Test 1: Verify with correct QR code (should be authentic)
    correct_qr = product.get('qr_code_hash')
    if correct_qr:
        verification_correct = verify_product_with_qr(
            token, product['id'], "Test Location", correct_qr, "Testing with correct QR"
        )
        
        if verification_correct:
            print(f"\n🔍 Correct QR Verification:")
            print(f"   Authentic: {verification_correct['is_authentic']}")
            print(f"   Confidence Score: {verification_correct.get('confidence_score', 'N/A')}")
            print(f"   Detection Reasons: {verification_correct.get('detection_reasons', [])}")
    
    # Test 2: Verify with incorrect QR code (should detect counterfeit)
    fake_qr = hashlib.sha256("fake_qr_code_data".encode()).hexdigest()
    verification_fake = verify_product_with_qr(
        token, product['id'], "Test Location", fake_qr, "Testing with fake QR"
    )
    
    if verification_fake:
        print(f"\n🔍 Fake QR Verification:")
        print(f"   Authentic: {verification_fake['is_authentic']}")
        print(f"   Confidence Score: {verification_fake.get('confidence_score', 'N/A')}")
        print(f"   Detection Reasons: {verification_fake.get('detection_reasons', [])}")
    
    # Test 3: Verify without QR code (should work but with limited validation)
    verification_no_qr = verify_product_with_qr(
        token, product['id'], "Test Location", None, "Testing without QR"
    )
    
    if verification_no_qr:
        print(f"\n🔍 No QR Verification:")
        print(f"   Authentic: {verification_no_qr['is_authentic']}")
        print(f"   Confidence Score: {verification_no_qr.get('confidence_score', 'N/A')}")
        print(f"   Detection Reasons: {verification_no_qr.get('detection_reasons', [])}")
    
    # Validate results
    success = True
    if correct_qr and verification_correct and not verification_correct['is_authentic']:
        print("❌ FAIL: Correct QR code marked as counterfeit")
        success = False
    
    if verification_fake and verification_fake['is_authentic']:
        print("❌ FAIL: Fake QR code not detected as counterfeit")
        success = False
    
    if success:
        print("✅ QR code validation working correctly")
    
    return success

def test_confidence_scoring():
    """Test confidence scoring algorithm"""
    print("\n" + "="*60)
    print("TESTING CONFIDENCE SCORING ALGORITHM")
    print("="*60)
    
    # Create test user
    user = create_test_user("confidence_test@test.com", "password123", "manufacturer")
    if not user:
        return False
    
    token = user.get("token") or user.get("access_token")
    if not token:
        return False
    
    # Setup wallet
    setup_user_with_wallet(token, "0x70997970C51812dc3A010C7d01b50e0d17dc79C8")
    
    # Create product
    product = create_test_product(token, {
        "product_name": "Confidence Test Product",
        "product_description": "Product for confidence scoring testing",
        "category": "electronics",
        "batch_number": "CONF-TEST-001",
        "manufacturing_date": "2024-01-15"
    })
    
    if not product:
        return False
    
    print(f"✅ Created product: {product['product_name']}")
    
    # Test authentic product (should have high confidence)
    verification_authentic = verify_product_with_qr(
        token, product['id'], "Official Store", product.get('qr_code_hash'), "Authentic verification"
    )
    
    if verification_authentic:
        print(f"\n🔍 Authentic Product:")
        print(f"   Authentic: {verification_authentic['is_authentic']}")
        print(f"   Confidence Score: {verification_authentic.get('confidence_score', 'N/A')}")
        print(f"   Detection Reasons: {verification_authentic.get('detection_reasons', [])}")
    
    # Test counterfeit product (should have low confidence)
    fake_qr = hashlib.sha256("fake_qr_code_data".encode()).hexdigest()
    verification_counterfeit = verify_product_with_qr(
        token, product['id'], "Suspicious Location", fake_qr, "Counterfeit verification"
    )
    
    if verification_counterfeit:
        print(f"\n🔍 Counterfeit Product:")
        print(f"   Authentic: {verification_counterfeit['is_authentic']}")
        print(f"   Confidence Score: {verification_counterfeit.get('confidence_score', 'N/A')}")
        print(f"   Detection Reasons: {verification_counterfeit.get('detection_reasons', [])}")
    
    # Validate confidence scores
    success = True
    if verification_authentic and verification_counterfeit:
        authentic_score = verification_authentic.get('confidence_score', 0)
        counterfeit_score = verification_counterfeit.get('confidence_score', 1)
        
        if authentic_score <= counterfeit_score:
            print("❌ FAIL: Authentic product should have higher confidence than counterfeit")
            success = False
        else:
            print("✅ Confidence scoring working correctly")
    
    return success

def test_detection_reasons():
    """Test detection reasons are properly stored and returned"""
    print("\n" + "="*60)
    print("TESTING DETECTION REASONS STORAGE")
    print("="*60)
    
    # Create test user
    user = create_test_user("reasons_test@test.com", "password123", "manufacturer")
    if not user:
        return False
    
    token = user.get("token") or user.get("access_token")
    if not token:
        return False
    
    # Setup wallet
    setup_user_with_wallet(token, "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC")
    
    # Create product
    product = create_test_product(token, {
        "product_name": "Reasons Test Product",
        "product_description": "Product for detection reasons testing",
        "category": "electronics",
        "batch_number": "REASONS-TEST-001",
        "manufacturing_date": "2024-01-15"
    })
    
    if not product:
        return False
    
    print(f"✅ Created product: {product['product_name']}")
    
    # Test with fake QR to trigger detection reasons
    fake_qr = hashlib.sha256("fake_qr_code_data".encode()).hexdigest()
    verification = verify_product_with_qr(
        token, product['id'], "Test Location", fake_qr, "Testing detection reasons"
    )
    
    if verification:
        print(f"\n🔍 Detection Reasons Test:")
        print(f"   Authentic: {verification['is_authentic']}")
        print(f"   Detection Reasons: {verification.get('detection_reasons', [])}")
        print(f"   Confidence Score: {verification.get('confidence_score', 'N/A')}")
        
        # Check if detection reasons are present
        reasons = verification.get('detection_reasons', [])
        if not reasons:
            print("❌ FAIL: No detection reasons returned")
            return False
        
        # Check if counterfeit-related reasons are present
        counterfeit_reasons = [r for r in reasons if 'counterfeit' in r.lower() or 'mismatch' in r.lower()]
        if not counterfeit_reasons:
            print("❌ FAIL: No counterfeit-related detection reasons found")
            return False
        
        print("✅ Detection reasons working correctly")
        return True
    
    return False

def test_analyze_counterfeit_endpoint():
    """Test the analyze counterfeit endpoint"""
    print("\n" + "="*60)
    print("TESTING ANALYZE COUNTERFEIT ENDPOINT")
    print("="*60)
    
    # Create test user
    user = create_test_user("analyze_test@test.com", "password123", "manufacturer")
    if not user:
        return False
    
    token = user.get("token") or user.get("access_token")
    if not token:
        return False
    
    # Setup wallet
    setup_user_with_wallet(token, "0x90F79bf6EB2c4f870365E785982E1f101E93b906")
    
    # Create product
    product = create_test_product(token, {
        "product_name": "Analyze Test Product",
        "product_description": "Product for analyze endpoint testing",
        "category": "electronics",
        "batch_number": "ANALYZE-TEST-001",
        "manufacturing_date": "2024-01-15"
    })
    
    if not product:
        return False
    
    print(f"✅ Created product: {product['product_name']}")
    
    # Test analysis with fake QR
    fake_qr = hashlib.sha256("fake_qr_code_data".encode()).hexdigest()
    analysis = analyze_counterfeit(
        token, product['id'], qr_code_hash=fake_qr, location="Suspicious Location"
    )
    
    if analysis:
        print(f"\n🔍 Counterfeit Analysis:")
        print(f"   Product ID: {analysis.get('product_id')}")
        print(f"   Product Name: {analysis.get('product_name')}")
        print(f"   Detection Result: {analysis.get('detection_result', {})}")
        print(f"   Risk Assessment: {analysis.get('risk_assessment', {})}")
        print(f"   Pattern Analysis: {analysis.get('pattern_analysis', {})}")
        
        # Validate analysis structure
        required_fields = ['detection_result', 'risk_assessment', 'pattern_analysis']
        success = all(field in analysis for field in required_fields)
        
        if success:
            print("✅ Analyze counterfeit endpoint working correctly")
        else:
            print("❌ FAIL: Missing required fields in analysis response")
        
        return success
    
    return False

def main():
    """Run all tests to verify fixes"""
    print("🚀 TESTING FIXED COUNTERFEIT DETECTION SYSTEM")
    print("This validates all the fixes made based on the documentation")
    
    test_results = []
    
    try:
        # Test QR code validation
        test_results.append(("QR Code Validation", test_qr_code_validation()))
        
        # Test confidence scoring
        test_results.append(("Confidence Scoring", test_confidence_scoring()))
        
        # Test detection reasons
        test_results.append(("Detection Reasons", test_detection_reasons()))
        
        # Test analyze endpoint
        test_results.append(("Analyze Endpoint", test_analyze_counterfeit_endpoint()))
        
        # Summary
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED!")
            print("The counterfeit detection system fixes are working correctly.")
        else:
            print(f"\n⚠️  {total - passed} tests failed. Please review the implementation.")
        
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
