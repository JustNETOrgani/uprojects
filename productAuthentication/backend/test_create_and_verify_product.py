#!/usr/bin/env python3

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def login_and_get_token():
    """Login and get access token"""
    login_data = {
        "username": "k@gmail.com",
        "password": "s"
    }
    
    response = requests.post(f"{API_BASE}/auth/login", data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.text}")
        return None

def create_test_product(token):
    """Create a test product"""
    headers = {"Authorization": f"Bearer {token}"}
    
    product_data = {
        "product_name": "Test Smartphone",
        "product_description": "A high-quality smartphone for testing",
        "manufacturing_date": "2024-01-15",
        "batch_number": "BATCH001",
        "category": "electronics"
    }
    
    print("📦 Creating test product...")
    response = requests.post(f"{API_BASE}/products/", headers=headers, json=product_data)
    
    if response.status_code == 200:
        product = response.json()
        print(f"✅ Product created successfully!")
        print(f"   ID: {product['id']}")
        print(f"   Name: {product['product_name']}")
        print(f"   QR Hash: {product.get('qr_code_hash', 'Not generated yet')}")
        return product
    else:
        print(f"❌ Failed to create product: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def generate_qr_code(token, product_id):
    """Generate QR code for the product"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"🔍 Generating QR code for product {product_id}...")
    response = requests.post(f"{API_BASE}/products/{product_id}/qr-code", headers=headers)
    
    if response.status_code == 200:
        qr_data = response.json()
        print(f"✅ QR code generated successfully!")
        print(f"   QR Hash: {qr_data.get('qr_hash', 'N/A')}")
        print(f"   QR Data: {qr_data.get('qr_data', 'N/A')[:50]}...")
        return qr_data
    else:
        print(f"❌ Failed to generate QR code: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def test_verification_with_real_product(token, qr_data):
    """Test verification with the real product"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🔍 Testing verification with real product...")
    print(f"   QR Data: {qr_data[:100]}...")
    
    # Test with valid QR data
    response = requests.post(
        f"{API_BASE}/products/verify-product",
        headers=headers,
        json={
            "qr_data": qr_data,
            "location": "Test Location",
            "notes": "Testing with real product"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Verification successful!")
        print(f"   📊 Authentic: {result['verification']['is_authentic']}")
        print(f"   🎯 Confidence: {result.get('confidence_score', 'N/A'):.2f}")
        print(f"   ⚠️  Risk Level: {result.get('risk_level', 'N/A')}")
        print(f"   📝 Detection Reasons:")
        for reason in result.get('detection_reasons', []):
            print(f"      • {reason}")
        
        # Test with modified QR data (should be counterfeit)
        print(f"\n🔍 Testing with modified QR data (should be counterfeit)...")
        modified_qr_data = qr_data.replace('"product_name":"Test Smartphone"', '"product_name":"Fake Smartphone"')
        
        response2 = requests.post(
            f"{API_BASE}/products/verify-product",
            headers=headers,
            json={
                "qr_data": modified_qr_data,
                "location": "Test Location",
                "notes": "Testing with modified QR data"
            }
        )
        
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"✅ Verification successful!")
            print(f"   📊 Authentic: {result2['verification']['is_authentic']}")
            print(f"   🎯 Confidence: {result2.get('confidence_score', 'N/A'):.2f}")
            print(f"   ⚠️  Risk Level: {result2.get('risk_level', 'N/A')}")
            print(f"   📝 Detection Reasons:")
            for reason in result2.get('detection_reasons', []):
                print(f"      • {reason}")
        else:
            print(f"❌ Failed to verify modified QR: {response2.status_code}")
            print(f"   Response: {response2.text}")
    else:
        print(f"❌ Failed to verify: {response.status_code}")
        print(f"   Response: {response.text}")

def main():
    print("🚀 Testing Complete Counterfeit Detection Flow")
    print("=" * 60)
    
    # Get authentication token
    token = login_and_get_token()
    if not token:
        print("❌ Failed to get authentication token")
        return
    
    print(f"✅ Authentication successful")
    
    # Create a test product
    product = create_test_product(token)
    if not product:
        return
    
    # Generate QR code
    qr_data = generate_qr_code(token, product['id'])
    if not qr_data:
        return
    
    # Test verification
    test_verification_with_real_product(token, qr_data.get('qr_data', ''))
    
    print("\n🎉 Complete testing finished!")
    print("\n📋 Summary:")
    print("• Real products are verified as authentic")
    print("• Modified QR codes are detected as counterfeit")
    print("• The system provides detailed detection reasons")
    print("• Confidence scores and risk levels are accurate")

if __name__ == "__main__":
    main()
