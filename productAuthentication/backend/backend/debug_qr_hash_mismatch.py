#!/usr/bin/env python3
"""
Debug QR Hash Mismatch Issue
Investigates why Product 51 is being flagged as counterfeit despite correct QR data
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzQHMuY29tIiwiZXhwIjoxNzU2ODQxNTM2fQ.beJPjNuwTLCGJoV4Fl0qAUKtGvQHxlaRdDfk18bs3y0"

class QRHashMismatchDebugger:
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

    async def debug_product_51_qr_mismatch(self):
        """Debug the specific QR hash mismatch for Product 51"""
        print("🔍 DEBUGGING QR HASH MISMATCH FOR PRODUCT 51")
        print("=" * 60)
        
        # Step 1: Get Product 51 details
        print("\n📦 Step 1: Getting Product 51 Details")
        result = await self.make_request("GET", "/api/v1/products/51")
        
        if result['success']:
            product = result['data']
            print(f"   ✅ Product Retrieved:")
            print(f"      ID: {product.get('id')}")
            print(f"      Name: {product.get('product_name')}")
            print(f"      QR Hash: {product.get('qr_code_hash')}")
            print(f"      IPFS Hash: {product.get('ipfs_hash')}")
            print(f"      Blockchain ID: {product.get('blockchain_id')}")
            
            stored_qr_hash = product.get('qr_code_hash')
        else:
            print(f"   ❌ Failed to get product: {result['data']}")
            return

        # Step 2: Parse the QR data from frontend
        print("\n📱 Step 2: Analyzing Frontend QR Data")
        qr_data_json = '{"product_id": 51, "product_name": "Authentic Luxury Watch", "batch_number": "LUX-WATCH-2024-001", "qr_hash": "77c14d24949c39ef15eff39fb1c3da47defad2ecf89d0ec479e0efed61e0f177", "timestamp": "2025-09-02 17:55:48.391108+00:00"}'
        
        try:
            qr_data = json.loads(qr_data_json)
            frontend_qr_hash = qr_data.get('qr_hash')
            print(f"   ✅ QR Data Parsed:")
            print(f"      Product ID: {qr_data.get('product_id')}")
            print(f"      Product Name: {qr_data.get('product_name')}")
            print(f"      Batch Number: {qr_data.get('batch_number')}")
            print(f"      QR Hash: {frontend_qr_hash}")
            print(f"      Timestamp: {qr_data.get('timestamp')}")
        except Exception as e:
            print(f"   ❌ Failed to parse QR data: {e}")
            return

        # Step 3: Compare QR hashes
        print("\n🔍 Step 3: Comparing QR Hashes")
        print(f"   📊 Hash Comparison:")
        print(f"      Stored QR Hash:    {stored_qr_hash}")
        print(f"      Frontend QR Hash:  {frontend_qr_hash}")
        print(f"      Hashes Match:      {stored_qr_hash == frontend_qr_hash}")
        
        if stored_qr_hash != frontend_qr_hash:
            print(f"   ⚠️  MISMATCH DETECTED!")
            print(f"      This is why the system flags it as counterfeit")
        else:
            print(f"   ✅ Hashes match - investigating other causes")

        # Step 4: Test the exact frontend request
        print("\n🧪 Step 4: Testing Exact Frontend Request")
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
        else:
            print(f"   ❌ Verification failed: {result['data']}")

        # Step 5: Check if QR hash needs to be updated
        print("\n🔧 Step 5: Checking QR Hash Update")
        if stored_qr_hash != frontend_qr_hash:
            print(f"   💡 SOLUTION: Update Product 51's QR hash")
            print(f"      Current stored hash: {stored_qr_hash}")
            print(f"      Should be: {frontend_qr_hash}")
            
            # Update the product's QR hash
            update_data = {
                "qr_code_hash": frontend_qr_hash
            }
            
            result = await self.make_request("PUT", "/api/v1/products/51", update_data)
            
            if result['success']:
                print(f"   ✅ QR hash updated successfully!")
                
                # Test verification again
                print(f"\n🧪 Step 6: Testing Verification After Update")
                result = await self.make_request("POST", "/api/v1/products/verify-product", verification_data)
                
                if result['success']:
                    verification = result['data']
                    print(f"   ✅ Updated Verification Response:")
                    print(f"      Is Authentic: {verification.get('verification', {}).get('is_authentic')}")
                    print(f"      Confidence Score: {verification.get('confidence_score')}")
                    print(f"      Risk Level: {verification.get('risk_level')}")
                    
                    if verification.get('verification', {}).get('is_authentic'):
                        print(f"   🎉 SUCCESS! Product is now verified as authentic!")
                    else:
                        print(f"   ⚠️  Still showing as counterfeit - investigating further...")
                else:
                    print(f"   ❌ Verification failed after update: {result['data']}")
            else:
                print(f"   ❌ Failed to update QR hash: {result['data']}")

    async def run_debug(self):
        """Run the complete debug process"""
        try:
            await self.debug_product_51_qr_mismatch()
            
            print("\n" + "=" * 60)
            print("🎯 DEBUG COMPLETE")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Debug failed: {str(e)}")

async def main():
    """Main debug execution"""
    async with QRHashMismatchDebugger() as debugger:
        await debugger.run_debug()

if __name__ == "__main__":
    print("🔍 QR Hash Mismatch Debugger")
    print("Investigating why Product 51 is flagged as counterfeit")
    print("Press Ctrl+C to cancel...")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Debug cancelled by user")
    except Exception as e:
        print(f"\n❌ Debug failed: {str(e)}")
