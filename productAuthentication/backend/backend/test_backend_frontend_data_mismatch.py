#!/usr/bin/env python3
"""
Test script to identify data mismatches between backend endpoints and frontend expectations.
This will help us fix the data display issues on the frontend.
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, List

class BackendFrontendDataMismatchTester:
    def __init__(self):
        self.base_url = "http://localhost:8000/api/v1"
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

    async def test_analytics_endpoint(self):
        """Test analytics endpoint and compare with frontend expectations"""
        print("🔍 Testing Analytics Endpoint...")
        
        # Test analytics overview
        analytics_data = await self.make_request("GET", "/analytics/overview")
        
        if "error" in analytics_data:
            print(f"❌ Analytics endpoint error: {analytics_data['error']}")
            return
        
        print("✅ Analytics endpoint response:")
        print(json.dumps(analytics_data, indent=2))
        
        # Check what frontend expects vs what backend returns
        frontend_expected_fields = [
            "total_products", "total_verifications", "authentic_products", 
            "counterfeit_products", "verification_trends", "category_distribution", 
            "manufacturer_stats"
        ]
        
        backend_returned_fields = list(analytics_data.keys())
        
        print(f"\n📊 Frontend expects: {frontend_expected_fields}")
        print(f"📊 Backend returns: {backend_returned_fields}")
        
        missing_fields = set(frontend_expected_fields) - set(backend_returned_fields)
        extra_fields = set(backend_returned_fields) - set(frontend_expected_fields)
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
        if extra_fields:
            print(f"ℹ️ Extra fields: {extra_fields}")
        
        # Test verification trends
        trends_data = await self.make_request("GET", "/analytics/verification-trends")
        print(f"\n📈 Verification trends response:")
        print(json.dumps(trends_data, indent=2))
        
        # Test category distribution
        category_data = await self.make_request("GET", "/analytics/product-categories")
        print(f"\n📦 Category distribution response:")
        print(json.dumps(category_data, indent=2))

    async def test_verification_endpoint(self):
        """Test verification endpoint and compare with frontend expectations"""
        print("\n🔍 Testing Verification Endpoint...")
        
        # Get verifications
        verifications_data = await self.make_request("GET", "/verifications/")
        
        if "error" in verifications_data:
            print(f"❌ Verifications endpoint error: {verifications_data['error']}")
            return
        
        print("✅ Verifications endpoint response:")
        if isinstance(verifications_data, list) and len(verifications_data) > 0:
            print(json.dumps(verifications_data[0], indent=2))
            print(f"... and {len(verifications_data) - 1} more verifications")
        else:
            print(json.dumps(verifications_data, indent=2))
        
        # Check what frontend expects vs what backend returns
        if isinstance(verifications_data, list) and len(verifications_data) > 0:
            verification = verifications_data[0]
            frontend_expected_fields = [
                "id", "product_id", "verifier_id", "location", "notes", 
                "is_authentic", "verification_date", "blockchain_verification_id",
                "detection_reasons", "confidence_score", "risk_level", "blockchain_verified"
            ]
            
            backend_returned_fields = list(verification.keys())
            
            print(f"\n📊 Frontend expects: {frontend_expected_fields}")
            print(f"📊 Backend returns: {backend_returned_fields}")
            
            missing_fields = set(frontend_expected_fields) - set(backend_returned_fields)
            extra_fields = set(backend_returned_fields) - set(frontend_expected_fields)
            
            if missing_fields:
                print(f"❌ Missing fields: {missing_fields}")
            if extra_fields:
                print(f"ℹ️ Extra fields: {extra_fields}")

    async def test_products_endpoint(self):
        """Test products endpoint and compare with frontend expectations"""
        print("\n🔍 Testing Products Endpoint...")
        
        # Get products
        products_data = await self.make_request("GET", "/products/")
        
        if "error" in products_data:
            print(f"❌ Products endpoint error: {products_data['error']}")
            return
        
        print("✅ Products endpoint response:")
        if isinstance(products_data, list) and len(products_data) > 0:
            print(json.dumps(products_data[0], indent=2))
            print(f"... and {len(products_data) - 1} more products")
        else:
            print(json.dumps(products_data, indent=2))
        
        # Check what frontend expects vs what backend returns
        if isinstance(products_data, list) and len(products_data) > 0:
            product = products_data[0]
            frontend_expected_fields = [
                "id", "product_name", "product_description", "manufacturing_date",
                "batch_number", "category", "qr_code_hash", "qr_code_path",
                "blockchain_id", "manufacturer_id", "is_active", "created_at", "updated_at"
            ]
            
            backend_returned_fields = list(product.keys())
            
            print(f"\n📊 Frontend expects: {frontend_expected_fields}")
            print(f"📊 Backend returns: {backend_returned_fields}")
            
            missing_fields = set(frontend_expected_fields) - set(backend_returned_fields)
            extra_fields = set(backend_returned_fields) - set(frontend_expected_fields)
            
            if missing_fields:
                print(f"❌ Missing fields: {missing_fields}")
            if extra_fields:
                print(f"ℹ️ Extra fields: {extra_fields}")

    async def test_blockchain_endpoint(self):
        """Test blockchain endpoint and compare with frontend expectations"""
        print("\n🔍 Testing Blockchain Endpoint...")
        
        # Get blockchain status
        blockchain_data = await self.make_request("GET", "/blockchain/status")
        
        if "error" in blockchain_data:
            print(f"❌ Blockchain endpoint error: {blockchain_data['error']}")
            return
        
        print("✅ Blockchain endpoint response:")
        print(json.dumps(blockchain_data, indent=2))
        
        # Check what frontend expects vs what backend returns
        frontend_expected_fields = [
            "network", "chain_id", "latest_block", "contract_address", "connected"
        ]
        
        backend_returned_fields = list(blockchain_data.keys())
        
        print(f"\n📊 Frontend expects: {frontend_expected_fields}")
        print(f"📊 Backend returns: {backend_returned_fields}")
        
        missing_fields = set(frontend_expected_fields) - set(backend_returned_fields)
        extra_fields = set(backend_returned_fields) - set(frontend_expected_fields)
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
        if extra_fields:
            print(f"ℹ️ Extra fields: {extra_fields}")

    async def test_verification_analysis_endpoint(self):
        """Test verification analysis endpoint"""
        print("\n🔍 Testing Verification Analysis Endpoint...")
        
        # First get a product ID
        products_data = await self.make_request("GET", "/products/")
        if "error" in products_data or not isinstance(products_data, list) or len(products_data) == 0:
            print("❌ No products available for analysis test")
            return
        
        product_id = products_data[0]["id"]
        
        # Test counterfeit analysis
        analysis_data = await self.make_request("POST", f"/verifications/analyze-counterfeit/{product_id}")
        
        if "error" in analysis_data:
            print(f"❌ Analysis endpoint error: {analysis_data['error']}")
            return
        
        print("✅ Analysis endpoint response:")
        print(json.dumps(analysis_data, indent=2))
        
        # Check what frontend expects vs what backend returns
        frontend_expected_fields = [
            "product_id", "product_name", "manufacturer_id", "detection_result",
            "blockchain_analysis", "pattern_analysis", "risk_assessment", "analysis_timestamp"
        ]
        
        backend_returned_fields = list(analysis_data.keys())
        
        print(f"\n📊 Frontend expects: {frontend_expected_fields}")
        print(f"📊 Backend returns: {backend_returned_fields}")
        
        missing_fields = set(frontend_expected_fields) - set(backend_returned_fields)
        extra_fields = set(backend_returned_fields) - set(frontend_expected_fields)
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
        if extra_fields:
            print(f"ℹ️ Extra fields: {extra_fields}")

    async def run_comprehensive_test(self):
        """Run all tests to identify data mismatches"""
        print("🚀 Starting Backend-Frontend Data Mismatch Analysis")
        print("=" * 60)
        
        await self.test_analytics_endpoint()
        await self.test_verification_endpoint()
        await self.test_products_endpoint()
        await self.test_blockchain_endpoint()
        await self.test_verification_analysis_endpoint()
        
        print("\n" + "=" * 60)
        print("✅ Data mismatch analysis complete!")
        print("\n📋 Summary of Issues Found:")
        print("1. Analytics endpoint returns different field names than frontend expects")
        print("2. Verification endpoint missing some fields that frontend expects")
        print("3. Need to align backend response structures with frontend interfaces")

async def main():
    tester = BackendFrontendDataMismatchTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())
