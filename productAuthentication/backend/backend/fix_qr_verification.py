#!/usr/bin/env python3
"""
Fix QR Code Verification Issue
Demonstrates the correct way to verify products using QR codes
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzQHMuY29tIiwiZXhwIjoxNzU2ODM4NzQ5fQ.GvLkcrPEyTfekcM86gsjVnsgi648C_OQQp2fyNWoiMI"

class QRVerificationFixer:
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

    async def demonstrate_correct_verification_methods(self):
        """Demonstrate the correct ways to verify products"""
        print("🔧 FIXING QR CODE VERIFICATION ISSUE")
        print("=" * 60)
        
        # Get product 51 details
        result = await self.make_request("GET", "/api/v1/products/51")
        
        if not result['success']:
            print(f"❌ Failed to get product 51: {result['data']}")
            return
        
        product = result['data']
        print(f"📦 Product 51 Details:")
        print(f"   ID: {product['id']}")
        print(f"   Name: {product['product_name']}")
        print(f"   QR Hash: {product['qr_code_hash']}")
        print(f"   IPFS Hash: {product.get('ipfs_hash', 'N/A')}")
        
        print(f"\n🎯 SOLUTION: Use Direct Verification Instead of QR Verification")
        print("-" * 60)
        
        # Method 1: Direct verification using product ID
        print(f"\n✅ Method 1: Direct Verification (RECOMMENDED)")
        direct_verification = {
            "product_id": product['id'],
            "location": "Fixed Verification Test",
            "notes": "Using direct verification method",
            "qr_code_hash": product['qr_code_hash']  # Include QR hash for validation
        }
        
        result = await self.make_request("POST", "/api/v1/verifications/", direct_verification)
        
        if result['success']:
            verification = result['data']
            print(f"✅ Direct Verification Result:")
            print(f"   Is Authentic: {verification.get('is_authentic', 'N/A')}")
            print(f"   Confidence Score: {verification.get('confidence_score', 'N/A')}")
            print(f"   Risk Level: {verification.get('risk_level', 'N/A')}")
            print(f"   Detection Reasons: {len(verification.get('detection_reasons', []))} reasons")
            
            # Show detection reasons
            reasons = verification.get('detection_reasons', [])
            for i, reason in enumerate(reasons, 1):
                print(f"     {i}. {reason}")
        else:
            print(f"❌ Direct verification failed: {result['data']}")
        
        # Method 2: Create proper QR code JSON format
        print(f"\n✅ Method 2: Proper QR Code JSON Format")
        proper_qr_data = {
            "product_id": product['id'],
            "product_name": product['product_name'],
            "batch_number": product['batch_number'],
            "qr_hash": product['qr_code_hash']
        }
        
        qr_verification = {
            "qr_data": json.dumps(proper_qr_data),  # Convert to JSON string
            "location": "Fixed QR Verification Test",
            "notes": "Using proper QR code JSON format"
        }
        
        result = await self.make_request("POST", "/api/v1/products/verify-product", qr_verification)
        
        if result['success']:
            verification = result['data']
            print(f"✅ QR Verification Result:")
            print(f"   Is Authentic: {verification.get('is_authentic', 'N/A')}")
            print(f"   Confidence Score: {verification.get('confidence_score', 'N/A')}")
            print(f"   Risk Level: {verification.get('risk_level', 'N/A')}")
            print(f"   Detection Reasons: {len(verification.get('detection_reasons', []))} reasons")
            
            # Show detection reasons
            reasons = verification.get('detection_reasons', [])
            for i, reason in enumerate(reasons, 1):
                print(f"     {i}. {reason}")
        else:
            print(f"❌ QR verification failed: {result['data']}")

    async def show_verification_methods_comparison(self):
        """Show comparison of different verification methods"""
        print(f"\n📊 VERIFICATION METHODS COMPARISON")
        print("=" * 60)
        
        print(f"🔍 Method 1: Direct Verification (RECOMMENDED)")
        print(f"   Endpoint: POST /api/v1/verifications/")
        print(f"   Data: {{'product_id': 51, 'location': '...', 'qr_code_hash': '...'}}")
        print(f"   Pros: ✅ Simple, reliable, works with product ID")
        print(f"   Cons: ❌ Requires knowing the product ID")
        
        print(f"\n🔍 Method 2: QR Code Verification (COMPLEX)")
        print(f"   Endpoint: POST /api/v1/products/verify-product")
        print(f"   Data: {{'qr_data': '{{JSON}}', 'location': '...'}}")
        print(f"   Pros: ✅ Works with QR code scanning")
        print(f"   Cons: ❌ Requires proper JSON format in QR code")
        
        print(f"\n🔍 Method 3: Counterfeit Analysis")
        print(f"   Endpoint: POST /api/v1/verifications/analyze-counterfeit/51")
        print(f"   Data: {{'qr_code_hash': '...', 'location': '...'}}")
        print(f"   Pros: ✅ Detailed analysis, works with QR hash")
        print(f"   Cons: ❌ More complex response")

    async def create_working_verification_examples(self):
        """Create working examples for all verification methods"""
        print(f"\n💡 WORKING VERIFICATION EXAMPLES")
        print("=" * 60)
        
        # Get product 51
        result = await self.make_request("GET", "/api/v1/products/51")
        if not result['success']:
            return
        
        product = result['data']
        
        print(f"📝 Example 1: Direct Verification (BEST METHOD)")
        print(f"```bash")
        print(f"curl -X POST '{BASE_URL}/api/v1/verifications/' \\")
        print(f"  -H 'Authorization: Bearer {BEARER_TOKEN[:20]}...' \\")
        print(f"  -H 'Content-Type: application/json' \\")
        print(f"  -d '{{")
        print(f"    \"product_id\": {product['id']},")
        print(f"    \"location\": \"Your Location\",")
        print(f"    \"notes\": \"Verification notes\",")
        print(f"    \"qr_code_hash\": \"{product['qr_code_hash']}\"")
        print(f"  }}'")
        print(f"```")
        
        print(f"\n📝 Example 2: QR Code Verification (IF YOU HAVE PROPER QR)")
        print(f"```bash")
        print(f"curl -X POST '{BASE_URL}/api/v1/products/verify-product' \\")
        print(f"  -H 'Authorization: Bearer {BEARER_TOKEN[:20]}...' \\")
        print(f"  -H 'Content-Type: application/json' \\")
        print(f"  -d '{{")
        print(f"    \"qr_data\": \"{{\\\"product_id\\\": {product['id']}, \\\"product_name\\\": \\\"{product['product_name']}\\\", \\\"batch_number\\\": \\\"{product['batch_number']}\\\", \\\"qr_hash\\\": \\\"{product['qr_code_hash']}\\\"}}\",")
        print(f"    \"location\": \"Your Location\",")
        print(f"    \"notes\": \"Verification notes\"")
        print(f"  }}'")
        print(f"```")
        
        print(f"\n📝 Example 3: Counterfeit Analysis")
        print(f"```bash")
        print(f"curl -X POST '{BASE_URL}/api/v1/verifications/analyze-counterfeit/{product['id']}' \\")
        print(f"  -H 'Authorization: Bearer {BEARER_TOKEN[:20]}...' \\")
        print(f"  -H 'Content-Type: application/json' \\")
        print(f"  -d '{{")
        print(f"    \"qr_code_hash\": \"{product['qr_code_hash']}\",")
        print(f"    \"location\": \"Your Location\"")
        print(f"  }}'")
        print(f"```")

    async def run_fix_analysis(self):
        """Run complete fix analysis"""
        print("🔧 QR CODE VERIFICATION FIX ANALYSIS")
        print("=" * 60)
        
        try:
            await self.demonstrate_correct_verification_methods()
            await self.show_verification_methods_comparison()
            await self.create_working_verification_examples()
            
            print(f"\n" + "=" * 60)
            print(f"🎯 SUMMARY OF THE ISSUE AND SOLUTION")
            print(f"=" * 60)
            print(f"❌ PROBLEM:")
            print(f"   - You were passing just the QR hash string")
            print(f"   - The system expects a JSON object with specific fields")
            print(f"   - This caused 'QR code format invalid' error")
            print(f"")
            print(f"✅ SOLUTION:")
            print(f"   - Use direct verification with product ID (RECOMMENDED)")
            print(f"   - Or create proper QR JSON format")
            print(f"   - The system is working correctly - it's protecting against invalid QR codes")
            print(f"")
            print(f"🚀 RECOMMENDED APPROACH:")
            print(f"   - Use Method 1 (Direct Verification) for reliability")
            print(f"   - Use product ID instead of QR code parsing")
            print(f"   - Include QR hash for validation if needed")
            print(f"=" * 60)
            
        except Exception as e:
            print(f"\n❌ Fix analysis failed: {str(e)}")

async def main():
    """Main fix execution"""
    async with QRVerificationFixer() as fixer:
        await fixer.run_fix_analysis()

if __name__ == "__main__":
    print("🔧 QR Code Verification Fix Tool")
    print("Make sure your FastAPI server is running on http://localhost:8000")
    print("Press Ctrl+C to cancel...")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Fix cancelled by user")
    except Exception as e:
        print(f"\n❌ Fix failed: {str(e)}")
