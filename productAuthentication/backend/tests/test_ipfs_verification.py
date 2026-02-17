#!/usr/bin/env python3
"""
IPFS-Specific Verification Tests
Tests IPFS integration with product verification
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzQHMuY29tIiwiZXhwIjoxNzU2ODM4NzQ5fQ.GvLkcrPEyTfekcM86gsjVnsgi648C_OQQp2fyNWoiMI"

class IPFSTester:
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

    async def test_ipfs_service_status(self):
        """Test IPFS service status and connectivity"""
        print("\n🌐 Testing IPFS Service Status")
        print("-" * 40)
        
        # Test IPFS data retrieval for a product
        result = await self.make_request("GET", "/api/v1/products/")
        
        if not result['success'] or not result['data']:
            print("❌ No products found. Creating a test product...")
            await self.create_test_product()
            return
        
        product = result['data'][0]
        print(f"📦 Testing IPFS with product: {product['product_name']}")
        
        if product.get('ipfs_hash'):
            print(f"✅ Product has IPFS hash: {product['ipfs_hash']}")
            await self.test_ipfs_data_retrieval(product)
        else:
            print("⚠️ Product has no IPFS hash. Creating new product with IPFS...")
            await self.create_test_product()

    async def create_test_product(self):
        """Create a test product with IPFS storage"""
        print("\n📦 Creating Test Product with IPFS Storage")
        print("-" * 40)
        
        product_data = {
            "product_name": "IPFS Verification Test Product",
            "product_description": "A product specifically created for testing IPFS verification",
            "manufacturing_date": "2024-01-15T10:00:00Z",
            "batch_number": "IPFS-VERIFY-001",
            "category": "electronics"
        }
        
        result = await self.make_request("POST", "/api/v1/products/", product_data)
        
        if result['success']:
            product = result['data']
            print(f"✅ Product created successfully:")
            print(f"   ID: {product['id']}")
            print(f"   Name: {product['product_name']}")
            print(f"   IPFS Hash: {product.get('ipfs_hash', 'N/A')}")
            print(f"   IPFS URL: {product.get('ipfs_url', 'N/A')}")
            print(f"   Blockchain ID: {product.get('blockchain_id', 'N/A')}")
            
            if product.get('ipfs_hash'):
                await self.test_ipfs_data_retrieval(product)
            else:
                print("⚠️ Product created but no IPFS hash generated")
        else:
            print(f"❌ Failed to create product: {result['data']}")

    async def test_ipfs_data_retrieval(self, product):
        """Test IPFS data retrieval"""
        print(f"\n🔍 Testing IPFS Data Retrieval for Product {product['id']}")
        print("-" * 40)
        
        result = await self.make_request("GET", f"/api/v1/products/{product['id']}/ipfs-data")
        
        if result['success']:
            ipfs_data = result['data']
            print(f"✅ IPFS Data Retrieved Successfully:")
            print(f"   IPFS Hash: {ipfs_data.get('ipfs_hash', 'N/A')}")
            print(f"   IPFS URL: {ipfs_data.get('ipfs_url', 'N/A')}")
            print(f"   Retrieved At: {ipfs_data.get('retrieved_at', 'N/A')}")
            
            if ipfs_data.get('product_data'):
                product_data = ipfs_data['product_data']
                print(f"   Product Data:")
                print(f"     Name: {product_data.get('product_name', 'N/A')}")
                print(f"     Description: {product_data.get('product_description', 'N/A')}")
                print(f"     Batch Number: {product_data.get('batch_number', 'N/A')}")
                print(f"     Category: {product_data.get('category', 'N/A')}")
                print(f"     Manufacturing Date: {product_data.get('manufacturing_date', 'N/A')}")
            
            if ipfs_data.get('metadata'):
                metadata = ipfs_data['metadata']
                print(f"   Metadata:")
                print(f"     Version: {metadata.get('version', 'N/A')}")
                print(f"     Type: {metadata.get('type', 'N/A')}")
                print(f"     Timestamp: {metadata.get('timestamp', 'N/A')}")
            
            # Test public IPFS URL access
            if ipfs_data.get('ipfs_url'):
                await self.test_public_ipfs_access(ipfs_data['ipfs_url'])
        else:
            print(f"❌ IPFS data retrieval failed: {result['data']}")

    async def test_public_ipfs_access(self, ipfs_url):
        """Test public IPFS URL access"""
        print(f"\n🌍 Testing Public IPFS URL Access")
        print("-" * 40)
        print(f"   IPFS URL: {ipfs_url}")
        
        try:
            async with self.session.get(ipfs_url) as response:
                if response.status == 200:
                    data = await response.text()
                    print(f"✅ Public IPFS access successful")
                    print(f"   Response length: {len(data)} characters")
                    print(f"   First 100 chars: {data[:100]}...")
                else:
                    print(f"⚠️ Public IPFS access returned status: {response.status}")
        except Exception as e:
            print(f"⚠️ Public IPFS access failed: {str(e)}")
            print("   This is normal if using mock IPFS service")

    async def test_ipfs_verification_integration(self):
        """Test IPFS integration with verification"""
        print("\n🔍 Testing IPFS Integration with Verification")
        print("-" * 40)
        
        # Get a product with IPFS data
        result = await self.make_request("GET", "/api/v1/products/")
        
        if not result['success'] or not result['data']:
            print("❌ No products found")
            return
        
        # Find a product with IPFS hash
        product_with_ipfs = None
        for product in result['data']:
            if product.get('ipfs_hash'):
                product_with_ipfs = product
                break
        
        if not product_with_ipfs:
            print("❌ No products with IPFS data found")
            return
        
        print(f"📦 Testing verification with IPFS-enabled product:")
        print(f"   Name: {product_with_ipfs['product_name']}")
        print(f"   IPFS Hash: {product_with_ipfs['ipfs_hash']}")
        
        # Test verification
        verification_data = {
            "qr_data": product_with_ipfs['qr_code_hash'],
            "location": "IPFS Verification Test",
            "notes": "Testing IPFS integration with verification"
        }
        
        result = await self.make_request("POST", "/api/v1/products/verify-product", verification_data)
        
        if result['success']:
            verification = result['data']
            print(f"✅ Verification with IPFS integration:")
            print(f"   Is Authentic: {verification.get('is_authentic', 'N/A')}")
            print(f"   Confidence Score: {verification.get('confidence_score', 'N/A')}")
            print(f"   Risk Level: {verification.get('risk_level', 'N/A')}")
            
            # Check if IPFS validation was included
            reasons = verification.get('detection_reasons', [])
            ipfs_reasons = [r for r in reasons if 'ipfs' in r.lower()]
            
            if ipfs_reasons:
                print(f"   IPFS Validation Reasons:")
                for reason in ipfs_reasons:
                    print(f"     - {reason}")
            else:
                print(f"   ⚠️ No IPFS-specific validation reasons found")
        else:
            print(f"❌ Verification failed: {result['data']}")

    async def test_ipfs_vs_swarm_comparison(self):
        """Test comparison between IPFS and Swarm data"""
        print("\n🔄 Testing IPFS vs Swarm Data Comparison")
        print("-" * 40)
        
        # Get a product
        result = await self.make_request("GET", "/api/v1/products/")
        
        if not result['success'] or not result['data']:
            print("❌ No products found")
            return
        
        product = result['data'][0]
        print(f"📦 Comparing storage for product: {product['product_name']}")
        
        # Test IPFS data
        if product.get('ipfs_hash'):
            print(f"✅ IPFS Hash: {product['ipfs_hash']}")
            ipfs_result = await self.make_request("GET", f"/api/v1/products/{product['id']}/ipfs-data")
            if ipfs_result['success']:
                print(f"   IPFS Data: Available")
            else:
                print(f"   IPFS Data: Failed to retrieve")
        else:
            print(f"⚠️ No IPFS hash found")
        
        # Test Swarm data (legacy)
        if product.get('swarm_hash'):
            print(f"✅ Swarm Hash: {product['swarm_hash']}")
            swarm_result = await self.make_request("GET", f"/api/v1/products/{product['id']}/swarm-data")
            if swarm_result['success']:
                print(f"   Swarm Data: Available")
            else:
                print(f"   Swarm Data: Failed to retrieve")
        else:
            print(f"⚠️ No Swarm hash found")

    async def run_all_ipfs_tests(self):
        """Run all IPFS-specific tests"""
        print("🚀 Starting IPFS-Specific Verification Tests")
        print("=" * 60)
        
        try:
            await self.test_ipfs_service_status()
            await self.test_ipfs_verification_integration()
            await self.test_ipfs_vs_swarm_comparison()
            
            print("\n" + "=" * 60)
            print("✅ All IPFS tests completed!")
            
        except Exception as e:
            print(f"\n❌ IPFS test execution failed: {str(e)}")

async def main():
    """Main IPFS test execution"""
    async with IPFSTester() as tester:
        await tester.run_all_ipfs_tests()

if __name__ == "__main__":
    print("🌐 IPFS-Specific Verification Test Suite")
    print("Make sure your FastAPI server is running on http://localhost:8000")
    print("Press Ctrl+C to cancel...")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Tests cancelled by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
