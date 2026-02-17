#!/usr/bin/env python3
"""
Specific Test Scenarios for Verification System
Tests specific counterfeit detection scenarios
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzQHMuY29tIiwiZXhwIjoxNzU2ODM4NzQ5fQ.GvLkcrPEyTfekcM86gsjVnsgi648C_OQQp2fyNWoiMI"

class ScenarioTester:
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

    async def test_scenario_1_authentic_product(self):
        """Test Scenario 1: Authentic Product Verification"""
        print("\n🔍 Scenario 1: Authentic Product Verification")
        print("-" * 50)
        
        # First, get an existing product
        result = await self.make_request("GET", "/api/v1/products/")
        
        if not result['success'] or not result['data']:
            print("❌ No products found. Please create a product first.")
            return
        
        product = result['data'][0]  # Use first product
        print(f"📦 Testing with product: {product['product_name']}")
        print(f"   Product ID: {product['id']}")
        print(f"   QR Hash: {product['qr_code_hash']}")
        print(f"   IPFS Hash: {product.get('ipfs_hash', 'N/A')}")
        
        # Test authentic verification
        verification_data = {
            "qr_data": product['qr_code_hash'],
            "location": "Authentic Test Location",
            "notes": "Testing authentic product verification"
        }
        
        result = await self.make_request("POST", "/api/v1/products/verify-product", verification_data)
        
        if result['success']:
            verification = result['data']
            print(f"\n✅ Verification Result:")
            print(f"   Is Authentic: {verification.get('is_authentic', 'N/A')}")
            print(f"   Confidence Score: {verification.get('confidence_score', 'N/A')}")
            print(f"   Risk Level: {verification.get('risk_level', 'N/A')}")
            print(f"   Detection Reasons: {len(verification.get('detection_reasons', []))} reasons")
            
            # Show first few reasons
            reasons = verification.get('detection_reasons', [])
            for i, reason in enumerate(reasons[:3], 1):
                print(f"     {i}. {reason}")
        else:
            print(f"❌ Verification failed: {result['data']}")

    async def test_scenario_2_fake_qr_code(self):
        """Test Scenario 2: Fake QR Code Detection"""
        print("\n🔍 Scenario 2: Fake QR Code Detection")
        print("-" * 50)
        
        # Test with completely fake QR code
        fake_qr_data = {
            "qr_data": "fake_qr_hash_1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "location": "Fake QR Test Location",
            "notes": "Testing fake QR code detection"
        }
        
        result = await self.make_request("POST", "/api/v1/products/verify-product", fake_qr_data)
        
        if result['success']:
            verification = result['data']
            print(f"✅ Fake QR Detection Result:")
            print(f"   Is Authentic: {verification.get('is_authentic', 'N/A')}")
            print(f"   Confidence Score: {verification.get('confidence_score', 'N/A')}")
            print(f"   Risk Level: {verification.get('risk_level', 'N/A')}")
            print(f"   Detection Reasons: {len(verification.get('detection_reasons', []))} reasons")
            
            # Show detection reasons
            reasons = verification.get('detection_reasons', [])
            for i, reason in enumerate(reasons, 1):
                print(f"     {i}. {reason}")
        else:
            print(f"❌ Fake QR test failed: {result['data']}")

    async def test_scenario_3_invalid_qr_format(self):
        """Test Scenario 3: Invalid QR Code Format"""
        print("\n🔍 Scenario 3: Invalid QR Code Format")
        print("-" * 50)
        
        # Test with invalid QR format (too short)
        invalid_qr_data = {
            "qr_data": "short_hash",
            "location": "Invalid Format Test",
            "notes": "Testing invalid QR format detection"
        }
        
        result = await self.make_request("POST", "/api/v1/products/verify-product", invalid_qr_data)
        
        if result['success']:
            verification = result['data']
            print(f"✅ Invalid Format Detection Result:")
            print(f"   Is Authentic: {verification.get('is_authentic', 'N/A')}")
            print(f"   Confidence Score: {verification.get('confidence_score', 'N/A')}")
            print(f"   Risk Level: {verification.get('risk_level', 'N/A')}")
            print(f"   Detection Reasons: {len(verification.get('detection_reasons', []))} reasons")
            
            # Show detection reasons
            reasons = verification.get('detection_reasons', [])
            for i, reason in enumerate(reasons, 1):
                print(f"     {i}. {reason}")
        else:
            print(f"❌ Invalid format test failed: {result['data']}")

    async def test_scenario_4_ipfs_data_verification(self):
        """Test Scenario 4: IPFS Data Verification"""
        print("\n🔍 Scenario 4: IPFS Data Verification")
        print("-" * 50)
        
        # Get a product with IPFS data
        result = await self.make_request("GET", "/api/v1/products/")
        
        if not result['success'] or not result['data']:
            print("❌ No products found.")
            return
        
        product = result['data'][0]
        
        if not product.get('ipfs_hash'):
            print("⚠️ Product has no IPFS hash. Creating a new product...")
            # Create a new product to get IPFS data
            new_product_data = {
                "product_name": "IPFS Test Product",
                "product_description": "Product for testing IPFS data verification",
                "manufacturing_date": "2024-01-15T00:00:00Z",
                "batch_number": "IPFS-TEST-001",
                "category": "electronics"
            }
            
            result = await self.make_request("POST", "/api/v1/products/", new_product_data)
            if result['success']:
                product = result['data']
                print(f"✅ Created new product with IPFS hash: {product.get('ipfs_hash', 'N/A')}")
            else:
                print(f"❌ Failed to create product: {result['data']}")
                return
        
        # Test IPFS data retrieval
        print(f"📦 Testing IPFS data for product: {product['product_name']}")
        print(f"   IPFS Hash: {product.get('ipfs_hash', 'N/A')}")
        
        result = await self.make_request("GET", f"/api/v1/products/{product['id']}/ipfs-data")
        
        if result['success']:
            ipfs_data = result['data']
            print(f"✅ IPFS Data Retrieved:")
            print(f"   IPFS Hash: {ipfs_data.get('ipfs_hash', 'N/A')}")
            print(f"   IPFS URL: {ipfs_data.get('ipfs_url', 'N/A')}")
            print(f"   Product Data Available: {'Yes' if ipfs_data.get('product_data') else 'No'}")
            print(f"   Metadata Available: {'Yes' if ipfs_data.get('metadata') else 'No'}")
            
            if ipfs_data.get('product_data'):
                product_data = ipfs_data['product_data']
                print(f"   Product Name in IPFS: {product_data.get('product_name', 'N/A')}")
                print(f"   Batch Number in IPFS: {product_data.get('batch_number', 'N/A')}")
        else:
            print(f"❌ IPFS data retrieval failed: {result['data']}")

    async def test_scenario_5_duplicate_detection(self):
        """Test Scenario 5: Duplicate Detection"""
        print("\n🔍 Scenario 5: Duplicate Detection")
        print("-" * 50)
        
        # Get existing products
        result = await self.make_request("GET", "/api/v1/products/")
        
        if not result['success'] or not result['data']:
            print("❌ No products found.")
            return
        
        products = result['data']
        if len(products) < 1:
            print("❌ Need at least one product for duplicate testing.")
            return
        
        # Use the first product's QR hash for duplicate testing
        original_product = products[0]
        print(f"📦 Original Product: {original_product['product_name']}")
        print(f"   QR Hash: {original_product['qr_code_hash']}")
        
        # Test verification with the same QR hash (should detect as duplicate if used elsewhere)
        duplicate_test_data = {
            "qr_data": original_product['qr_code_hash'],
            "location": "Duplicate Detection Test",
            "notes": "Testing duplicate QR code detection"
        }
        
        result = await self.make_request("POST", "/api/v1/products/verify-product", duplicate_test_data)
        
        if result['success']:
            verification = result['data']
            print(f"✅ Duplicate Detection Result:")
            print(f"   Is Authentic: {verification.get('is_authentic', 'N/A')}")
            print(f"   Confidence Score: {verification.get('confidence_score', 'N/A')}")
            print(f"   Risk Level: {verification.get('risk_level', 'N/A')}")
            print(f"   Detection Reasons: {len(verification.get('detection_reasons', []))} reasons")
            
            # Show detection reasons
            reasons = verification.get('detection_reasons', [])
            for i, reason in enumerate(reasons, 1):
                print(f"     {i}. {reason}")
        else:
            print(f"❌ Duplicate detection test failed: {result['data']}")

    async def test_scenario_6_analytics_and_history(self):
        """Test Scenario 6: Analytics and Verification History"""
        print("\n🔍 Scenario 6: Analytics and Verification History")
        print("-" * 50)
        
        # Test analytics overview
        result = await self.make_request("GET", "/api/v1/analytics/overview")
        
        if result['success']:
            overview = result['data']
            print(f"✅ Analytics Overview:")
            print(f"   Total Products: {overview.get('totalProducts', 'N/A')}")
            print(f"   Total Users: {overview.get('totalUsers', 'N/A')}")
            print(f"   Total Verifications: {overview.get('totalVerifications', 'N/A')}")
            print(f"   Counterfeit Alerts: {overview.get('counterfeitAlerts', 'N/A')}")
            print(f"   Blockchain Transactions: {overview.get('blockchainTransactions', 'N/A')}")
        else:
            print(f"❌ Analytics overview failed: {result['data']}")
        
        # Test verification history
        result = await self.make_request("GET", "/api/v1/verifications/")
        
        if result['success']:
            verifications = result['data']
            print(f"\n✅ Verification History:")
            print(f"   Total Verifications: {len(verifications)}")
            
            if verifications:
                authentic_count = sum(1 for v in verifications if v.get('is_authentic', False))
                counterfeit_count = len(verifications) - authentic_count
                
                print(f"   Authentic Verifications: {authentic_count}")
                print(f"   Counterfeit Detections: {counterfeit_count}")
                
                # Show latest verification
                latest = verifications[0]
                print(f"   Latest Verification:")
                print(f"     Date: {latest.get('verification_date', 'N/A')}")
                print(f"     Location: {latest.get('location', 'N/A')}")
                print(f"     Is Authentic: {latest.get('is_authentic', 'N/A')}")
                print(f"     Confidence Score: {latest.get('confidence_score', 'N/A')}")
        else:
            print(f"❌ Verification history failed: {result['data']}")

    async def run_all_scenarios(self):
        """Run all test scenarios"""
        print("🚀 Starting Specific Verification Scenarios")
        print("=" * 60)
        
        try:
            await self.test_scenario_1_authentic_product()
            await self.test_scenario_2_fake_qr_code()
            await self.test_scenario_3_invalid_qr_format()
            await self.test_scenario_4_ipfs_data_verification()
            await self.test_scenario_5_duplicate_detection()
            await self.test_scenario_6_analytics_and_history()
            
            print("\n" + "=" * 60)
            print("✅ All scenarios completed!")
            
        except Exception as e:
            print(f"\n❌ Scenario execution failed: {str(e)}")

async def main():
    """Main scenario execution"""
    async with ScenarioTester() as tester:
        await tester.run_all_scenarios()

if __name__ == "__main__":
    print("🔍 Specific Verification Scenarios Test Suite")
    print("Make sure your FastAPI server is running on http://localhost:8000")
    print("Press Ctrl+C to cancel...")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Tests cancelled by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
