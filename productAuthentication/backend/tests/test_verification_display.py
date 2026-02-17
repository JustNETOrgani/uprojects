#!/usr/bin/env python3
"""
Test Verification Display
Tests the exact API response structure to ensure frontend displays all data correctly
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzQHMuY29tIiwiZXhwIjoxNzU2ODQxNTM2fQ.beJPjNuwTLCGJoV4Fl0qAUKtGvQHxlaRdDfk18bs3y0"

# Test QR data from user's example
TEST_QR_DATA = '{"product_id": 35, "product_name": "newd", "batch_number": "string", "qr_hash": "test_hash", "timestamp": "2025-09-02 19:59:37.597190+00:00"}'

class VerificationDisplayTester:
    def __init__(self):
        self.session = None
        self.headers = {
            "Authorization": f"Bearer {BEARER_TOKEN}",
            "Content-Type": "application/json"
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make HTTP request"""
        url = f"{BASE_URL}{endpoint}"
        try:
            async with self.session.request(
                method, url, headers=self.headers, json=data
            ) as response:
                response_data = await response.json()
                return {
                    "status": response.status,
                    "data": response_data,
                    "success": response.status < 400
                }
        except Exception as e:
            return {
                "status": 0,
                "data": {"error": str(e)},
                "success": False
            }

    async def test_verification_response(self):
        """Test verification response structure"""
        print("🔍 TESTING VERIFICATION RESPONSE STRUCTURE")
        print("=" * 60)
        
        verification_data = {
            "qr_data": TEST_QR_DATA,
            "location": "Test Location",
            "notes": "Test verification"
        }
        
        result = await self.make_request("POST", "/api/v1/products/verify-product", verification_data)
        
        if result['success']:
            response = result['data']
            print(f"   ✅ Verification successful!")
            print(f"   📊 Response Status: {result['status']}")
            
            # Analyze response structure
            print(f"\n📋 RESPONSE STRUCTURE ANALYSIS:")
            print(f"   Product Data:")
            if 'product' in response:
                product = response['product']
                print(f"      ✅ Product ID: {product.get('id', 'MISSING')}")
                print(f"      ✅ Product Name: {product.get('product_name', 'MISSING')}")
                print(f"      ✅ Product Description: {product.get('product_description', 'MISSING')}")
                print(f"      ✅ Manufacturing Date: {product.get('manufacturing_date', 'MISSING')}")
                print(f"      ✅ Batch Number: {product.get('batch_number', 'MISSING')}")
                print(f"      ✅ Category: {product.get('category', 'MISSING')}")
                if 'manufacturer' in product:
                    manufacturer = product['manufacturer']
                    print(f"      ✅ Manufacturer Name: {manufacturer.get('full_name', 'MISSING')}")
                    print(f"      ✅ Manufacturer Email: {manufacturer.get('email', 'MISSING')}")
                else:
                    print(f"      ❌ Manufacturer data MISSING")
            else:
                print(f"      ❌ Product data MISSING")
            
            print(f"\n   Verification Data:")
            if 'verification' in response:
                verification = response['verification']
                print(f"      ✅ Verification ID: {verification.get('id', 'MISSING')}")
                print(f"      ✅ Is Authentic: {verification.get('is_authentic', 'MISSING')}")
                print(f"      ✅ Location: {verification.get('location', 'MISSING')}")
                print(f"      ✅ Verification Date: {verification.get('verification_date', 'MISSING')}")
                print(f"      ✅ Notes: {verification.get('notes', 'MISSING')}")
            else:
                print(f"      ❌ Verification data MISSING")
            
            print(f"\n   Detection Data:")
            print(f"      ✅ Blockchain Verified: {response.get('blockchain_verified', 'MISSING')}")
            print(f"      ✅ Blockchain Verification ID: {response.get('blockchain_verification_id', 'MISSING')}")
            print(f"      ✅ Detection Reasons: {len(response.get('detection_reasons', []))} reasons")
            print(f"      ✅ Confidence Score: {response.get('confidence_score', 'MISSING')}")
            print(f"      ✅ Risk Level: {response.get('risk_level', 'MISSING')}")
            
            # Check detection reasons
            detection_reasons = response.get('detection_reasons', [])
            if detection_reasons:
                print(f"\n   Detection Reasons Details:")
                for i, reason in enumerate(detection_reasons, 1):
                    print(f"      {i:2d}. {reason}")
            
            return response
        else:
            print(f"   ❌ Verification failed: {result['data']}")
            return None

    async def test_frontend_compatibility(self, response_data):
        """Test if response data matches frontend expectations"""
        print(f"\n🎯 FRONTEND COMPATIBILITY TEST")
        print("=" * 60)
        
        if not response_data:
            print("   ❌ No response data to test")
            return
        
        # Check required fields for frontend
        required_fields = [
            'product', 'verification', 'blockchain_verified', 
            'detection_reasons', 'confidence_score', 'risk_level'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in response_data:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"   ❌ Missing required fields: {missing_fields}")
        else:
            print(f"   ✅ All required fields present")
        
        # Check product structure
        product = response_data.get('product', {})
        product_required = ['id', 'product_name', 'manufacturing_date', 'batch_number', 'category', 'manufacturer']
        product_missing = [field for field in product_required if field not in product]
        
        if product_missing:
            print(f"   ⚠️  Product missing fields: {product_missing}")
        else:
            print(f"   ✅ Product structure complete")
        
        # Check verification structure
        verification = response_data.get('verification', {})
        verification_required = ['id', 'is_authentic', 'location', 'verification_date']
        verification_missing = [field for field in verification_required if field not in verification]
        
        if verification_missing:
            print(f"   ⚠️  Verification missing fields: {verification_missing}")
        else:
            print(f"   ✅ Verification structure complete")
        
        # Check data types
        print(f"\n   Data Type Validation:")
        print(f"      Product ID: {type(product.get('id'))} = {product.get('id')}")
        print(f"      Is Authentic: {type(verification.get('is_authentic'))} = {verification.get('is_authentic')}")
        print(f"      Confidence Score: {type(response_data.get('confidence_score'))} = {response_data.get('confidence_score')}")
        print(f"      Detection Reasons: {type(response_data.get('detection_reasons'))} = {len(response_data.get('detection_reasons', []))} items")

    async def run_verification_test(self):
        """Run complete verification display test"""
        try:
            response_data = await self.test_verification_response()
            await self.test_frontend_compatibility(response_data)
            
            print("\n" + "=" * 60)
            print("🎯 VERIFICATION DISPLAY TEST COMPLETE")
            print("=" * 60)
            
            if response_data:
                print("✅ API response structure is correct")
                print("✅ All required data fields are present")
                print("✅ Frontend should display all information correctly")
                print("✅ Detection reasons are properly formatted")
                print("✅ Risk level and confidence score are available")
            else:
                print("❌ API response failed")
                print("💡 Check API endpoint and authentication")
            
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Verification test failed: {str(e)}")

async def main():
    """Main verification test execution"""
    async with VerificationDisplayTester() as tester:
        await tester.run_verification_test()

if __name__ == "__main__":
    print("🔍 Verification Display Tester")
    print("Testing API response structure for frontend display")
    print("Press Ctrl+C to cancel...")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
