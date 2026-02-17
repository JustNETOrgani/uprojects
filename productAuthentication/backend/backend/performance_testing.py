#!/usr/bin/env python3
"""
Performance Testing Script for Anti-Counterfeit System
Tests the key performance metrics mentioned in Chapter 4:
- Average Verification Latency (target: <3 seconds)
- IPFS Data Retrieval (target: <2 seconds)
- Blockchain Verification (target: <1 second)
- QR Code Processing (target: <0.5 seconds)
"""

import asyncio
import time
import statistics
import requests
import json
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.ipfs_service import IPFSService
from app.services.qr_service import QRService
from app.services.counterfeit_detection_service import CounterfeitDetectionService
from app.services.blockchain_service import BlockchainService

class PerformanceTester:
    def __init__(self, base_url: str = "http://localhost:8000", bearer_token: str = None):
        self.base_url = base_url
        self.bearer_token = bearer_token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer_token}" if bearer_token else None
        }
        
        # Initialize services
        self.ipfs_service = IPFSService()
        self.qr_service = QRService()
        self.counterfeit_service = CounterfeitDetectionService()
        self.blockchain_service = BlockchainService()
        
        # Performance results
        self.results = {
            "verification_latency": [],
            "ipfs_retrieval": [],
            "blockchain_verification": [],
            "qr_processing": [],
            "concurrent_verifications": [],
            "error_rates": {}
        }

    def measure_time(self, func, *args, **kwargs):
        """Measure execution time of a function"""
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            return result, end_time - start_time, None
        except Exception as e:
            end_time = time.time()
            return None, end_time - start_time, str(e)

    def test_qr_processing_performance(self, iterations: int = 10) -> Dict:
        """Test QR code processing performance"""
        print("🔍 Testing QR Code Processing Performance...")
        
        # Sample QR data for testing
        sample_qr_data = {
            "product_id": 51,
            "product_name": "Test Product",
            "batch_number": "TEST-001",
            "qr_hash": "test_hash_12345",
            "timestamp": "2025-01-01T00:00:00Z"
        }
        
        qr_json = json.dumps(sample_qr_data)
        
        for i in range(iterations):
            print(f"  QR Test {i+1}/{iterations}...", end=" ")
            
            # Test QR code generation
            result, duration, error = self.measure_time(
                self.qr_service.generate_qr_code, 
                qr_json
            )
            
            if error:
                print(f"❌ Error: {error}")
                self.results["error_rates"]["qr_processing"] = self.results["error_rates"].get("qr_processing", 0) + 1
            else:
                print(f"✅ {duration:.3f}s")
                self.results["qr_processing"].append(duration)
        
        return {
            "average": statistics.mean(self.results["qr_processing"]) if self.results["qr_processing"] else 0,
            "min": min(self.results["qr_processing"]) if self.results["qr_processing"] else 0,
            "max": max(self.results["qr_processing"]) if self.results["qr_processing"] else 0,
            "median": statistics.median(self.results["qr_processing"]) if self.results["qr_processing"] else 0,
            "target": 0.5,
            "passed": statistics.mean(self.results["qr_processing"]) < 0.5 if self.results["qr_processing"] else False
        }

    def test_ipfs_retrieval_performance(self, iterations: int = 10) -> Dict:
        """Test IPFS data retrieval performance"""
        print("🌐 Testing IPFS Data Retrieval Performance...")
        
        # Test with a known IPFS hash (if available)
        test_hash = "QmTestHash12345"  # This would be a real hash in production
        
        for i in range(iterations):
            print(f"  IPFS Test {i+1}/{iterations}...", end=" ")
            
            # Test IPFS data retrieval
            result, duration, error = self.measure_time(
                self.ipfs_service.get_data,
                test_hash
            )
            
            if error:
                print(f"❌ Error: {error}")
                self.results["error_rates"]["ipfs_retrieval"] = self.results["error_rates"].get("ipfs_retrieval", 0) + 1
            else:
                print(f"✅ {duration:.3f}s")
                self.results["ipfs_retrieval"].append(duration)
        
        return {
            "average": statistics.mean(self.results["ipfs_retrieval"]) if self.results["ipfs_retrieval"] else 0,
            "min": min(self.results["ipfs_retrieval"]) if self.results["ipfs_retrieval"] else 0,
            "max": max(self.results["ipfs_retrieval"]) if self.results["ipfs_retrieval"] else 0,
            "median": statistics.median(self.results["ipfs_retrieval"]) if self.results["ipfs_retrieval"] else 0,
            "target": 2.0,
            "passed": statistics.mean(self.results["ipfs_retrieval"]) < 2.0 if self.results["ipfs_retrieval"] else False
        }

    def test_blockchain_verification_performance(self, iterations: int = 10) -> Dict:
        """Test blockchain verification performance"""
        print("⛓️ Testing Blockchain Verification Performance...")
        
        # Test with a sample product ID
        test_product_id = 51
        
        for i in range(iterations):
            print(f"  Blockchain Test {i+1}/{iterations}...", end=" ")
            
            # Test blockchain verification
            result, duration, error = self.measure_time(
                self.blockchain_service.verify_product_on_blockchain,
                test_product_id
            )
            
            if error:
                print(f"❌ Error: {error}")
                self.results["error_rates"]["blockchain_verification"] = self.results["error_rates"].get("blockchain_verification", 0) + 1
            else:
                print(f"✅ {duration:.3f}s")
                self.results["blockchain_verification"].append(duration)
        
        return {
            "average": statistics.mean(self.results["blockchain_verification"]) if self.results["blockchain_verification"] else 0,
            "min": min(self.results["blockchain_verification"]) if self.results["blockchain_verification"] else 0,
            "max": max(self.results["blockchain_verification"]) if self.results["blockchain_verification"] else 0,
            "median": statistics.median(self.results["blockchain_verification"]) if self.results["blockchain_verification"] else 0,
            "target": 1.0,
            "passed": statistics.mean(self.results["blockchain_verification"]) < 1.0 if self.results["blockchain_verification"] else False
        }

    def test_verification_latency(self, iterations: int = 10) -> Dict:
        """Test end-to-end verification latency"""
        print("🔄 Testing End-to-End Verification Latency...")
        
        # Sample verification data
        verification_data = {
            "product_id": 51,
            "location": "Test Location",
            "notes": "Performance test",
            "qr_data": json.dumps({
                "product_id": 51,
                "product_name": "Test Product",
                "batch_number": "TEST-001",
                "qr_hash": "test_hash_12345",
                "timestamp": "2025-01-01T00:00:00Z"
            })
        }
        
        for i in range(iterations):
            print(f"  Verification Test {i+1}/{iterations}...", end=" ")
            
            # Test complete verification process
            result, duration, error = self.measure_time(
                self._perform_verification,
                verification_data
            )
            
            if error:
                print(f"❌ Error: {error}")
                self.results["error_rates"]["verification_latency"] = self.results["error_rates"].get("verification_latency", 0) + 1
            else:
                print(f"✅ {duration:.3f}s")
                self.results["verification_latency"].append(duration)
        
        return {
            "average": statistics.mean(self.results["verification_latency"]) if self.results["verification_latency"] else 0,
            "min": min(self.results["verification_latency"]) if self.results["verification_latency"] else 0,
            "max": max(self.results["verification_latency"]) if self.results["verification_latency"] else 0,
            "median": statistics.median(self.results["verification_latency"]) if self.results["verification_latency"] else 0,
            "target": 3.0,
            "passed": statistics.mean(self.results["verification_latency"]) < 3.0 if self.results["verification_latency"] else False
        }

    def _perform_verification(self, verification_data: Dict):
        """Perform a complete verification process"""
        if not self.bearer_token:
            raise Exception("Bearer token required for verification testing")
        
        response = requests.post(
            f"{self.base_url}/api/v1/verifications/",
            headers=self.headers,
            json=verification_data,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Verification failed: {response.status_code} - {response.text}")
        
        return response.json()

    def test_concurrent_verifications(self, concurrent_users: int = 5, iterations_per_user: int = 3) -> Dict:
        """Test system performance under concurrent load"""
        print(f"👥 Testing Concurrent Verifications ({concurrent_users} users, {iterations_per_user} iterations each)...")
        
        def user_verification(user_id: int):
            """Simulate a user performing verifications"""
            user_results = []
            for i in range(iterations_per_user):
                verification_data = {
                    "product_id": 51,
                    "location": f"User {user_id} Location",
                    "notes": f"Concurrent test {i+1}",
                    "qr_data": json.dumps({
                        "product_id": 51,
                        "product_name": f"User {user_id} Product",
                        "batch_number": f"USER-{user_id}-{i+1}",
                        "qr_hash": f"user_{user_id}_hash_{i+1}",
                        "timestamp": "2025-01-01T00:00:00Z"
                    })
                }
                
                result, duration, error = self.measure_time(
                    self._perform_verification,
                    verification_data
                )
                
                if not error:
                    user_results.append(duration)
            
            return user_results
        
        # Execute concurrent verifications
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(user_verification, i) for i in range(concurrent_users)]
            
            for future in as_completed(futures):
                user_results = future.result()
                self.results["concurrent_verifications"].extend(user_results)
        
        return {
            "total_verifications": len(self.results["concurrent_verifications"]),
            "average": statistics.mean(self.results["concurrent_verifications"]) if self.results["concurrent_verifications"] else 0,
            "min": min(self.results["concurrent_verifications"]) if self.results["concurrent_verifications"] else 0,
            "max": max(self.results["concurrent_verifications"]) if self.results["concurrent_verifications"] else 0,
            "median": statistics.median(self.results["concurrent_verifications"]) if self.results["concurrent_verifications"] else 0,
            "concurrent_users": concurrent_users
        }

    def test_api_endpoints_performance(self) -> Dict:
        """Test API endpoint response times"""
        print("🌐 Testing API Endpoints Performance...")
        
        endpoints = [
            ("/api/v1/products/", "GET"),
            ("/api/v1/analytics/overview", "GET"),
            ("/api/v1/verifications/", "GET"),
        ]
        
        endpoint_results = {}
        
        for endpoint, method in endpoints:
            print(f"  Testing {method} {endpoint}...", end=" ")
            
            times = []
            for i in range(5):  # Test each endpoint 5 times
                start_time = time.time()
                try:
                    if method == "GET":
                        response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers, timeout=10)
                    else:
                        response = requests.post(f"{self.base_url}{endpoint}", headers=self.headers, timeout=10)
                    
                    end_time = time.time()
                    duration = end_time - start_time
                    times.append(duration)
                    
                except Exception as e:
                    print(f"❌ Error: {e}")
                    continue
            
            if times:
                endpoint_results[endpoint] = {
                    "average": statistics.mean(times),
                    "min": min(times),
                    "max": max(times),
                    "median": statistics.median(times)
                }
                print(f"✅ {statistics.mean(times):.3f}s avg")
            else:
                print("❌ No successful requests")
        
        return endpoint_results

    def run_comprehensive_test(self, iterations: int = 10, concurrent_users: int = 5):
        """Run comprehensive performance testing"""
        print("🚀 Starting Comprehensive Performance Testing")
        print("=" * 60)
        
        # Test individual components
        qr_results = self.test_qr_processing_performance(iterations)
        ipfs_results = self.test_ipfs_retrieval_performance(iterations)
        blockchain_results = self.test_blockchain_verification_performance(iterations)
        verification_results = self.test_verification_latency(iterations)
        
        # Test concurrent performance
        concurrent_results = self.test_concurrent_verifications(concurrent_users, 3)
        
        # Test API endpoints
        api_results = self.test_api_endpoints_performance()
        
        # Compile results
        self.results["summary"] = {
            "qr_processing": qr_results,
            "ipfs_retrieval": ipfs_results,
            "blockchain_verification": blockchain_results,
            "verification_latency": verification_results,
            "concurrent_verifications": concurrent_results,
            "api_endpoints": api_results
        }
        
        return self.results

    def generate_report(self) -> str:
        """Generate a comprehensive performance report"""
        if "summary" not in self.results:
            return "No test results available. Run tests first."
        
        summary = self.results["summary"]
        
        report = []
        report.append("📊 PERFORMANCE TESTING REPORT")
        report.append("=" * 60)
        report.append("")
        
        # QR Processing Performance
        qr = summary["qr_processing"]
        report.append("🔍 QR Code Processing Performance:")
        report.append(f"  Average: {qr['average']:.3f}s (Target: <{qr['target']}s)")
        report.append(f"  Min: {qr['min']:.3f}s, Max: {qr['max']:.3f}s, Median: {qr['median']:.3f}s")
        report.append(f"  Status: {'✅ PASSED' if qr['passed'] else '❌ FAILED'}")
        report.append("")
        
        # IPFS Retrieval Performance
        ipfs = summary["ipfs_retrieval"]
        report.append("🌐 IPFS Data Retrieval Performance:")
        report.append(f"  Average: {ipfs['average']:.3f}s (Target: <{ipfs['target']}s)")
        report.append(f"  Min: {ipfs['min']:.3f}s, Max: {ipfs['max']:.3f}s, Median: {ipfs['median']:.3f}s")
        report.append(f"  Status: {'✅ PASSED' if ipfs['passed'] else '❌ FAILED'}")
        report.append("")
        
        # Blockchain Verification Performance
        blockchain = summary["blockchain_verification"]
        report.append("⛓️ Blockchain Verification Performance:")
        report.append(f"  Average: {blockchain['average']:.3f}s (Target: <{blockchain['target']}s)")
        report.append(f"  Min: {blockchain['min']:.3f}s, Max: {blockchain['max']:.3f}s, Median: {blockchain['median']:.3f}s")
        report.append(f"  Status: {'✅ PASSED' if blockchain['passed'] else '❌ FAILED'}")
        report.append("")
        
        # Verification Latency
        verification = summary["verification_latency"]
        report.append("🔄 End-to-End Verification Latency:")
        report.append(f"  Average: {verification['average']:.3f}s (Target: <{verification['target']}s)")
        report.append(f"  Min: {verification['min']:.3f}s, Max: {verification['max']:.3f}s, Median: {verification['median']:.3f}s")
        report.append(f"  Status: {'✅ PASSED' if verification['passed'] else '❌ FAILED'}")
        report.append("")
        
        # Concurrent Performance
        concurrent = summary["concurrent_verifications"]
        report.append("👥 Concurrent Verification Performance:")
        report.append(f"  Total Verifications: {concurrent['total_verifications']}")
        report.append(f"  Concurrent Users: {concurrent['concurrent_users']}")
        report.append(f"  Average: {concurrent['average']:.3f}s")
        report.append(f"  Min: {concurrent['min']:.3f}s, Max: {concurrent['max']:.3f}s, Median: {concurrent['median']:.3f}s")
        report.append("")
        
        # API Endpoints Performance
        api = summary["api_endpoints"]
        report.append("🌐 API Endpoints Performance:")
        for endpoint, stats in api.items():
            report.append(f"  {endpoint}: {stats['average']:.3f}s avg")
        report.append("")
        
        # Error Rates
        if self.results["error_rates"]:
            report.append("❌ Error Rates:")
            for component, count in self.results["error_rates"].items():
                report.append(f"  {component}: {count} errors")
            report.append("")
        
        # Overall Assessment
        passed_tests = sum([
            qr['passed'],
            ipfs['passed'],
            blockchain['passed'],
            verification['passed']
        ])
        
        total_tests = 4
        report.append("📈 Overall Performance Assessment:")
        report.append(f"  Tests Passed: {passed_tests}/{total_tests}")
        report.append(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            report.append("  Status: ✅ ALL TESTS PASSED - System meets performance targets")
        elif passed_tests >= total_tests * 0.75:
            report.append("  Status: ⚠️ MOSTLY PASSED - Minor performance issues detected")
        else:
            report.append("  Status: ❌ FAILED - Significant performance issues detected")
        
        return "\n".join(report)

def main():
    """Main function to run performance tests"""
    print("🚀 Anti-Counterfeit System Performance Testing")
    print("=" * 60)
    
    # Configuration
    BASE_URL = "http://localhost:8000"
    BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzQHMuY29tIiwiZXhwIjoxNzU2ODQxNTM2fQ.beJPjNuwTLCGJoV4Fl0qAUKtGvQHxlaRdDfk18bs3y0"
    
    # Initialize tester
    tester = PerformanceTester(BASE_URL, BEARER_TOKEN)
    
    try:
        # Run comprehensive tests
        results = tester.run_comprehensive_test(iterations=10, concurrent_users=5)
        
        # Generate and display report
        report = tester.generate_report()
        print("\n" + report)
        
        # Save results to file
        with open("performance_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📁 Detailed results saved to: performance_test_results.json")
        
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
