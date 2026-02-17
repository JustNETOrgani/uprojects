#!/usr/bin/env python3
"""
Complete Verification Workflow Demo
Demonstrates the full verification system with IPFS integration
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzQHMuY29tIiwiZXhwIjoxNzU2ODM4NzQ5fQ.GvLkcrPEyTfekcM86gsjVnsgi648C_OQQp2fyNWoiMI"

class VerificationDemo:
    def __init__(self):
        self.session = None
        self.headers = {
            "Authorization": f"Bearer {BEARER_TOKEN}",
            "Content-Type": "application/json"
        }
        self.demo_products = []

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

    async def demo_step_1_create_products(self):
        """Step 1: Create demo products with IPFS storage"""
        print("\n" + "="*60)
        print("📦 STEP 1: Creating Demo Products with IPFS Storage")
        print("="*60)
        
        demo_products = [
            {
                "product_name": "Authentic Luxury Watch",
                "product_description": "Premium Swiss-made luxury watch with IPFS verification",
                "manufacturing_date": "2024-01-15T08:00:00Z",
                "batch_number": "LUX-WATCH-2024-001",
                "category": "luxury_goods"
            },
            {
                "product_name": "Genuine Medicine Bottle",
                "product_description": "FDA-approved pharmaceutical product with blockchain verification",
                "manufacturing_date": "2024-01-20T10:30:00Z",
                "batch_number": "MED-PHARMA-2024-002",
                "category": "pharmaceuticals"
            },
            {
                "product_name": "Premium Electronics Device",
                "product_description": "High-end electronic device with comprehensive verification",
                "manufacturing_date": "2024-01-25T14:15:00Z",
                "batch_number": "ELEC-PREMIUM-2024-003",
                "category": "electronics"
            }
        ]
        
        for i, product_data in enumerate(demo_products, 1):
            print(f"\n🔧 Creating Product {i}: {product_data['product_name']}")
            
            result = await self.make_request("POST", "/api/v1/products/", product_data)
            
            if result['success']:
                product = result['data']
                self.demo_products.append(product)
                print(f"✅ Product {i} Created Successfully:")
                print(f"   📋 ID: {product['id']}")
                print(f"   🏷️  Name: {product['product_name']}")
                print(f"   📦 Batch: {product['batch_number']}")
                print(f"   🌐 IPFS Hash: {product.get('ipfs_hash', 'N/A')}")
                print(f"   🔗 IPFS URL: {product.get('ipfs_url', 'N/A')}")
                print(f"   ⛓️  Blockchain ID: {product.get('blockchain_id', 'N/A')}")
                print(f"   📱 QR Hash: {product['qr_code_hash'][:20]}...")
            else:
                print(f"❌ Failed to create Product {i}: {result['data']}")

    async def demo_step_2_verify_authentic_products(self):
        """Step 2: Verify authentic products"""
        print("\n" + "="*60)
        print("✅ STEP 2: Verifying Authentic Products")
        print("="*60)
        
        for i, product in enumerate(self.demo_products, 1):
            print(f"\n🔍 Verifying Product {i}: {product['product_name']}")
            
            verification_data = {
                "qr_data": product['qr_code_hash'],
                "location": f"Demo Warehouse {i}",
                "notes": f"Authentic product verification demo for {product['product_name']}"
            }
            
            result = await self.make_request("POST", "/api/v1/products/verify-product", verification_data)
            
            if result['success']:
                verification = result['data']
                print(f"✅ Verification Result:")
                print(f"   🎯 Is Authentic: {verification.get('is_authentic', 'N/A')}")
                print(f"   📊 Confidence Score: {verification.get('confidence_score', 'N/A')}")
                print(f"   ⚠️  Risk Level: {verification.get('risk_level', 'N/A')}")
                print(f"   📝 Detection Reasons: {len(verification.get('detection_reasons', []))} reasons")
                
                # Show key detection reasons
                reasons = verification.get('detection_reasons', [])
                for j, reason in enumerate(reasons[:3], 1):
                    print(f"     {j}. {reason}")
                if len(reasons) > 3:
                    print(f"     ... and {len(reasons) - 3} more reasons")
            else:
                print(f"❌ Verification failed: {result['data']}")

    async def demo_step_3_test_counterfeit_scenarios(self):
        """Step 3: Test counterfeit detection scenarios"""
        print("\n" + "="*60)
        print("🚨 STEP 3: Testing Counterfeit Detection Scenarios")
        print("="*60)
        
        # Scenario 1: Fake QR Code
        print(f"\n🔍 Scenario 1: Fake QR Code Detection")
        fake_qr_data = {
            "qr_data": "fake_qr_hash_1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "location": "Suspicious Location",
            "notes": "Testing fake QR code detection"
        }
        
        result = await self.make_request("POST", "/api/v1/products/verify-product", fake_qr_data)
        
        if result['success']:
            verification = result['data']
            print(f"✅ Fake QR Detection Result:")
            print(f"   🎯 Is Authentic: {verification.get('is_authentic', 'N/A')}")
            print(f"   📊 Confidence Score: {verification.get('confidence_score', 'N/A')}")
            print(f"   ⚠️  Risk Level: {verification.get('risk_level', 'N/A')}")
            print(f"   🚨 Detection Reasons:")
            reasons = verification.get('detection_reasons', [])
            for i, reason in enumerate(reasons, 1):
                print(f"     {i}. {reason}")
        
        # Scenario 2: Invalid QR Format
        print(f"\n🔍 Scenario 2: Invalid QR Format Detection")
        invalid_qr_data = {
            "qr_data": "short_invalid_hash",
            "location": "Test Location",
            "notes": "Testing invalid QR format detection"
        }
        
        result = await self.make_request("POST", "/api/v1/products/verify-product", invalid_qr_data)
        
        if result['success']:
            verification = result['data']
            print(f"✅ Invalid Format Detection Result:")
            print(f"   🎯 Is Authentic: {verification.get('is_authentic', 'N/A')}")
            print(f"   📊 Confidence Score: {verification.get('confidence_score', 'N/A')}")
            print(f"   ⚠️  Risk Level: {verification.get('risk_level', 'N/A')}")

    async def demo_step_4_ipfs_data_verification(self):
        """Step 4: Demonstrate IPFS data verification"""
        print("\n" + "="*60)
        print("🌐 STEP 4: IPFS Data Verification Demo")
        print("="*60)
        
        for i, product in enumerate(self.demo_products, 1):
            if not product.get('ipfs_hash'):
                continue
                
            print(f"\n🔍 IPFS Verification for Product {i}: {product['product_name']}")
            
            # Retrieve IPFS data
            result = await self.make_request("GET", f"/api/v1/products/{product['id']}/ipfs-data")
            
            if result['success']:
                ipfs_data = result['data']
                print(f"✅ IPFS Data Retrieved:")
                print(f"   🌐 IPFS Hash: {ipfs_data.get('ipfs_hash', 'N/A')}")
                print(f"   🔗 IPFS URL: {ipfs_data.get('ipfs_url', 'N/A')}")
                print(f"   ⏰ Retrieved At: {ipfs_data.get('retrieved_at', 'N/A')}")
                
                if ipfs_data.get('product_data'):
                    product_data = ipfs_data['product_data']
                    print(f"   📦 Product Data in IPFS:")
                    print(f"     Name: {product_data.get('product_name', 'N/A')}")
                    print(f"     Batch: {product_data.get('batch_number', 'N/A')}")
                    print(f"     Category: {product_data.get('category', 'N/A')}")
                    print(f"     Manufacturing Date: {product_data.get('manufacturing_date', 'N/A')}")
                
                if ipfs_data.get('metadata'):
                    metadata = ipfs_data['metadata']
                    print(f"   📋 Metadata:")
                    print(f"     Version: {metadata.get('version', 'N/A')}")
                    print(f"     Type: {metadata.get('type', 'N/A')}")
                    print(f"     Timestamp: {metadata.get('timestamp', 'N/A')}")
            else:
                print(f"❌ IPFS data retrieval failed: {result['data']}")

    async def demo_step_5_analytics_dashboard(self):
        """Step 5: Show analytics and verification history"""
        print("\n" + "="*60)
        print("📊 STEP 5: Analytics and Verification Dashboard")
        print("="*60)
        
        # Get analytics overview
        result = await self.make_request("GET", "/api/v1/analytics/overview")
        
        if result['success']:
            overview = result['data']
            print(f"✅ System Analytics Overview:")
            print(f"   📦 Total Products: {overview.get('totalProducts', 'N/A')}")
            print(f"   👥 Total Users: {overview.get('totalUsers', 'N/A')}")
            print(f"   🔍 Total Verifications: {overview.get('totalVerifications', 'N/A')}")
            print(f"   🚨 Counterfeit Alerts: {overview.get('counterfeitAlerts', 'N/A')}")
            print(f"   ⛓️  Blockchain Transactions: {overview.get('blockchainTransactions', 'N/A')}")
        
        # Get verification history
        result = await self.make_request("GET", "/api/v1/verifications/")
        
        if result['success']:
            verifications = result['data']
            print(f"\n✅ Verification History:")
            print(f"   📊 Total Verifications: {len(verifications)}")
            
            if verifications:
                authentic_count = sum(1 for v in verifications if v.get('is_authentic', False))
                counterfeit_count = len(verifications) - authentic_count
                
                print(f"   ✅ Authentic Verifications: {authentic_count}")
                print(f"   🚨 Counterfeit Detections: {counterfeit_count}")
                
                # Show recent verifications
                print(f"\n📋 Recent Verifications:")
                for i, verification in enumerate(verifications[:3], 1):
                    print(f"   {i}. Date: {verification.get('verification_date', 'N/A')}")
                    print(f"      Location: {verification.get('location', 'N/A')}")
                    print(f"      Authentic: {verification.get('is_authentic', 'N/A')}")
                    print(f"      Confidence: {verification.get('confidence_score', 'N/A')}")

    async def demo_step_6_blockchain_status(self):
        """Step 6: Show blockchain connectivity and status"""
        print("\n" + "="*60)
        print("⛓️  STEP 6: Blockchain Status and Connectivity")
        print("="*60)
        
        # Get blockchain status
        result = await self.make_request("GET", "/api/v1/blockchain/status")
        
        if result['success']:
            status = result['data']
            print(f"✅ Blockchain Status:")
            print(f"   🔗 Connected: {status.get('connected', 'N/A')}")
            print(f"   🌐 Network: {status.get('network', 'N/A')}")
            print(f"   🔢 Chain ID: {status.get('chain_id', 'N/A')}")
            print(f"   📊 Latest Block: {status.get('latest_block', 'N/A')}")
            print(f"   ⛽ Gas Price: {status.get('gas_price', 'N/A')}")
        
        # Get total products on blockchain
        result = await self.make_request("GET", "/api/v1/blockchain/products/count")
        
        if result['success']:
            count_data = result['data']
            print(f"\n✅ Blockchain Products:")
            print(f"   📦 Total Products on Blockchain: {count_data.get('total_products', 'N/A')}")

    async def run_complete_demo(self):
        """Run the complete verification workflow demo"""
        print("🚀 COMPLETE VERIFICATION SYSTEM DEMO")
        print("🎯 Demonstrating IPFS Integration with 7-Layer Counterfeit Detection")
        print("="*80)
        
        try:
            await self.demo_step_1_create_products()
            await self.demo_step_2_verify_authentic_products()
            await self.demo_step_3_test_counterfeit_scenarios()
            await self.demo_step_4_ipfs_data_verification()
            await self.demo_step_5_analytics_dashboard()
            await self.demo_step_6_blockchain_status()
            
            print("\n" + "="*80)
            print("🎉 DEMO COMPLETED SUCCESSFULLY!")
            print("="*80)
            print("✅ Key Features Demonstrated:")
            print("   🌐 IPFS Integration for decentralized storage")
            print("   🔍 7-Layer Counterfeit Detection Algorithm")
            print("   ⛓️  Blockchain Verification and Registration")
            print("   📊 Real-time Analytics and Monitoring")
            print("   🚨 Comprehensive Risk Assessment")
            print("   📱 QR Code Validation and Security")
            print("   🔄 Duplicate Detection and Prevention")
            print("="*80)
            
        except Exception as e:
            print(f"\n❌ Demo execution failed: {str(e)}")

async def main():
    """Main demo execution"""
    async with VerificationDemo() as demo:
        await demo.run_complete_demo()

if __name__ == "__main__":
    print("🎬 Complete Verification System Demo")
    print("Make sure your FastAPI server is running on http://localhost:8000")
    print("Press Ctrl+C to cancel...")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Demo cancelled by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
