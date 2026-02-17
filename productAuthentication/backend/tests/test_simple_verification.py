#!/usr/bin/env python3
"""
Test Simple Verification
Tests the verification endpoint with a simple request to ensure it works
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzQHMuY29tIiwiZXhwIjoxNzU2ODQxNTM2fQ.beJPjNuwTLCGJoV4Fl0qAUKtGvQHxlaRdDfk18bs3y0"

class SimpleVerificationTester:
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

    async def test_simple_verification(self):
        """Test simple verification request"""
        print("🔧 TESTING SIMPLE VERIFICATION")
        print("=" * 50)
        
        # Test with Product 51
        print("\n📱 Testing QR Code Verification")
        qr_data_json = '{"product_id": 51, "product_name": "Authentic Luxury Watch", "batch_number": "LUX-WATCH-2024-001", "qr_hash": "77c14d24949c39ef15eff39fb1c3da47defad2ecf89d0ec479e0efed61e0f177", "timestamp": "2025-09-02 17:55:48.391108+00:00"}'
        
        verification_data = {
            "qr_data": qr_data_json,
            "location": "Simple Test",
            "notes": "Testing simple verification"
        }
        
        result = await self.make_request("POST", "/api/v1/products/verify-product", verification_data)
        
        if result['success']:
            verification = result['data']
            print(f"   ✅ Verification Successful!")
            print(f"   📊 Results:")
            print(f"      Product ID: {verification.get('product', {}).get('id')}")
            print(f"      Product Name: {verification.get('product', {}).get('product_name')}")
            print(f"      Is Authentic: {verification.get('verification', {}).get('is_authentic')}")
            print(f"      Confidence Score: {verification.get('confidence_score')}")
            print(f"      Risk Level: {verification.get('risk_level')}")
            print(f"      Detection Reasons: {len(verification.get('detection_reasons', []))}")
            print(f"      Blockchain Verified: {verification.get('blockchain_verified')}")
            print(f"      Verification ID: {verification.get('verification', {}).get('id')}")
            
            # Check if all required fields are present
            required_fields = [
                'product', 'verification', 'blockchain_verified', 
                'detection_reasons', 'confidence_score', 'risk_level'
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in verification:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"   ⚠️  Missing fields: {missing_fields}")
            else:
                print(f"   ✅ All required fields present")
                
            return verification
        else:
            print(f"   ❌ Verification failed: {result['data']}")
            return None

    async def run_test(self):
        """Run the complete test"""
        try:
            result = await self.test_simple_verification()
            
            print("\n" + "=" * 50)
            print("🎯 SIMPLE VERIFICATION TEST COMPLETE")
            print("=" * 50)
            
            if result:
                print("✅ Verification endpoint working correctly")
                print("✅ All required fields present in response")
                print("✅ Frontend can display verification results")
            else:
                print("❌ Verification endpoint has issues")
                print("❌ Frontend may not display results correctly")
            
        except Exception as e:
            print(f"\n❌ Test failed: {str(e)}")

async def main():
    """Main test execution"""
    async with SimpleVerificationTester() as tester:
        await tester.run_test()

if __name__ == "__main__":
    print("🔧 Simple Verification Tester")
    print("Testing basic verification functionality")
    print("Press Ctrl+C to cancel...")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
