#!/usr/bin/env python3
"""
Comprehensive Test Suite for Product Verification System with IPFS Integration
Tests all verification scenarios including counterfeit detection
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzQHMuY29tIiwiZXhwIjoxNzU2ODM4NzQ5fQ.GvLkcrPEyTfekcM86gsjVnsgi648C_OQQp2fyNWoiMI"

class VerificationTester:
    def __init__(self):
        self.session = None
        self.headers = {
            "Authorization": f"Bearer {BEARER_TOKEN}",
            "Content-Type": "application/json"
        }
        self.test_products = []
        self.test_results = []

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
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

    async def test_ipfs_status(self):
        """Test IPFS service status"""
        print("\n🔍 Testing IPFS Service Status...")
        
        # Test IPFS service directly
        result = await self.make_request("GET", "/api/v1/products/1/ipfs-data")
        print(f"IPFS Status Check: {result['status']}")
        
        if result['success']:
            print("✅ IPFS service is working")
        else:
            print("⚠️ IPFS service may be using mock mode")

    async def create_test_products(self):
        """Create test products for verification testing"""
        print("\n📦 Creating Test Products...")
        
        test_products_data = [
            {
                "product_name": "Authentic Test Product 1",
                "product_description": "A genuine product for testing verification",
                "manufacturing_date": "2024-01-01T00:00:00Z",
                "batch_number": "AUTH-001-2024",
                "category": "electronics"
            },
            {
                "product_name": "Authentic Test Product 2",
                "product_description": "Another genuine product for testing",
                "manufacturing_date": "2024-01-02T00:00:00Z",
                "batch_number": "AUTH-002-2024",
                "category": "pharmaceuticals"
            },
            {
                "product_name": "Suspicious Test Product",
                "product_description": "Product with incomplete information",
                "manufacturing_date": "2024-01-03T00:00:00Z",
                "batch_number": "SUSP-001-2024",
                "category": "luxury_goods"
            }
        ]
        
        for i, product_data in enumerate(test_products_data):
            result = await self.make_request("POST", "/api/v1/products/", product_data)
            
            if result['success']:
                product = result['data']
                self.test_products.append(product)
                print(f"✅ Created Product {i+1}: {product['product_name']}")
                print(f"   ID: {product['id']}")
                print(f"   IPFS Hash: {product.get('ipfs_hash', 'N/A')}")
                print(f"   Blockchain ID: {product.get('blockchain_id', 'N/A')}")
            else:
                print(f"❌ Failed to create Product {i+1}: {result['data']}")

    async def test_qr_verification(self):
        """Test QR code verification scenarios"""
        print("\n📱 Testing QR Code Verification...")
        
        if not self.test_products:
            print("❌ No test products available")
            return
        
        product = self.test_products[0]
        
        # Test 1: Valid QR verification
        print("\n🔍 Test 1: Valid QR Code Verification")
        qr_data = {
            "qr_data": product['qr_code_hash'],
            "location": "Test Warehouse",
            "notes": "Valid QR code test"
        }
        
        result = await self.make_request("POST", "/api/v1/products/verify-product", qr_data)
        
        if result['success']:
            verification = result['data']
            print(f"✅ Valid QR Verification: {verification['is_authentic']}")
            print(f"   Confidence Score: {verification.get('confidence_score', 'N/A')}")
            print(f"   Risk Level: {verification.get('risk_level', 'N/A')}")
            print(f"   Detection Reasons: {len(verification.get('detection_reasons', []))} reasons")
        else:
            print(f"❌ Valid QR Verification Failed: {result['data']}")
        
        # Test 2: Invalid QR verification
        print("\n🔍 Test 2: Invalid QR Code Verification")
        invalid_qr_data = {
            "qr_data": "invalid_qr_hash_12345",
            "location": "Test Location",
            "notes": "Invalid QR code test"
        }
        
        result = await self.make_request("POST", "/api/v1/products/verify-product", invalid_qr_data)
        
        if result['success']:
            verification = result['data']
            print(f"✅ Invalid QR Verification: {verification['is_authentic']}")
            print(f"   Confidence Score: {verification.get('confidence_score', 'N/A')}")
            print(f"   Risk Level: {verification.get('risk_level', 'N/A')}")
        else:
            print(f"❌ Invalid QR Verification Failed: {result['data']}")

    async def test_direct_verification(self):
        """Test direct product verification"""
        print("\n🎯 Testing Direct Product Verification...")
        
        if not self.test_products:
            print("❌ No test products available")
            return
        
        product = self.test_products[0]
        
        verification_data = {
            "product_id": product['id'],
            "location": "Direct Verification Test",
            "notes": "Testing direct verification method",
            "qr_code_hash": product['qr_code_hash']
        }
        
        result = await self.make_request("POST", "/api/v1/verifications/", verification_data)
        
        if result['success']:
            verification = result['data']
            print(f"✅ Direct Verification: {verification['is_authentic']}")
            print(f"   Verification ID: {verification['id']}")
            print(f"   Confidence Score: {verification.get('confidence_score', 'N/A')}")
            print(f"   Detection Reasons: {verification.get('detection_reasons', [])}")
        else:
            print(f"❌ Direct Verification Failed: {result['data']}")

    async def test_counterfeit_analysis(self):
        """Test detailed counterfeit analysis"""
        print("\n🔬 Testing Detailed Counterfeit Analysis...")
        
        if not self.test_products:
            print("❌ No test products available")
            return
        
        product = self.test_products[0]
        
        analysis_data = {
            "qr_code_hash": product['qr_code_hash'],
            "location": "Counterfeit Analysis Test"
        }
        
        result = await self.make_request(
            "POST", 
            f"/api/v1/verifications/analyze-counterfeit/{product['id']}",
            analysis_data
        )
        
        if result['success']:
            analysis = result['data']
            print(f"✅ Counterfeit Analysis Complete")
            print(f"   Is Authentic: {analysis.get('is_authentic', 'N/A')}")
            print(f"   Confidence Score: {analysis.get('confidence_score', 'N/A')}")
            print(f"   Risk Level: {analysis.get('risk_level', 'N/A')}")
            print(f"   Detection Reasons: {len(analysis.get('detection_reasons', []))} reasons")
            
            # Print detailed reasons
            reasons = analysis.get('detection_reasons', [])
            for i, reason in enumerate(reasons[:5], 1):  # Show first 5 reasons
                print(f"     {i}. {reason}")
            if len(reasons) > 5:
                print(f"     ... and {len(reasons) - 5} more reasons")
        else:
            print(f"❌ Counterfeit Analysis Failed: {result['data']}")

    async def test_ipfs_data_retrieval(self):
        """Test IPFS data retrieval"""
        print("\n🌐 Testing IPFS Data Retrieval...")
        
        if not self.test_products:
            print("❌ No test products available")
            return
        
        for i, product in enumerate(self.test_products[:2]):  # Test first 2 products
            print(f"\n🔍 Testing IPFS Data for Product {i+1}: {product['product_name']}")
            
            result = await self.make_request("GET", f"/api/v1/products/{product['id']}/ipfs-data")
            
            if result['success']:
                ipfs_data = result['data']
                print(f"✅ IPFS Data Retrieved")
                print(f"   IPFS Hash: {ipfs_data.get('ipfs_hash', 'N/A')}")
                print(f"   IPFS URL: {ipfs_data.get('ipfs_url', 'N/A')}")
                print(f"   Product Data Available: {'Yes' if ipfs_data.get('product_data') else 'No'}")
                print(f"   Metadata Available: {'Yes' if ipfs_data.get('metadata') else 'No'}")
            else:
                print(f"❌ IPFS Data Retrieval Failed: {result['data']}")

    async def test_duplicate_detection(self):
        """Test duplicate detection scenarios"""
        print("\n🔄 Testing Duplicate Detection...")
        
        if len(self.test_products) < 2:
            print("❌ Need at least 2 products for duplicate testing")
            return
        
        # Try to create a product with duplicate batch number
        duplicate_product = {
            "product_name": "Duplicate Test Product",
            "product_description": "Product with duplicate batch number",
            "manufacturing_date": "2024-01-04T00:00:00Z",
            "batch_number": self.test_products[0]['batch_number'],  # Same batch number
            "category": "electronics"
        }
        
        result = await self.make_request("POST", "/api/v1/products/", duplicate_product)
        
        if result['success']:
            print("⚠️ Duplicate product created (this might be expected behavior)")
        else:
            print("✅ Duplicate detection working - prevented duplicate batch number")

    async def test_verification_history(self):
        """Test verification history and analytics"""
        print("\n📊 Testing Verification History...")
        
        # Get all verifications
        result = await self.make_request("GET", "/api/v1/verifications/")
        
        if result['success']:
            verifications = result['data']
            print(f"✅ Retrieved {len(verifications)} verifications")
            
            # Analyze verification patterns
            authentic_count = sum(1 for v in verifications if v.get('is_authentic', False))
            counterfeit_count = len(verifications) - authentic_count
            
            print(f"   Authentic Verifications: {authentic_count}")
            print(f"   Counterfeit Detections: {counterfeit_count}")
            
            if verifications:
                latest = verifications[0]
                print(f"   Latest Verification: {latest.get('verification_date', 'N/A')}")
                print(f"   Latest Location: {latest.get('location', 'N/A')}")
        else:
            print(f"❌ Failed to retrieve verification history: {result['data']}")

    async def test_analytics(self):
        """Test analytics endpoints"""
        print("\n📈 Testing Analytics...")
        
        # Test overview analytics
        result = await self.make_request("GET", "/api/v1/analytics/overview")
        
        if result['success']:
            overview = result['data']
            print(f"✅ Analytics Overview:")
            print(f"   Total Products: {overview.get('totalProducts', 'N/A')}")
            print(f"   Total Users: {overview.get('totalUsers', 'N/A')}")
            print(f"   Total Verifications: {overview.get('totalVerifications', 'N/A')}")
            print(f"   Counterfeit Alerts: {overview.get('counterfeitAlerts', 'N/A')}")
        else:
            print(f"❌ Analytics Overview Failed: {result['data']}")

    async def test_blockchain_status(self):
        """Test blockchain connectivity"""
        print("\n⛓️ Testing Blockchain Status...")
        
        result = await self.make_request("GET", "/api/v1/blockchain/status")
        
        if result['success']:
            status = result['data']
            print(f"✅ Blockchain Status:")
            print(f"   Connected: {status.get('connected', 'N/A')}")
            print(f"   Network: {status.get('network', 'N/A')}")
            print(f"   Chain ID: {status.get('chain_id', 'N/A')}")
        else:
            print(f"❌ Blockchain Status Failed: {result['data']}")

    async def run_all_tests(self):
        """Run all verification tests"""
        print("🚀 Starting Comprehensive Verification System Tests")
        print("=" * 60)
        
        try:
            # Test IPFS status first
            await self.test_ipfs_status()
            
            # Create test products
            await self.create_test_products()
            
            # Test various verification methods
            await self.test_qr_verification()
            await self.test_direct_verification()
            await self.test_counterfeit_analysis()
            
            # Test IPFS data retrieval
            await self.test_ipfs_data_retrieval()
            
            # Test duplicate detection
            await self.test_duplicate_detection()
            
            # Test verification history
            await self.test_verification_history()
            
            # Test analytics
            await self.test_analytics()
            
            # Test blockchain status
            await self.test_blockchain_status()
            
            print("\n" + "=" * 60)
            print("✅ All tests completed!")
            
        except Exception as e:
            print(f"\n❌ Test execution failed: {str(e)}")

async def main():
    """Main test execution"""
    async with VerificationTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    print("🔍 Verification System Test Suite")
    print("Make sure your FastAPI server is running on http://localhost:8000")
    print("Press Ctrl+C to cancel...")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Tests cancelled by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
