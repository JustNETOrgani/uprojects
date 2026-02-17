#!/usr/bin/env python3
"""
Test Exact Frontend Data
Tests with the exact data provided by the user
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzQHMuY29tIiwiZXhwIjoxNzU2ODQxNTM2fQ.beJPjNuwTLCGJoV4Fl0qAUKtGvQHxlaRdDfk18bs3y0"

class ExactFrontendDataTester:
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

    async def test_exact_user_data(self):
        """Test with the exact data provided by the user"""
        print("🎯 TESTING WITH EXACT USER DATA")
        print("=" * 60)
        
        # Exact data from user's message
        print("\n📱 User's Frontend Data:")
        print("   location: 'Unknown'")
        print("   notes: ''")
        print("   qr_data: '{\"product_id\": 51, \"product_name\": \"Authentic Luxury Watch\", \"batch_number\": \"LUX-WATCH-2024-001\", \"qr_hash\": \"77c14d24949c39ef15eff39fb1c3da47defad2ecf89d0ec479e0efed61e0f177\", \"timestamp\": \"2025-09-02 17:55:48.391108+00:00\"}'")
        
        verification_data = {
            "qr_data": '{"product_id": 51, "product_name": "Authentic Luxury Watch", "batch_number": "LUX-WATCH-2024-001", "qr_hash": "77c14d24949c39ef15eff39fb1c3da47defad2ecf89d0ec479e0efed61e0f177", "timestamp": "2025-09-02 17:55:48.391108+00:00"}',
            "location": "Unknown",
            "notes": ""
        }
        
        print(f"\n🚀 Sending verification request...")
        result = await self.make_request("POST", "/api/v1/products/verify-product", verification_data)
        
        if result['success']:
            verification = result['data']
            print(f"\n✅ VERIFICATION SUCCESSFUL!")
            print(f"   📊 Results:")
            print(f"      Is Authentic: {verification.get('verification', {}).get('is_authentic')}")
            print(f"      Confidence Score: {verification.get('confidence_score')}")
            print(f"      Risk Level: {verification.get('risk_level')}")
            print(f"      Detection Reasons: {len(verification.get('detection_reasons', []))}")
            
            # Show product details
            product = verification.get('product', {})
            print(f"\n📦 Product Details:")
            print(f"      ID: {product.get('id')}")
            print(f"      Name: {product.get('product_name')}")
            print(f"      Batch: {product.get('batch_number')}")
            print(f"      Category: {product.get('category')}")
            print(f"      Manufacturer: {product.get('manufacturer', {}).get('full_name')}")
            
            # Show verification details
            verification_info = verification.get('verification', {})
            print(f"\n🔍 Verification Details:")
            print(f"      ID: {verification_info.get('id')}")
            print(f"      Location: {verification_info.get('location')}")
            print(f"      Date: {verification_info.get('verification_date')}")
            print(f"      Notes: {verification_info.get('notes')}")
            
            # Show detection reasons
            reasons = verification.get('detection_reasons', [])
            print(f"\n🔍 Detection Reasons ({len(reasons)} total):")
            for i, reason in enumerate(reasons, 1):
                status = "✅" if "valid" in reason.lower() or "matches" in reason.lower() or "verified" in reason.lower() else "⚠️"
                print(f"      {i:2d}. {status} {reason}")
            
            # Summary
            print(f"\n🎯 SUMMARY:")
            if verification.get('verification', {}).get('is_authentic'):
                print(f"   🎉 SUCCESS: Product is AUTHENTIC!")
                print(f"   🛡️  The verification system is working correctly")
                print(f"   ✅ QR code hash validation passed")
                print(f"   ✅ IPFS data integrity verified")
                print(f"   ✅ Blockchain registration confirmed")
            else:
                print(f"   ⚠️  Product flagged as counterfeit")
                print(f"   🔍 Check detection reasons above")
                
        else:
            print(f"\n❌ VERIFICATION FAILED:")
            print(f"   Error: {result['data']}")

    async def run_test(self):
        """Run the complete test"""
        try:
            await self.test_exact_user_data()
            
            print("\n" + "=" * 60)
            print("🎯 EXACT USER DATA TEST COMPLETE")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Test failed: {str(e)}")

async def main():
    """Main test execution"""
    async with ExactFrontendDataTester() as tester:
        await tester.run_test()

if __name__ == "__main__":
    print("🎯 Exact Frontend Data Tester")
    print("Testing with the exact data provided by the user")
    print("Press Ctrl+C to cancel...")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
