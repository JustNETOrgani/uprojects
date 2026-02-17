#!/usr/bin/env python3
"""
Test QR Hash Fix
Tests if the QR hash mismatch issue is resolved
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzQHMuY29tIiwiZXhwIjoxNzU2ODQxNTM2fQ.beJPjNuwTLCGJoV4Fl0qAUKtGvQHxlaRdDfk18bs3y0"

class QRFixTester:
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

    async def test_qr_fix(self):
        """Test if the QR hash fix works"""
        print("🔧 TESTING QR HASH FIX")
        print("=" * 50)
        
        # Test with the exact frontend data
        print("\n📱 Testing with Frontend QR Data")
        qr_data_json = '{"product_id": 51, "product_name": "Authentic Luxury Watch", "batch_number": "LUX-WATCH-2024-001", "qr_hash": "77c14d24949c39ef15eff39fb1c3da47defad2ecf89d0ec479e0efed61e0f177", "timestamp": "2025-09-02 17:55:48.391108+00:00"}'
        
        verification_data = {
            "qr_data": qr_data_json,
            "location": "Unknown",
            "notes": ""
        }
        
        result = await self.make_request("POST", "/api/v1/products/verify-product", verification_data)
        
        if result['success']:
            verification = result['data']
            print(f"   ✅ Verification Response:")
            print(f"      Is Authentic: {verification.get('verification', {}).get('is_authentic')}")
            print(f"      Confidence Score: {verification.get('confidence_score')}")
            print(f"      Risk Level: {verification.get('risk_level')}")
            print(f"      Detection Reasons: {len(verification.get('detection_reasons', []))}")
            
            # Show detection reasons
            reasons = verification.get('detection_reasons', [])
            print(f"   🔍 Detection Reasons:")
            for i, reason in enumerate(reasons, 1):
                print(f"      {i}. {reason}")
            
            # Check if QR hash mismatch is still present
            qr_mismatch_found = any("QR code hash mismatch" in reason for reason in reasons)
            if qr_mismatch_found:
                print(f"   ❌ QR hash mismatch still present - fix not working")
            else:
                print(f"   ✅ QR hash mismatch resolved!")
                
            # Check if product is now authentic
            if verification.get('verification', {}).get('is_authentic'):
                print(f"   🎉 SUCCESS! Product is now verified as authentic!")
            else:
                print(f"   ⚠️  Product still showing as counterfeit")
                
        else:
            print(f"   ❌ Verification failed: {result['data']}")

    async def run_test(self):
        """Run the complete test"""
        try:
            await self.test_qr_fix()
            
            print("\n" + "=" * 50)
            print("🎯 QR FIX TEST COMPLETE")
            print("=" * 50)
            
        except Exception as e:
            print(f"\n❌ Test failed: {str(e)}")

async def main():
    """Main test execution"""
    async with QRFixTester() as tester:
        await tester.run_test()

if __name__ == "__main__":
    print("🔧 QR Hash Fix Tester")
    print("Testing if the QR hash mismatch issue is resolved")
    print("Press Ctrl+C to cancel...")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
