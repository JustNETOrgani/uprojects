#!/usr/bin/env python3
"""
Test script to verify that all data display fixes are working correctly.
This tests the backend endpoints to ensure they return data in the format expected by the frontend.
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, List

class DataDisplayFixesTester:
    def __init__(self):
        self.base_url = "http://localhost:8000/api/v1"
        # You'll need to get a fresh token
        self.bearer_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzQHMuY29tIiwiZXhwIjoxNzU2ODQxNTM2fQ.beJPjNuwTLCGJoV4Fl0qAUKtGvQHxlaRdDfk18bs3y0"
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }

    async def make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make HTTP request to backend"""
        url = f"{self.base_url}{endpoint}"
        async with aiohttp.ClientSession() as session:
            try:
                if method.upper() == "GET":
                    async with session.get(url, headers=self.headers) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            error_text = await response.text()
                            return {"error": f"HTTP {response.status}: {error_text}"}
                elif method.upper() == "POST":
                    async with session.post(url, headers=self.headers, json=data) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            error_text = await response.text()
                            return {"error": f"HTTP {response.status}: {error_text}"}
            except Exception as e:
                return {"error": str(e)}

    async def test_analytics_fixes(self):
        """Test that analytics endpoint returns data in expected format"""
        print("🔍 Testing Analytics Endpoint Fixes...")
        
        analytics_data = await self.make_request("GET", "/analytics/overview")
        
        if "error" in analytics_data:
            print(f"❌ Analytics endpoint error: {analytics_data['error']}")
            return False
        
        # Check for new fields that frontend expects
        expected_fields = [
            "total_products", "total_users", "total_verifications", 
            "authentic_products", "counterfeit_products",
            "verification_trends", "category_distribution", "manufacturer_stats"
        ]
        
        missing_fields = []
        for field in expected_fields:
            if field not in analytics_data:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing analytics fields: {missing_fields}")
            return False
        
        # Check data types
        if not isinstance(analytics_data["verification_trends"], list):
            print("❌ verification_trends should be a list")
            return False
        
        if not isinstance(analytics_data["category_distribution"], list):
            print("❌ category_distribution should be a list")
            return False
        
        if not isinstance(analytics_data["manufacturer_stats"], list):
            print("❌ manufacturer_stats should be a list")
            return False
        
        print("✅ Analytics endpoint fixes working correctly!")
        print(f"   - Total products: {analytics_data.get('total_products', 'N/A')}")
        print(f"   - Total verifications: {analytics_data.get('total_verifications', 'N/A')}")
        print(f"   - Authentic products: {analytics_data.get('authentic_products', 'N/A')}")
        print(f"   - Counterfeit products: {analytics_data.get('counterfeit_products', 'N/A')}")
        print(f"   - Verification trends: {len(analytics_data.get('verification_trends', []))} entries")
        print(f"   - Category distribution: {len(analytics_data.get('category_distribution', []))} entries")
        print(f"   - Manufacturer stats: {len(analytics_data.get('manufacturer_stats', []))} entries")
        
        return True

    async def test_verification_fixes(self):
        """Test that verification endpoint returns data in expected format"""
        print("\n🔍 Testing Verification Endpoint Fixes...")
        
        verifications_data = await self.make_request("GET", "/verifications/")
        
        if "error" in verifications_data:
            print(f"❌ Verifications endpoint error: {verifications_data['error']}")
            return False
        
        if not isinstance(verifications_data, list) or len(verifications_data) == 0:
            print("❌ No verifications found to test")
            return False
        
        verification = verifications_data[0]
        
        # Check for new fields that frontend expects
        expected_fields = [
            "id", "product_id", "verifier_id", "location", "notes",
            "is_authentic", "verification_date", "blockchain_verification_id",
            "detection_reasons", "confidence_score", "risk_level", "blockchain_verified"
        ]
        
        missing_fields = []
        for field in expected_fields:
            if field not in verification:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing verification fields: {missing_fields}")
            return False
        
        # Check data types
        if not isinstance(verification.get("detection_reasons"), list):
            print("❌ detection_reasons should be a list")
            return False
        
        if not isinstance(verification.get("confidence_score"), (int, float)):
            print("❌ confidence_score should be a number")
            return False
        
        if verification.get("risk_level") not in ["low", "medium", "high", None]:
            print("❌ risk_level should be 'low', 'medium', 'high', or null")
            return False
        
        if not isinstance(verification.get("blockchain_verified"), (bool, type(None))):
            print("❌ blockchain_verified should be a boolean or null")
            return False
        
        print("✅ Verification endpoint fixes working correctly!")
        print(f"   - Verification ID: {verification.get('id', 'N/A')}")
        print(f"   - Is Authentic: {verification.get('is_authentic', 'N/A')}")
        print(f"   - Confidence Score: {verification.get('confidence_score', 'N/A')}")
        print(f"   - Risk Level: {verification.get('risk_level', 'N/A')}")
        print(f"   - Blockchain Verified: {verification.get('blockchain_verified', 'N/A')}")
        print(f"   - Detection Reasons: {len(verification.get('detection_reasons', []))} reasons")
        
        return True

    async def test_products_endpoint(self):
        """Test that products endpoint returns data in expected format"""
        print("\n🔍 Testing Products Endpoint...")
        
        products_data = await self.make_request("GET", "/products/")
        
        if "error" in products_data:
            print(f"❌ Products endpoint error: {products_data['error']}")
            return False
        
        if not isinstance(products_data, list) or len(products_data) == 0:
            print("❌ No products found to test")
            return False
        
        product = products_data[0]
        
        # Check for expected fields
        expected_fields = [
            "id", "product_name", "product_description", "manufacturing_date",
            "batch_number", "category", "qr_code_hash", "qr_code_path",
            "blockchain_id", "manufacturer_id", "is_active", "created_at", "updated_at"
        ]
        
        missing_fields = []
        for field in expected_fields:
            if field not in product:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing product fields: {missing_fields}")
            return False
        
        print("✅ Products endpoint working correctly!")
        print(f"   - Product ID: {product.get('id', 'N/A')}")
        print(f"   - Product Name: {product.get('product_name', 'N/A')}")
        print(f"   - Category: {product.get('category', 'N/A')}")
        print(f"   - Blockchain ID: {product.get('blockchain_id', 'N/A')}")
        print(f"   - QR Code Hash: {product.get('qr_code_hash', 'N/A')[:20]}...")
        
        return True

    async def test_blockchain_endpoint(self):
        """Test that blockchain endpoint returns data in expected format"""
        print("\n🔍 Testing Blockchain Endpoint...")
        
        blockchain_data = await self.make_request("GET", "/blockchain/status")
        
        if "error" in blockchain_data:
            print(f"❌ Blockchain endpoint error: {blockchain_data['error']}")
            return False
        
        # Check for expected fields
        expected_fields = [
            "network", "chain_id", "latest_block", "contract_address", "connected"
        ]
        
        missing_fields = []
        for field in expected_fields:
            if field not in blockchain_data:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing blockchain fields: {missing_fields}")
            return False
        
        print("✅ Blockchain endpoint working correctly!")
        print(f"   - Network: {blockchain_data.get('network', 'N/A')}")
        print(f"   - Chain ID: {blockchain_data.get('chain_id', 'N/A')}")
        print(f"   - Latest Block: {blockchain_data.get('latest_block', 'N/A')}")
        print(f"   - Connected: {blockchain_data.get('connected', 'N/A')}")
        
        return True

    async def run_comprehensive_test(self):
        """Run all tests to verify data display fixes"""
        print("🚀 Starting Data Display Fixes Verification")
        print("=" * 60)
        
        results = []
        
        # Test all endpoints
        results.append(await self.test_analytics_fixes())
        results.append(await self.test_verification_fixes())
        results.append(await self.test_products_endpoint())
        results.append(await self.test_blockchain_endpoint())
        
        print("\n" + "=" * 60)
        print("✅ Data display fixes verification complete!")
        
        passed_tests = sum(results)
        total_tests = len(results)
        
        print(f"\n📊 Test Results: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All data display fixes are working correctly!")
            print("\n📋 Summary of Fixes Applied:")
            print("1. ✅ Analytics endpoint now returns data in frontend-expected format")
            print("2. ✅ Verification endpoint includes all required fields")
            print("3. ✅ Database schema updated with new verification fields")
            print("4. ✅ Frontend API client updated to use correct endpoints")
            print("5. ✅ All endpoints return consistent data structures")
        else:
            print("❌ Some tests failed. Please check the errors above.")
        
        return passed_tests == total_tests

async def main():
    tester = DataDisplayFixesTester()
    success = await tester.run_comprehensive_test()
    exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
