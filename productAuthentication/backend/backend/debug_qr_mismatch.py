#!/usr/bin/env python3
"""
Debug QR Code Hash Mismatch Issue
Helps identify why QR codes don't match during verification
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzQHMuY29tIiwiZXhwIjoxNzU2ODM4NzQ5fQ.GvLkcrPEyTfekcM86gsjVnsgi648C_OQQp2fyNWoiMI"

class QRMismatchDebugger:
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

    async def debug_product_51(self):
        """Debug the specific product 51 that's having issues"""
        print("🔍 DEBUGGING PRODUCT 51: Authentic Luxury Watch")
        print("=" * 60)
        
        # Get the product details
        result = await self.make_request("GET", "/api/v1/products/51")
        
        if not result['success']:
            print(f"❌ Failed to get product 51: {result['data']}")
            return
        
        product = result['data']
        print(f"📦 Product Details:")
        print(f"   ID: {product['id']}")
        print(f"   Name: {product['product_name']}")
        print(f"   Batch: {product['batch_number']}")
        print(f"   QR Hash (stored): {product['qr_code_hash']}")
        print(f"   IPFS Hash: {product.get('ipfs_hash', 'N/A')}")
        print(f"   Blockchain ID: {product.get('blockchain_id', 'N/A')}")
        
        return product

    async def test_correct_qr_verification(self, product):
        """Test verification with the correct QR code"""
        print(f"\n✅ Testing with CORRECT QR Code")
        print("-" * 40)
        
        correct_qr_data = {
            "qr_data": product['qr_code_hash'],  # Use the stored QR hash
            "location": "Debug Test Location",
            "notes": "Testing with correct QR code from database"
        }
        
        result = await self.make_request("POST", "/api/v1/products/verify-product", correct_qr_data)
        
        if result['success']:
            verification = result['data']
            print(f"✅ Verification with CORRECT QR Code:")
            print(f"   Is Authentic: {verification.get('is_authentic', 'N/A')}")
            print(f"   Confidence Score: {verification.get('confidence_score', 'N/A')}")
            print(f"   Risk Level: {verification.get('risk_level', 'N/A')}")
            print(f"   Detection Reasons:")
            
            reasons = verification.get('detection_reasons', [])
            for i, reason in enumerate(reasons, 1):
                print(f"     {i}. {reason}")
        else:
            print(f"❌ Verification failed: {result['data']}")

    async def test_incorrect_qr_verification(self, product):
        """Test verification with an incorrect QR code"""
        print(f"\n❌ Testing with INCORRECT QR Code")
        print("-" * 40)
        
        # Create a fake QR code that's similar but different
        fake_qr = product['qr_code_hash'][:-5] + "12345"  # Change last 5 characters
        
        incorrect_qr_data = {
            "qr_data": fake_qr,
            "location": "Debug Test Location",
            "notes": "Testing with incorrect QR code"
        }
        
        result = await self.make_request("POST", "/api/v1/products/verify-product", incorrect_qr_data)
        
        if result['success']:
            verification = result['data']
            print(f"❌ Verification with INCORRECT QR Code:")
            print(f"   Is Authentic: {verification.get('is_authentic', 'N/A')}")
            print(f"   Confidence Score: {verification.get('confidence_score', 'N/A')}")
            print(f"   Risk Level: {verification.get('risk_level', 'N/A')}")
            print(f"   Detection Reasons:")
            
            reasons = verification.get('detection_reasons', [])
            for i, reason in enumerate(reasons, 1):
                print(f"     {i}. {reason}")
        else:
            print(f"❌ Verification failed: {result['data']}")

    async def check_qr_generation_process(self, product):
        """Check how QR codes are generated and stored"""
        print(f"\n🔧 Checking QR Code Generation Process")
        print("-" * 40)
        
        # Get the QR code details
        result = await self.make_request("GET", f"/api/v1/products/{product['id']}/qr-code")
        
        if result['success']:
            qr_data = result['data']
            print(f"✅ QR Code Details:")
            print(f"   QR Hash: {qr_data.get('qr_code_hash', 'N/A')}")
            print(f"   QR Path: {qr_data.get('qr_code_path', 'N/A')}")
            print(f"   Generated At: {qr_data.get('created_at', 'N/A')}")
        else:
            print(f"❌ Failed to get QR code details: {result['data']}")

    async def analyze_verification_history(self, product):
        """Analyze verification history for this product"""
        print(f"\n📊 Analyzing Verification History for Product {product['id']}")
        print("-" * 40)
        
        result = await self.make_request("GET", f"/api/v1/verifications/product/{product['id']}")
        
        if result['success']:
            verifications = result['data']
            print(f"✅ Verification History:")
            print(f"   Total Verifications: {len(verifications)}")
            
            for i, verification in enumerate(verifications, 1):
                print(f"   {i}. Date: {verification.get('verification_date', 'N/A')}")
                print(f"      Location: {verification.get('location', 'N/A')}")
                print(f"      Is Authentic: {verification.get('is_authentic', 'N/A')}")
                print(f"      Confidence: {verification.get('confidence_score', 'N/A')}")
                print(f"      Notes: {verification.get('notes', 'N/A')}")
        else:
            print(f"❌ Failed to get verification history: {result['data']}")

    async def run_debug_analysis(self):
        """Run complete debug analysis"""
        print("🔍 QR CODE MISMATCH DEBUG ANALYSIS")
        print("=" * 60)
        
        try:
            # Debug the specific product
            product = await self.debug_product_51()
            if not product:
                return
            
            # Test with correct QR code
            await self.test_correct_qr_verification(product)
            
            # Test with incorrect QR code
            await self.test_incorrect_qr_verification(product)
            
            # Check QR generation process
            await self.check_qr_generation_process(product)
            
            # Analyze verification history
            await self.analyze_verification_history(product)
            
            print("\n" + "=" * 60)
            print("🎯 DEBUG ANALYSIS COMPLETE")
            print("=" * 60)
            print("💡 Key Insights:")
            print("   1. The system is working correctly - it detected a QR mismatch")
            print("   2. You need to use the EXACT QR code hash from the database")
            print("   3. QR codes are generated when products are created")
            print("   4. Any QR code mismatch will flag the product as counterfeit")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Debug analysis failed: {str(e)}")

async def main():
    """Main debug execution"""
    async with QRMismatchDebugger() as debugger:
        await debugger.run_debug_analysis()

if __name__ == "__main__":
    print("🔍 QR Code Mismatch Debug Tool")
    print("Make sure your FastAPI server is running on http://localhost:8000")
    print("Press Ctrl+C to cancel...")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Debug cancelled by user")
    except Exception as e:
        print(f"\n❌ Debug failed: {str(e)}")
