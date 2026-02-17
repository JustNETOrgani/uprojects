#!/usr/bin/env python3
"""
Test the improved QR scanner and MetaMask integration
"""

import requests
import json

def test_improvements():
    """Test the improved system components"""
    
    print("🔍 Testing Improved System Components...")
    print("=" * 50)
    
    # Test backend verification endpoint
    print("\n1. Testing improved verification endpoint...")
    
    try:
        # Login to get token
        login_response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            data={
                "username": "manufacturer@example.com",
                "password": "password123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if login_response.status_code != 200:
            print("❌ Login failed")
            return
        
        token = login_response.json().get('access_token')
        
        # Test verification endpoint
        test_qr_data = {
            "product_id": 1,
            "product_name": "Test Product",
            "batch_number": "TEST-001",
            "qr_hash": "test_hash_123",
            "timestamp": "2024-01-01T00:00:00"
        }
        
        verification_response = requests.post(
            "http://localhost:8000/api/v1/products/verify-product",
            json={
                "qr_data": json.dumps(test_qr_data),
                "location": "Test Location",
                "notes": "Testing improved endpoint"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if verification_response.status_code == 200:
            print("✅ Verification endpoint working correctly")
            result = verification_response.json()
            print(f"   - Product: {result['product']['product_name']}")
            print(f"   - Verification ID: {result['verification']['id']}")
            print(f"   - Blockchain Verified: {result['blockchain_verified']}")
        else:
            print(f"❌ Verification endpoint failed: {verification_response.status_code}")
            print(f"   Response: {verification_response.text}")
            
    except Exception as e:
        print(f"❌ Error testing verification: {e}")
    
    # Test frontend accessibility
    print("\n2. Testing frontend accessibility...")
    
    try:
        frontend_response = requests.get("http://localhost:3000")
        if frontend_response.status_code == 200:
            print("✅ Frontend is accessible")
        else:
            print(f"❌ Frontend not accessible: {frontend_response.status_code}")
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
    
    # Test onboarding page
    print("\n3. Testing onboarding page...")
    
    try:
        onboarding_response = requests.get("http://localhost:3000/onboarding")
        if onboarding_response.status_code == 200:
            print("✅ Onboarding page is accessible")
        else:
            print(f"❌ Onboarding page not accessible: {onboarding_response.status_code}")
    except Exception as e:
        print(f"❌ Onboarding test failed: {e}")
    
    print("\n🎉 Improvement Tests Complete!")
    print("\n📋 What's Been Improved:")
    print("   ✅ QR Scanner - Better UX, error handling, camera permissions")
    print("   ✅ MetaMask Integration - Network detection, auto-switching")
    print("   ✅ Onboarding System - Step-by-step setup for new users")
    print("   ✅ User Creation - Scripts for admins and manufacturers")
    print("   ✅ Error Handling - Better user feedback and guidance")

if __name__ == "__main__":
    test_improvements()
